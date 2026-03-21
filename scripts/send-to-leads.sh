#!/usr/bin/env zsh
# send-to-leads.sh — PM 세션에서 4개 Lead CLI에 메시지를 안전하게 전송
#
# 사용법:
#   ./scripts/send-to-leads.sh "메시지"                    # 4개 모두에 동일 메시지
#   ./scripts/send-to-leads.sh --div market "메시지"       # 특정 Division만
#   ./scripts/send-to-leads.sh --phase2 <project-name>     # Phase 2 표준 지시 전송

set -euo pipefail

SESSION="research-v2"
WINDOW="${SESSION}:leads"
DIVISIONS=("market" "product" "capability" "finance")

# --- tmux 세션 확인 ---
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "오류: tmux 세션 '${SESSION}'이 없습니다."
  echo "  먼저 spawn-leads.sh를 실행하세요."
  exit 1
fi

# --- pane ID 수집 (빈 줄 필터링) ---
PANE_IDS=(${(f)"$(tmux list-panes -t "$WINDOW" -F '#{pane_id}' | grep -v '^$')"})

if [ "${#PANE_IDS[@]}" -ne 4 ]; then
  echo "오류: pane ${#PANE_IDS[@]}개 감지 (4개 필요)"
  echo "  감지된 pane: ${PANE_IDS[*]}"
  exit 1
fi

# --- 인자 파싱 ---
TARGET_DIV=""
PHASE2_MODE=""
MESSAGE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --div)
      TARGET_DIV="$2"
      shift 2
      ;;
    --phase2)
      PHASE2_MODE="$2"
      shift 2
      ;;
    *)
      MESSAGE="$1"
      shift
      ;;
  esac
done

# --- Phase 2 표준 지시 모드 ---
if [ -n "$PHASE2_MODE" ]; then
  PROJECT="$PHASE2_MODE"
  echo "Phase 2 지시 전송 (프로젝트: ${PROJECT})"
  echo ""
  for i in 1 2 3 4; do
    DIV="${DIVISIONS[$i]}"
    PANE="${PANE_IDS[$i]}"
    MSG="sync/round-1-briefing.md와 sync/phase2-${DIV}.md를 읽고 Phase 2를 진행해."
    tmux send-keys -t "$PANE" "$MSG" Enter
    echo "  ✅ ${DIV} → ${PANE}"
  done
  echo ""
  echo "4개 Division에 Phase 2 지시 전송 완료."
  exit 0
fi

# --- 메시지 필수 확인 ---
if [ -z "$MESSAGE" ]; then
  echo "사용법:"
  echo "  ./scripts/send-to-leads.sh \"메시지\"                    # 4개 모두"
  echo "  ./scripts/send-to-leads.sh --div market \"메시지\"       # 특정 Division"
  echo "  ./scripts/send-to-leads.sh --phase2 <project-name>     # Phase 2 표준 지시"
  exit 1
fi

# --- 특정 Division만 전송 ---
if [ -n "$TARGET_DIV" ]; then
  for i in 1 2 3 4; do
    if [ "${DIVISIONS[$i]}" = "$TARGET_DIV" ]; then
      PANE="${PANE_IDS[$i]}"
      tmux send-keys -t "$PANE" "$MESSAGE" Enter
      echo "  ✅ ${TARGET_DIV} → ${PANE}: ${MESSAGE}"
      exit 0
    fi
  done
  echo "오류: '${TARGET_DIV}'은 유효한 Division이 아닙니다 (market/product/capability/finance)"
  exit 1
fi

# --- 4개 모두 전송 ---
echo "4개 Lead에 메시지 전송:"
echo ""
for i in 1 2 3 4; do
  DIV="${DIVISIONS[$i]}"
  PANE="${PANE_IDS[$i]}"
  tmux send-keys -t "$PANE" "$MESSAGE" Enter
  echo "  ✅ ${DIV} → ${PANE}"
done
echo ""
echo "전송 완료."
