#!/usr/bin/env python3
"""
render-onepager-pdf.py — one-pager.html → one-pager.pdf (Phase 4.7)

Chrome headless를 사용해 A4 1페이지 PDF를 생성한다.
외부 Python 의존성 없음 (표준 라이브러리만).

우선순위:
    1. macOS: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
    2. Linux: google-chrome / chromium / chromium-browser
    3. weasyprint (설치된 경우 fallback)

사용법:
    python3 scripts/render-onepager-pdf.py {project-name}
    python3 scripts/render-onepager-pdf.py {project-name} --input custom.html --output custom.pdf

※ report-docs.pdf는 경영진 배포 대상이 아니므로 기본적으로 생성하지 않음.
  필요 시 --target docs 플래그 추가.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple


CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "msedge",
]


def find_chrome() -> Optional[str]:
    """사용 가능한 Chrome/Chromium 실행 경로 탐색."""
    for candidate in CHROME_CANDIDATES:
        if "/" in candidate:
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
        else:
            found = shutil.which(candidate)
            if found:
                return found
    return None


def _validate_pdf(pdf_path: Path) -> Tuple[bool, str]:
    """PDF 파일 무결성 검증.

    1) %PDF- 헤더 존재
    2) %%EOF 트레일러 존재 (파일 끝 1KB 내)
    3) 최소 크기 1KB
    """
    if not pdf_path.exists():
        return False, "파일 없음"
    size = pdf_path.stat().st_size
    if size < 1000:
        return False, f"파일 크기 부족 ({size} bytes)"
    try:
        with open(pdf_path, "rb") as f:
            head = f.read(8)
            if not head.startswith(b"%PDF-"):
                return False, f"PDF 헤더 없음 (head={head[:8]!r})"
            f.seek(max(0, size - 1024))
            tail = f.read()
            if b"%%EOF" not in tail:
                return False, "PDF %%EOF 트레일러 없음"
    except OSError as e:
        return False, f"파일 읽기 실패: {e}"
    return True, f"{size / 1024:.1f} KB"


def _wait_for_stable_size(pdf_path: Path, intervals: int = 3, wait_s: float = 1.5) -> bool:
    """파일 크기가 안정화될 때까지 polling (타임아웃 후 사용).

    Chrome이 kill된 직후 부분 PDF가 남았을 수 있으므로,
    연속 N회 측정에서 크기가 변하지 않으면 안정화로 간주.
    """
    import time
    last_size = -1
    stable_count = 0
    for _ in range(intervals * 2):
        if not pdf_path.exists():
            time.sleep(wait_s)
            continue
        current = pdf_path.stat().st_size
        if current == last_size and current > 0:
            stable_count += 1
            if stable_count >= intervals:
                return True
        else:
            stable_count = 0
        last_size = current
        time.sleep(wait_s)
    return stable_count >= intervals


def render_with_chrome(html_path: Path, pdf_path: Path, chrome: str) -> bool:
    """Chrome headless로 HTML을 PDF 변환.

    일부 환경에서 Chrome이 PDF를 쓴 뒤 프로세스 종료가 지연되므로,
    타임아웃 후에도 파일 안정화 + %PDF-/EOF 헤더 검증으로 성공 판정.
    """
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    # 이전 실행 잔여물 제거 (재판정 오염 방지)
    if pdf_path.exists():
        pdf_path.unlink()

    timeout_s = 90
    timed_out = False
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--virtual-time-budget=8000",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={pdf_path}",
            f"--user-data-dir={tmpdir}",
            html_path.resolve().as_uri(),
        ]
        print(f"[CHROME] --print-to-pdf={pdf_path.name}  ({html_path.name})")
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout_s
            )
        except subprocess.TimeoutExpired:
            timed_out = True
            result = None
            sys.stderr.write(
                f"[WARN] Chrome headless {timeout_s}s 타임아웃 — "
                f"파일 안정화 대기 후 무결성 검증\n"
            )
            # 부분 PDF 방지: 크기가 안정화될 때까지 대기
            _wait_for_stable_size(pdf_path)

    if result is not None and result.returncode != 0:
        sys.stderr.write(f"[ERROR] Chrome 실행 실패 (rc={result.returncode})\n")
        sys.stderr.write(f"        stderr: {result.stderr[:400]}\n")
        return False

    # 반드시 헤더/EOF 검증 (타임아웃 여부 무관)
    ok, msg = _validate_pdf(pdf_path)
    if not ok:
        sys.stderr.write(
            f"[ERROR] PDF 무결성 실패: {msg}"
            + (" (timeout)" if timed_out else "")
            + "\n"
        )
        if pdf_path.exists():
            pdf_path.unlink()  # 손상된 PDF 삭제 — weasyprint fallback 유도
        return False

    if timed_out:
        print(f"[OK]    타임아웃이었으나 PDF 무결성 검증 통과 ({msg})")
    return True


def render_with_weasyprint(html_path: Path, pdf_path: Path) -> bool:
    """fallback: weasyprint (설치된 경우에만)."""
    try:
        from weasyprint import HTML  # type: ignore
    except ImportError:
        return False

    try:
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return pdf_path.exists() and pdf_path.stat().st_size > 100
    except Exception as e:
        sys.stderr.write(f"[ERROR] weasyprint 실패: {e}\n")
        return False


def verify_pdf_watermark(pdf_path: Path, expected: str = "CONFIDENTIAL") -> Tuple[bool, str]:
    """선택적 PDF 텍스트 검증.

    pdftotext(Poppler)가 설치된 경우 PDF 내용에서 `expected` 문자열을 검색.
    미설치 시 skip (CONFIDENTIAL 보고서일 때만 호출 — 워터마크 누락 방지).
    """
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        return True, "pdftotext 미설치 — 텍스트 검증 생략 (best-effort)"
    try:
        result = subprocess.run(
            [pdftotext, "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=15,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return True, f"pdftotext 실행 실패: {e} — 검증 생략"
    if result.returncode != 0:
        return True, "pdftotext 실패 — 검증 생략"
    # @page @top-center는 페이지 헤더로 들어가므로 전체 텍스트에서 검색
    if expected.upper() in result.stdout.upper():
        return True, f"워터마크 검증 통과 ('{expected}' 발견)"
    return False, f"워터마크 누락 — '{expected}' 미발견 (CSS @page @top-center 지원 확인 필요)"


def main():
    parser = argparse.ArgumentParser(description="Phase 4.7: one-pager.html → PDF")
    parser.add_argument("project", help="프로젝트 디렉토리명")
    parser.add_argument(
        "--target",
        choices=["one-pager", "docs", "both"],
        default="one-pager",
        help="변환 대상 (기본: one-pager만)",
    )
    parser.add_argument("--input", help="커스텀 입력 HTML 경로")
    parser.add_argument("--output", help="커스텀 출력 PDF 경로")
    parser.add_argument(
        "--project-root",
        default=".",
        help="프로젝트 루트 (기본: 현재 디렉토리)",
    )
    parser.add_argument(
        "--verify-watermark",
        action="store_true",
        help="CONFIDENTIAL 보고서 PDF에 'CONFIDENTIAL' 텍스트 실재 확인 (pdftotext 필요)",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_root).resolve() / args.project
    reports_dir = project_dir / "reports"

    if args.input and args.output:
        targets = [(Path(args.input), Path(args.output))]
    else:
        targets = []
        if args.target in ("one-pager", "both"):
            targets.append(
                (reports_dir / "one-pager.html", reports_dir / "one-pager.pdf")
            )
        if args.target in ("docs", "both"):
            targets.append(
                (reports_dir / "report-docs.html", reports_dir / "report-docs.pdf")
            )

    chrome = find_chrome()
    if chrome:
        print(f"[ENGINE] Chrome headless: {chrome}")
    else:
        print("[ENGINE] Chrome 미발견 — weasyprint fallback 시도")

    success_count = 0
    for html_path, pdf_path in targets:
        if not html_path.exists():
            print(f"[SKIP] {html_path} 없음 (render-report-html.py 먼저 실행 필요)")
            continue

        ok = False
        if chrome:
            ok = render_with_chrome(html_path, pdf_path, chrome)
        if not ok:
            ok = render_with_weasyprint(html_path, pdf_path)

        if ok:
            size_kb = pdf_path.stat().st_size / 1024
            print(f"[OK]    {pdf_path}  ({size_kb:.1f} KB)")

            # CONFIDENTIAL 워터마크 검증 (--verify-watermark 플래그 시)
            if args.verify_watermark:
                # MD에서 classification 확인 후 CONFIDENTIAL이면 텍스트 검증
                md_candidate = html_path.with_suffix(".md")
                classification = "internal"
                if md_candidate.exists():
                    try:
                        md_text = md_candidate.read_text(encoding="utf-8")
                        if re.search(r"confidential|기밀", md_text, re.IGNORECASE):
                            classification = "confidential"
                    except OSError:
                        pass
                if classification == "confidential":
                    wm_ok, wm_msg = verify_pdf_watermark(pdf_path, "CONFIDENTIAL")
                    if wm_ok:
                        print(f"[VERIFY] {wm_msg}")
                    else:
                        sys.stderr.write(f"[VERIFY-FAIL] {wm_msg}\n")

            success_count += 1
        else:
            sys.stderr.write(
                f"[FAIL]  {pdf_path} 생성 실패 — "
                f"Chrome 또는 weasyprint 설치 필요\n"
            )

    if success_count == 0:
        # Chrome + weasyprint 모두 없으면 의존성 문제 → exit 2 (render-report-html.py와 일관)
        has_weasyprint = False
        try:
            import weasyprint as _wp  # noqa: F401
            has_weasyprint = True
        except ImportError:
            pass
        if not chrome and not has_weasyprint:
            sys.stderr.write(
                "[DEPENDENCY] Chrome과 weasyprint 모두 미설치 — PDF 생성 불가\n"
            )
            sys.exit(2)
        sys.exit(1)
    print(f"[DONE] PDF {success_count}개 생성")


if __name__ == "__main__":
    main()
