#!/usr/bin/env python3
"""
Claim에 대한 반증(Disconfirming Evidence) 자동 검색.
각 Claim을 분석하여 반대 가설을 생성하고, 이를 검색 쿼리로 변환하여
반증 후보를 자동 수집한다.

사용법:
  python scripts/generate-disconfirming.py <project-name>
  python scripts/generate-disconfirming.py <project-name> --division market
  python scripts/generate-disconfirming.py <project-name> --claim-id MGE-01
  python scripts/generate-disconfirming.py <project-name> --high-impact-only
  python scripts/generate-disconfirming.py <project-name> --dry-run

모드:
  --dry-run (기본에 가까움): 쿼리 생성만 수행. 에이전트가 WebSearch/WebFetch로 검색
  검색 모드: requests로 직접 검색 (standalone 사용 시). --dry-run 없이 실행
"""

import argparse
import glob
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import yaml

try:
    import requests
except ImportError:
    requests = None  # --dry-run 모드에서는 불필요


# ============================================================
# 데이터 클래스
# ============================================================

@dataclass
class Claim:
    """리서치 산출물에서 추출된 단일 Claim"""
    id: str                          # 예: MGE-01
    claim: str                       # Claim 텍스트
    confidence: str = "unverified"   # high | medium | low | unverified
    strategic_impact: str = "medium" # high | medium | low
    division: str = ""               # 소속 Division
    source_file: str = ""            # 원본 파일 경로
    existing_disconfirming: str = "" # 기존 반증 내용


@dataclass
class DisconfirmingEvidence:
    """반증 검색 결과 단건"""
    query: str
    source: str = ""
    title: str = ""
    summary: str = ""
    strength: str = "irrelevant"  # strong | moderate | weak | irrelevant
    implication: str = ""


@dataclass
class ClaimReport:
    """단일 Claim에 대한 반증 보고서"""
    claim_id: str
    claim: str
    confidence: str
    strategic_impact: str
    queries_generated: List[str] = field(default_factory=list)
    evidence_found: List[DisconfirmingEvidence] = field(default_factory=list)
    recommendation: str = ""


# ============================================================
# 긍정→부정 키워드 매핑
# ============================================================

# 한국어 매핑
NEGATION_MAP_KO: Dict[str, List[str]] = {
    '성장': ['하락', '둔화', '정체', '축소'],
    '증가': ['감소', '하락', '정체'],
    '기회': ['위협', '리스크', '장벽'],
    '강점': ['약점', '한계', '취약점'],
    '성공': ['실패', '좌절', '철수'],
    '확대': ['축소', '철수', '중단'],
    '혁신': ['정체', '뒤처짐', '레거시'],
    '상승': ['하락', '하강', '감소'],
    '호조': ['부진', '악화', '침체'],
    '수익': ['손실', '적자', '비용 증가'],
    '선도': ['후발', '추격', '뒤처짐'],
    '우위': ['열위', '약세', '경쟁 열위'],
    '급증': ['급감', '급락', '감소세'],
    '진출': ['철수', '포기', '실패'],
    '효과': ['부작용', '역효과', '비효율'],
    '최적': ['차선', '비효율', '부적합'],
    '유리': ['불리', '불리한 조건', '장벽'],
    '긍정': ['부정', '비관', '우려'],
}

# 영어 매핑
NEGATION_MAP_EN: Dict[str, List[str]] = {
    'growth': ['decline', 'stagnation', 'contraction', 'slowdown'],
    'increase': ['decrease', 'drop', 'fall', 'reduction'],
    'opportunity': ['threat', 'risk', 'barrier', 'challenge'],
    'leading': ['lagging', 'trailing', 'behind', 'losing'],
    'success': ['failure', 'setback', 'collapse'],
    'expansion': ['contraction', 'withdrawal', 'shutdown'],
    'innovation': ['stagnation', 'legacy', 'outdated'],
    'profit': ['loss', 'deficit', 'cost overrun'],
    'advantage': ['disadvantage', 'weakness', 'vulnerability'],
    'strong': ['weak', 'fragile', 'declining'],
    'rising': ['falling', 'dropping', 'sinking'],
    'dominant': ['marginal', 'niche', 'losing share'],
    'optimal': ['suboptimal', 'inefficient', 'poor fit'],
    'positive': ['negative', 'pessimistic', 'concerning'],
    'surge': ['plunge', 'crash', 'collapse'],
}


# ============================================================
# Claim 추출기
# ============================================================

class ClaimExtractor:
    """리서치 산출물에서 Claim 추출"""

    def extract_from_findings(self, findings_dir: str,
                              division_filter: Optional[str] = None,
                              claim_id_filter: Optional[str] = None) -> List[Claim]:
        """findings/{division}/ 내 YAML에서 claims 섹션 추출"""
        claims = []

        if not os.path.isdir(findings_dir):
            print(f"[경고] findings 디렉토리 없음: {findings_dir}", file=sys.stderr)
            return claims

        # YAML 파일 탐색
        yaml_pattern = os.path.join(findings_dir, "**", "*.yaml")
        yaml_files = glob.glob(yaml_pattern, recursive=True)
        yml_pattern = os.path.join(findings_dir, "**", "*.yml")
        yaml_files.extend(glob.glob(yml_pattern, recursive=True))

        for fpath in sorted(yaml_files):
            # golden-facts.yaml 등 비 Claim 파일 제외
            basename = os.path.basename(fpath)
            if basename in ("golden-facts.yaml", "golden-facts.yml"):
                continue

            # Division 필터
            if division_filter:
                rel = os.path.relpath(fpath, findings_dir)
                if not rel.startswith(division_filter):
                    continue

            extracted = self._parse_claims_from_file(fpath)
            claims.extend(extracted)

        # Claim ID 필터
        if claim_id_filter:
            claims = [c for c in claims if c.id == claim_id_filter]

        return claims

    def extract_high_priority(self, claims: List[Claim]) -> List[Claim]:
        """strategic_impact: high인 Claim만 필터"""
        return [c for c in claims if c.strategic_impact == "high"]

    def _parse_claims_from_file(self, fpath: str) -> List[Claim]:
        """단일 YAML 파일에서 Claim 추출"""
        results = []
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"[경고] YAML 파싱 실패: {fpath} — {e}", file=sys.stderr)
            return results

        if not isinstance(data, dict):
            return results

        # Division 추론 (파일 경로 기반)
        division = self._infer_division(fpath)

        # claims 섹션 파싱
        raw_claims = data.get("claims", [])
        if not isinstance(raw_claims, list):
            return results

        # 기존 disconfirming 수집 (evidence 섹션)
        disconfirming_map = self._extract_disconfirming(data)

        for rc in raw_claims:
            if not isinstance(rc, dict):
                continue
            claim_id = rc.get("id", "")
            if not claim_id:
                continue

            claim = Claim(
                id=claim_id,
                claim=rc.get("claim", ""),
                confidence=rc.get("confidence", "unverified"),
                strategic_impact=rc.get("strategic_impact", "medium"),
                division=division,
                source_file=fpath,
                existing_disconfirming=disconfirming_map.get(claim_id, ""),
            )
            results.append(claim)

        return results

    def _infer_division(self, fpath: str) -> str:
        """파일 경로에서 Division명 추론"""
        # findings/market/... → "market"
        parts = fpath.replace("\\", "/").split("/")
        try:
            idx = parts.index("findings")
            if idx + 1 < len(parts):
                return parts[idx + 1]
        except ValueError:
            pass
        return "unknown"

    def _extract_disconfirming(self, data: dict) -> Dict[str, str]:
        """evidence 섹션에서 기존 disconfirming 내용 수집"""
        result = {}
        evidence_list = data.get("evidence", [])
        if not isinstance(evidence_list, list):
            return result

        for ev in evidence_list:
            if not isinstance(ev, dict):
                continue
            claim_id = ev.get("claim_id", "")
            disconf = ev.get("disconfirming", [])
            if isinstance(disconf, list):
                summaries = []
                for d in disconf:
                    if isinstance(d, dict):
                        summaries.append(d.get("summary", ""))
                    elif isinstance(d, str):
                        summaries.append(d)
                result[claim_id] = " | ".join(s for s in summaries if s)
            elif isinstance(disconf, str):
                result[claim_id] = disconf

        return result


# ============================================================
# 반증 쿼리 생성기
# ============================================================

class DisconfirmingQueryGenerator:
    """Claim → 반대 가설 → 검색 쿼리 변환"""

    def generate_queries(self, claim: Claim) -> List[str]:
        """
        Claim을 분석하여 3~5개의 반증 검색 쿼리를 생성한다.

        전략:
        1. 부정 반전(Negation): "시장이 성장한다" → "시장 성장 둔화 OR 시장 축소"
        2. 대안 가설(Alternative): "A가 최적이다" → "B가 A보다 우수한 사례"
        3. 실패 사례(Failure): "이 전략이 효과적이다" → "유사 전략 실패 사례"
        4. 시점 반전(Temporal): "성장 추세이다" → "최근 하락 OR 트렌드 반전 징후"
        5. 조건 한정(Condition): "X가 성립한다" → "X가 성립하지 않는 조건"
        """
        queries = []
        keywords = self._extract_keywords(claim.claim)
        negated = self._negate_sentiment(keywords)

        # 전략 1: 부정 반전 쿼리
        if negated:
            neg_query = " OR ".join(negated[:3])
            # 원본 키워드 중 주제어 유지
            subject_kws = [k for k in keywords if k not in self._get_sentiment_keywords()]
            if subject_kws:
                queries.append(f"{' '.join(subject_kws[:3])} {neg_query}")
            else:
                queries.append(neg_query)

        # 전략 2: 대안 가설 쿼리
        alt_query = self._generate_alternative_query(claim.claim, keywords)
        if alt_query:
            queries.append(alt_query)

        # 전략 3: 실패 사례 쿼리
        failure_query = self._generate_failure_query(claim.claim, keywords)
        if failure_query:
            queries.append(failure_query)

        # 전략 4: 시점 반전 쿼리
        temporal_query = self._generate_temporal_query(claim.claim, keywords)
        if temporal_query:
            queries.append(temporal_query)

        # 전략 5: 조건 한정 쿼리
        condition_query = self._generate_condition_query(claim.claim, keywords)
        if condition_query:
            queries.append(condition_query)

        # 중복 제거 + 최대 5개 제한
        seen = set()
        unique = []
        for q in queries:
            normalized = q.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique.append(q.strip())
        return unique[:5]

    def _extract_keywords(self, claim_text: str) -> List[str]:
        """Claim에서 핵심 키워드 추출"""
        # 불용어 제거 (한국어 + 영어)
        stopwords_ko = {
            '의', '가', '이', '은', '는', '을', '를', '에', '에서', '으로', '로',
            '와', '과', '도', '만', '까지', '부터', '보다', '처럼', '같은',
            '할', '한', '하는', '된', '되는', '있는', '있다', '없다', '등',
            '및', '그', '이', '저', '것', '수', '때', '년', '월', '일',
        }
        stopwords_en = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'shall',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'as', 'into', 'through', 'during', 'before', 'after',
            'and', 'but', 'or', 'nor', 'not', 'so', 'yet', 'both',
            'that', 'this', 'these', 'those', 'it', 'its',
        }
        all_stopwords = stopwords_ko | stopwords_en

        # 숫자+단위 패턴 보존 (예: 8%, $15B, 2026년)
        # 일반 토큰화
        tokens = re.findall(r'[\w\$%\.]+', claim_text)
        keywords = [t for t in tokens if t.lower() not in all_stopwords and len(t) > 1]

        return keywords

    def _negate_sentiment(self, keywords: List[str]) -> List[str]:
        """긍정 키워드 → 부정 키워드 변환"""
        negated = []
        for kw in keywords:
            kw_lower = kw.lower()
            # 한국어 매핑
            if kw in NEGATION_MAP_KO:
                negated.extend(NEGATION_MAP_KO[kw])
            # 영어 매핑
            elif kw_lower in NEGATION_MAP_EN:
                negated.extend(NEGATION_MAP_EN[kw_lower])
            else:
                # 부분 매칭: 키워드가 매핑 키를 포함하는 경우
                for map_key, map_vals in NEGATION_MAP_KO.items():
                    if map_key in kw:
                        negated.extend(map_vals)
                        break
                for map_key, map_vals in NEGATION_MAP_EN.items():
                    if map_key in kw_lower:
                        negated.extend(map_vals)
                        break

        return list(dict.fromkeys(negated))  # 순서 보존 중복 제거

    def _get_sentiment_keywords(self) -> set:
        """매핑에 등록된 감성 키워드 집합"""
        keys = set(NEGATION_MAP_KO.keys())
        keys.update(k.lower() for k in NEGATION_MAP_EN.keys())
        return keys

    def _generate_alternative_query(self, claim_text: str, keywords: List[str]) -> str:
        """대안 가설 쿼리 생성"""
        subject_kws = [k for k in keywords[:4] if k not in self._get_sentiment_keywords()]
        if not subject_kws:
            return ""
        subject = " ".join(subject_kws[:3])

        # 한국어/영어 혼합 Claim 판별
        has_korean = bool(re.search(r'[가-힣]', claim_text))
        if has_korean:
            return f"{subject} 대안 OR 다른 접근 OR 반론"
        else:
            return f"{subject} alternative OR counter-argument OR criticism"

    def _generate_failure_query(self, claim_text: str, keywords: List[str]) -> str:
        """실패 사례 쿼리 생성"""
        subject_kws = [k for k in keywords[:4] if k not in self._get_sentiment_keywords()]
        if not subject_kws:
            return ""
        subject = " ".join(subject_kws[:3])

        has_korean = bool(re.search(r'[가-힣]', claim_text))
        if has_korean:
            return f"{subject} 실패 사례 OR 리스크 OR 한계"
        else:
            return f"{subject} failure case OR risk OR limitation"

    def _generate_temporal_query(self, claim_text: str, keywords: List[str]) -> str:
        """시점 반전 쿼리 생성"""
        subject_kws = [k for k in keywords[:4] if k not in self._get_sentiment_keywords()]
        if not subject_kws:
            return ""
        subject = " ".join(subject_kws[:3])

        # 연도 추출
        years = re.findall(r'20\d{2}', claim_text)
        year_ctx = years[-1] if years else "2025"

        has_korean = bool(re.search(r'[가-힣]', claim_text))
        if has_korean:
            return f"{subject} 최근 하락 OR 트렌드 반전 OR 전망 악화 {year_ctx}"
        else:
            return f"{subject} recent decline OR trend reversal OR outlook downgrade {year_ctx}"

    def _generate_condition_query(self, claim_text: str, keywords: List[str]) -> str:
        """조건 한정 쿼리 생성"""
        subject_kws = [k for k in keywords[:4] if k not in self._get_sentiment_keywords()]
        if not subject_kws:
            return ""
        subject = " ".join(subject_kws[:3])

        has_korean = bool(re.search(r'[가-힣]', claim_text))
        if has_korean:
            return f"{subject} 예외 상황 OR 성립하지 않는 조건 OR 전제 조건 붕괴"
        else:
            return f"{subject} exception OR condition not met OR assumption invalid"


# ============================================================
# 반증 검색 실행기
# ============================================================

class DisconfirmingSearcher:
    """생성된 쿼리로 실제 검색 수행 (standalone 모드)"""

    # Google Custom Search API 엔드포인트
    GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY", "")
        self.cx = os.environ.get("GOOGLE_CX", "")

    def search(self, queries: List[str], claim: Claim,
               max_results_per_query: int = 3) -> List[DisconfirmingEvidence]:
        """
        검색 전략:
        1. 쿼리별로 웹 검색 실행 (최대 3개 결과)
        2. 결과 페이지 요약 수집 (제목 + snippet)
        3. Claim과의 관련성 판정
        4. 반증 강도(strength) 판정
        """
        if requests is None:
            print("[오류] requests 패키지 미설치. pip install requests", file=sys.stderr)
            return []

        all_evidence = []

        for query in queries:
            results = self._execute_search(query, max_results_per_query)
            for result in results:
                strength = self.assess_strength(claim, result.get("snippet", ""))
                evidence = DisconfirmingEvidence(
                    query=query,
                    source=result.get("link", ""),
                    title=result.get("title", ""),
                    summary=result.get("snippet", ""),
                    strength=strength,
                    implication=self._generate_implication(claim, strength, result.get("snippet", "")),
                )
                all_evidence.append(evidence)

        return all_evidence

    def _execute_search(self, query: str, max_results: int) -> List[dict]:
        """Google Custom Search API 호출"""
        if not self.api_key or not self.cx:
            print(f"[경고] Google API 키/CX 미설정. 검색 건너뜀: {query}", file=sys.stderr)
            return []

        try:
            params = {
                "key": self.api_key,
                "cx": self.cx,
                "q": query,
                "num": min(max_results, 10),
            }
            resp = requests.get(self.GOOGLE_SEARCH_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])[:max_results]
        except Exception as e:
            print(f"[경고] 검색 실패: {query} — {e}", file=sys.stderr)
            return []

    def assess_strength(self, claim: Claim, evidence_summary: str) -> str:
        """
        반증 강도 판정 (키워드 기반 휴리스틱).
        에이전트 환경에서는 LLM이 더 정밀하게 판정할 수 있으므로,
        이 함수는 standalone 실행 시의 근사 판정용이다.
        """
        if not evidence_summary:
            return "irrelevant"

        claim_keywords = set(re.findall(r'[\w]+', claim.claim.lower()))
        evidence_keywords = set(re.findall(r'[\w]+', evidence_summary.lower()))

        # 공통 키워드 비율
        overlap = claim_keywords & evidence_keywords
        overlap_ratio = len(overlap) / max(len(claim_keywords), 1)

        # 반증 신호 키워드
        strong_signals_ko = ['반박', '틀렸', '오류', '실패', '하락', '급감', '철수', '붕괴', '위기']
        strong_signals_en = ['refute', 'disprove', 'wrong', 'fail', 'decline', 'crash', 'collapse', 'crisis']
        moderate_signals_ko = ['둔화', '감소', '우려', '리스크', '약화', '제한', '한계']
        moderate_signals_en = ['slow', 'decrease', 'concern', 'risk', 'weaken', 'limit', 'challenge']

        summary_lower = evidence_summary.lower()

        has_strong = any(s in summary_lower for s in strong_signals_ko + strong_signals_en)
        has_moderate = any(s in summary_lower for s in moderate_signals_ko + moderate_signals_en)

        if overlap_ratio >= 0.2 and has_strong:
            return "strong"
        elif overlap_ratio >= 0.15 and has_moderate:
            return "moderate"
        elif overlap_ratio >= 0.1:
            return "weak"
        else:
            return "irrelevant"

    def _generate_implication(self, claim: Claim, strength: str, summary: str) -> str:
        """반증 강도에 따른 시사점 생성"""
        if strength == "strong":
            return f"Claim '{claim.id}'을 직접 반박하는 증거. confidence 하향 및 Claim 수정 검토 필요"
        elif strength == "moderate":
            return f"Claim '{claim.id}'의 전제를 간접적으로 약화시키는 정보. 하방 리스크 요인으로 반영 검토"
        elif strength == "weak":
            return f"관련은 있으나 반박력 약함. 참고 수준으로 기록"
        else:
            return "Claim과 무관한 결과"


# ============================================================
# 보고서 생성기
# ============================================================

class ReportGenerator:
    """반증 검색 결과를 구조화된 YAML 보고서로 출력"""

    def generate(self, project: str, claim_reports: List[ClaimReport],
                 output_path: str, dry_run: bool = False) -> dict:
        """보고서 딕셔너리 생성 및 파일 저장"""
        # 요약 집계
        total = len(claim_reports)
        strong_count = sum(
            1 for cr in claim_reports
            if any(e.strength == "strong" for e in cr.evidence_found)
        )
        moderate_count = sum(
            1 for cr in claim_reports
            if any(e.strength == "moderate" for e in cr.evidence_found)
            and not any(e.strength == "strong" for e in cr.evidence_found)
        )
        weak_only_count = sum(
            1 for cr in claim_reports
            if cr.evidence_found
            and all(e.strength in ("weak", "irrelevant") for e in cr.evidence_found)
        )
        no_evidence = sum(1 for cr in claim_reports if not cr.evidence_found)

        report = {
            "disconfirming_report": {
                "project": project,
                "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "mode": "dry_run" if dry_run else "search",
                "summary": {
                    "total_claims_checked": total,
                    "claims_with_strong_disconfirming": strong_count,
                    "claims_with_moderate": moderate_count,
                    "claims_with_weak_only": weak_only_count,
                    "claims_no_disconfirming": no_evidence,
                },
                "details": [],
            }
        }

        for cr in claim_reports:
            detail = {
                "claim_id": cr.claim_id,
                "claim": cr.claim,
                "confidence": cr.confidence,
                "strategic_impact": cr.strategic_impact,
                "queries_generated": cr.queries_generated,
            }

            if cr.evidence_found:
                detail["evidence_found"] = [
                    {
                        "query": e.query,
                        "source": e.source,
                        "title": e.title,
                        "summary": e.summary,
                        "strength": e.strength,
                        "implication": e.implication,
                    }
                    for e in cr.evidence_found
                ]

            if cr.recommendation:
                detail["recommendation"] = cr.recommendation

            report["disconfirming_report"]["details"].append(detail)

        # 파일 저장
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(report, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        return report


# ============================================================
# 추천 생성기
# ============================================================

def generate_recommendation(claim: Claim, evidence_list: List[DisconfirmingEvidence]) -> str:
    """반증 결과 기반 추천 사항 생성"""
    strengths = [e.strength for e in evidence_list]

    if "strong" in strengths:
        strong_count = strengths.count("strong")
        if claim.confidence == "high":
            return (
                f"strong 반증 {strong_count}건 발견. "
                f"confidence를 high → medium으로 하향 검토. "
                f"Claim 수치 범위 확대 또는 조건 한정 권장"
            )
        else:
            return (
                f"strong 반증 {strong_count}건 발견. "
                f"Claim 수정 또는 폐기 검토. "
                f"반증 내용을 disconfirming 필드에 상세 기재 필수"
            )
    elif "moderate" in strengths:
        mod_count = strengths.count("moderate")
        return (
            f"moderate 반증 {mod_count}건 발견. "
            f"하방 리스크로 반영하고 disconfirming 필드 보강 권장"
        )
    elif "weak" in strengths:
        return "weak 반증만 발견. 현재 confidence 유지하되 disconfirming 필드에 검색 내역 기재"
    else:
        return "검색 범위 내 유의미한 반증 미발견. disconfirming 필드에 검색 방법 및 쿼리 명시"


# ============================================================
# 메인 실행
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="반증(Disconfirming Evidence) 자동 검색",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 전체 프로젝트 Claim에 대해 쿼리 생성 (dry-run)
  python scripts/generate-disconfirming.py my-project --dry-run

  # Market Division의 high-impact Claim만
  python scripts/generate-disconfirming.py my-project --division market --high-impact-only

  # 특정 Claim만
  python scripts/generate-disconfirming.py my-project --claim-id MGE-01

  # 실제 검색 수행 (Google API 키 필요)
  python scripts/generate-disconfirming.py my-project
        """,
    )
    parser.add_argument("project", help="프로젝트 디렉토리명")
    parser.add_argument("--division", help="특정 Division만 (예: market, product, capability, finance)")
    parser.add_argument("--claim-id", help="특정 Claim ID만 (예: MGE-01)")
    parser.add_argument("--high-impact-only", action="store_true",
                        help="strategic_impact: high인 Claim만 처리")
    parser.add_argument("--output", help="출력 파일 경로 (기본: {project}/qa/disconfirming-report.yaml)")
    parser.add_argument("--dry-run", action="store_true",
                        help="쿼리 생성만 수행 (검색 실행 안 함). 에이전트 연동 시 기본 모드")

    args = parser.parse_args()

    # 프로젝트 경로 확인
    # 스크립트 위치 기준 상위 = 프로젝트 루트
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    project_dir = os.path.join(project_root, args.project)

    if not os.path.isdir(project_dir):
        print(f"[오류] 프로젝트 디렉토리 없음: {project_dir}", file=sys.stderr)
        sys.exit(1)

    findings_dir = os.path.join(project_dir, "findings")
    output_path = args.output or os.path.join(project_dir, "qa", "disconfirming-report.yaml")

    # 1단계: Claim 추출
    print(f"[1/4] Claim 추출 중... (project={args.project})")
    extractor = ClaimExtractor()
    claims = extractor.extract_from_findings(
        findings_dir,
        division_filter=args.division,
        claim_id_filter=args.claim_id,
    )

    if args.high_impact_only:
        claims = extractor.extract_high_priority(claims)

    if not claims:
        print("[완료] 조건에 맞는 Claim이 없습니다.", file=sys.stderr)
        sys.exit(0)

    print(f"  → {len(claims)}개 Claim 발견")

    # 2단계: 반증 쿼리 생성
    print(f"[2/4] 반증 쿼리 생성 중...")
    generator = DisconfirmingQueryGenerator()
    claim_queries = {}
    for claim in claims:
        queries = generator.generate_queries(claim)
        claim_queries[claim.id] = queries
        print(f"  → {claim.id}: {len(queries)}개 쿼리 생성")

    # 3단계: 검색 실행 (dry-run이 아닌 경우)
    searcher = DisconfirmingSearcher() if not args.dry_run else None
    claim_reports = []

    if args.dry_run:
        print(f"[3/4] dry-run 모드 — 검색 건너뜀")
        for claim in claims:
            queries = claim_queries.get(claim.id, [])
            report = ClaimReport(
                claim_id=claim.id,
                claim=claim.claim,
                confidence=claim.confidence,
                strategic_impact=claim.strategic_impact,
                queries_generated=queries,
                recommendation="dry-run 모드. 에이전트가 WebSearch로 위 쿼리를 검색하여 반증 수집 필요",
            )
            claim_reports.append(report)
    else:
        print(f"[3/4] 반증 검색 실행 중...")
        for claim in claims:
            queries = claim_queries.get(claim.id, [])
            evidence = searcher.search(queries, claim)
            # irrelevant 제외
            relevant = [e for e in evidence if e.strength != "irrelevant"]
            recommendation = generate_recommendation(claim, relevant)

            report = ClaimReport(
                claim_id=claim.id,
                claim=claim.claim,
                confidence=claim.confidence,
                strategic_impact=claim.strategic_impact,
                queries_generated=queries,
                evidence_found=relevant,
                recommendation=recommendation,
            )
            claim_reports.append(report)
            strong = sum(1 for e in relevant if e.strength == "strong")
            moderate = sum(1 for e in relevant if e.strength == "moderate")
            print(f"  → {claim.id}: strong={strong}, moderate={moderate}")

    # 4단계: 보고서 생성
    print(f"[4/4] 보고서 생성 중... → {output_path}")
    report_gen = ReportGenerator()
    report = report_gen.generate(args.project, claim_reports, output_path, dry_run=args.dry_run)

    # 요약 출력
    summary = report["disconfirming_report"]["summary"]
    print()
    print("=" * 60)
    print("반증 검색 완료 요약")
    print("=" * 60)
    print(f"  총 Claim 검사:        {summary['total_claims_checked']}")
    print(f"  strong 반증 보유:      {summary['claims_with_strong_disconfirming']}")
    print(f"  moderate 반증 보유:    {summary['claims_with_moderate']}")
    print(f"  weak 반증만:           {summary['claims_with_weak_only']}")
    print(f"  반증 미발견:           {summary['claims_no_disconfirming']}")
    print(f"  보고서: {output_path}")

    if summary["claims_with_strong_disconfirming"] > 0:
        print()
        print("[주의] strong 반증이 발견된 Claim:")
        for cr in claim_reports:
            if any(e.strength == "strong" for e in cr.evidence_found):
                print(f"  - {cr.claim_id}: {cr.claim[:60]}...")
                print(f"    → {cr.recommendation}")

    print()


if __name__ == "__main__":
    main()
