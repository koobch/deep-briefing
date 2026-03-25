#!/bin/bash
# check-env.sh — 세션 시작 시 환경 상태 빠른 점검
# SessionStart 훅에서 호출됨. JSON stdout으로 systemMessage를 반환하여 Claude 컨텍스트에 주입.

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Lead CLI 감지 — 환경 체크 불필요 (PM이 이미 실행)
if [ -n "${CLAUDE_AGENT_NAME:-}" ]; then
  echo '{"continue": true}'
  exit 0
fi

# === 상태 수집 ===

# 1. 도메인 설정 여부
DOMAINS=$(find "$REPO_DIR/domains" -maxdepth 1 -type d ! -name "domains" ! -name "example" 2>/dev/null)
if [ -z "$DOMAINS" ]; then
  DOMAIN_STATUS="example (범용)"
  SETUP_NEEDED=false
else
  DOMAIN_STATUS="$(echo "$DOMAINS" | xargs -I{} basename {} | tr '\n' ', ')"
  SETUP_NEEDED=false
fi

# 2. 진행 중 프로젝트
PROJECT_LIST=""
HAS_PROJECT=false
PROJECTS=$(find "$REPO_DIR" -maxdepth 2 -name "00-client-brief.md" 2>/dev/null | head -5)
if [ -n "$PROJECTS" ]; then
  HAS_PROJECT=true
  while IFS= read -r p; do
    dir=$(dirname "$p")
    name=$(basename "$dir")
    if [ -f "$dir/findings/checkpoint.yaml" ]; then
      phase=$(grep "current_phase" "$dir/findings/checkpoint.yaml" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
      PROJECT_LIST="${PROJECT_LIST}${name}(Phase:${phase:-?}), "
    else
      PROJECT_LIST="${PROJECT_LIST}${name}(초기화), "
    fi
  done <<< "$PROJECTS"
fi

# 3. 필수 도구
PYTHON_VER="미설치"
TMUX_VER="미설치"
command -v python3 &>/dev/null && PYTHON_VER="$(python3 --version 2>&1 | awk '{print $2}')"
command -v tmux &>/dev/null && TMUX_VER="$(tmux -V 2>&1)"

# 4. API 키
API_STATUS=".env 없음"
if [ -f "$REPO_DIR/.env" ]; then
  KEY_COUNT=$(grep -v "^#" "$REPO_DIR/.env" 2>/dev/null | grep "=." 2>/dev/null | grep -v "your_.*_here" | wc -l | tr -d ' ')
  API_STATUS="${KEY_COUNT}개 설정됨"
fi

# 5. 도메인 지식 성숙도
MATURITY="empty"
META="$REPO_DIR/domains/example/knowledge/_meta.yaml"
[ -f "$META" ] && MATURITY=$(grep "maturity:" "$META" 2>/dev/null | awk '{print $2}' | tr -d '"')

# === SETUP_NEEDED 재판정: .env 없음 또는 Python 미설치 시에만 true ===
if [ ! -f "$REPO_DIR/.env" ] || [ "$PYTHON_VER" = "미설치" ]; then
  SETUP_NEEDED=true
fi

# === ACTION 결정 ===
if [ "$SETUP_NEEDED" = true ] && [ "$HAS_PROJECT" = false ]; then
  ACTION="first_setup"
  GUIDE="처음 사용입니다. 환경 설정이 필요합니다. /setup 실행을 제안하세요."
elif [ "$HAS_PROJECT" = false ]; then
  ACTION="new_research"
  GUIDE="설정 완료 상태입니다. 어떤 주제를 리서치할지 물어보세요. /research 실행을 제안하세요."
else
  ACTION="continue_or_new"
  GUIDE="진행 중 프로젝트: ${PROJECT_LIST}. 이어서 진행할지, 새 리서치를 시작할지 선택지를 제시하세요."
fi

# === JSON systemMessage 출력 ===
cat <<EOF
{
  "continue": true,
  "systemMessage": "Deep-Briefing 환경 상태 — 도메인: ${DOMAIN_STATUS} | 프로젝트: ${PROJECT_LIST:-없음} | Python: ${PYTHON_VER} | tmux: ${TMUX_VER} | API: ${API_STATUS} | 지식: ${MATURITY} | ACTION: ${ACTION} — ${GUIDE}"
}
EOF

exit 0
