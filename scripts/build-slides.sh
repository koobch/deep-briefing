#!/bin/bash
# build-slides.sh — Markdown DSL → 단일 HTML 슬라이드 빌드
# 외부 의존성 0 (cat + sed만 사용)
#
# 사용법:
#   ./scripts/build-slides.sh <slides.md> [output.html]
#
# 예시:
#   ./scripts/build-slides.sh my-project/reports/slides/slides.md
#   → my-project/reports/slides/slide-deck.html 생성
#
#   ./scripts/build-slides.sh slides.md output.html
#   → output.html 생성

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
V2_DIR="${REPO_DIR}/core/style/v2"

INPUT="${1:?사용법: ./scripts/build-slides.sh <slides.md> [output.html]}"
OUTPUT="${2:-$(dirname "$INPUT")/slide-deck.html}"

# 파일 존재 확인
if [ ! -f "$INPUT" ]; then
  echo "❌ 입력 파일이 없습니다: $INPUT"
  exit 1
fi

for f in slide-core.css slide-parser.js slide-renderer.js slide-fit.js; do
  if [ ! -f "${V2_DIR}/${f}" ]; then
    echo "❌ ${f}가 없습니다: ${V2_DIR}/${f}"
    exit 1
  fi
done

# Markdown 소스 읽기
MD_SOURCE=$(cat "$INPUT")

# CSS 읽기
CSS_SOURCE=$(cat "${V2_DIR}/slide-core.css")

# JS 읽기
JS_PARSER=$(cat "${V2_DIR}/slide-parser.js")
JS_RENDERER=$(cat "${V2_DIR}/slide-renderer.js")
JS_FIT=$(cat "${V2_DIR}/slide-fit.js")

# 단일 HTML 생성
cat > "$OUTPUT" << HTMLEOF
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920">
  <title>Deep-Briefing Slides</title>
  <style>
${CSS_SOURCE}
  </style>
</head>
<body>

<script type="text/plain" id="deck-source">
${MD_SOURCE}
</script>

<script>
// ─── slide-parser.js ───
${JS_PARSER}

// ─── slide-renderer.js ───
${JS_RENDERER}

// ─── slide-fit.js ───
${JS_FIT}

// ─── 실행 ───
(function() {
  const source = document.getElementById('deck-source').textContent;
  const ast = SlideParser.parse(source);
  SlideRenderer.render(ast, document.body);
  const result = SlideFit.check();
  console.log('[build] 슬라이드 빌드 완료:', result);
})();
</script>

</body>
</html>
HTMLEOF

echo "✅ 슬라이드 빌드 완료: ${OUTPUT}"
echo "  입력: ${INPUT}"
echo "  슬라이드 수: $(grep -c '^---$' "$INPUT" || echo "N/A")"
echo "  브라우저에서 열기: open \"${OUTPUT}\""
