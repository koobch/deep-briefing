#!/usr/bin/env zsh
# send-to-leads.sh — PM 세션에서 활성 Lead CLI에 메시지를 안전하게 전송
#
# Division을 동적 감지하여 N개 Division을 모두 지원한다 (핵심 4 + 확장 3).
#
# 사용법:
#   ./scripts/send-to-leads.sh <project-name> "메시지"                # 활성 Division 모두에 동일 메시지
#   ./scripts/send-to-leads.sh <project-name> --div market "메시지"   # 특정 Division만
#   ./scripts/send-to-leads.sh <project-name> --phase2                # Phase 2 표준 지시 전송

set -euo pipefail

SESSION="research-v2"
WINDOW="${SESSION}:leads"

# --- tmux 세션 확인 ---
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "오류: tmux 세션 '${SESSION}'이 없습니다."
  echo "  먼저 spawn-leads.sh를 실행하세요."
  exit 1
fi

# --- 인자 파싱 ---
PROJECT=""
TARGET_DIV=""
PHASE2_MODE=false
MESSAGE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --div)
      TARGET_DIV="$2"
      shift 2
      ;;
    --phase2)
      PHASE2_MODE=true
      shift
      ;;
    *)
      if [[ -z "$PROJECT" ]]; then
        PROJECT="$1"
      else
        MESSAGE="$1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$PROJECT" ]]; then
  echo "사용법:"
  echo "  ./scripts/send-to-leads.sh <project> \"메시지\"                # 모든 활성 Division"
  echo "  ./scripts/send-to-leads.sh <project> --div market \"메시지\"   # 특정 Division"
  echo "  ./scripts/send-to-leads.sh <project> --phase2                # Phase 2 표준 지시"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- pane 매핑 파일에서 Division-pane 매핑 로드 ---
PANE_MAP="/tmp/research-v2-pane-map.txt"
if [[ ! -f "$PANE_MAP" ]]; then
  echo "오류: pane 매핑 파일이 없습니다 (${PANE_MAP})"
  echo "  spawn-leads.sh가 정상 실행되었는지 확인하세요."
  exit 1
fi

# 매핑 로드: {division}={pane_id}
typeset -A DIV_PANE_MAP
DIVISIONS=()
while IFS='=' read -r div pane; do
  [[ -z "$div" ]] && continue
  DIV_PANE_MAP[$div]="$pane"
  DIVISIONS+=("$div")
done < "$PANE_MAP"

NUM_DIVISIONS=${#DIVISIONS[@]}
if [[ "$NUM_DIVISIONS" -eq 0 ]]; then
  echo "오류: 활성 Division이 없습니다."
  exit 1
fi

echo "활성 Division: ${NUM_DIVISIONS}개 — ${DIVISIONS[*]}"

# --- Phase 2 표준 지시 모드 ---
if [[ "$PHASE2_MODE" == true ]]; then
  echo ""
  echo "Phase 2 지시 전송 (프로젝트: ${PROJECT})"
  echo ""
  for div in "${DIVISIONS[@]}"; do
    PANE="${DIV_PANE_MAP[$div]}"
    # pane 생존 확인
    if ! tmux list-panes -t "$SESSION" -F '#{pane_id}' 2>/dev/null | grep -Fxq "$PANE"; then
      echo "  ⚠️ ${div} pane (${PANE}) 사망 — 스킵"
      continue
    fi
    MSG="${PROJECT}/sync/round-1-briefing.md와 ${PROJECT}/sync/phase2-${div}.md를 읽고 Phase 2를 진행해."
    tmux send-keys -t "$PANE" "$MSG" Enter
    echo "  ✅ ${div} → ${PANE}"
  done
  echo ""
  echo "${NUM_DIVISIONS}개 Division에 Phase 2 지시 전송 완료."
  exit 0
fi

# --- 메시지 필수 확인 ---
if [[ -z "$MESSAGE" ]]; then
  echo ""
  echo "오류: 메시지가 필요합니다."
  echo "사용법:"
  echo "  ./scripts/send-to-leads.sh ${PROJECT} \"메시지\""
  echo "  ./scripts/send-to-leads.sh ${PROJECT} --div market \"메시지\""
  echo "  ./scripts/send-to-leads.sh ${PROJECT} --phase2"
  exit 1
fi

# --- 특정 Division만 전송 ---
if [[ -n "$TARGET_DIV" ]]; then
  if [[ -n "${DIV_PANE_MAP[$TARGET_DIV]:-}" ]]; then
    PANE="${DIV_PANE_MAP[$TARGET_DIV]}"
    if ! tmux list-panes -t "$SESSION" -F '#{pane_id}' 2>/dev/null | grep -Fxq "$PANE"; then
      echo "  ⚠️ ${TARGET_DIV} pane (${PANE}) 사망"
      exit 1
    fi
    tmux send-keys -t "$PANE" "$MESSAGE" Enter
    echo "  ✅ ${TARGET_DIV} → ${PANE}: ${MESSAGE}"
  else
    echo "오류: '${TARGET_DIV}'은 활성 Division이 아닙니다."
    echo "활성 Division: ${DIVISIONS[*]}"
    exit 1
  fi
  exit 0
fi

# --- 모든 활성 Division에 전송 ---
echo ""
echo "${NUM_DIVISIONS}개 Lead에 메시지 전송:"
echo ""
for div in "${DIVISIONS[@]}"; do
  PANE="${DIV_PANE_MAP[$div]}"
  if ! tmux list-panes -t "$SESSION" -F '#{pane_id}' 2>/dev/null | grep -Fxq "$PANE"; then
    echo "  ⚠️ ${div} pane (${PANE}) 사망 — 스킵"
    continue
  fi
  tmux send-keys -t "$PANE" "$MESSAGE" Enter
  echo "  ✅ ${div} → ${PANE}"
done
echo ""
echo "전송 완료."
