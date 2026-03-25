#!/bin/bash
# check-env.sh — 세션 시작 시 환경 상태 빠른 점검
# 출력은 Claude에 컨텍스트로 전달되어 자동 안내에 활용됨

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Deep-Briefing 환경 상태 ==="

# 1. 도메인 설정 여부
DOMAINS=$(find "$REPO_DIR/domains" -maxdepth 1 -type d ! -name "domains" ! -name "example" 2>/dev/null)
if [ -z "$DOMAINS" ]; then
  echo "도메인: 미설정 (example만 존재)"
  SETUP_NEEDED=true
else
  echo "도메인: $(echo "$DOMAINS" | xargs -I{} basename {} | tr '\n' ', ')"
  SETUP_NEEDED=false
fi

# 2. 진행 중 프로젝트
PROJECTS=$(find "$REPO_DIR" -maxdepth 2 -name "00-client-brief.md" 2>/dev/null | head -5)
if [ -z "$PROJECTS" ]; then
  echo "프로젝트: 없음"
  HAS_PROJECT=false
else
  HAS_PROJECT=true
  for p in $PROJECTS; do
    dir=$(dirname "$p")
    name=$(basename "$dir")
    if [ -f "$dir/findings/checkpoint.yaml" ]; then
      phase=$(grep "current_phase" "$dir/findings/checkpoint.yaml" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
      echo "프로젝트: $name (Phase: ${phase:-unknown})"
    else
      echo "프로젝트: $name (초기화됨)"
    fi
  done
fi

# 3. 필수 도구
PYTHON_OK=false
TMUX_OK=false
if command -v python3 &>/dev/null; then
  echo "Python: $(python3 --version 2>&1 | awk '{print $2}')"
  PYTHON_OK=true
else
  echo "Python: 미설치"
fi

if command -v tmux &>/dev/null; then
  echo "tmux: $(tmux -V 2>&1)"
  TMUX_OK=true
else
  echo "tmux: 미설치 (Agent tool 모드 B로 자동 전환)"
fi

# 4. API 키
if [ -f "$REPO_DIR/.env" ]; then
  KEY_COUNT=$(grep -v "^#" "$REPO_DIR/.env" 2>/dev/null | grep -c "=." 2>/dev/null || echo 0)
  echo "API 키: ${KEY_COUNT}개 설정됨"
else
  echo "API 키: .env 없음 (웹 검색으로 리서치 가능)"
fi

# 5. 도메인 지식 축적 현황
META="$REPO_DIR/domains/example/knowledge/_meta.yaml"
if [ -f "$META" ]; then
  MATURITY=$(grep "maturity:" "$META" 2>/dev/null | awk '{print $2}' | tr -d '"')
  echo "지식 축적: ${MATURITY:-empty}"
fi

# 6. 안내 요약
echo ""
echo "--- 권장 다음 단계 ---"
if [ "$SETUP_NEEDED" = true ] && [ "$HAS_PROJECT" = false ]; then
  echo "ACTION: first_setup"
  echo "처음 사용입니다. /setup 으로 환경 설정을 시작하세요."
elif [ "$HAS_PROJECT" = false ]; then
  echo "ACTION: new_research"
  echo "설정 완료. /research 로 새 리서치를 시작하세요."
else
  echo "ACTION: continue_or_new"
  echo "진행 중인 프로젝트가 있습니다. 이어서 진행하거나 새 리서치를 시작하세요."
fi
