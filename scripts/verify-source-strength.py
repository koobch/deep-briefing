#!/usr/bin/env python3
"""
verify-source-strength.py — 소스 강도 게이트 검증 (v4.12 Issue #1)

목적:
    Claim의 declared confidence가 실제 evidence source 조합의 신뢰도로
    뒷받침되는지 자동 검증한다.

배경:
    기존 verify-source-traceability.py는 [S##] 태그가 source_index에
    존재하는지만 검증했다. 그러나 fact-check-protocol과 output-format의
    '신뢰도 정량화' 규칙은 소스 type/reliability 조합에 따라 confidence
    상한을 강제한다. 이 규칙이 형식적 검증에 머물러, 'high confidence +
    estimate 소스 1개' 같은 부적합한 조합이 통과 가능했다.

규칙 매트릭스 (core/protocols/output-format.md §소스 추적 규칙):
    primary 2개+          → high
    primary 1 + secondary 1+ → high
    secondary 2개+        → high
    secondary 1개         → medium
    estimate/tertiary만    → low
    소스 없음             → insufficient

사용법:
    python3 scripts/verify-source-strength.py {project-name}
    python3 scripts/verify-source-strength.py {project-name} --project-root .

산출물:
    {project}/qa/source-strength-report.yaml

종료 코드:
    0 : PASS (모든 Claim이 소스 강도와 일치)
    1 : FAIL (mismatch 또는 insufficient 1건+)
    2 : 실행 오류 (의존성, 파일 읽기 실패 등)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    sys.stderr.write("[ERROR] pyyaml 미설치 — pip install -r requirements.txt\n")
    sys.exit(2)


# ─── Confidence 서열 (비교용) ────────────────────────────────────
CONFIDENCE_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "unverified": 0,  # unverified는 평가 대상 외
}


def _normalize_confidence(value: str) -> str:
    """confidence 값 정규화 — EP-026 한글 라벨도 허용."""
    if not value:
        return ""
    v = str(value).strip().lower().strip("[]")
    mapping = {
        "확정": "high",
        "유력": "medium",
        "가정": "low",
        "미확인": "unverified",
    }
    return mapping.get(v, v)


def _normalize_source_type(value: str) -> str:
    """source type 정규화."""
    if not value:
        return "unknown"
    v = str(value).strip().lower()
    # estimate/tertiary 계열은 estimate로 통일
    if v in ("tertiary", "guess", "추정"):
        return "estimate"
    if v in ("primary", "secondary", "estimate"):
        return v
    return "unknown"


def _is_web_only_source(src: dict) -> bool:
    """API 미사용 + 웹 검색만 소스인지 판정.

    기준:
      - type == secondary
      - url에 'api'/'dart.fss.or.kr'/'fred.stlouisfed.org' 등 API 도메인 없음
      - note에 'web', '웹', 'crawl', '크롤' 포함 또는 name이 특정 API 키워드 없음
    """
    if src.get("type") != "secondary":
        return False
    url = (src.get("url") or "").lower()
    api_markers = ("api", "dart.fss", "fred", "ecos", "worldbank", "oecd", "data.go.kr")
    if any(m in url for m in api_markers):
        return False
    # 기본 보수적 판정: url이 없거나 일반 웹 도메인이면 web_only
    return True


def collect_source_index(findings_dir: Path) -> Dict[str, dict]:
    """모든 findings YAML에서 source_index를 전역 dict로 수집.

    키: source id (예: S01)
    값: {type, reliability, name, source_file}
    """
    global_index: Dict[str, dict] = {}
    if not findings_dir.exists():
        return global_index

    for yaml_path in findings_dir.rglob("*.yaml"):
        try:
            with yaml_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except (yaml.YAMLError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        src_list = data.get("source_index") or []
        if not isinstance(src_list, list):
            continue
        for src in src_list:
            if not isinstance(src, dict) or not src.get("id"):
                continue
            sid = str(src["id"]).strip()
            if sid in global_index:
                continue  # 첫 등장 우선
            global_index[sid] = {
                "type": _normalize_source_type(src.get("type", "")),
                "reliability": (src.get("reliability") or "unknown").lower(),
                "name": src.get("name", ""),
                "source_file": str(yaml_path.relative_to(findings_dir.parent)),
            }
    return global_index


def compute_max_confidence(
    primary_count: int,
    secondary_count: int,
    estimate_count: int,
    total: int,
    web_only_secondary_count: int = 0,
) -> Tuple[str, str]:
    """소스 조합으로 허용 가능한 max confidence 산출.

    Returns:
        (max_confidence, rule_applied)
    """
    if total == 0:
        return ("insufficient", "소스 없음 → confidence 평가 불가")

    if primary_count >= 2:
        return ("high", "primary 2개+ 일치 → high 허용")
    if primary_count >= 1 and secondary_count >= 1:
        return ("high", "primary 1 + secondary 1+ → high 허용")
    if secondary_count >= 2:
        # 웹 검색만 기반이면 high 불가 (output-format §소스 추적 규칙)
        if web_only_secondary_count == secondary_count:
            return ("medium", "secondary 2개+이나 모두 웹 검색/API 미사용 → medium 상한")
        return ("high", "secondary 2개+ 독립 확인 → high 허용")
    if secondary_count == 1:
        return ("medium", "secondary 1개만 → medium 상한")
    if primary_count == 1:
        # primary 1 + secondary 0 → medium (단일 소스 상한)
        return ("medium", "primary 1개 (교차 없음) → medium 상한")
    # 모두 estimate/unknown
    return ("low", "estimate/unknown만 → low 상한")


def evaluate_claim(
    claim: dict, evidence_list: List[dict], source_index: Dict[str, dict]
) -> Optional[dict]:
    """단일 Claim을 평가하고 violation이 있으면 violation dict 반환.

    Returns:
        None if OK, else violation dict
    """
    claim_id = claim.get("id", "")
    declared = _normalize_confidence(claim.get("confidence", ""))
    if not claim_id:
        return None
    if declared == "unverified":
        return None  # unverified는 평가 제외

    # 해당 claim을 지지하는 evidence의 sources 수집
    source_ids: List[str] = []
    for ev in evidence_list:
        if str(ev.get("claim_id", "")).strip() != claim_id:
            continue
        supports = ev.get("supports") or []
        for s in supports:
            if isinstance(s, dict):
                sources = s.get("sources") or []
                for src_id in sources:
                    if src_id and str(src_id).strip():
                        source_ids.append(str(src_id).strip())

    # 중복 제거 (순서 유지)
    seen = set()
    unique_sources = []
    for sid in source_ids:
        if sid not in seen:
            seen.add(sid)
            unique_sources.append(sid)

    # type 분포 계산
    primary_count = 0
    secondary_count = 0
    estimate_count = 0
    web_only_secondary_count = 0
    missing_source_ids: List[str] = []
    evidence_sources_detail = []
    for sid in unique_sources:
        src = source_index.get(sid)
        if not src:
            # 미등록 source id는 Critical 위반으로 별도 처리
            missing_source_ids.append(sid)
            evidence_sources_detail.append({"id": sid, "type": "missing"})
            continue
        t = src["type"]
        evidence_sources_detail.append({"id": sid, "type": t})
        if t == "primary":
            primary_count += 1
        elif t == "secondary":
            secondary_count += 1
            if _is_web_only_source(src):
                web_only_secondary_count += 1
        else:  # estimate, unknown
            estimate_count += 1

    # 미등록 source id가 있으면 INSUFFICIENT (Critical) 우선 판정
    if missing_source_ids:
        return {
            "claim_id": claim_id,
            "declared_confidence": declared,
            "max_allowed_confidence": "insufficient",
            "evidence_sources": evidence_sources_detail,
            "rule_applied": f"source_index 미등록 소스 {len(missing_source_ids)}건: {missing_source_ids}",
            "severity": "critical",
            "verdict": "INSUFFICIENT",
        }

    total = primary_count + secondary_count + estimate_count
    max_allowed, rule = compute_max_confidence(
        primary_count, secondary_count, estimate_count, total, web_only_secondary_count
    )

    # 평가
    # v4.12: declared가 'insufficient'인 경우 실패 인정 경로로 수용 (OK)
    if declared == "insufficient":
        return None  # 정직한 실패 인정은 위반이 아님

    if max_allowed == "insufficient":
        # 소스 없음 + declared가 insufficient 외의 값 → 진짜 이슈
        # declared가 low면 Major, high/medium이면 Critical
        severity = "critical" if declared in ("high", "medium") else "major"
        return {
            "claim_id": claim_id,
            "declared_confidence": declared,
            "max_allowed_confidence": "insufficient",
            "evidence_sources": evidence_sources_detail,
            "rule_applied": rule + " (선언이 'insufficient'이면 합법적 실패 인정으로 처리)",
            "severity": severity,
            "verdict": "INSUFFICIENT",
        }

    declared_rank = CONFIDENCE_ORDER.get(declared, 0)
    max_rank = CONFIDENCE_ORDER.get(max_allowed, 0)
    if declared_rank > max_rank:
        return {
            "claim_id": claim_id,
            "declared_confidence": declared,
            "max_allowed_confidence": max_allowed,
            "evidence_sources": evidence_sources_detail,
            "rule_applied": rule,
            "severity": "major",
            "verdict": "MISMATCH",
        }

    return None  # OK


def verify_project(
    project_dir: Path,
) -> Tuple[List[dict], int, int, int, List[str]]:
    """프로젝트 전체 검증.

    Returns:
        (violations, total_claims, ok_count, issue_count, io_errors)
    """
    findings_dir = project_dir / "findings"
    if not findings_dir.exists():
        return ([], 0, 0, 0, [f"findings/ 디렉토리 없음: {findings_dir}"])

    source_index = collect_source_index(findings_dir)

    violations: List[dict] = []
    io_errors: List[str] = []
    total_claims = 0
    ok_count = 0

    for yaml_path in findings_dir.rglob("*.yaml"):
        try:
            with yaml_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            io_errors.append(f"YAML parse 실패 {yaml_path.name}: {e}")
            continue
        except OSError as e:
            io_errors.append(f"파일 읽기 실패 {yaml_path.name}: {e}")
            continue
        if not isinstance(data, dict):
            continue

        claims = data.get("claims") or []
        evidence_list = data.get("evidence") or []
        if not isinstance(claims, list) or not isinstance(evidence_list, list):
            continue

        for claim in claims:
            if not isinstance(claim, dict):
                continue
            total_claims += 1
            result = evaluate_claim(claim, evidence_list, source_index)
            if result is None:
                ok_count += 1
            else:
                result["source_file"] = str(yaml_path.relative_to(project_dir))
                violations.append(result)

    issue_count = len(violations)
    return (violations, total_claims, ok_count, issue_count, io_errors)


def write_report(
    project_dir: Path,
    violations: List[dict],
    total: int,
    ok: int,
) -> Path:
    """qa/source-strength-report.yaml 작성."""
    qa_dir = project_dir / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)

    mismatch_count = sum(1 for v in violations if v["verdict"] == "MISMATCH")
    insufficient_count = sum(1 for v in violations if v["verdict"] == "INSUFFICIENT")
    overall = "PASS" if (mismatch_count == 0 and insufficient_count == 0) else "FAIL"

    report = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": project_dir.name,
        "script_version": "v4.12",
        "summary": {
            "total_claims": total,
            "ok": ok,
            "mismatch": mismatch_count,
            "insufficient": insufficient_count,
            "overall_verdict": overall,
        },
        "violations": violations,
    }

    out = qa_dir / "source-strength-report.yaml"
    with out.open("w", encoding="utf-8") as f:
        yaml.dump(
            report, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="v4.12: Claim confidence vs source strength 검증"
    )
    parser.add_argument("project", help="프로젝트 디렉토리명")
    parser.add_argument(
        "--project-root",
        default=".",
        help="프로젝트 루트 (기본: 현재 디렉토리)",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_root).resolve() / args.project
    if not project_dir.exists():
        sys.stderr.write(f"[ERROR] 프로젝트 디렉토리 없음: {project_dir}\n")
        return 2

    violations, total, ok, issues, io_errors = verify_project(project_dir)

    if io_errors:
        sys.stderr.write(f"[IO-ERROR] {len(io_errors)}건 발생:\n")
        for err in io_errors[:10]:
            sys.stderr.write(f"  - {err}\n")
        if len(io_errors) > 10:
            sys.stderr.write(f"  ... ({len(io_errors) - 10}건 더)\n")
        sys.stderr.write(
            "[FAIL-RUNTIME] I/O 오류 발생 — 일부 파일 검증 누락. exit 2로 종료\n"
        )
        return 2

    if total == 0:
        sys.stderr.write(
            "[FAIL-RUNTIME] claims 없음: findings/ 디렉토리 비어있거나 스키마 불일치. "
            "정상 리서치 결과가 아니면 exit 2\n"
        )
        return 2

    out_path = write_report(project_dir, violations, total, ok)
    print(f"[REPORT] {out_path}")
    print(f"[SUMMARY] total={total} ok={ok} issues={issues}")

    if issues == 0:
        print("[PASS] 모든 Claim이 소스 강도와 일치")
        return 0

    # 이슈 간단 출력
    mismatch = [v for v in violations if v["verdict"] == "MISMATCH"]
    insufficient = [v for v in violations if v["verdict"] == "INSUFFICIENT"]
    if mismatch:
        print(f"[MISMATCH {len(mismatch)}건]")
        for v in mismatch[:5]:
            print(
                f"  {v['claim_id']}: declared={v['declared_confidence']}, "
                f"max_allowed={v['max_allowed_confidence']} — {v['rule_applied']}"
            )
        if len(mismatch) > 5:
            print(f"  ... ({len(mismatch) - 5}건 더)")
    if insufficient:
        print(f"[INSUFFICIENT {len(insufficient)}건]")
        for v in insufficient[:5]:
            print(f"  {v['claim_id']}: 소스 없음")
        if len(insufficient) > 5:
            print(f"  ... ({len(insufficient) - 5}건 더)")

    print("[FAIL] Critical/Major 이슈 존재 — qa/source-strength-report.yaml 확인")
    return 1


if __name__ == "__main__":
    sys.exit(main())
