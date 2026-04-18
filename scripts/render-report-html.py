#!/usr/bin/env python3
"""
render-report-html.py — MD → HTML 변환기 (Phase 4.7)

report-docs.md / one-pager.md → HTML + sources.html 인덱스 페이지 생성.
MD는 SSOT, HTML은 뷰어용 파생물.

사용법:
    python3 scripts/render-report-html.py {project-name}

    # 옵션
    --only {docs|one-pager|sources}   # 특정 보고서만 변환 (기본: 모두)
    --docs-tags {link|mark|strip}     # report-docs의 태그 처리 (기본: link)
    --one-pager-tags {link|mark|strip} # one-pager의 태그 처리 (기본: strip)

태그 처리 모드:
    link  — <a href="sources.html#gf-001">[GF-001]</a> (클릭 시 출처 페이지)
    mark  — <mark class="rt-tag-gf">[GF-001]</mark> (하이라이트만)
    strip — 태그 자체를 텍스트에서 제거

산출물:
    {project}/reports/report-docs.html
    {project}/reports/one-pager.html
    {project}/reports/sources.html
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

try:
    import markdown
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError as e:
    sys.stderr.write(
        f"[ERROR] 필수 의존성 누락: {e}\n"
        f"        pip install -r requirements.txt 실행 필요\n"
    )
    sys.exit(2)

# ─── 경로 상수 ────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "core" / "style" / "report-templates"
SHARED_CSS_DIR = TEMPLATE_DIR / "shared"
DOCS_DIR = TEMPLATE_DIR / "report-docs"
ONE_PAGER_DIR = TEMPLATE_DIR / "one-pager"
SOURCES_DIR = TEMPLATE_DIR / "sources"

# ─── GF/S 태그 정규식 (보고서 본문 인라인 추적용) ───────────────
GF_TAG_RE = re.compile(r"\[GF-(\d{3,4})\]")
S_TAG_RE = re.compile(r"\[S(\d{1,3})\]")


def load_css(name: str) -> str:
    """shared/ 또는 템플릿별 CSS 로드. 존재하지 않으면 빈 문자열."""
    candidates = [
        SHARED_CSS_DIR / f"{name}.css",
        DOCS_DIR / f"{name}.css",
        ONE_PAGER_DIR / f"{name}.css",
        SOURCES_DIR / f"{name}.css",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


def transform_tags(text: str, mode: str = "link", sources_href: str = "sources.html") -> str:
    """[GF-###], [S##] 태그를 mode에 따라 처리.

    mode:
      - link  : <a href="sources.html#gf-001">[GF-001]</a>
      - mark  : <mark class="rt-tag-gf">[GF-001]</mark>
      - strip : 태그 제거 + 인접 공백 정리 (ASCII + 한국어 문장부호 처리)
    """
    if mode == "strip":
        text = GF_TAG_RE.sub("", text)
        text = S_TAG_RE.sub("", text)
        # 공백 정리: 문장부호 전 공백 제거 (ASCII + 중간점·일본어/한국어 괄호 포함)
        text = re.sub(r"\s+([,.;:!?)\]}·，。！？、；：）】］〕〉》」』])", r"\1", text)
        # 여는 괄호 뒤 공백 제거
        text = re.sub(r"([(\[{（【［〔〈《「『])\s+", r"\1", text)
        # 빈 괄호 제거
        text = re.sub(r"[(\[{（【]\s*[)\]}）】]", "", text)
        # 연속 공백을 하나로
        text = re.sub(r"\s{2,}", " ", text)
        # 라인 끝 공백 제거
        text = re.sub(r" +(\n|$)", r"\1", text)
        return text

    if mode == "mark":
        text = GF_TAG_RE.sub(
            lambda m: f'<mark class="rt-tag-gf">[GF-{m.group(1)}]</mark>', text
        )
        text = S_TAG_RE.sub(
            lambda m: f'<mark class="rt-tag-s">[S{m.group(1)}]</mark>', text
        )
        return text

    # link (default) — 앵커 ID는 원본 숫자 그대로 유지 (sources.html.j2의 id="gf-001"과 일치)
    text = GF_TAG_RE.sub(
        lambda m: (
            f'<a class="rt-tag-gf" href="{sources_href}#gf-{m.group(1)}" '
            f'title="Golden Fact {m.group(1)} — 출처 확인">[GF-{m.group(1)}]</a>'
        ),
        text,
    )
    text = S_TAG_RE.sub(
        lambda m: (
            f'<a class="rt-tag-s" href="{sources_href}#s-{m.group(1)}" '
            f'title="Source {m.group(1)} — 출처 확인">[S{m.group(1)}]</a>'
        ),
        text,
    )
    return text


def render_markdown(md_text: str, tag_mode: str = "link"):
    """Python-markdown으로 HTML 생성 + 추적성 태그 후처리."""
    md_engine = markdown.Markdown(
        extensions=[
            "extra",
            "toc",
            "sane_lists",
            "smarty",
            "nl2br",
        ],
        extension_configs={
            "toc": {"permalink": False, "toc_depth": "2-3"},
        },
    )
    html = md_engine.convert(md_text)
    html = transform_tags(html, mode=tag_mode)
    return html, md_engine.toc_tokens


def extract_toc_items(toc_tokens: list) -> list:
    """Python-markdown의 toc_tokens에서 h2만 추출 (사이드바용)."""
    items = []
    for t in toc_tokens:
        items.append({"title": t.get("name", ""), "anchor": t.get("id", "")})
    return items


def load_sources(project_dir: Path) -> dict:
    """golden-facts.yaml + findings/**/*.yaml의 source_index 집계."""
    try:
        import yaml
    except ImportError:
        sys.stderr.write("[WARN] pyyaml 미설치 — sources.html 생성 skip\n")
        return {"golden_facts": [], "source_index": [], "last_verified": None}

    result = {"golden_facts": [], "source_index": [], "last_verified": None}

    gf_path = project_dir / "findings" / "golden-facts.yaml"
    if gf_path.exists():
        try:
            data = yaml.safe_load(gf_path.read_text(encoding="utf-8")) or {}
            result["golden_facts"] = data.get("facts", []) or []
            result["last_verified"] = data.get("last_verified")
        except Exception as e:
            sys.stderr.write(f"[WARN] golden-facts.yaml 파싱 실패: {e}\n")

    findings_dir = project_dir / "findings"
    if findings_dir.exists():
        for yaml_file in findings_dir.rglob("*.yaml"):
            if yaml_file.name == "golden-facts.yaml":
                continue
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            src_idx = data.get("source_index") or []
            if not isinstance(src_idx, list):
                continue
            division_path = yaml_file.relative_to(findings_dir)
            division = division_path.parts[0] if division_path.parts else ""
            for s in src_idx:
                if not isinstance(s, dict) or not s.get("id"):
                    continue
                s = dict(s)
                s["_division"] = division
                s["_file"] = str(yaml_file.relative_to(project_dir))
                result["source_index"].append(s)

    # dedupe by id (최초 등장 우선)
    seen = set()
    deduped = []
    for s in result["source_index"]:
        sid = s.get("id", "")
        if sid in seen:
            continue
        seen.add(sid)
        deduped.append(s)
    # ID 순 정렬 (S01, S02, ...)
    deduped.sort(key=lambda x: (len(x.get("id", "")), x.get("id", "")))
    result["source_index"] = deduped

    # Golden Facts ID 순 정렬
    result["golden_facts"].sort(key=lambda x: x.get("id", ""))

    return result


def build_trust_badges(project_dir: Path, sources: dict) -> list:
    """qa-report + golden-facts + red-team에서 Trust Badge 생성."""
    badges = []

    qa_report = project_dir / "qa" / "qa-report.md"
    if qa_report.exists():
        content = qa_report.read_text(encoding="utf-8", errors="ignore")
        if "PASS" in content and "FAIL" not in content[:500]:
            badges.append({"label": "QA PASS", "status": "pass"})
        elif "CONDITIONAL" in content:
            badges.append({"label": "QA CONDITIONAL", "status": "warn"})

    n_gf = len(sources.get("golden_facts", []))
    if n_gf:
        badges.append({"label": f"Golden Facts {n_gf}건", "status": "pass"})

    n_s = len(sources.get("source_index", []))
    if n_s:
        badges.append({"label": f"Sources {n_s}건", "status": "pass"})

    red_team = project_dir / "thinking-loop" / "red-team-report.md"
    if red_team.exists():
        content = red_team.read_text(encoding="utf-8", errors="ignore")
        if content.count("Strong") == 0:
            badges.append({"label": "Red Team 통과", "status": "pass"})

    return badges


def extract_title(md_text: str) -> str:
    """MD 첫 h1을 타이틀로 추출."""
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_classification(md_text: str) -> Tuple[str, str]:
    """MD에서 기밀 등급 + 배포 범위 추출.

    찾는 패턴:
      - `## Classification` 섹션 하위 본문
      - `기밀 등급: PUBLIC | INTERNAL | CONFIDENTIAL`
      - `배포 범위: ...`
    """
    classification = "internal"
    distribution = ""

    # Classification 섹션 (any level heading) 하위 본문
    section_match = re.search(
        r"^#+\s*(?:기밀|Classification)[^\n]*\n(.+?)(?=\n#+\s|\Z)",
        md_text,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    body = section_match.group(1) if section_match else md_text

    if re.search(r"confidential|기밀", body, re.IGNORECASE):
        classification = "confidential"
    elif re.search(r"\bpublic\b|공개", body, re.IGNORECASE):
        classification = "public"
    elif re.search(r"internal|내부", body, re.IGNORECASE):
        classification = "internal"

    dist_match = re.search(
        r"(?:배포\s*범위|Distribution)\s*[:：]\s*([^\n]+)",
        md_text,
        re.IGNORECASE,
    )
    if dist_match:
        distribution = dist_match.group(1).strip()

    return classification, distribution


def _sum_issues_in_table(content: str, column: str) -> int:
    """qa-report.md의 '검증 결과 요약' 표에서 특정 컬럼의 합계 추출.

    qa-orchestrator 출력 포맷:
        | 모듈 | 결과 | Critical | Major | Minor |
        |------|------|----------|-------|-------|
        | ...  | PASS | 0        | 0     | 1     |
    """
    # 테이블 헤더에서 컬럼 인덱스 찾기
    header_match = re.search(
        r"\|\s*모듈\s*\|[^\n]+",
        content,
    )
    if not header_match:
        return 0
    headers = [h.strip().lower() for h in header_match.group(0).strip("|").split("|")]
    try:
        col_idx = headers.index(column.lower())
    except ValueError:
        return 0

    # 헤더 다음 줄들에서 숫자 추출 (| --- |--- | 구분선 제외)
    total = 0
    found_separator = False
    for line in content[header_match.end():].splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if found_separator:
                break  # 표 끝
            continue
        if re.match(r"\|[\s:|-]+\|$", line):
            found_separator = True
            continue
        if not found_separator:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if col_idx >= len(cells):
            continue
        num_match = re.match(r"^([0-9]+)", cells[col_idx])
        if num_match:
            total += int(num_match.group(1))
    return total


def check_qa_pass(project_dir: Path) -> Tuple[bool, str]:
    """qa/qa-report.md에서 PASS 판정을 엄격히 확인.

    검증 순서:
      1) '## 판정: FAIL' 또는 Status=FAIL 명시 → 거부
      2) '검증 결과 요약' 표에서 Critical/Major 합계 1건 이상 → 거부
      3) key-value 형식 'Critical: N'으로도 재검증 → 1건 이상 거부
      4) '## 판정: PASS' 또는 Status=PASS 있고 위 2/3이 0 → 통과
      5) CONDITIONAL은 거부
    """
    qa_report = project_dir / "qa" / "qa-report.md"
    if not qa_report.exists():
        return False, "qa/qa-report.md 없음 (Phase 5 QA 미실행)"
    try:
        content = qa_report.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return False, f"qa-report 읽기 실패: {e}"

    # 1) 명시 FAIL
    if re.search(
        r"판정\s*[:：]\s*FAIL|Status\s*[:：]\s*FAIL|결과\s*[:：]\s*FAIL|Verdict\s*[:：]\s*FAIL",
        content,
        re.IGNORECASE,
    ):
        return False, "qa-report: 판정=FAIL"

    # 2) 표 기반 Critical/Major 합계
    table_crit = _sum_issues_in_table(content, "Critical")
    table_major = _sum_issues_in_table(content, "Major")

    # 3) key-value 형식도 동시 검증 (표와 중복되면 max 사용)
    kv_crit_match = re.search(r"Critical\s*[:：]\s*([0-9]+)", content, re.IGNORECASE)
    kv_major_match = re.search(r"Major\s*[:：]\s*([0-9]+)", content, re.IGNORECASE)
    kv_crit = int(kv_crit_match.group(1)) if kv_crit_match else 0
    kv_major = int(kv_major_match.group(1)) if kv_major_match else 0

    crit = max(table_crit, kv_crit)
    major = max(table_major, kv_major)
    if crit > 0 or major > 0:
        return False, f"qa-report: Critical={crit}, Major={major} — 이슈 해소 필요"

    # 4) 명시적 PASS 판정 (우선순위: 판정 > Status > Verdict > 결과)
    status_match = re.search(
        r"(?:판정|Status|Verdict|결과)\s*[:：]\s*(\w+)",
        content,
        re.IGNORECASE,
    )
    if status_match:
        status = status_match.group(1).strip().upper()
        if status == "PASS":
            return True, f"qa-report: 판정=PASS (Critical=0, Major=0)"
        if status == "CONDITIONAL":
            return False, "qa-report: 판정=CONDITIONAL (Major 이슈 미해소 가능성)"
        return False, f"qa-report: 판정={status} (PASS 필요)"

    # 5) 명시 판정 없음 — 보수적으로 거부
    return False, "qa-report: 판정 명시 없음 (## 판정: PASS 필요)"


def audit_log_append(project_dir: Path, event: str, detail: dict) -> None:
    """기밀 우회/감사 이벤트를 qa/audit-log.md에 append.

    CONFIDENTIAL 우회 사용 시 누가 언제 어떤 파일을 내보냈는지 추적 가능하게 한다.
    """
    import sys as _sys
    audit_log = project_dir / "qa" / "audit-log.md"
    audit_log.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    lines = [f"## {timestamp} — {event}", ""]
    for k, v in detail.items():
        lines.append(f"- {k}: {v}")
    lines.append(f"- argv: {' '.join(_sys.argv)}")
    lines.append("")
    with audit_log.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _strip_source_column(md_table: str) -> str:
    """MD 테이블에서 '출처'/'Source' 헤더가 있는 열을 제거.

    원페이퍼는 공간이 제한되므로 출처 열을 시각적으로 표시하지 않는다.
    (출처 추적은 sources.html에서 별도로 확인 — one-pager.md에 열이 있어도 여기서 제거)
    """
    source_keywords = ("출처", "source", "소스", "src", "ref", "출전")
    lines = md_table.strip().split("\n")
    if len(lines) < 2:
        return md_table

    # 첫 줄(헤더)에서 출처 열 인덱스 탐지
    header_raw = lines[0].strip().strip("|")
    header_cells = [c.strip() for c in header_raw.split("|")]
    drop_idx = None
    for i, cell in enumerate(header_cells):
        if any(kw in cell.lower() for kw in source_keywords):
            drop_idx = i
            break
    if drop_idx is None:
        return md_table

    def pop_cell(line: str) -> str:
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            return line
        cells = line.strip("|").split("|")
        if drop_idx < len(cells):
            cells.pop(drop_idx)
        return "|" + "|".join(cells) + "|"

    return "\n".join(pop_cell(l) for l in lines)


def parse_one_pager_sections(md_text: str, tag_mode: str = "strip") -> dict:
    """원페이퍼 MD를 섹션별로 파싱 (brief-writer.md 레이아웃 기준)."""
    sections = {
        "bluf": None,
        "key_findings": [],
        "financial_table_html": "",
        "recommended_actions": [],
        "risks": [],
        "classification": "internal",
        "subtitle": "",
    }

    def md_inline(text: str) -> str:
        """짧은 텍스트를 inline HTML로 (p 태그 제거)."""
        html = markdown.markdown(text, extensions=["extra"])
        html = transform_tags(html, mode=tag_mode)
        return re.sub(r"^<p>|</p>$", "", html.strip())

    def md_block(text: str) -> str:
        return transform_tags(markdown.markdown(text, extensions=["extra"]), mode=tag_mode)

    blocks = re.split(r"\n(?=##\s|■\s)", md_text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        head_line = block.splitlines()[0].lower()
        body = "\n".join(block.splitlines()[1:]).strip()

        if "bluf" in head_line or "bottom line" in head_line:
            lines = [l for l in body.splitlines() if l.strip()]
            if lines:
                sections["bluf"] = {
                    "statement": md_inline(lines[0]),
                    "reason": md_block("\n".join(lines[1:])) if len(lines) > 1 else "",
                }

        elif "key finding" in head_line or "핵심" in head_line:
            items = re.findall(
                r"(?:^|\n)\s*[-*0-9.]+\s+(.+?)(?=\n\s*[-*0-9.]|\Z)",
                body,
                re.DOTALL,
            )
            sections["key_findings"] = [
                md_inline(item.strip()) for item in items if item.strip()
            ]

        elif "financial" in head_line or "snapshot" in head_line or "재무" in head_line:
            table_match = re.search(r"\|.+\|(?:\n\|.+\|)+", body)
            if table_match:
                cleaned = _strip_source_column(table_match.group(0))
                sections["financial_table_html"] = md_block(cleaned)

        elif "action" in head_line or "권고" in head_line or "추천" in head_line:
            for line in body.splitlines():
                m = re.match(r"\s*(P[012])[:\s]+(.+)", line)
                if m:
                    priority, rest = m.group(1), m.group(2)
                    parts = re.split(r"\s+—\s+|\s+-\s+", rest, maxsplit=1)
                    title = parts[0].strip()
                    description = parts[1] if len(parts) > 1 else ""
                    owner = ""
                    milestone = ""
                    owner_m = re.search(r"담당\s*[:：]\s*([^,，·]+)", description)
                    if owner_m:
                        owner = owner_m.group(1).strip()
                    ms_m = re.search(r"(\d+일|\d+개월|\d+분기|\d+년)", description)
                    if ms_m:
                        milestone = ms_m.group(1)
                    sections["recommended_actions"].append({
                        "priority": priority.lower(),
                        "title": transform_tags(title, mode=tag_mode),
                        "description": transform_tags(description, mode=tag_mode),
                        "owner": owner,
                        "milestone": milestone,
                    })

        elif "risk" in head_line or "리스크" in head_line or "위험" in head_line:
            items = re.findall(
                r"(?:^|\n)\s*(?:⚠\s*)?[-*]\s+(.+?)(?=\n\s*[-*]|\Z)",
                body,
                re.DOTALL,
            )
            sections["risks"] = [
                md_inline(item.strip()) for item in items if item.strip()
            ]

        elif "기밀" in head_line or "classification" in head_line:
            if "confidential" in body.lower() or "기밀" in body:
                sections["classification"] = "confidential"
            elif "public" in body.lower():
                sections["classification"] = "public"

    return sections


def _sources_to_json_lookup(sources: dict) -> str:
    """report-docs.html에 임베드할 출처 JSON 생성.

    키: gf-001, s-01 등 앵커와 일치하는 형태.
    값: title + url + confidence + category 등 최소 필드.
    FF 수정 — 산출물이 분리돼도 [GF-###] 링크 클릭 시 임베드된 데이터로 모달 표시.
    """
    import json
    lookup = {}
    for f in sources.get("golden_facts", []) or []:
        fid = f.get("id", "")
        if not fid:
            continue
        key = fid.lower()  # 'GF-001' → 'gf-001'
        lookup[key] = {
            "id": fid,
            "title": (
                (f.get("entity") or "") + " — " + (f.get("metric") or "")
            ).strip(" —"),
            "value": f.get("value"),
            "unit": f.get("unit", ""),
            "as_of": f.get("as_of", ""),
            "confidence": f.get("confidence", ""),
            "category": f.get("category", ""),
            "source_id": f.get("source_id", ""),
            "source_detail": f.get("source_detail", ""),
        }
    for s in sources.get("source_index", []) or []:
        sid = s.get("id", "")
        if not sid:
            continue
        key = sid.lower()  # 'S01' → 's01'. 앵커는 s-01 형식이므로 별도 변환
        # S01 → s-01
        m = re.match(r"[Ss](\d+)$", sid)
        if m:
            key = f"s-{m.group(1)}"
        lookup[key] = {
            "id": sid,
            "title": s.get("name", ""),
            "url": s.get("url") or "",
            "type": s.get("type", ""),
            "reliability": s.get("reliability", ""),
            "summary": s.get("summary", ""),
            "accessed": s.get("accessed", ""),
        }
    return json.dumps(lookup, ensure_ascii=False)


def render_report_docs(
    project_dir: Path,
    out_path: Path,
    sources: dict,
    tag_mode: str = "link",
    allow_confidential: bool = False,
) -> bool:
    """report-docs.md → report-docs.html."""
    md_path = project_dir / "reports" / "report-docs.md"
    if not md_path.exists():
        print(f"[SKIP] {md_path} 없음")
        return False

    md_text = md_path.read_text(encoding="utf-8")
    classification, distribution = extract_classification(md_text)

    if classification == "confidential" and not allow_confidential:
        sys.stderr.write(
            f"[BLOCK] {md_path} 기밀등급=CONFIDENTIAL → HTML 내보내기 차단됨.\n"
            f"        명시적 허용: --allow-confidential-export 플래그 추가\n"
        )
        # 기존 HTML이 남아 있으면 stale 노출 방지를 위해 삭제
        if out_path.exists():
            out_path.unlink()
            sys.stderr.write(f"        기존 {out_path.name} 삭제됨 (stale 노출 방지)\n")
        return False

    if classification == "confidential" and allow_confidential:
        audit_log_append(
            project_dir,
            "CONFIDENTIAL_EXPORT_BYPASS",
            {
                "file": str(md_path.relative_to(project_dir)),
                "target": str(out_path.relative_to(project_dir)),
                "classification": classification,
                "distribution": distribution or "(미지정)",
            },
        )
        sys.stderr.write(
            f"[AUDIT] CONFIDENTIAL 내보내기 우회 사용됨 — qa/audit-log.md에 기록\n"
        )

    body_html, toc_tokens = render_markdown(md_text, tag_mode=tag_mode)

    env = Environment(
        loader=FileSystemLoader(DOCS_DIR),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report-docs.html.j2")

    meta = {
        "title": extract_title(md_text) or "전략 보고서",
        "project": project_dir.name,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "kicker": "Strategic Research Report",
        "classification": classification,
        "distribution": distribution,
    }

    # FF 수정: 산출물 분리 시에도 태그 클릭이 작동하도록 sources JSON 임베드
    sources_json = _sources_to_json_lookup(sources) if tag_mode == "link" else "{}"
    # LL: 임베드 JSON 크기 경고 (> 512KB = 약 500+ 출처)
    if len(sources_json) > 512 * 1024:
        sys.stderr.write(
            f"[WARN] sources JSON 크기 {len(sources_json) // 1024} KB — "
            f"report-docs.html 로드 지연 가능. --docs-tags mark 사용 고려.\n"
        )
    # XSS 방지: script 태그 종료 시퀀스를 escape (JSON 내부에 </script>가 있으면 embed 깨짐)
    sources_json = sources_json.replace("</", "<\\/")

    html = template.render(
        meta=meta,
        toc=extract_toc_items(toc_tokens),
        trust_badges=build_trust_badges(project_dir, sources),
        body_html=body_html,
        sources_json=sources_json,
        css_tokens=load_css("tokens"),
        css_base=load_css("base"),
        css_print=load_css("print"),
        css_report_docs=load_css("report-docs"),
        tag_mode=tag_mode,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(
        f"[OK]   {out_path}  "
        f"({len(html):,} bytes, tags={tag_mode}, class={classification.upper()})"
    )
    return True


def render_one_pager(
    project_dir: Path,
    out_path: Path,
    sources: dict,
    tag_mode: str = "strip",
    allow_confidential: bool = False,
    strict: bool = False,
) -> bool:
    """one-pager.md → one-pager.html."""
    md_path = project_dir / "reports" / "one-pager.md"
    if not md_path.exists():
        print(f"[SKIP] {md_path} 없음")
        return False

    md_text = md_path.read_text(encoding="utf-8")
    classification, _ = extract_classification(md_text)

    if classification == "confidential" and not allow_confidential:
        sys.stderr.write(
            f"[BLOCK] {md_path} 기밀등급=CONFIDENTIAL → HTML 내보내기 차단됨.\n"
            f"        명시적 허용: --allow-confidential-export 플래그 추가\n"
        )
        if out_path.exists():
            out_path.unlink()
            sys.stderr.write(f"        기존 {out_path.name} 삭제됨 (stale 노출 방지)\n")
        return False

    if classification == "confidential" and allow_confidential:
        audit_log_append(
            project_dir,
            "CONFIDENTIAL_EXPORT_BYPASS",
            {
                "file": str(md_path.relative_to(project_dir)),
                "target": str(out_path.relative_to(project_dir)),
                "classification": classification,
            },
        )
        sys.stderr.write(
            f"[AUDIT] CONFIDENTIAL 내보내기 우회 사용됨 — qa/audit-log.md에 기록\n"
        )

    parsed = parse_one_pager_sections(md_text, tag_mode=tag_mode)

    # Strict 모드: 핵심 섹션 누락 시 FAIL
    if strict:
        missing = []
        if not parsed.get("bluf"):
            missing.append("BLUF")
        if not parsed.get("key_findings"):
            missing.append("Key Findings")
        if not parsed.get("financial_table_html"):
            missing.append("Financial Snapshot")
        if not parsed.get("recommended_actions"):
            missing.append("Recommended Actions")
        if not parsed.get("risks"):
            missing.append("Risk Alert")
        if missing:
            sys.stderr.write(
                f"[STRICT-FAIL] {md_path} 필수 섹션 누락: {', '.join(missing)}\n"
                f"              MD 섹션 헤더 확인 (## BLUF / Key Findings / "
                f"Financial Snapshot / Recommended Actions / Risk Alert)\n"
            )
            if out_path.exists():
                out_path.unlink()
                sys.stderr.write(f"              기존 {out_path.name} 삭제됨 (stale 방지)\n")
            return False

    env = Environment(
        loader=FileSystemLoader(ONE_PAGER_DIR),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("one-pager.html.j2")

    meta = {
        "title": extract_title(md_text) or "경영진 원페이퍼",
        "subtitle": parsed.get("subtitle", ""),
        "project": project_dir.name,
        "generated_at": datetime.now().strftime("%Y-%m-%d"),
        "classification": parsed.get("classification", "internal"),
    }

    html = template.render(
        meta=meta,
        bluf=parsed.get("bluf"),
        key_findings=parsed.get("key_findings", []),
        financial_table_html=parsed.get("financial_table_html", ""),
        recommended_actions=parsed.get("recommended_actions", []),
        risks=parsed.get("risks", []),
        trust_badges=build_trust_badges(project_dir, sources),
        css_tokens=load_css("tokens"),
        css_base=load_css("base"),
        css_print=load_css("print"),
        css_one_pager=load_css("one-pager"),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"[OK]   {out_path}  ({len(html):,} bytes, tags={tag_mode})")
    return True


def _report_has_confidential(project_dir: Path) -> bool:
    """프로젝트의 보고서 중 하나라도 CONFIDENTIAL이면 True.

    sources.html도 동일한 보호 대상 — 한 문서가 CONFIDENTIAL이면
    그 문서가 참조하는 출처도 기밀성 경계 안으로 들어간다.
    """
    for name in ("report-docs.md", "one-pager.md"):
        p = project_dir / "reports" / name
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        cls, _ = extract_classification(text)
        if cls == "confidential":
            return True
    return False


def render_sources(
    project_dir: Path,
    out_path: Path,
    sources: dict,
    allow_confidential: bool = False,
) -> bool:
    """sources.html — 출처 인덱스 페이지 생성.

    보고서 중 하나라도 CONFIDENTIAL이면 sources.html도 차단
    (출처 데이터가 기밀 정보를 뒷받침하므로 동일 기밀성 적용).
    """
    if not sources["golden_facts"] and not sources["source_index"]:
        print(f"[SKIP] Golden Facts + Source Index 모두 비어 있음 — sources.html 생략")
        return False

    if _report_has_confidential(project_dir) and not allow_confidential:
        sys.stderr.write(
            f"[BLOCK] 보고서 중 CONFIDENTIAL 존재 → sources.html도 차단됨.\n"
            f"        명시적 허용: --allow-confidential-export 플래그 추가\n"
        )
        if out_path.exists():
            out_path.unlink()
            sys.stderr.write(f"        기존 {out_path.name} 삭제됨 (stale 노출 방지)\n")
        return False

    # CONFIDENTIAL 허용된 경우 classification 메타데이터를 sources.html에도 전파
    classification = "confidential" if _report_has_confidential(project_dir) else "internal"

    env = Environment(
        loader=FileSystemLoader(SOURCES_DIR),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("sources.html.j2")

    meta = {
        "project": project_dir.name,
        "last_verified": sources.get("last_verified") or "—",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "classification": classification,
    }

    html = template.render(
        meta=meta,
        golden_facts=sources["golden_facts"],
        source_index=sources["source_index"],
        css_tokens=load_css("tokens"),
        css_base=load_css("base"),
        css_print=load_css("print"),
        css_sources=load_css("sources"),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(
        f"[OK]   {out_path}  "
        f"({len(html):,} bytes, GF={len(sources['golden_facts'])} S={len(sources['source_index'])}, class={classification.upper()})"
    )
    return True


def _hash_inputs(project_dir: Path) -> dict:
    """HTML 재생성 트리거 입력들의 핑거프린트 수집.

    핑거프린트: mtime_ns(나노초) + size + 콘텐츠 길이 기반 CRC32.
    - 민감 콘텐츠 역추적 불가 (CRC32 32-bit = 약 40억 해시 공간, mtime_ns 필요)
    - 같은 초 내 수정/동일 크기 해결 (mtime_ns + CRC32 조합)
    """
    import zlib

    targets = {
        "report-docs.md": project_dir / "reports" / "report-docs.md",
        "one-pager.md": project_dir / "reports" / "one-pager.md",
        "golden-facts.yaml": project_dir / "findings" / "golden-facts.yaml",
        "qa-report.md": project_dir / "qa" / "qa-report.md",
    }

    def _fp(p: Path) -> str:
        if not p.exists():
            return "-"
        st = p.stat()
        try:
            crc = zlib.crc32(p.read_bytes())
        except OSError:
            crc = 0
        # mtime 나노초 + size + CRC32 조합
        return f"{st.st_mtime_ns}-{st.st_size}-{crc:08x}"

    result = {key: _fp(p) for key, p in targets.items()}

    # findings/**/*.yaml은 통합 핑거프린트 (CRC32 누적)
    findings = project_dir / "findings"
    if findings.exists():
        files = sorted(
            [y for y in findings.rglob("*.yaml") if y.name != "golden-facts.yaml"]
        )
        if files:
            crc = 0
            max_mtime_ns = 0
            total_size = 0
            for f in files:
                try:
                    crc = zlib.crc32(f.read_bytes(), crc)
                    st = f.stat()
                    max_mtime_ns = max(max_mtime_ns, st.st_mtime_ns)
                    total_size += st.st_size
                except OSError:
                    pass
            result["findings-source_index"] = (
                f"{len(files)}-{max_mtime_ns}-{total_size}-{crc:08x}"
            )
        else:
            result["findings-source_index"] = "-"
    else:
        result["findings-source_index"] = "-"
    return result


def _manifest_path(project_dir: Path) -> Path:
    """Manifest 위치 — 프로젝트 루트의 숨김 파일 (reports/ 바깥).

    reports/ 디렉토리 단위로 경영진에게 전달 시 manifest가 딸려가지 않도록.
    """
    return project_dir / ".html-manifest.txt"


def check_stale_inputs(reports_dir: Path, project_dir: Path) -> list:
    """이전 실행 이후 입력이 변경/삭제됐는지 감지.

    Returns: stale로 판정된 파일 키 리스트 (없으면 [])
    """
    manifest_path = _manifest_path(project_dir)
    if not manifest_path.exists():
        # 마이그레이션: 구 위치(reports/)에 있으면 읽되 다음 실행에서 새 위치로 이동
        legacy = reports_dir / ".html-manifest.txt"
        if legacy.exists():
            manifest_path = legacy
        else:
            return []  # 최초 실행
    try:
        prev_lines = manifest_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    prev_hashes = {}
    for line in prev_lines:
        m = re.match(r"input\[([^\]]+)\]:\s*(\S+)", line)
        if m:
            prev_hashes[m.group(1)] = m.group(2)

    if not prev_hashes:
        return []

    current = _hash_inputs(project_dir)
    stale = []
    for key, curr_fp in current.items():
        prev_fp = prev_hashes.get(key)
        if not prev_fp:
            continue
        if prev_fp != curr_fp and curr_fp != "-":
            stale.append(f"{key} 변경")
        elif curr_fp == "-" and prev_fp != "-":
            stale.append(f"{key} 삭제됨")
    return stale


def write_manifest(reports_dir: Path, project_dir: Path, generated_files: list) -> None:
    """HTML 생성물 + 입력 핑거프린트 manifest 기록.

    위치: 프로젝트 루트 `.html-manifest.txt` (reports/ 밖)
    핑거프린트: mtime_ns + size + CRC32 (역추적 불가, 충돌 최소화)
    """
    manifest_lines = [
        "# HTML Export Manifest (Phase 4.7)",
        "# GENERATED — do not edit manually",
        "# 핑거프린트: mtime_ns + size + CRC32 (stale 감지 전용, content hash 아님)",
        f"# generated_at: {datetime.now().isoformat()}",
        "",
        "## Generated HTML files",
    ]
    for html_path in generated_files:
        if not html_path.exists():
            continue
        size = html_path.stat().st_size
        manifest_lines.append(f"output[{html_path.name}]: size={size}")

    manifest_lines.append("")
    manifest_lines.append("## Input fingerprints (Phase 4.7 재실행 트리거)")
    inputs = _hash_inputs(project_dir)
    for key, fp in inputs.items():
        manifest_lines.append(f"input[{key}]: {fp}")

    _manifest_path(project_dir).write_text(
        "\n".join(manifest_lines) + "\n", encoding="utf-8"
    )

    # 구 위치(reports/.html-manifest.txt) 제거 (마이그레이션)
    legacy = reports_dir / ".html-manifest.txt"
    if legacy.exists():
        try:
            legacy.unlink()
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser(description="Phase 4.7: MD → HTML 변환기")
    parser.add_argument("project", help="프로젝트 디렉토리명")
    parser.add_argument(
        "--only",
        choices=["docs", "one-pager", "sources"],
        help="특정 보고서만 변환 (기본: 모두)",
    )
    parser.add_argument(
        "--docs-tags",
        choices=["link", "mark", "strip"],
        default="link",
        help="report-docs의 태그 처리 (기본: link)",
    )
    parser.add_argument(
        "--one-pager-tags",
        choices=["link", "mark", "strip"],
        default="strip",
        help="one-pager의 태그 처리 (기본: strip)",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="프로젝트 루트 (기본: 현재 디렉토리)",
    )
    parser.add_argument(
        "--require-qa-pass",
        action="store_true",
        default=True,
        help="qa/qa-report.md PASS 판정이 없으면 중단 (기본: 활성)",
    )
    parser.add_argument(
        "--skip-qa-check",
        dest="require_qa_pass",
        action="store_false",
        help="QA PASS 게이트 우회 (Phase 5 전 프리뷰용)",
    )
    parser.add_argument(
        "--allow-confidential-export",
        action="store_true",
        default=False,
        help="기밀등급=CONFIDENTIAL 보고서를 HTML로 내보낼 수 있게 허용",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="one-pager 필수 섹션(BLUF/Findings/Financial/Actions/Risks) 누락 시 FAIL",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_root).resolve() / args.project
    if not project_dir.exists():
        sys.stderr.write(f"[ERROR] 프로젝트 디렉토리 없음: {project_dir}\n")
        sys.exit(1)

    # QA PASS 게이트
    if args.require_qa_pass:
        qa_ok, qa_msg = check_qa_pass(project_dir)
        if not qa_ok:
            sys.stderr.write(
                f"[BLOCK] QA PASS 게이트 실패: {qa_msg}\n"
                f"        우회: --skip-qa-check 플래그 추가 (프리뷰 용도)\n"
            )
            sys.exit(2)
        print(f"[GATE] {qa_msg}")

    reports_dir = project_dir / "reports"

    # Stale 감지 — 이전 실행 이후 입력이 바뀌었는지 경고
    stale = check_stale_inputs(reports_dir, project_dir)
    if stale:
        sys.stderr.write(
            "[STALE] 이전 HTML 생성 이후 입력이 변경됨:\n"
            + "\n".join(f"        - {s}" for s in stale)
            + "\n        → 계속 진행. 재생성된 HTML이 최신 상태로 갱신됩니다.\n"
        )

    sources = load_sources(project_dir)

    results = []
    generated = []

    if args.only in (None, "docs"):
        ok = render_report_docs(
            project_dir,
            reports_dir / "report-docs.html",
            sources,
            tag_mode=args.docs_tags,
            allow_confidential=args.allow_confidential_export,
        )
        results.append(ok)
        if ok:
            generated.append(reports_dir / "report-docs.html")

    if args.only in (None, "one-pager"):
        ok = render_one_pager(
            project_dir,
            reports_dir / "one-pager.html",
            sources,
            tag_mode=args.one_pager_tags,
            allow_confidential=args.allow_confidential_export,
            strict=args.strict,
        )
        results.append(ok)
        if ok:
            generated.append(reports_dir / "one-pager.html")

    if args.only in (None, "sources"):
        ok = render_sources(
            project_dir,
            reports_dir / "sources.html",
            sources,
            allow_confidential=args.allow_confidential_export,
        )
        results.append(ok)
        if ok:
            generated.append(reports_dir / "sources.html")

    if not any(results):
        sys.stderr.write("[WARN] 변환된 파일 없음\n")
        sys.exit(1)

    if generated:
        write_manifest(reports_dir, project_dir, generated)

    print(f"[DONE] {sum(results)}개 HTML 생성 — {reports_dir}")


if __name__ == "__main__":
    main()
