#!/usr/bin/env python3
"""
feedback-impact.py — Phase 5.5 피드백 영향 범위 분석 (v4.12 Issue #6)

목적:
    사용자 피드백이 보고서의 어느 Division/Phase/산출물에 영향을 주는지
    자동으로 판정하여, 부분 재실행(minimal/division/cross_division) 범위를
    명시한다.

배경:
    v4.10까지는 PM이 자율 판정하는 방식이었으나, 판정 기준의 모호성으로
    결국 '전체 재실행' 또는 '무시'로 수렴하는 경우가 많았다.
    v4.12에서는 규칙 기반 자동 매핑으로 일관성을 확보한다.

사용법:
    python3 scripts/feedback-impact.py {project} "사용자 피드백 내용"
    python3 scripts/feedback-impact.py {project} --feedback-file feedback.txt

산출물:
    {project}/sync/feedback-impact.yaml

피드백 분류 매트릭스:
    - minimal: 표현/수치/태그 수준 → report-fixer만
    - division: 단일 Division 분석 재작성 → 해당 Lead 재투입
    - cross_division: 복수 Division 또는 Sync 필요 → Sync 재실행

종료 코드:
    0 : 분석 완료
    1 : 피드백 해석 실패 (명확한 분류 불가)
    2 : 실행 오류
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError:
    sys.stderr.write("[ERROR] pyyaml 미설치 — pip install -r requirements.txt\n")
    sys.exit(2)


# ─── Division 키워드 매핑 ──────────────────────────────────────
DIVISION_KEYWORDS = {
    "market": ["시장", "경쟁사", "고객", "채널", "세분화", "TAM", "SAM", "SOM",
               "점유율", "트렌드", "수요"],
    "product": ["제품", "서비스", "가치", "차별화", "가격", "수익 모델",
                "GTM", "포지셔닝", "UX"],
    "capability": ["기술", "IP", "특허", "자산", "인재", "조직", "역량",
                   "실행력", "트랙레코드"],
    "finance": ["매출", "수익", "비용", "영업이익", "CAPEX", "OPEX",
                "ROI", "IRR", "밸류에이션", "투자"],
    "people-org": ["조직 구조", "거버넌스", "문화", "리더십", "HR", "보상"],
    "operations": ["프로세스", "공급망", "물류", "인프라", "품질"],
    "regulatory": ["규제", "컴플라이언스", "법률", "ESG", "지배구조"],
}

# ─── 영향 강도 키워드 ──────────────────────────────────────────
MINIMAL_KEYWORDS = [
    "표현", "문구", "오타", "번역", "용어", "표기", "라벨",
    "숫자 오류", "단위", "날짜", "이름",
]
CROSS_DIVISION_KEYWORDS = [
    "전략 방향", "전체", "결론", "근본", "재검토",
    "기본 가정", "프레임", "접근법", "전면",
]

# ─── Phase 영향 매핑 ──────────────────────────────────────────
PHASE_IMPACT_MAP = {
    "minimal": {
        "affected_phases": ["4-A", "5"],
        "agents": ["report-fixer"],
        "rerun_scope": "report-fixer 자동 수정 + QA 재실행",
    },
    "division": {
        "affected_phases": ["1", "Sync-R1", "2", "4-A", "5"],
        "agents": ["{division}-lead", "report-writer", "qa-orchestrator"],
        "rerun_scope": "해당 Division Lead 재투입 → 합성 → 보고서 수정 → QA",
    },
    "cross_division": {
        "affected_phases": ["1", "Sync-R1", "2", "Sync-R2", "3", "4-A", "5"],
        "agents": ["multiple-leads", "cross-domain-synthesizer",
                   "insight-synthesizer", "report-writer", "qa-orchestrator"],
        "rerun_scope": "복수 Division 재투입 → Sync Round 재실행 → 사고 루프 → 보고서 재작성 → QA",
    },
}


def classify_scope(feedback: str) -> str:
    """피드백 텍스트에서 영향 범위 판정."""
    text = feedback.lower()

    # 1. 교차 영향 키워드 우선 (전략/결론/근본 등)
    for kw in CROSS_DIVISION_KEYWORDS:
        if kw in text:
            return "cross_division"

    # 2. 최소 영향 키워드 (표현/오타 등)
    for kw in MINIMAL_KEYWORDS:
        if kw in text:
            return "minimal"

    # 3. Division 키워드 매칭
    matched_divisions = detect_divisions(feedback)
    if len(matched_divisions) >= 2:
        return "cross_division"
    if len(matched_divisions) == 1:
        return "division"

    # 4. 모호 → 중간값(division) 반환하되 warning
    return "ambiguous"


def detect_divisions(feedback: str) -> List[str]:
    """피드백에서 언급된 Division 식별."""
    text = feedback.lower()
    matched = []
    for div, keywords in DIVISION_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                matched.append(div)
                break
    return matched


def find_affected_files(
    project_dir: Path, scope: str, divisions: List[str]
) -> List[str]:
    """영향 받는 파일 경로 목록 반환."""
    files = []

    if scope == "minimal":
        files.extend([
            "reports/report-docs.md",
            "reports/one-pager.md",
            "qa/qa-report.md",
        ])
    elif scope == "division":
        for div in divisions:
            div_path = project_dir / "findings" / div
            if div_path.exists():
                files.append(f"findings/{div}/*.yaml")
                files.append(f"findings/{div}/division-synthesis.yaml")
        files.extend([
            "sync/round-1-briefing.md",
            "reports/report-docs.md",
            "qa/qa-report.md",
        ])
    elif scope == "cross_division":
        files.append("findings/**/*.yaml")
        files.extend([
            "sync/round-1-briefing.md",
            "sync/round-2-briefing.md",
            "sync/cross-domain-synthesis.md",
            "thinking-loop/*.md",
            "reports/report-docs.md",
            "reports/one-pager.md",
            "qa/qa-report.md",
        ])
        if (project_dir / "intent-coverage.yaml").exists():
            files.append("intent-coverage.yaml")

    return files


def check_downstream_invalidation(
    project_dir: Path, scope: str
) -> List[str]:
    """변경 범위로 인해 무효화되는 후속 산출물 식별."""
    invalidated = []
    reports_dir = project_dir / "reports"

    # Phase 4.7 HTML/PDF는 MD가 바뀌면 무조건 무효
    if scope in ("minimal", "division", "cross_division"):
        for suffix in (".html", ".pdf", "sources.html"):
            candidates = (
                list(reports_dir.glob(f"*{suffix}"))
                if suffix.startswith(".")
                else [reports_dir / suffix]
            )
            for c in candidates:
                if c.exists():
                    invalidated.append(str(c.relative_to(project_dir)))

    # 사용자가 결론/전략을 바꾸면 thinking-loop 전체 무효
    if scope == "cross_division":
        tl_dir = project_dir / "thinking-loop"
        if tl_dir.exists():
            for f in tl_dir.glob("*.md"):
                invalidated.append(str(f.relative_to(project_dir)))

    return invalidated


def write_impact_report(
    project_dir: Path,
    feedback: str,
    scope: str,
    divisions: List[str],
    affected_files: List[str],
    invalidated: List[str],
) -> Path:
    """sync/feedback-impact.yaml 작성."""
    sync_dir = project_dir / "sync"
    sync_dir.mkdir(parents=True, exist_ok=True)

    impact_info = PHASE_IMPACT_MAP.get(scope, {})

    # 에이전트 목록 전개 (division 치환)
    agents = []
    for agent in impact_info.get("agents", []):
        if "{division}" in agent and divisions:
            for div in divisions:
                agents.append(agent.replace("{division}", div))
        else:
            agents.append(agent)

    report = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": project_dir.name,
        "script_version": "v4.12",
        "feedback": feedback[:500],  # 처음 500자만 기록
        "classification": {
            "scope": scope,
            "divisions_affected": divisions,
            "rationale": _rationale_for(scope, divisions, feedback),
        },
        "rerun_plan": {
            "phases": impact_info.get("affected_phases", []),
            "agents": agents,
            "scope_description": impact_info.get("rerun_scope", ""),
        },
        "files_affected": affected_files,
        "downstream_invalidated": invalidated,
        "user_confirmation_required": scope == "ambiguous"
        or scope == "cross_division",
    }

    out = sync_dir / "feedback-impact.yaml"
    with out.open("w", encoding="utf-8") as f:
        yaml.dump(
            report, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
    return out


def _rationale_for(scope: str, divisions: List[str], feedback: str) -> str:
    """분류 근거 문자열 생성."""
    if scope == "minimal":
        return "표현/오타/태그/수치 수정 키워드 감지 — report-fixer만으로 해소 가능"
    if scope == "division":
        return f"단일 Division 키워드({divisions[0] if divisions else '-'}) 감지 — 해당 Lead 재투입"
    if scope == "cross_division":
        if len(divisions) >= 2:
            return f"복수 Division 키워드({', '.join(divisions)}) 감지 — Sync 재실행 필요"
        return "전략/결론/근본 재검토 키워드 감지 — 사고 루프 재실행 필요"
    if scope == "ambiguous":
        return "명확한 Division/범위 키워드 미검출 — 사용자 확인 필요"
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="v4.12 Issue #6: Phase 5.5 피드백 영향 범위 자동 분석"
    )
    parser.add_argument("project", help="프로젝트 디렉토리명")
    parser.add_argument("feedback", nargs="?", default="", help="피드백 텍스트 (인라인)")
    parser.add_argument(
        "--feedback-file", help="피드백 텍스트 파일 경로"
    )
    parser.add_argument(
        "--project-root", default=".", help="프로젝트 루트"
    )
    args = parser.parse_args()

    project_dir = Path(args.project_root).resolve() / args.project
    if not project_dir.exists():
        sys.stderr.write(f"[ERROR] 프로젝트 디렉토리 없음: {project_dir}\n")
        return 2

    # 피드백 로드
    feedback_text = args.feedback
    if args.feedback_file:
        try:
            feedback_text = Path(args.feedback_file).read_text(encoding="utf-8")
        except OSError as e:
            sys.stderr.write(f"[ERROR] 피드백 파일 읽기 실패: {e}\n")
            return 2

    if not feedback_text.strip():
        sys.stderr.write("[ERROR] 피드백 텍스트가 비어있음\n")
        return 2

    # 분석
    scope = classify_scope(feedback_text)
    divisions = detect_divisions(feedback_text)
    affected_files = find_affected_files(project_dir, scope, divisions)
    invalidated = check_downstream_invalidation(project_dir, scope)

    # 리포트 작성
    out_path = write_impact_report(
        project_dir, feedback_text, scope, divisions, affected_files, invalidated
    )

    # 요약 출력
    print(f"[REPORT] {out_path}")
    print(f"[SCOPE] {scope}")
    if divisions:
        print(f"[DIVISIONS] {', '.join(divisions)}")
    print(f"[AFFECTED_FILES] {len(affected_files)}건")
    print(f"[DOWNSTREAM_INVALIDATED] {len(invalidated)}건 (HTML/PDF/thinking-loop)")

    if scope == "ambiguous":
        sys.stderr.write(
            "[WARN] 분류 모호함 — 사용자 확인 필요 (scope 수동 지정 권장)\n"
        )
        return 1

    print(f"[OK] 재실행 계획 완료 — {out_path.name} 참조")
    return 0


if __name__ == "__main__":
    sys.exit(main())
