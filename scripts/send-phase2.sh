#!/bin/bash
# send-phase2.sh — Phase 2 지시를 새 tmux 세션으로 실행 (기존 pane 재사용 안 함)
#
# 사용법:
#   ./scripts/send-phase2.sh <project-name> [--auto]
#
# 동작:
#   1. 기존 research-${PROJECT} tmux 세션을 정리 (Phase 1 완료 후 idle 상태)
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

SESSION="research-${PROJECT}-p2"

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

if [ "$NUM_DIVISIONS" -eq 0 ]; then
  echo "❌ division-briefs/*.md 파일이 없습니다."
  echo "  init-project.sh를 먼저 실행하세요."
  exit 1
fi

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

# --- Phase 2 완료/미완료 Division 분류 ---
INCOMPLETE_DIVS=()
INCOMPLETE_AGENTS=()
COMPLETED_DIVS=()

for ((i=0; i<NUM_DIVISIONS; i++)); do
  div="${DIVISIONS[$i]}"
  agent="${AGENTS[$i]}"
  DONE_FILE="${REPO_DIR}/${PROJECT}/findings/${div}/.done"
  if grep -q "status: success" "$DONE_FILE" 2>/dev/null && grep -q "phase: 2" "$DONE_FILE" 2>/dev/null; then
    COMPLETED_DIVS+=("$div")
    echo "  ✅ ${div} — Phase 2 이미 완료 (건너뜀)"
  else
    INCOMPLETE_DIVS+=("$div")
    INCOMPLETE_AGENTS+=("${agent}")
  fi
done

NUM_INCOMPLETE=${#INCOMPLETE_DIVS[@]}

if [ "$NUM_INCOMPLETE" -eq 0 ]; then
  echo ""
  echo "✅ 모든 Division이 Phase 2를 완료했습니다."
  echo "PM CLI에서 Sync Round 2를 시작하세요."
  exit 0
fi

echo ""
echo "Phase 2 미완료: ${NUM_INCOMPLETE}개 — ${INCOMPLETE_DIVS[*]}"
if [ ${#COMPLETED_DIVS[@]} -gt 0 ]; then
  echo "Phase 2 완료 (건너뜀): ${#COMPLETED_DIVS[@]}개 — ${COMPLETED_DIVS[*]}"
fi

# --- .done 파일 Phase 전환: 미완료 Division만 phase: 2-in-progress로 갱신 ---
for div in "${INCOMPLETE_DIVS[@]}"; do
  DONE_FILE="${REPO_DIR}/${PROJECT}/findings/${div}/.done"
  FINDINGS_DIR="${REPO_DIR}/${PROJECT}/findings/${div}"
  mkdir -p "$FINDINGS_DIR"
  # .done이 존재하면 phase를 2-in-progress로 갱신, 없으면 신규 생성
  cat > "$DONE_FILE" << DONE_EOF
division: ${div}
phase: 2
status: in_progress
started_at: $(date -u +%Y-%m-%dT%H:%M:%S)
DONE_EOF
  echo "  📝 ${div}/.done → phase: 2, status: in_progress"
done

# --- .progress 파일 Phase 2 관리 (미완료 Division만) ---
for div in "${INCOMPLETE_DIVS[@]}"; do
  PROGRESS_FILE="${REPO_DIR}/${PROJECT}/findings/${div}/.progress"
  if [ -f "$PROGRESS_FILE" ] && grep -q "phase: 2" "$PROGRESS_FILE" 2>/dev/null; then
    # Phase 2 .progress가 이미 존재 → 부분 완료 상태 보존 (재개용)
    echo "  ♻️  ${div}/.progress → Phase 2 기존 진행분 보존 (부분 재개)"
  else
    # Phase 1 .progress이거나 미존재 → Phase 2용 초기화
    if [ -f "$PROGRESS_FILE" ]; then
      cp "$PROGRESS_FILE" "${PROGRESS_FILE}.phase1-backup"
    fi
    cat > "$PROGRESS_FILE" << PROGRESS_EOF
division: ${div}
phase: 2
updated_at: $(date -u +%Y-%m-%dT%H:%M:%S)
leaves_completed: []
leaves_in_progress: []
synthesis_status: pending
PROGRESS_EOF
    echo "  📝 ${div}/.progress → Phase 2 초기화"
  fi
done

# --- 기존 세션 정리 (Phase 1 세션만. Phase 2 세션이 이미 있으면 정리 후 재생성) ---
tmux kill-session -t "research-${PROJECT}" 2>/dev/null && echo "기존 Phase 1 세션 정리" || true
tmux kill-session -t "$SESSION" 2>/dev/null && echo "기존 Phase 2 세션 정리 (미완료 Division 재스폰)" || true

echo ""
echo "=== Phase 2 tmux 세션 생성 (미완료 ${NUM_INCOMPLETE}개 Division) ==="

# --- 새 세션 + N-pane: 미완료 Division만 스폰 ---
FIRST_DIV="${INCOMPLETE_DIVS[0]}"
FIRST_AGENT="${INCOMPLETE_AGENTS[0]}"
FIRST_CMD="claude ${AUTO_PERMISSIONS} --agent ${FIRST_AGENT} '${PROJECT}/sync/round-1-briefing.md와 ${PROJECT}/sync/phase2-${FIRST_DIV}.md를 읽고 Phase 2 심화 리서치를 수행하라. ${PROJECT}/findings/${FIRST_DIV}/.progress를 확인하여 완료된 Leaf는 건너뛰어라. 결과를 ${PROJECT}/findings/${FIRST_DIV}/에 업데이트하고 .done 파일에 phase: 2와 status: success를 기록하라.'"

tmux new-session -d -s "$SESSION" -n "phase2" -c "$REPO_DIR"
sleep 0.3
tmux send-keys -t "${SESSION}:phase2" "$FIRST_CMD" Enter
echo "  ✅ ${FIRST_AGENT} → pane 0"

# 나머지 미완료 Division
for ((i=1; i<NUM_INCOMPLETE; i++)); do
  DIV="${INCOMPLETE_DIVS[$i]}"
  AGENT="${INCOMPLETE_AGENTS[$i]}"
  CMD="claude ${AUTO_PERMISSIONS} --agent ${AGENT} '${PROJECT}/sync/round-1-briefing.md와 ${PROJECT}/sync/phase2-${DIV}.md를 읽고 Phase 2 심화 리서치를 수행하라. ${PROJECT}/findings/${DIV}/.progress를 확인하여 완료된 Leaf는 건너뛰어라. 결과를 ${PROJECT}/findings/${DIV}/에 업데이트하고 .done 파일에 phase: 2와 status: success를 기록하라.'"

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
echo "${NUM_INCOMPLETE}개 Division Phase 2 실행! (${#COMPLETED_DIVS[@]}개는 이미 완료)"
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
    if grep -q "phase: 2" "${PROJECT_DIR}/findings/${div}/.done" 2>/dev/null && grep -q "status: success" "${PROJECT_DIR}/findings/${div}/.done" 2>/dev/null; then
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

echo "$MONITOR_SCRIPT" > "/tmp/research-${PROJECT}-p2-monitor.sh"
chmod +x "/tmp/research-${PROJECT}-p2-monitor.sh"
bash "/tmp/research-${PROJECT}-p2-monitor.sh" "${REPO_DIR}/${PROJECT}" "$DIVISION_LIST" &
# --- checkpoint.yaml 갱신 (기존 필드 보존) ---
CHECKPOINT="${REPO_DIR}/${PROJECT}/findings/checkpoint.yaml"
if [ -f "$CHECKPOINT" ]; then
  sed -i'' -e "s/^current_phase:.*/current_phase: \"2-cross-reflection\"/" "$CHECKPOINT"
  sed -i'' -e "s/^current_status:.*/current_status: in-progress/" "$CHECKPOINT"
  sed -i'' -e "s/^last_updated:.*/last_updated: $(date -u +%Y-%m-%dT%H:%M:%S)/" "$CHECKPOINT"
  sed -i'' -e "s/^active_divisions:.*/active_divisions: [$(IFS=,; echo "${DIVISIONS[*]}")]/" "$CHECKPOINT"
else
  cat > "$CHECKPOINT" << CKPT_EOF
project: ${PROJECT}
current_phase: "2-cross-reflection"
current_status: in-progress
last_updated: $(date -u +%Y-%m-%dT%H:%M:%S)
active_divisions: [$(IFS=,; echo "${DIVISIONS[*]}")]
CKPT_EOF
fi
echo "checkpoint.yaml → Phase 2 in-progress"
echo "완료 감지 모니터 시작"
