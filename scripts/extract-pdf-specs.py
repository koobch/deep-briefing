#!/usr/bin/env python3
"""
PDF 전수 추출 스크립트 — JSON 구조 + 고해상도 이미지
pymupdf(fitz)로 텍스트/도형/이미지 좌표 추출 + 페이지별 PNG 변환
"""
import fitz  # pymupdf
import json
import os
import sys
from pathlib import Path

# PDF 목록 (9개, 216p)
PDFS = [
    ("ai-first-win", "/Users/noname/Desktop/executive-perspectives-ai-first-companies-win-the-future-10june.pdf"),
    ("ai-first-pu", "/Users/noname/Desktop/executive-perspectives-ai-first-companies-win-the-future-power-and-utilities.pdf"),
    ("ai-first-telco", "/Users/noname/Desktop/executive-perspectives-ai-first-companies-telecommunications-industry.pdf"),
    ("genai-hr", "/Users/noname/Desktop/executive-perspectives-unlocking-impact-from-genai-and-agenticai-hr-ep1-7nov2025.pdf"),
    ("genai-marketing", "/Users/noname/Desktop/executive-perspectives-the-future-of-marketing-with-genai-13june.pdf"),
    ("ai-cost-advantage", "/Users/noname/Desktop/executive-perspectives-driving-sustainable-cost-advantage-with-ai-20may.pdf"),
    ("ai-engineering", "/Users/noname/Desktop/executive-perspectives-ai-enabled-engineering-excellence-23april.pdf"),
    ("bcg-cost", "/Users/noname/Desktop/executive-perspectives-guide-to-cost-and-growth-15jan.pdf"),
    ("mckinsey-nature", "/Users/noname/Desktop/taking-action-on-nature-webinar-slides.pdf"),
    ("consumer-spending", "/Users/noname/Desktop/under-pressure-consumers-shift-their-spending-dec-2025-n.pdf"),
    ("insurance-vcr", "/Users/noname/Desktop/2024-insurance-vcr-sep-2024-edit.pdf"),
    ("dt-telecom", "/Users/noname/Desktop/what-data-tells-us-about-digital-transformation-telecommunications.pdf"),
    ("dt-media", "/Users/noname/Desktop/what-data-tells-us-about-digital-transformation-media.pdf"),
    ("dt-tech-hw", "/Users/noname/Desktop/what-data-tells-us-about-digital-transformation-tech-hardware.pdf"),
    ("dt-software", "/Users/noname/Desktop/what-data-tells-us-about-digital-transformation-software-and-services.pdf"),
    ("decarb-oil-gas", "/Users/noname/Desktop/what-decarbonization-leaders-in-oil-and-gas-do-differently-hybrid-april-2025-edit-02.pdf"),
    ("virtual-mentoring", "/Users/noname/Desktop/how-to-build-virtual-mentoring-platform-sergio-panday.pdf"),
]

# 출력 경로
SPEC_DIR = Path("/Users/noname/deep-briefing/core/style/ref-specs")
IMG_DIR = SPEC_DIR / "images"

def extract_page(page, page_num):
    """페이지에서 텍스트/도형/이미지 좌표 추출"""
    result = {
        "page": page_num,
        "width": page.rect.width,
        "height": page.rect.height,
        "texts": [],
        "drawings": [],
        "images": [],
    }

    # 텍스트 블록 추출 (dict 모드로 상세 정보)
    text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
    for block in text_dict.get("blocks", []):
        if block["type"] == 0:  # 텍스트 블록
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span["text"].strip():
                        result["texts"].append({
                            "text": span["text"],
                            "x": round(span["bbox"][0], 1),
                            "y": round(span["bbox"][1], 1),
                            "w": round(span["bbox"][2] - span["bbox"][0], 1),
                            "h": round(span["bbox"][3] - span["bbox"][1], 1),
                            "font": span["font"],
                            "size": round(span["size"], 1),
                            "color": f"#{span['color']:06x}" if isinstance(span['color'], int) else str(span['color']),
                            "flags": span["flags"],  # bold=16, italic=2 등
                        })

    # 도형(drawings) 추출
    try:
        drawings = page.get_drawings()
        for d in drawings:
            rect = d.get("rect")
            if rect:
                result["drawings"].append({
                    "type": d.get("type", "unknown"),
                    "x": round(rect[0], 1),
                    "y": round(rect[1], 1),
                    "w": round(rect[2] - rect[0], 1),
                    "h": round(rect[3] - rect[1], 1),
                    "fill": str(d.get("fill")) if d.get("fill") else None,
                    "color": str(d.get("color")) if d.get("color") else None,
                    "stroke_opacity": d.get("stroke_opacity"),
                    "fill_opacity": d.get("fill_opacity"),
                })
    except Exception:
        pass

    # 이미지 추출
    for img_info in page.get_images(full=True):
        xref = img_info[0]
        try:
            img_rects = page.get_image_rects(xref)
            for rect in img_rects:
                result["images"].append({
                    "xref": xref,
                    "x": round(rect[0], 1),
                    "y": round(rect[1], 1),
                    "w": round(rect[2] - rect[0], 1),
                    "h": round(rect[3] - rect[1], 1),
                })
        except Exception:
            pass

    return result


def process_pdf(name, pdf_path):
    """PDF 1개 처리: JSON 추출 + 이미지 변환"""
    if not os.path.exists(pdf_path):
        print(f"  ❌ 파일 없음: {pdf_path}")
        return 0

    doc = fitz.open(pdf_path)
    total = len(doc)
    print(f"  📄 {name}: {total}p 처리 중...")

    for i in range(total):
        page = doc[i]
        page_num = i + 1

        # JSON 추출
        json_path = SPEC_DIR / f"{name}-p{page_num:02d}.json"
        if not json_path.exists():  # 이미 있으면 스킵
            spec = extract_page(page, page_num)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(spec, f, ensure_ascii=False, indent=2)

        # 이미지 변환 (2x 해상도)
        img_path = IMG_DIR / f"{name}-p{page_num:02d}.png"
        if not img_path.exists():
            pix = page.get_pixmap(dpi=144)  # 2x 해상도
            pix.save(str(img_path))

    doc.close()
    print(f"  ✅ {name}: {total}p 완료")
    return total


def main():
    # 디렉토리 생성
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # 특정 PDF만 처리 (인자로 이름 전달)
    target = sys.argv[1] if len(sys.argv) > 1 else None

    total_pages = 0
    for name, path in PDFS:
        if target and name != target:
            continue
        total_pages += process_pdf(name, path)

    print(f"\n총 {total_pages}p 처리 완료")
    print(f"JSON: {SPEC_DIR}")
    print(f"이미지: {IMG_DIR}")


if __name__ == "__main__":
    main()
