#!/usr/bin/env python3
"""
Golden Facts vs 보고서 수치 자동 검증.
golden-facts.yaml의 모든 수치를 보고서(report-docs.md, report-slides.md)에서 찾아
일치/불일치를 판정하고 리포트를 생성한다.

사용법:
  python scripts/verify-facts.py <project-name>
  python scripts/verify-facts.py <project-name> --strict        # 허용 오차 없이 정확 일치
  python scripts/verify-facts.py <project-name> --tolerance 0.03 # 허용 오차 3%
  python scripts/verify-facts.py <project-name> --format csv     # CSV 리포트 출력
  python scripts/verify-facts.py <project-name> --report-only    # report-docs.md만 검증
"""

import argparse
import csv
import io
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("오류: pyyaml이 설치되지 않았습니다. pip install pyyaml 실행 후 재시도하세요.")
    sys.exit(1)


# ============================================================
# 데이터 클래스
# ============================================================

@dataclass
class Fact:
    """golden-facts.yaml의 개별 수치 항목"""
    id: str                     # GF-001
    category: str               # company-basic, market-size 등
    entity: str                 # 대상 엔터티명
    entity_label: str           # [그룹], [별도], [부문]
    metric: str                 # 지표명
    value: float                # 정규화된 수치
    raw_value: str              # 원본 값 문자열
    unit: str                   # 단위
    as_of: str                  # 기준 시점
    confidence: str             # [확정], [유력], [가정], [미확인]
    source_id: str              # S## 참조


@dataclass
class ReportNumber:
    """보고서에서 추출된 수치"""
    value: float                # 정규화된 수치
    raw_text: str               # 원본 텍스트
    unit: str                   # 감지된 단위
    gf_ref: Optional[str]       # [GF-###] 태그 (있는 경우)
    location: str               # 파일명:줄번호
    context: str                # 주변 텍스트 (매칭 보조용)
    line_number: int            # 줄번호


@dataclass
class MatchResult:
    """개별 수치 검증 결과"""
    fact_id: str
    metric: str
    golden_value: str           # 원본 표기
    report_value: str           # 보고서 표기
    diff_pct: float             # 차이 비율 (%)
    status: str                 # MATCH, WITHIN_TOLERANCE, MISMATCH, ROUNDING, MISSING, UNTRACKED
    report_location: str
    note: str = ""


@dataclass
class ConfidenceIssue:
    """confidence-prominence 위반 항목"""
    fact_id: str
    confidence: str
    location: str
    issue: str
    severity: str               # critical, warning


@dataclass
class VerificationReport:
    """전체 검증 결과"""
    project: str
    verified_at: str
    tolerance: float
    matches: List[MatchResult] = field(default_factory=list)
    confidence_issues: List[ConfidenceIssue] = field(default_factory=list)


# ============================================================
# A. Golden Facts 파서
# ============================================================

class GoldenFactsParser:
    """golden-facts.yaml 파싱 + 정규화"""

    # 한국어 수치 단위 매핑
    KR_UNITS = {
        '조': 1_000_000_000_000,
        '억': 100_000_000,
        '만': 10_000,
        '천': 1_000,
    }

    # 영어 수치 단위 매핑
    EN_UNITS = {
        'T': 1_000_000_000_000,   # Trillion
        'B': 1_000_000_000,       # Billion
        'M': 1_000_000,           # Million
        'K': 1_000,               # Thousand
    }

    def parse(self, facts_path: str) -> List[Fact]:
        """YAML 파싱 → Fact 객체 리스트"""
        with open(facts_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data or 'facts' not in data:
            print(f"경고: {facts_path}에 facts 키가 없습니다.")
            return []

        facts = []
        for item in data['facts']:
            raw_value = str(item.get('value', ''))
            unit = str(item.get('unit', ''))
            normalized = self.normalize_value(raw_value, unit)

            fact = Fact(
                id=str(item.get('id', '')),
                category=str(item.get('category', '')),
                entity=str(item.get('entity', '')),
                entity_label=str(item.get('entity_label', '')),
                metric=str(item.get('metric', '')),
                value=normalized,
                raw_value=raw_value,
                unit=unit,
                as_of=str(item.get('as_of', '')),
                confidence=str(item.get('confidence', '')),
                source_id=str(item.get('source_id', '')),
            )
            facts.append(fact)

        return facts

    def normalize_value(self, value_str: str, unit: str) -> float:
        """
        수치 정규화 (단위 통일).
        "$2.3B" → 2300000000
        "15.2%" → 15.2 (퍼센트는 숫자 그대로)
        "₩1.2조" → 1200000000000
        "4,500만" → 45000000
        "1210" (단위: 억원) → 121000000000
        """
        if value_str is None:
            return 0.0

        val_str = str(value_str).strip()

        # 쉼표 제거
        val_str = val_str.replace(',', '')

        # 퍼센트 처리: 숫자만 추출, 단위가 %이면 그대로 반환
        if unit == '%' or val_str.endswith('%'):
            num = self._extract_number(val_str.replace('%', ''))
            return num

        # 통화 기호 제거
        val_str = val_str.replace('$', '').replace('₩', '').replace('원', '')

        # 한국어 단위가 값에 포함된 경우
        for kr_unit, multiplier in self.KR_UNITS.items():
            if kr_unit in val_str:
                num = self._extract_number(val_str.replace(kr_unit, ''))
                return num * multiplier

        # 영어 단위가 값에 포함된 경우 (예: 2.3B, 15M)
        for en_unit, multiplier in self.EN_UNITS.items():
            if val_str.upper().endswith(en_unit):
                num = self._extract_number(val_str[:-1])
                return num * multiplier

        # 기본 숫자 추출
        num = self._extract_number(val_str)

        # 단위 필드에서 추가 배율 적용
        unit_lower = unit.lower().replace(' ', '')
        for kr_unit, multiplier in self.KR_UNITS.items():
            if kr_unit in unit_lower:
                return num * multiplier

        for en_unit, multiplier in self.EN_UNITS.items():
            if en_unit in unit.upper():
                return num * multiplier

        # 특수 단위: "억원", "조원" 등
        if '억원' in unit or '억' in unit:
            return num * 100_000_000
        if '조원' in unit or '조' in unit:
            return num * 1_000_000_000_000
        if '만원' in unit or '만' in unit:
            return num * 10_000

        return num

    def _extract_number(self, s: str) -> float:
        """문자열에서 숫자(소수 포함) 추출"""
        # 음수 포함 숫자 매칭
        match = re.search(r'-?\d+\.?\d*', s)
        if match:
            return float(match.group())
        return 0.0


# ============================================================
# B. 보고서 수치 추출기
# ============================================================

class ReportNumberExtractor:
    """보고서에서 수치 + [GF-###] 태그 추출"""

    # [GF-###] 태그 패턴
    GF_TAG_PATTERN = re.compile(r'\[GF-(\d+)\]')

    # 수치 패턴들
    NUMBER_PATTERNS = [
        # $숫자B/M/K (예: $56.9B, $2.3M)
        re.compile(r'\$[\d,]+\.?\d*\s*[TBMK]', re.IGNORECASE),
        # $숫자 (단위 없음, 예: $39M → 위에서 잡힘, $106.5M)
        re.compile(r'\$[\d,]+\.?\d*'),
        # 숫자% (예: 15.2%, -4.1%)
        re.compile(r'-?\d+\.?\d*\s*%'),
        # ₩숫자조/억/만 (예: ₩1.2조, ₩468억)
        re.compile(r'₩[\d,]+\.?\d*\s*[조억만]?원?'),
        # 한국어 수치 (예: 1,210억원, 95~110억원, 5~10억원)
        re.compile(r'[\d,]+\.?\d*\s*[~\-]\s*[\d,]+\.?\d*\s*억원'),
        re.compile(r'[\d,]+\.?\d*\s*억원'),
        re.compile(r'[\d,]+\.?\d*\s*조원'),
        re.compile(r'[\d,]+\.?\d*\s*만원'),
        re.compile(r'[\d,]+\.?\d*\s*만'),
    ]

    def extract_from_markdown(self, report_path: str) -> List[ReportNumber]:
        """마크다운 보고서에서 수치 추출"""
        if not os.path.exists(report_path):
            return []

        with open(report_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        results = []
        filename = os.path.basename(report_path)

        for line_num, line in enumerate(lines, 1):
            # [GF-###] 태그가 있는 수치 추출
            gf_numbers = self._extract_gf_tagged(line, filename, line_num)
            results.extend(gf_numbers)

            # 태그 없는 수치 추출
            bare_numbers = self._extract_bare_numbers(line, filename, line_num)
            results.extend(bare_numbers)

        return results

    def _extract_gf_tagged(self, line: str, filename: str, line_num: int) -> List[ReportNumber]:
        """[GF-###] 태그가 달린 수치 추출"""
        results = []
        for match in self.GF_TAG_PATTERN.finditer(line):
            gf_id = f"GF-{match.group(1)}"
            # 태그 주변에서 수치 찾기
            start = max(0, match.start() - 100)
            end = min(len(line), match.end() + 100)
            context = line[start:end].strip()

            # 주변 수치 추출
            for pattern in self.NUMBER_PATTERNS:
                for num_match in pattern.finditer(context):
                    raw_text = num_match.group()
                    normalized = self._normalize_report_number(raw_text)
                    unit = self._detect_unit(raw_text)
                    results.append(ReportNumber(
                        value=normalized,
                        raw_text=raw_text,
                        unit=unit,
                        gf_ref=gf_id,
                        location=f"{filename}:{line_num}",
                        context=context,
                        line_number=line_num,
                    ))

        return results

    def _extract_bare_numbers(self, line: str, filename: str, line_num: int) -> List[ReportNumber]:
        """태그 없는 수치 추출 (퍼지 매칭용)"""
        # [GF-###] 태그가 있는 줄은 태그 매칭에서 처리하므로 중복 방지
        if self.GF_TAG_PATTERN.search(line):
            return []

        results = []
        # 주변 컨텍스트 (줄 전체)
        context = line.strip()
        if not context:
            return results

        seen_spans = set()  # 중복 매칭 방지

        for pattern in self.NUMBER_PATTERNS:
            for match in pattern.finditer(line):
                span = (match.start(), match.end())
                # 이미 더 넓은 범위로 매칭된 경우 건너뜀
                if any(s[0] <= span[0] and s[1] >= span[1] and s != span for s in seen_spans):
                    continue
                seen_spans.add(span)

                raw_text = match.group()
                normalized = self._normalize_report_number(raw_text)
                unit = self._detect_unit(raw_text)

                # 컨텍스트: 매칭 위치 전후 50자
                ctx_start = max(0, match.start() - 50)
                ctx_end = min(len(line), match.end() + 50)
                ctx = line[ctx_start:ctx_end].strip()

                results.append(ReportNumber(
                    value=normalized,
                    raw_text=raw_text,
                    unit=unit,
                    gf_ref=None,
                    location=f"{filename}:{line_num}",
                    context=ctx,
                    line_number=line_num,
                ))

        return results

    def _normalize_report_number(self, raw: str) -> float:
        """보고서에서 추출한 수치를 정규화"""
        s = raw.strip().replace(',', '')

        # 퍼센트
        if '%' in s:
            num_match = re.search(r'-?\d+\.?\d*', s.replace('%', ''))
            return float(num_match.group()) if num_match else 0.0

        # 통화 기호 제거
        s = s.replace('$', '').replace('₩', '')

        # 한국어 단위
        kr_units = {'조': 1e12, '억': 1e8, '만': 1e4}
        for unit_str, mult in kr_units.items():
            if unit_str in s:
                s_clean = s.replace(unit_str, '').replace('원', '').strip()
                num_match = re.search(r'-?\d+\.?\d*', s_clean)
                if num_match:
                    return float(num_match.group()) * mult
                return 0.0

        # 영어 단위 (B/M/K/T)
        en_map = {'T': 1e12, 'B': 1e9, 'M': 1e6, 'K': 1e3}
        for suffix, mult in en_map.items():
            if s.upper().endswith(suffix):
                num_match = re.search(r'-?\d+\.?\d*', s[:-1])
                if num_match:
                    return float(num_match.group()) * mult
                return 0.0

        # 일반 숫자
        s = s.replace('원', '').strip()
        num_match = re.search(r'-?\d+\.?\d*', s)
        return float(num_match.group()) if num_match else 0.0

    def _detect_unit(self, raw: str) -> str:
        """수치 문자열에서 단위 감지"""
        if '%' in raw:
            return '%'
        if '$' in raw:
            if re.search(r'[Tt]', raw) and not re.search(r'[Bb]', raw):
                return 'USD_T'
            if re.search(r'[Bb]', raw):
                return 'USD_B'
            if re.search(r'[Mm]', raw):
                return 'USD_M'
            if re.search(r'[Kk]', raw):
                return 'USD_K'
            return 'USD'
        if '₩' in raw or '원' in raw:
            if '조' in raw:
                return 'KRW_조'
            if '억' in raw:
                return 'KRW_억'
            if '만' in raw:
                return 'KRW_만'
            return 'KRW'
        if '억' in raw:
            return 'KRW_억'
        if '조' in raw:
            return 'KRW_조'
        if '만' in raw:
            return 'KRW_만'
        return 'unknown'


# ============================================================
# C. 검증 엔진
# ============================================================

class FactVerifier:
    """수치 대조 + 불일치 판정"""

    def verify_all(self, facts: List[Fact], report_numbers: List[ReportNumber],
                   tolerance: float = 0.05) -> VerificationReport:
        """전체 검증 실행"""
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        report = VerificationReport(
            project="",
            verified_at=now,
            tolerance=tolerance,
        )

        # 1. [GF-###] 태그 기반 직접 매칭
        gf_tagged = [rn for rn in report_numbers if rn.gf_ref is not None]
        matched_fact_ids = set()

        for fact in facts:
            # 이 fact에 대한 GF 태그 참조 찾기
            tagged_refs = [rn for rn in gf_tagged if rn.gf_ref == fact.id]

            if tagged_refs:
                # 가장 가까운 수치로 비교 (여러 참조가 있을 수 있음)
                best_match = self._find_best_tagged_match(fact, tagged_refs)
                if best_match:
                    status, diff_pct, note = self.compare_values(
                        fact.value, best_match.value, tolerance, fact.unit, best_match.unit
                    )
                    report.matches.append(MatchResult(
                        fact_id=fact.id,
                        metric=fact.metric,
                        golden_value=f"{fact.raw_value} {fact.unit}",
                        report_value=best_match.raw_text,
                        diff_pct=round(diff_pct, 1),
                        status=status,
                        report_location=best_match.location,
                        note=note,
                    ))
                    matched_fact_ids.add(fact.id)
                    continue

            # 2. 퍼지 매칭 (태그가 없는 경우)
            bare_numbers = [rn for rn in report_numbers if rn.gf_ref is None]
            fuzzy_match = self._fuzzy_match(fact, bare_numbers)

            if fuzzy_match:
                status, diff_pct, note = self.compare_values(
                    fact.value, fuzzy_match.value, tolerance, fact.unit, fuzzy_match.unit
                )
                report.matches.append(MatchResult(
                    fact_id=fact.id,
                    metric=fact.metric,
                    golden_value=f"{fact.raw_value} {fact.unit}",
                    report_value=fuzzy_match.raw_text,
                    diff_pct=round(diff_pct, 1),
                    status=status,
                    report_location=fuzzy_match.location,
                    note=f"퍼지 매칭 — {note}" if note else "퍼지 매칭",
                ))
                matched_fact_ids.add(fact.id)
            else:
                # 3. MISSING: golden-facts에 있지만 보고서 미인용
                report.matches.append(MatchResult(
                    fact_id=fact.id,
                    metric=fact.metric,
                    golden_value=f"{fact.raw_value} {fact.unit}",
                    report_value="—",
                    diff_pct=0.0,
                    status="MISSING",
                    report_location="—",
                    note="golden-facts에 있으나 보고서에서 미발견",
                ))

        # 4. UNTRACKED: 보고서 수치가 golden-facts에 미등록
        #    (달러 또는 원화 단위의 주요 수치만 감지 — 퍼센트 등은 제외)
        tracked_values = {f.value for f in facts}
        for rn in report_numbers:
            if rn.gf_ref is None and rn.unit in ('USD_B', 'USD_M', 'KRW_조', 'KRW_억'):
                # 이미 퍼지 매칭된 값인지 확인
                is_matched = any(
                    abs(rn.value - f.value) / max(abs(f.value), 1e-9) < 0.10
                    for f in facts if f.value != 0
                )
                if not is_matched and rn.value > 0:
                    report.matches.append(MatchResult(
                        fact_id="—",
                        metric="(미등록 수치)",
                        golden_value="—",
                        report_value=rn.raw_text,
                        diff_pct=0.0,
                        status="UNTRACKED",
                        report_location=rn.location,
                        note=f"보고서 수치가 golden-facts에 미등록 — 컨텍스트: {rn.context[:80]}",
                    ))

        return report

    def _find_best_tagged_match(self, fact: Fact, tagged_refs: List[ReportNumber]) -> Optional[ReportNumber]:
        """태그된 참조 중 fact 값에 가장 가까운 수치 반환"""
        if not tagged_refs:
            return None

        best = None
        best_diff = float('inf')

        for rn in tagged_refs:
            if fact.value == 0 and rn.value == 0:
                return rn
            if fact.value == 0:
                continue

            diff = abs(rn.value - fact.value) / max(abs(fact.value), 1e-9)
            if diff < best_diff:
                best_diff = diff
                best = rn

        return best

    def _fuzzy_match(self, fact: Fact, bare_numbers: List[ReportNumber]) -> Optional[ReportNumber]:
        """
        태그 없는 수치에 대한 퍼지 매칭.
        오탐 방지: metric 키워드가 주변 컨텍스트에 포함되어야 함.
        """
        # metric에서 핵심 키워드 추출
        keywords = self._extract_keywords(fact.metric, fact.entity)
        if not keywords:
            return None

        candidates = []
        for rn in bare_numbers:
            # 1단계: 수치가 근사한지 확인 (20% 이내)
            if fact.value == 0:
                continue
            diff_ratio = abs(rn.value - fact.value) / max(abs(fact.value), 1e-9)
            if diff_ratio > 0.20:
                continue

            # 2단계: 컨텍스트에 키워드가 포함되는지 확인
            context_lower = rn.context.lower()
            keyword_score = sum(1 for kw in keywords if kw.lower() in context_lower)
            if keyword_score == 0:
                continue

            candidates.append((rn, diff_ratio, keyword_score))

        if not candidates:
            return None

        # 키워드 매칭 점수 높은 순, 수치 차이 작은 순으로 정렬
        candidates.sort(key=lambda x: (-x[2], x[1]))
        return candidates[0][0]

    def _extract_keywords(self, metric: str, entity: str) -> List[str]:
        """metric + entity에서 매칭용 키워드 추출"""
        keywords = []

        # 엔터티명 추가 (2글자 이상)
        if entity and len(entity) >= 2:
            keywords.append(entity)

        # metric에서 핵심 단어 추출 (조사/접미사 제거)
        # 한국어/영어 혼합 처리
        words = re.split(r'[\s/\-,]+', metric)
        for word in words:
            cleaned = word.strip()
            if len(cleaned) >= 2:
                keywords.append(cleaned)

        return keywords

    def compare_values(self, fact_value: float, report_value: float,
                       tolerance: float, fact_unit: str = "", report_unit: str = "") -> Tuple[str, float, str]:
        """
        수치 비교 판정.
        반환: (status, diff_pct, note)
        """
        # 단위 불일치 감지
        if self._is_unit_mismatch(fact_unit, report_unit):
            return ("MISMATCH", 100.0, f"단위 불일치: golden={fact_unit}, report={report_unit}")

        # 둘 다 0이면 일치
        if fact_value == 0 and report_value == 0:
            return ("MATCH", 0.0, "")

        # golden이 0인데 report가 0이 아니면
        if fact_value == 0:
            return ("MISMATCH", 100.0, "golden-facts 값이 0")

        diff_pct = abs(report_value - fact_value) / abs(fact_value) * 100

        if diff_pct == 0:
            return ("MATCH", 0.0, "")

        # 반올림 차이 감지 (예: 2.34B vs 2.3B)
        if diff_pct < 1.0:
            return ("ROUNDING", round(diff_pct, 2), "반올림 차이")

        if diff_pct <= tolerance * 100:
            return ("WITHIN_TOLERANCE", round(diff_pct, 2),
                    f"허용 범위 내 ({tolerance*100:.0f}%)")

        return ("MISMATCH", round(diff_pct, 2),
                f"허용 오차 {tolerance*100:.0f}% 초과 — 확인 필요")

    def _is_unit_mismatch(self, fact_unit: str, report_unit: str) -> bool:
        """단위 불일치 감지 (B vs M, 원 vs 달러 등)"""
        if not fact_unit or not report_unit:
            return False
        if fact_unit == report_unit:
            return False

        # 같은 통화 계열이면 OK (정규화에서 처리됨)
        usd_units = {'USD', 'USD_T', 'USD_B', 'USD_M', 'USD_K'}
        krw_units = {'KRW', 'KRW_조', 'KRW_억', 'KRW_만'}

        fact_is_usd = fact_unit in usd_units or '$' in str(fact_unit)
        fact_is_krw = fact_unit in krw_units or '₩' in str(fact_unit) or '원' in str(fact_unit)
        report_is_usd = report_unit in usd_units
        report_is_krw = report_unit in krw_units

        # 달러 vs 원화 혼용 = 단위 불일치
        if (fact_is_usd and report_is_krw) or (fact_is_krw and report_is_usd):
            return True

        return False


# ============================================================
# D. Confidence-Prominence 체크
# ============================================================

class ConfidenceProminenceChecker:
    """confidence: low/medium 수치가 보고서 전면에 사용되는지 감지"""

    # Executive Summary 범위 감지 패턴
    EXEC_SUMMARY_PATTERN = re.compile(r'^##\s*Executive\s+Summary', re.IGNORECASE)
    # 슬라이드 타이틀 패턴
    SLIDE_TITLE_PATTERN = re.compile(r'^#+\s+')
    # 가정 라벨 패턴
    ASSUMPTION_LABEL = re.compile(r'\[가정\]|\[미확인\]|\[추정\]')

    def check(self, facts: List[Fact], report_path: str) -> List[ConfidenceIssue]:
        """
        규칙:
        - confidence: [가정]/low인 수치가 Executive Summary에 사용 → critical
        - confidence: [유력]/medium인 수치가 슬라이드 타이틀에 사용 → warning
        - confidence: [가정]/low인 수치에 [가정] 라벨 미표기 → critical
        """
        if not os.path.exists(report_path):
            return []

        with open(report_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        issues = []
        filename = os.path.basename(report_path)

        # Executive Summary 영역 식별
        exec_start = -1
        exec_end = -1
        for i, line in enumerate(lines):
            if self.EXEC_SUMMARY_PATTERN.search(line):
                exec_start = i
            elif exec_start >= 0 and re.match(r'^##\s+[^#]', line) and i > exec_start:
                exec_end = i
                break
        if exec_start >= 0 and exec_end < 0:
            exec_end = len(lines)

        # confidence 매핑 정규화
        low_facts = {f.id: f for f in facts
                     if f.confidence in ('[가정]', '[미확인]', 'low', 'unverified')}
        medium_facts = {f.id: f for f in facts
                        if f.confidence in ('[유력]', 'medium')}

        gf_pattern = re.compile(r'\[GF-(\d+)\]')

        for line_num, line in enumerate(lines):
            gf_matches = gf_pattern.findall(line)
            for gf_num in gf_matches:
                gf_id = f"GF-{gf_num}"

                # Low confidence가 Executive Summary에 사용
                if gf_id in low_facts and exec_start <= line_num < exec_end:
                    issues.append(ConfidenceIssue(
                        fact_id=gf_id,
                        confidence=low_facts[gf_id].confidence,
                        location=f"{filename}:{line_num + 1} (Executive Summary)",
                        issue=f"confidence: {low_facts[gf_id].confidence} 수치가 Executive Summary에 사용됨",
                        severity="critical",
                    ))

                # Low confidence에 [가정] 라벨 미표기
                if gf_id in low_facts and not self.ASSUMPTION_LABEL.search(line):
                    issues.append(ConfidenceIssue(
                        fact_id=gf_id,
                        confidence=low_facts[gf_id].confidence,
                        location=f"{filename}:{line_num + 1}",
                        issue=f"confidence: {low_facts[gf_id].confidence} 수치에 [가정] 라벨 미표기",
                        severity="critical",
                    ))

                # Medium confidence가 슬라이드 타이틀(헤딩)에 사용
                if gf_id in medium_facts and self.SLIDE_TITLE_PATTERN.match(line):
                    issues.append(ConfidenceIssue(
                        fact_id=gf_id,
                        confidence=medium_facts[gf_id].confidence,
                        location=f"{filename}:{line_num + 1}",
                        issue=f"confidence: {medium_facts[gf_id].confidence} 수치가 섹션 타이틀에 사용됨",
                        severity="warning",
                    ))

        return issues


# ============================================================
# E. 리포트 생성
# ============================================================

class VerificationReportWriter:
    """검증 결과 리포트 생성"""

    def write_yaml(self, report: VerificationReport, output_path: str):
        """YAML 리포트 (QA 시스템 연동용)"""
        # 상태별 카운트
        status_counts = {}
        for m in report.matches:
            status_counts[m.status] = status_counts.get(m.status, 0) + 1

        total_facts = sum(1 for m in report.matches if m.status != "UNTRACKED")
        matched = status_counts.get("MATCH", 0)
        within_tolerance = status_counts.get("WITHIN_TOLERANCE", 0) + status_counts.get("ROUNDING", 0)
        mismatch = status_counts.get("MISMATCH", 0)
        missing = status_counts.get("MISSING", 0)
        untracked = status_counts.get("UNTRACKED", 0)

        verified_in_report = matched + within_tolerance
        pass_rate_denom = total_facts if total_facts > 0 else 1
        pass_rate = round((matched + within_tolerance) / pass_rate_denom * 100)
        verdict = "FAIL" if mismatch > 0 else "PASS"

        data = {
            'verification_report': {
                'project': report.project,
                'verified_at': report.verified_at,
                'tolerance': report.tolerance,
                'summary': {
                    'total_facts': total_facts,
                    'matched': matched,
                    'within_tolerance': within_tolerance,
                    'mismatch': mismatch,
                    'missing': missing,
                    'untracked': untracked,
                    'pass_rate': f"{pass_rate}%",
                    'verdict': verdict,
                },
                'details': [],
                'confidence_prominence_issues': [],
            }
        }

        for m in report.matches:
            data['verification_report']['details'].append({
                'fact_id': m.fact_id,
                'metric': m.metric,
                'golden_value': m.golden_value,
                'report_value': m.report_value,
                'diff_pct': m.diff_pct,
                'status': m.status,
                'report_location': m.report_location,
                'note': m.note,
            })

        for ci in report.confidence_issues:
            data['verification_report']['confidence_prominence_issues'].append({
                'fact_id': ci.fact_id,
                'confidence': ci.confidence,
                'location': ci.location,
                'issue': ci.issue,
                'severity': ci.severity,
            })

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        return data

    def write_csv(self, report: VerificationReport, output_path: str):
        """CSV 리포트 (사람 확인용)"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'fact_id', 'metric', 'golden_value', 'report_value',
                'diff_pct', 'status', 'location', 'note'
            ])
            for m in report.matches:
                writer.writerow([
                    m.fact_id, m.metric, m.golden_value, m.report_value,
                    m.diff_pct, m.status, m.report_location, m.note,
                ])

    def write_summary(self, report: VerificationReport) -> str:
        """콘솔 출력용 요약"""
        status_counts = {}
        for m in report.matches:
            status_counts[m.status] = status_counts.get(m.status, 0) + 1

        total = sum(1 for m in report.matches if m.status != "UNTRACKED")
        matched = status_counts.get("MATCH", 0)
        within_tol = status_counts.get("WITHIN_TOLERANCE", 0) + status_counts.get("ROUNDING", 0)
        mismatch = status_counts.get("MISMATCH", 0)
        missing = status_counts.get("MISSING", 0)
        untracked = status_counts.get("UNTRACKED", 0)
        verdict = "FAIL" if mismatch > 0 else "PASS"

        lines = [
            "",
            "=" * 60,
            f"  Golden Facts 수치 검증 결과 — {report.project}",
            "=" * 60,
            f"  검증 시각:   {report.verified_at}",
            f"  허용 오차:   {report.tolerance * 100:.0f}%",
            "",
            f"  MATCH:            {matched}건",
            f"  WITHIN_TOLERANCE: {within_tol}건",
            f"  MISMATCH:         {mismatch}건",
            f"  MISSING:          {missing}건 (golden-facts에 있으나 보고서 미인용)",
            f"  UNTRACKED:        {untracked}건 (보고서 수치 미등록)",
            "",
        ]

        # 불일치 상세
        mismatches = [m for m in report.matches if m.status == "MISMATCH"]
        if mismatches:
            lines.append("  --- MISMATCH 상세 ---")
            for m in mismatches:
                lines.append(f"  [{m.fact_id}] {m.metric}")
                lines.append(f"    golden: {m.golden_value} → report: {m.report_value} (차이: {m.diff_pct}%)")
                lines.append(f"    위치: {m.report_location}")
                if m.note:
                    lines.append(f"    비고: {m.note}")
                lines.append("")

        # Confidence-prominence 이슈
        if report.confidence_issues:
            lines.append("  --- Confidence-Prominence 이슈 ---")
            for ci in report.confidence_issues:
                severity_label = "CRITICAL" if ci.severity == "critical" else "WARN"
                lines.append(f"  [{severity_label}] {ci.fact_id} — {ci.issue}")
                lines.append(f"    위치: {ci.location}")
                lines.append("")

        verdict_line = f"  최종 판정: {verdict}"
        if verdict == "FAIL":
            verdict_line += f" (MISMATCH {mismatch}건)"
        lines.append(verdict_line)
        lines.append("=" * 60)
        lines.append("")

        return "\n".join(lines)


# ============================================================
# F. CLI 인터페이스
# ============================================================

def find_project_root() -> str:
    """스크립트 위치 기반으로 프로젝트 루트 탐색"""
    # scripts/ 디렉토리 안에 있으므로 한 단계 위
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Golden Facts 수치 검증 — golden-facts.yaml vs 보고서 자동 대조"
    )
    parser.add_argument("project", help="프로젝트 디렉토리명 (예: my-research)")
    parser.add_argument("--strict", action="store_true",
                        help="허용 오차 0%% (정확 일치)")
    parser.add_argument("--tolerance", type=float, default=0.05,
                        help="허용 오차 비율 (기본: 0.05 = 5%%)")
    parser.add_argument("--format", default="yaml", choices=["yaml", "csv", "both"],
                        help="출력 포맷 (기본: yaml)")
    parser.add_argument("--output",
                        help="출력 경로 (기본: {project}/qa/fact-verification.yaml)")
    parser.add_argument("--report-only", action="store_true",
                        help="report-docs.md만 검증 (slides 제외)")

    args = parser.parse_args()

    # 경로 설정
    root = find_project_root()
    project_dir = os.path.join(root, args.project)

    if not os.path.isdir(project_dir):
        print(f"오류: 프로젝트 디렉토리가 존재하지 않습니다: {project_dir}")
        sys.exit(1)

    facts_path = os.path.join(project_dir, "findings", "golden-facts.yaml")
    if not os.path.exists(facts_path):
        print(f"오류: golden-facts.yaml이 존재하지 않습니다: {facts_path}")
        sys.exit(1)

    report_docs_path = os.path.join(project_dir, "reports", "report-docs.md")
    report_slides_path = os.path.join(project_dir, "reports", "report-slides.md")

    tolerance = 0.0 if args.strict else args.tolerance

    # 1. Golden Facts 파싱
    gf_parser = GoldenFactsParser()
    facts = gf_parser.parse(facts_path)
    if not facts:
        print("오류: golden-facts.yaml에서 수치를 파싱할 수 없습니다.")
        sys.exit(1)
    print(f"Golden Facts 로드: {len(facts)}건")

    # 2. 보고서 수치 추출
    extractor = ReportNumberExtractor()
    all_report_numbers = []

    if os.path.exists(report_docs_path):
        nums = extractor.extract_from_markdown(report_docs_path)
        all_report_numbers.extend(nums)
        print(f"report-docs.md 수치 추출: {len(nums)}건")
    else:
        print(f"경고: report-docs.md 없음: {report_docs_path}")

    if not args.report_only and os.path.exists(report_slides_path):
        nums = extractor.extract_from_markdown(report_slides_path)
        all_report_numbers.extend(nums)
        print(f"report-slides.md 수치 추출: {len(nums)}건")
    elif not args.report_only:
        print(f"경고: report-slides.md 없음: {report_slides_path}")

    if not all_report_numbers:
        print("경고: 보고서에서 수치를 추출할 수 없습니다.")

    # 3. 검증 실행
    verifier = FactVerifier()
    verification = verifier.verify_all(facts, all_report_numbers, tolerance)
    verification.project = args.project

    # 4. Confidence-prominence 체크
    cp_checker = ConfidenceProminenceChecker()
    for report_path in [report_docs_path, report_slides_path]:
        if os.path.exists(report_path):
            issues = cp_checker.check(facts, report_path)
            verification.confidence_issues.extend(issues)

    # 5. 리포트 출력
    writer = VerificationReportWriter()

    # 콘솔 요약
    summary = writer.write_summary(verification)
    print(summary)

    # 파일 출력
    output_dir = os.path.join(project_dir, "qa")
    if args.output:
        yaml_path = args.output
        csv_path = args.output.replace('.yaml', '.csv')
    else:
        yaml_path = os.path.join(output_dir, "fact-verification.yaml")
        csv_path = os.path.join(output_dir, "fact-verification.csv")

    if args.format in ("yaml", "both"):
        writer.write_yaml(verification, yaml_path)
        print(f"YAML 리포트 저장: {yaml_path}")

    if args.format in ("csv", "both"):
        writer.write_csv(verification, csv_path)
        print(f"CSV 리포트 저장: {csv_path}")


if __name__ == "__main__":
    main()
