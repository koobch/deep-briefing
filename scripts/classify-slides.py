#!/usr/bin/env python3
"""
슬라이드 유형 자동 분류 — JSON 스펙 기반
텍스트/도형/이미지 패턴으로 216페이지를 유형별로 분류
"""
import json
from pathlib import Path
from collections import Counter

SPEC_DIR = Path("/Users/noname/deep-briefing/core/style/ref-specs")
OUT_PATH = SPEC_DIR / "slide-catalog.json"


def get_size(t):
    return t.get("size") or t.get("size_pt") or 0


def classify(spec):
    """JSON 스펙에서 슬라이드 유형 추정"""
    texts = spec.get("texts", [])
    drawings = spec.get("drawings", [])
    images = spec.get("images", [])
    page_w = spec.get("width", 960)
    page_h = spec.get("height", 540)

    if not texts:
        return "back-cover"

    # 텍스트 특성
    total_texts = len(texts)
    total_chars = sum(len(t.get("text", "")) for t in texts)
    max_size = max((get_size(t) for t in texts), default=0)
    large_texts = [t for t in texts if get_size(t) > 20]

    # 전체 텍스트 합치기 (소문자)
    all_text = " ".join(t.get("text", "") for t in texts).lower()

    # x 좌표 분포 (컬럼 분석)
    xs = [t.get("x", 0) for t in texts if t.get("x", 0) > 5]
    mid_x = page_w / 2

    # 큰 숫자 (Big Number 판별)
    big_nums = [t for t in texts if get_size(t) > 28 and any(c.isdigit() for c in t.get("text", ""))]
    pct_texts = [t for t in texts if "%" in t.get("text", "") and get_size(t) > 20]

    # 순위 기호
    has_ranking = any(t.get("text", "").strip().startswith("#") and any(c.isdigit() for c in t.get("text", "")) for t in texts)

    # 체크마크/아젠다
    has_check = any("✓" in t.get("text", "") or "✔" in t.get("text", "") for t in texts)

    # 도형 수
    n_drawings = len(drawings)
    n_images = len(images)

    # ─── 분류 로직 ───

    # 1. 커버 (텍스트 매우 적음 + 큰 폰트)
    if total_texts < 8 and max_size > 24:
        return "cover"

    # 2. 뒷표지 (텍스트 매우 적음)
    if total_texts < 5:
        return "back-cover"

    # 3. 아젠다 (체크마크)
    if has_check or "agenda" in all_text:
        return "agenda"

    # 4. 키워드 기반
    if "introduction" in all_text or "in this" in all_text and "we articulate" in all_text:
        return "introduction"

    if "case" in all_text and ("example" in all_text or "illustrative" in all_text):
        return "case-study"

    if "challenge" in all_text and total_texts < 35:
        return "table-list"

    # 5. Big Number (큰 숫자 2개+ 또는 %가 큰 폰트)
    if len(big_nums) >= 3 and total_texts < 40:
        return "big-number"

    # 6. 순위
    if has_ranking:
        return "ranked"

    # 7. 텍스트 x 분포로 레이아웃 판별
    if xs:
        left_count = sum(1 for x in xs if x < mid_x * 0.5)
        right_count = sum(1 for x in xs if x > mid_x * 1.1)
        center_count = sum(1 for x in xs if mid_x * 0.5 <= x <= mid_x * 1.1)

        # Before/After (3컬럼)
        thirds = [0, 0, 0]
        for x in xs:
            if x < page_w * 0.33:
                thirds[0] += 1
            elif x < page_w * 0.66:
                thirds[1] += 1
            else:
                thirds[2] += 1
        if all(t >= total_texts * 0.15 for t in thirds) and total_texts > 20:
            return "before-after"

        # 프레임워크/다이어그램 (도형 많음 + 텍스트 분산)
        if n_drawings > 25 and total_texts < 50:
            return "framework"

        # 2컬럼 (좌 차트 + 우 패널)
        if right_count > total_texts * 0.2 and left_count > total_texts * 0.3:
            if len(pct_texts) >= 2 or n_drawings > 15:
                return "insight-chart"
            if n_drawings > 20:
                return "process"
            return "two-column"

    # 8. 데이터 밀도
    if total_texts > 60:
        return "data-dense"

    # 9. 표/목록 (중간 텍스트, 정렬된 구조)
    if 20 < total_texts < 50 and n_drawings > 10:
        if len(pct_texts) >= 2:
            return "data-visualization"
        return "process"

    # 10. 텍스트 중심
    if total_chars > 800 and n_drawings < 10:
        return "text-heavy"

    return "standard"


def main():
    print("📊 슬라이드 유형 분류 시작...")

    catalog = {}
    type_counts = Counter()

    for f in sorted(SPEC_DIR.glob("*.json")):
        if f.name.startswith("analysis") or f.name.startswith("proto") or f.name.startswith("slide"):
            continue
        with open(f, encoding="utf-8") as fh:
            try:
                spec = json.load(fh)
                slide_type = classify(spec)
                key = f.stem  # 파일명에서 확장자 제거
                catalog[key] = slide_type
                type_counts[slide_type] += 1
            except json.JSONDecodeError:
                pass

    # 결과 저장
    result = {
        "total": len(catalog),
        "type_counts": dict(type_counts.most_common()),
        "catalog": catalog,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 요약
    print(f"\n=== 유형 분류 결과 ===")
    print(f"총 페이지: {len(catalog)}")
    print(f"유형 수: {len(type_counts)}")
    print(f"\n유형별 분포:")
    for t, c in type_counts.most_common():
        print(f"  {t}: {c}개 ({c/len(catalog)*100:.1f}%)")

    # 미분류 확인
    unknown = sum(1 for v in catalog.values() if v == "unknown")
    print(f"\n미분류: {unknown}건")
    print(f"저장: {OUT_PATH}")


if __name__ == "__main__":
    main()
