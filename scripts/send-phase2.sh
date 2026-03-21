#!/bin/bash
# send-phase2.sh — Phase 2 지시를 새 tmux 세션으로 실행 (기존 pane 재사용 안 함)
#
# 사용법:
#   ./scripts/send-phase2.sh <project-name> [--auto]
#
# 동작:
#   1. 기존 research-v2 tmux 세션을 정리 (Phase 1 완료 후 idle 상태)
#   2. 새 tmux 세션 생성 + Division별 깨끗한 claude 프로세스 스폰
#   3. Division은 division-briefs/*.md에서 자동 감지 (spawn-leads.sh와 동일)
#
# 왜 기존 pane을 재사용하지 않는가:
#   - Phase 1 완료 후 Lead CLI가 종료되어 쉘 프롬프트 상태
#   - send-keys로 명령 주입 시 쉘 히스토리/자동완성과 충돌 가능
#   - 새 프로세스가 깨끗하고 안전함
#
# 예시:
#   ./scripts/send-phase2.sh my-research --auto

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PROJECT="${1:?사용법: ./scripts/send-phase2.sh <project-name> [--auto]}"
AUTO_PERMISSIONS=""

shift || true
for arg in "$@"; do
  case "$arg" in
    --auto) AUTO_PERMISSIONS="--dangerously-skip-permissions" ;;
  esac
done

SESSION="research-v2-p2"

# --- Division 자동 감지 ---
BRIEFS_DIR="${REPO_DIR}/${PROJECT}/division-briefs"
DIVISIONS=()
AGENTS=()
for brief in "${BRIEFS_DIR}"/*.md; do
  [ -f "$brief" ] || continue
  div=$(basename "$brief" .md)
  DIVISIONS+=("$div")
  AGENTS+=("${div}-lead")
done

NUM_DIVISIONS=${#DIVISIONS[@]}
echo "감지된 Division: ${NUM_DIVISIONS}개 — ${DIVISIONS[*]}"

# --- Phase 2 지시서 존재 확인 ---
MISSING=0
for div in "${DIVISIONS[@]}"; do
  if [ ! -f "${REPO_DIR}/${PROJECT}/sync/phase2-${div}.md" ]; then
    echo "  ❌ sync/phase2-${div}.md 없음"
    MISSING=1
  fi
done

if [ "$MISSING" -eq 1 ]; then
  echo ""
  echo "Phase 2 지시서가 완성되지 않았습니다."
  echo "PM CLI에서 Sync Round 1을 먼저 완료하세요."
  exit 1
fi

# --- round-1-briefing 확인 ---
if [ ! -f "${REPO_DIR}/${PROJECT}/sync/round-1-briefing.md" ]; then
  echo "  ⚠ sync/round-1-briefing.md 없음"
fi

# --- 기존 세션 정리 ---
tmux kill-session -t "research-v2" 2>/dev/null && echo "기존 research-v2 세션 정리" || true
tmux kill-session -t "$SESSION" 2>/dev/null || true

echo ""
echo "=== Phase 2 새 tmux 세션 생성 ==="

# --- 새 세션 + N-pane: spawn-leads.sh와 동일한 방식 ---
# 첫 번째 Division
FIRST_DIV="${DIVISIONS[0]}"
FIRST_AGENT="${AGENTS[0]}"
FIRST_CMD="claude ${AUTO_PERMISSIONS} --agent ${FIRST_AGENT} '${PROJECT}/sync/round-1-briefing.md와 ${PROJECT}/sync/phase2-${FIRST_DIV}.md를 읽고 Phase 2 심화 리서치를 수행하라. 결과를 ${PROJECT}/findings/${FIRST_DIV}/에 업데이트하고 .done 파일의 phase를 2로 갱신하라.'"

tmux new-session -d -s "$SESSION" -n "phase2" -c "$REPO_DIR"
sleep 0.3
tmux send-keys -t "${SESSION}:phase2" "$FIRST_CMD" Enter
echo "  ✅ ${FIRST_AGENT} → pane 0"

# 나머지 Division
for ((i=1; i<NUM_DIVISIONS; i++)); do
  DIV="${DIVISIONS[$i]}"
  AGENT="${AGENTS[$i]}"
  CMD="claude ${AUTO_PERMISSIONS} --agent ${AGENT} '${PROJECT}/sync/round-1-briefing.md와 ${PROJECT}/sync/phase2-${DIV}.md를 읽고 Phase 2 심화 리서치를 수행하라. 결과를 ${PROJECT}/findings/${DIV}/에 업데이트하고 .done 파일의 phase를 2로 갱신하라.'"

  if (( i % 2 == 1 )); then
    tmux split-window -v -t "${SESSION}:phase2" -c "$REPO_DIR"
  else
    tmux split-window -h -t "${SESSION}:phase2" -c "$REPO_DIR"
  fi
  sleep 0.3
  tmux send-keys -t "${SESSION}:phase2" "$CMD" Enter
  echo "  ✅ ${AGENT} → pane ${i}"
done

tmux select-layout -t "${SESSION}:phase2" tiled

echo ""
echo "${NUM_DIVISIONS}개 Division Phase 2 실행 완료!"
echo ""
echo "접속: tmux attach -t ${SESSION}"
echo "종료: tmux kill-session -t ${SESSION}"
echo ""

# --- 완료 감지 ---
DIVISION_LIST=$(IFS=,; echo "${DIVISIONS[*]}")

MONITOR_SCRIPT=$(cat << 'MONITOR_EOF'
#!/bin/bash
PROJECT_DIR="$1"
IFS=',' read -ra DIVS <<< "$2"
TOTAL=${#DIVS[@]}

while true; do
  COMPLETED=0
  for div in "${DIVS[@]}"; do
    if grep -q "phase: 2" "${PROJECT_DIR}/findings/${div}/.done" 2>/dev/null; then
      ((COMPLETED++))
    fi
  done

  if [ "$COMPLETED" -ge "$TOTAL" ]; then
    echo ""
    echo "============================================"
    echo "  ✅ ${TOTAL}개 Division Phase 2 완료!"
    echo "  PM CLI에서 Sync Round 2를 시작하세요."
    echo "============================================"
    if command -v osascript &>/dev/null; then
      osascript -e "display notification \"${TOTAL}개 Division Phase 2 완료!\" with title \"Deep-Briefing\" sound name \"Glass\""
    fi
    break
  fi
  sleep 10
done
MONITOR_EOF
)

echo "$MONITOR_SCRIPT" > "/tmp/research-v2-p2-monitor.sh"
chmod +x "/tmp/research-v2-p2-monitor.sh"
bash "/tmp/research-v2-p2-monitor.sh" "${REPO_DIR}/${PROJECT}" "$DIVISION_LIST" &
echo "완료 감지 모니터 시작"
