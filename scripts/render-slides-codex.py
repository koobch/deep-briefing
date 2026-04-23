#!/usr/bin/env python3
"""
render-slides-codex.py — Phase 4.8: Codex gpt-image-2 기반 슬라이드 생성 (v4.12)

4단계 파이프라인:
    1. design   → {project}/slides/DESIGN.md
    2. plan     → {project}/slides/slide-outline.yaml
    3. prompt   → {project}/slides/prompts/page_*.json
    4. generate → {project}/slides/page_*.png (Codex exec)

사용법:
    python3 scripts/render-slides-codex.py {project}
    python3 scripts/render-slides-codex.py {project} --only plan
    python3 scripts/render-slides-codex.py {project} --pages 10
    python3 scripts/render-slides-codex.py {project} --language en

종료 코드:
    0 : 모든 단계 성공
    1 : 일부 실패 (로그 확인)
    2 : 의존성 또는 입력 오류
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    sys.stderr.write("[ERROR] pyyaml 미설치 — pip install -r requirements.txt\n")
    sys.exit(2)


# ─── 경로 상수 ─────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "core" / "style" / "report-templates"

# ─── analysis_type별 슬라이드 권장 ────────────────────────
TYPE_SLIDE_SPEC = {
    "decision": {
        "pages": 10,
        "structure": [
            ("cover", "표지"),
            ("bluf", "핵심 결론 (BLUF)"),
            ("key_finding_1", "Key Finding 1"),
            ("key_finding_2", "Key Finding 2"),
            ("key_finding_3", "Key Finding 3"),
            ("financial", "Financial Snapshot"),
            ("scenarios", "시나리오 (BASE/UP/DOWN)"),
            ("actions", "Recommended Actions"),
            ("risks", "Risk Alert"),
            ("next_steps", "Next Steps"),
        ],
    },
    "profile": {
        "pages": 14,
        "structure": [
            ("cover", "표지"),
            ("entity_overview", "엔터티 개요"),
            ("market_context", "Market Context"),
            ("market_size", "시장 규모"),
            ("competitive", "경쟁 구조"),
            ("product_portfolio", "제품/서비스 포트폴리오"),
            ("revenue", "매출 구조·추이"),
            ("financial", "재무 건전성"),
            ("capability", "핵심 역량·IP"),
            ("talent", "인재·조직"),
            ("strategy", "공식 전략·방향성"),
            ("ip_usage", "IP 활용 사례"),
            ("observations", "주목할 관찰점"),
            ("appendix", "부록"),
        ],
    },
    "exploration": {
        "pages": 8,
        "structure": [
            ("cover", "표지"),
            ("exploration_space", "탐색 공간"),
            ("candidate_matrix", "후보 가설 매트릭스"),
            ("confirmed", "확정 가설"),
            ("rejected", "기각 가설"),
            ("insufficient", "미해결 (추가 리서치 필요)"),
            ("implications", "확정된 시사점"),
            ("next_research", "추가 리서치 권고"),
        ],
    },
    "monitoring": {
        "pages": 5,
        "structure": [
            ("cover", "표지"),
            ("dashboard", "지표 대시보드"),
            ("changes", "변화 방향"),
            ("outliers", "이상치 / 임계값 초과"),
            ("watchlist", "관찰 포인트"),
        ],
    },
}

DEFAULT_DESIGN_TOKENS = {
    "primary": "#003a70",
    "accent": "#0066cc",
    "ink": "#121417",
    "paper": "#ffffff",
    "typography": "Pretendard",
    "dimensions": "1920x1080",
}


def find_codex() -> Optional[str]:
    """Codex CLI 실행 경로 탐지."""
    return shutil.which("codex")


def load_analysis_type(project_dir: Path) -> str:
    """Research Plan에서 analysis_type 추출."""
    rp_md = project_dir / "01-research-plan.md"
    if not rp_md.exists():
        return "decision"  # 기본값
    try:
        text = rp_md.read_text(encoding="utf-8")
    except OSError:
        return "decision"
    m = re.search(r"analysis_type\s*:\s*(decision|profile|exploration|monitoring)", text)
    return m.group(1) if m else "decision"


def load_entity_target(project_dir: Path) -> Dict:
    """Research Plan에서 entity_target 추출 (profile 타입용)."""
    rp_md = project_dir / "01-research-plan.md"
    if not rp_md.exists():
        return {}
    try:
        text = rp_md.read_text(encoding="utf-8")
    except OSError:
        return {}
    block = re.search(
        r"entity_target:\s*\n((?:\s+\w+:.*\n)+)", text
    )
    if not block:
        return {}
    result = {}
    for line in block.group(1).splitlines():
        m = re.match(r"\s+(\w+):\s*(.+)", line)
        if m:
            result[m.group(1)] = m.group(2).strip().strip('"')
    return result


def step1_design(project_dir: Path, slides_dir: Path, language: str) -> Path:
    """Step 1: DESIGN.md 생성."""
    design_md = slides_dir / "DESIGN.md"
    slides_dir.mkdir(parents=True, exist_ok=True)

    tokens_css = TEMPLATE_DIR / "shared" / "tokens.css"
    tokens_content = tokens_css.read_text(encoding="utf-8") if tokens_css.exists() else ""

    design = f"""# DESIGN — 슬라이드 비주얼 시스템 (v4.12 Phase 4.8)

> 생성: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 원천: core/style/report-templates/shared/tokens.css + deep-briefing McKinsey/BCG 스타일

## 색상 팔레트
- **Primary (딥 네이비)**: {DEFAULT_DESIGN_TOKENS['primary']}
- **Accent (블루)**: {DEFAULT_DESIGN_TOKENS['accent']}
- **Ink (본문)**: {DEFAULT_DESIGN_TOKENS['ink']}
- **Paper (배경)**: {DEFAULT_DESIGN_TOKENS['paper']}
- Success: #0b7d5a / Warning: #b8741a / Danger: #b93a30

## 타이포그래피
- **Sans**: Pretendard Variable + Inter + Noto Sans KR
- **Mono**: JetBrains Mono
- H1 40pt (표지) / H2 28pt (섹션) / H3 22pt / Body 18pt

## 레이아웃 컴포넌트
1. **표지**: 좌측 정렬 + 프로젝트명 + 큰 타이틀 + 서브타이틀 + 하단 메타 + 딥 네이비 상단 3px 라인
2. **본문 페이지**: 좌측 1/3 Key Message 세로 막대, 우측 2/3 본문 (Action Title + 데이터 앵커 + So What)
3. **KPI 박스**: 큰 숫자 (72pt) + 라벨 + 출처 태그
4. **차트**: 딥 네이비 기본, 비교 시 Accent 블루 + Warning 오렌지
5. **Pull Quote**: 좌측 3px 딥 네이비 라인 + 20pt 이탤릭 + Source

## Action Title 규칙
모든 슬라이드 제목은 **주장 문장형**:
- ✗ "시장 분석"
- ✓ "국내 AI 시장은 연 28% 성장 중이나 수익성은 상위 3사에 집중"

## 4-Layer 시각 원칙
- Layer 0 (Claim): 제목으로 노출
- Layer 1 (Evidence): 본문 주요 포인트 2~3개
- Layer 2 (Data): 차트/표로 요약
- Layer 3 (Source): 각주 형태로 [GF-001] 태그

## 언어 설정
- 본 DESIGN은 `{language}` 기준
- 모든 텍스트 한국어 `{'한국어' if language == 'ko' else '영어'}`로 렌더링

## 원본 CSS 토큰 (참조용, 상위 100줄)
```css
{tokens_content[:3000] if tokens_content else '(tokens.css 없음)'}
```
"""

    design_md.write_text(design, encoding="utf-8")
    return design_md


def step2_plan(
    project_dir: Path,
    slides_dir: Path,
    analysis_type: str,
    entity_target: Dict,
    pages_override: Optional[int],
) -> Path:
    """Step 2: slide-outline.yaml 생성."""
    spec = TYPE_SLIDE_SPEC.get(analysis_type, TYPE_SLIDE_SPEC["decision"])
    structure = spec["structure"]
    target_pages = pages_override or spec["pages"]

    # 구조를 target_pages에 맞춰 조정 (단순화: 초과 시 appendix 추가)
    if target_pages > len(structure):
        for i in range(target_pages - len(structure)):
            structure.append((f"appendix_{i+1}", f"부록 {i+1}"))
    elif target_pages < len(structure):
        structure = structure[:target_pages]

    # report-docs.md에서 핵심 메시지 추출
    report_md = project_dir / "reports" / "report-docs.md"
    report_text = ""
    if report_md.exists():
        try:
            report_text = report_md.read_text(encoding="utf-8")
        except OSError:
            pass

    # 제목 후보 추출 (H2 = Action Title들)
    action_titles = re.findall(r"^##\s+(.+)$", report_text, re.MULTILINE)[:10]

    outline = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": project_dir.name,
        "analysis_type": analysis_type,
        "entity_target": entity_target,
        "total_pages": len(structure),
        "design_reference": "slides/DESIGN.md",
        "source_md": "reports/report-docs.md",
        "pages": [],
    }

    for idx, (stype, ko_label) in enumerate(structure, start=1):
        page = {
            "page": idx,
            "type": stype,
            "label": ko_label,
        }
        # 본문 페이지 타입에 따라 Action Title 시드 추가
        if stype.startswith("key_finding") and action_titles:
            finding_idx = int(re.search(r"\d+", stype).group()) - 1
            if finding_idx < len(action_titles):
                page["action_title"] = action_titles[finding_idx]
        if stype == "cover":
            page["title"] = _extract_title(report_text) or project_dir.name
            page["subtitle"] = entity_target.get("scope", "Strategic Research Report")
        outline["pages"].append(page)

    out = slides_dir / "slide-outline.yaml"
    with out.open("w", encoding="utf-8") as f:
        yaml.dump(outline, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return out


def _extract_title(md_text: str) -> str:
    m = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def step3_prompt(slides_dir: Path, language: str) -> List[Path]:
    """Step 3: 페이지별 프롬프트 JSON 생성."""
    outline_path = slides_dir / "slide-outline.yaml"
    if not outline_path.exists():
        sys.stderr.write("[ERROR] slide-outline.yaml 없음 — Step 2 먼저 실행\n")
        return []

    with outline_path.open("r", encoding="utf-8") as f:
        outline = yaml.safe_load(f)

    prompts_dir = slides_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    for page in outline.get("pages", []):
        prompt = {
            "page_number": page["page"],
            "layout": page["type"],
            "language": language,
            "design_constraints": DEFAULT_DESIGN_TOKENS,
            "design_reference_file": "slides/DESIGN.md",
            "content": {
                "label": page.get("label", ""),
                "title": page.get("title", page.get("action_title", "")),
                "subtitle": page.get("subtitle", ""),
            },
            "image_generation_hint": _hint_for(page["type"], language),
            "source_md": "reports/report-docs.md",
            "analysis_type": outline.get("analysis_type"),
        }
        out = prompts_dir / f"page_{page['page']:02d}.json"
        with out.open("w", encoding="utf-8") as f:
            json.dump(prompt, f, ensure_ascii=False, indent=2)
        generated.append(out)

    return generated


def _hint_for(page_type: str, language: str) -> str:
    """페이지 타입별 이미지 생성 힌트."""
    ko_hints = {
        "cover": "클린한 표지. 좌측 상단 프로젝트명, 중앙 큰 타이틀, 하단 메타(일자/기밀등급). 딥 네이비 #003a70 강조.",
        "bluf": "상단 딥 네이비 박스에 핵심 결론 1문장. 본문 하단에 근거 3가지 불릿.",
        "key_finding_1": "Action Title + 좌측 KPI 박스 + 우측 본문.",
        "key_finding_2": "Action Title + 비교 차트 + So What 박스.",
        "key_finding_3": "Action Title + 테이블 + 인라인 수치 강조.",
        "financial": "표 또는 차트. 5~6행 주요 지표 + YoY 변화.",
        "scenarios": "3개 시나리오 (BASE/UP/DOWN) 테이블 또는 분기 차트.",
        "actions": "P0/P1/P2 우선순위 배지 + 액션 리스트.",
        "risks": "빨간 배너 + 리스크 2~4개 불릿.",
        "next_steps": "타임라인 또는 단계 카드 3~5개.",
        "entity_overview": "엔터티 로고 스페이스 + 기본 정보 + 핵심 숫자.",
        "market_context": "시장 지도 또는 세그먼트 다이어그램.",
        "market_size": "TAM/SAM/SOM 3층 케이크 차트.",
        "competitive": "플레이어 맵 (2x2 매트릭스 또는 점유율 파이).",
        "product_portfolio": "제품 카드 그리드 (3-4열).",
        "revenue": "3년 매출 추이 막대/선 차트.",
        "capability": "역량 레이더 또는 스킬 매트릭스.",
        "talent": "조직도 또는 인력 구성 파이.",
        "strategy": "전략 피라미드 또는 로드맵.",
        "ip_usage": "사례 타임라인 또는 카드 뷰.",
        "observations": "관찰 5개 불릿.",
        "exploration_space": "탐색 공간 다이어그램 (키워드 맵).",
        "candidate_matrix": "후보 가설 N×M 매트릭스.",
        "confirmed": "확정 가설 리스트 + 증거.",
        "rejected": "기각 가설 + 반증 근거.",
        "insufficient": "미해결 + 추가 리서치 질문.",
        "implications": "확정된 시사점 카드.",
        "next_research": "권고 리서치 우선순위.",
        "dashboard": "KPI 대시보드 (4-6개 KPI 타일).",
        "changes": "변화 방향 화살표 + 수치.",
        "outliers": "이상치 테이블 + 하이라이트.",
        "watchlist": "관찰 포인트 리스트.",
        "appendix": "부록: 데이터 테이블 또는 방법론.",
    }
    hint = ko_hints.get(page_type, "Action Title + 본문 + 출처 각주.")
    if language == "en":
        return hint + " (Render all text in English.)"
    return hint + " (한국어로 렌더링. Noto Sans KR 사용.)"


def step4_generate(
    project_dir: Path,
    slides_dir: Path,
    codex_bin: str,
) -> Tuple[int, int]:
    """Step 4: Codex exec로 이미지 생성.

    Returns:
        (success_count, fail_count)
    """
    prompts_dir = slides_dir / "prompts"
    if not prompts_dir.exists():
        sys.stderr.write("[ERROR] prompts/ 없음 — Step 3 먼저 실행\n")
        return (0, 0)

    prompt_files = sorted(prompts_dir.glob("page_*.json"))
    if not prompt_files:
        sys.stderr.write("[ERROR] 프롬프트 파일 없음\n")
        return (0, 0)

    success = 0
    fail = 0
    for pf in prompt_files:
        page_num = re.search(r"page_(\d+)", pf.name).group(1)
        output_png = slides_dir / f"page_{page_num}.png"

        prompt_instruction = f"""아래 JSON 프롬프트를 기반으로 슬라이드 이미지를 생성해주세요.
이미지를 파일로 저장: {output_png}

이미지 크기: 1920×1080 (16:9 와이드)
디자인 시스템: {slides_dir}/DESIGN.md 참조

프롬프트:
{pf.read_text(encoding='utf-8')}
"""
        cmd = [codex_bin, "exec", prompt_instruction]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=180
            )
        except subprocess.TimeoutExpired:
            sys.stderr.write(f"[TIMEOUT] page_{page_num} 생성 180s 초과\n")
            fail += 1
            continue
        except OSError as e:
            sys.stderr.write(f"[ERROR] codex 실행 실패: {e}\n")
            fail += 1
            continue

        if result.returncode != 0:
            sys.stderr.write(f"[FAIL] page_{page_num}: rc={result.returncode}\n")
            fail += 1
            continue

        # Codex가 파일을 실제 저장했는지 확인
        if output_png.exists() and output_png.stat().st_size > 1000:
            print(f"[OK] page_{page_num}.png ({output_png.stat().st_size // 1024} KB)")
            success += 1
        else:
            sys.stderr.write(
                f"[MISS] page_{page_num}.png 생성 안 됨 (Codex 응답에 이미지 없음)\n"
            )
            # Codex stdout/stderr에 힌트 저장 (디버깅용)
            log_path = slides_dir / f"page_{page_num}.codex-log.txt"
            log_path.write_text(
                f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}",
                encoding="utf-8",
            )
            fail += 1

    return (success, fail)


def write_manifest(slides_dir: Path, analysis_type: str, counts: Dict) -> Path:
    """slides-manifest.yaml 기록."""
    manifest = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "script_version": "v4.12",
        "analysis_type": analysis_type,
        "steps_completed": counts,
    }
    out = slides_dir / "slides-manifest.yaml"
    with out.open("w", encoding="utf-8") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="v4.12 Phase 4.8: Codex gpt-image-2 기반 슬라이드 생성"
    )
    parser.add_argument("project", help="프로젝트 디렉토리명")
    parser.add_argument("--project-root", default=".", help="프로젝트 루트")
    parser.add_argument(
        "--only",
        choices=["design", "plan", "prompt", "generate"],
        help="특정 단계만 실행 (생략 시 전체)",
    )
    parser.add_argument("--pages", type=int, help="슬라이드 수 override")
    parser.add_argument(
        "--language", choices=["ko", "en"], default="ko", help="슬라이드 언어"
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Step 4 생략 (프롬프트만 생성)",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_root).resolve() / args.project
    if not project_dir.exists():
        sys.stderr.write(f"[ERROR] 프로젝트 디렉토리 없음: {project_dir}\n")
        return 2

    # QA PASS 확인 (Phase 4.7 로직 재사용 개념)
    qa_report = project_dir / "qa" / "qa-report.md"
    if not args.only and qa_report.exists():
        content = qa_report.read_text(encoding="utf-8", errors="ignore")
        if "FAIL" in content[:500]:
            sys.stderr.write("[BLOCK] QA FAIL 상태 — Phase 4.8 스킵\n")
            return 2

    slides_dir = project_dir / "slides"
    analysis_type = load_analysis_type(project_dir)
    entity_target = load_entity_target(project_dir)

    print(f"[INIT] project={project_dir.name} type={analysis_type} lang={args.language}")

    counts = {}

    # Step 1: Design
    if args.only in (None, "design"):
        design_md = step1_design(project_dir, slides_dir, args.language)
        print(f"[STEP 1] {design_md.relative_to(project_dir)}")
        counts["design"] = "ok"

    # Step 2: Plan
    if args.only in (None, "plan"):
        outline = step2_plan(
            project_dir, slides_dir, analysis_type, entity_target, args.pages
        )
        print(f"[STEP 2] {outline.relative_to(project_dir)}")
        counts["plan"] = "ok"

    # Step 3: Prompt
    if args.only in (None, "prompt"):
        prompts = step3_prompt(slides_dir, args.language)
        print(f"[STEP 3] {len(prompts)}개 프롬프트 생성")
        counts["prompt"] = {"pages": len(prompts)}

    # Step 4: Generate
    if args.only in (None, "generate") and not args.skip_generate:
        codex_bin = find_codex()
        if not codex_bin:
            sys.stderr.write(
                "[SKIP] codex CLI 미설치 — Step 4 생략. 프롬프트만 사용하여 수동 생성 가능\n"
            )
            counts["generate"] = "skipped (codex not found)"
        else:
            print(f"[STEP 4] Codex {codex_bin} 이미지 생성 시작...")
            success, fail = step4_generate(project_dir, slides_dir, codex_bin)
            print(f"[STEP 4] 성공 {success}개 / 실패 {fail}개")
            counts["generate"] = {"success": success, "fail": fail}
            if fail > 0 and success == 0:
                sys.stderr.write(
                    "[HINT] Codex CLI로 이미지 생성 실패. Canva MCP 또는 수동 실행 고려.\n"
                )

    # Manifest
    manifest_path = write_manifest(slides_dir, analysis_type, counts)
    print(f"[MANIFEST] {manifest_path.relative_to(project_dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
