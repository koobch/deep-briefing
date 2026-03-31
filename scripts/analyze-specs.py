#!/usr/bin/env python3
"""
레퍼런스 JSON 전수 통계 분석 — 디자인 가이드 규칙 추출용
폰트/여백/색상/밀도/레이아웃 유형 분류
"""
import json
import os
from pathlib import Path
from collections import Counter, defaultdict
import statistics

SPEC_DIR = Path("/Users/noname/deep-briefing/core/style/ref-specs")
OUT_PATH = SPEC_DIR / "analysis-summary.json"

def load_all_specs():
    """모든 JSON 스펙 파일 로드"""
    specs = []
    for f in sorted(SPEC_DIR.glob("*.json")):
        if f.name.startswith("analysis") or f.name.startswith("proto"):
            continue
        with open(f, encoding="utf-8") as fh:
            try:
                data = json.load(fh)
                data["_filename"] = f.name
                specs.append(data)
            except json.JSONDecodeError:
                pass
    return specs


def analyze_fonts(specs):
    """폰트 크기 분포 분석"""
    sizes = []
    fonts = Counter()
    weights = Counter()  # bold(flags & 16) vs regular

    for spec in specs:
        for t in spec.get("texts", []):
            # 기존 형식(size_pt) + 새 형식(size) 모두 지원
            size = t.get("size") or t.get("size_pt")
            if not size:
                continue
            sizes.append(size)
            fonts[t.get("font", "unknown")] += 1
            is_bold = bool(t.get("flags", 0) & 16) or t.get("bold", False)
            weights["bold" if is_bold else "regular"] += 1

    if not sizes:
        return {}

    # 크기별 그룹화 (반올림)
    size_groups = Counter(round(s, 0) for s in sizes)

    return {
        "total_text_spans": len(sizes),
        "size_distribution": dict(size_groups.most_common(20)),
        "size_stats": {
            "min": round(min(sizes), 1),
            "max": round(max(sizes), 1),
            "median": round(statistics.median(sizes), 1),
            "mean": round(statistics.mean(sizes), 1),
        },
        "top_fonts": dict(fonts.most_common(10)),
        "weight_ratio": dict(weights),
    }


def analyze_colors(specs):
    """색상 palette 분석"""
    text_colors = Counter()
    fill_colors = Counter()

    for spec in specs:
        for t in spec.get("texts", []):
            color = str(t.get("color", ""))
            if color and color != "#000000":
                text_colors[color] += 1
            elif color == "#000000":
                text_colors["#000000"] += 1

        for d in spec.get("drawings", []):
            fill = d.get("fill")
            if fill and fill != "None":
                fill_colors[str(fill)] += 1

    return {
        "text_colors_top20": dict(text_colors.most_common(20)),
        "fill_colors_top20": dict(fill_colors.most_common(20)),
    }


def analyze_margins(specs):
    """여백 분석 — 텍스트 블록의 최소 x/y 좌표에서 여백 추정"""
    left_margins = []
    right_margins = []
    top_margins = []

    for spec in specs:
        texts = spec.get("texts", [])
        if not texts:
            continue

        page_w = spec.get("width", 960)
        xs = [t["x"] for t in texts if t["x"] > 5]
        ys = [t["y"] for t in texts if t["y"] > 5]
        right_xs = [t["x"] + t["w"] for t in texts]

        if xs:
            left_margins.append(min(xs))
        if right_xs and page_w:
            right_margins.append(page_w - max(right_xs))
        if ys:
            top_margins.append(min(ys))

    result = {}
    if left_margins:
        result["left_margin"] = {
            "median": round(statistics.median(left_margins), 1),
            "min": round(min(left_margins), 1),
            "max": round(max(left_margins), 1),
        }
    if right_margins:
        result["right_margin"] = {
            "median": round(statistics.median(right_margins), 1),
            "min": round(min(right_margins), 1),
            "max": round(max(right_margins), 1),
        }
    if top_margins:
        result["top_margin"] = {
            "median": round(statistics.median(top_margins), 1),
            "min": round(min(top_margins), 1),
            "max": round(max(top_margins), 1),
        }
    return result


def analyze_density(specs):
    """콘텐츠 밀도 분석 — 페이지당 텍스트/도형/이미지 수"""
    text_counts = []
    drawing_counts = []
    image_counts = []
    char_counts = []

    for spec in specs:
        texts = spec.get("texts", [])
        text_counts.append(len(texts))
        drawing_counts.append(len(spec.get("drawings", [])))
        image_counts.append(len(spec.get("images", [])))
        char_counts.append(sum(len(t.get("text", "")) for t in texts))

    return {
        "texts_per_page": {
            "median": round(statistics.median(text_counts)),
            "mean": round(statistics.mean(text_counts), 1),
            "min": min(text_counts),
            "max": max(text_counts),
        },
        "drawings_per_page": {
            "median": round(statistics.median(drawing_counts)),
            "mean": round(statistics.mean(drawing_counts), 1),
        },
        "images_per_page": {
            "median": round(statistics.median(image_counts)),
            "mean": round(statistics.mean(image_counts), 1),
        },
        "chars_per_page": {
            "median": round(statistics.median(char_counts)),
            "mean": round(statistics.mean(char_counts), 1),
            "min": min(char_counts),
            "max": max(char_counts),
        },
        "total_pages": len(specs),
    }


def classify_layout(spec):
    """레이아웃 유형 추정 — 텍스트/도형 분포 기반"""
    texts = spec.get("texts", [])
    drawings = spec.get("drawings", [])
    page_w = spec.get("width", 960)
    page_h = spec.get("height", 540)

    if not texts:
        return "empty"

    # 텍스트 수가 매우 적으면 표지/뒷표지
    if len(texts) < 5:
        return "cover"

    # 텍스트의 x 좌표 분포로 컬럼 구조 파악
    xs = [t["x"] for t in texts]
    mid_x = page_w / 2

    left_texts = [x for x in xs if x < mid_x * 0.6]
    right_texts = [x for x in xs if x > mid_x * 1.2]
    center_texts = [x for x in xs if mid_x * 0.6 <= x <= mid_x * 1.2]

    # 큰 폰트 텍스트 (제목급)
    def get_size(t):
        return t.get("size") or t.get("size_pt") or 0
    large_texts = [t for t in texts if get_size(t) > 20]

    # 숫자가 큰 텍스트 (Big Number)
    big_nums = [t for t in texts if get_size(t) > 30 and any(c.isdigit() for c in t.get("text", ""))]

    # 도형 수 (프로세스/프레임워크 판별)
    has_many_shapes = len(drawings) > 20

    # 분류 로직
    total = len(texts)

    if len(big_nums) >= 2 and total < 30:
        return "big-number"

    if left_texts and right_texts and len(right_texts) > total * 0.2:
        if has_many_shapes:
            return "process"
        return "two-column"

    if has_many_shapes and total < 40:
        return "framework"

    if total > 50:
        return "data-dense"

    return "standard"


def analyze_layouts(specs):
    """전체 페이지 레이아웃 유형 분류"""
    layout_map = defaultdict(list)

    for spec in specs:
        layout_type = classify_layout(spec)
        layout_map[layout_type].append(spec["_filename"])

    return {
        layout: {
            "count": len(pages),
            "pages": pages[:5],  # 대표 5개만
        }
        for layout, pages in sorted(layout_map.items(), key=lambda x: -len(x[1]))
    }


def main():
    print("📊 레퍼런스 JSON 통계 분석 시작...")
    specs = load_all_specs()
    print(f"  로드된 스펙: {len(specs)}개")

    if not specs:
        print("  ❌ 스펙 파일 없음")
        return

    result = {
        "total_pages": len(specs),
        "fonts": analyze_fonts(specs),
        "colors": analyze_colors(specs),
        "margins": analyze_margins(specs),
        "density": analyze_density(specs),
        "layouts": analyze_layouts(specs),
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 요약 출력
    print(f"\n=== 분석 결과 요약 ===")
    print(f"총 페이지: {result['total_pages']}")
    print(f"\n폰트 크기 분포 (상위 10):")
    for size, count in list(result['fonts']['size_distribution'].items())[:10]:
        print(f"  {size}pt: {count}회")
    print(f"\n폰트 통계: min={result['fonts']['size_stats']['min']}, "
          f"max={result['fonts']['size_stats']['max']}, "
          f"median={result['fonts']['size_stats']['median']}")
    print(f"\n콘텐츠 밀도:")
    d = result['density']
    print(f"  텍스트/페이지: median={d['texts_per_page']['median']}, "
          f"mean={d['texts_per_page']['mean']}")
    print(f"  글자/페이지: median={d['chars_per_page']['median']}, "
          f"mean={d['chars_per_page']['mean']}")
    print(f"\n레이아웃 유형:")
    for lt, info in result['layouts'].items():
        print(f"  {lt}: {info['count']}개")

    print(f"\n저장: {OUT_PATH}")


if __name__ == "__main__":
    main()
