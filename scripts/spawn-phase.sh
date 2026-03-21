#!/bin/bash
# spawn-phase.sh — 범용 Phase 스폰 스크립트 (Phase 1, 2, 2.5, 피드백 등)
#
# 사용법:
#   ./scripts/spawn-phase.sh <project> <phase> [--auto] [--divisions div1,div2]
#
# phase 값:
#   1        → division-briefs/{div}.md 기반 Phase 1 실행
#   2        → sync/phase2-{div}.md 기반 Phase 2 실행
#   feedback → sync/feedback-{div}.md 기반 피드백 재실행
#   custom   → --instruction "지시 내용" 으로 커스텀 지시
#
# 옵션:
#   --auto           권한 자동 승인
#   --divisions      특정 Division만 실행 (쉼표 구분). 생략 시 전체
#   --instruction    커스텀 지시 (phase=custom 시)
#
# 예시:
#   ./scripts/spawn-phase.sh my-research 1 --auto
#   ./scripts/spawn-phase.sh my-research 2 --auto --divisions market,capability
#   ./scripts/spawn-phase.sh my-research feedback --auto --divisions product

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PROJECT="${1:?사용법: ./scripts/spawn-phase.sh <project> <phase> [--auto] [--divisions div1,div2]}"
PHASE="${2:?Phase를 지정하세요 (1, 2, feedback, custom)}"
AUTO_PERMISSIONS=""
TARGET_DIVISIONS=""
CUSTOM_INSTRUCTION=""

shift 2
while [[ $# -gt 0 ]]; do
  case "$1" in
    --auto) AUTO_PERMISSIONS="--dangerously-skip-permissions" ;;
    --divisions) TARGET_DIVISIONS="$2"; shift ;;
    --instruction) CUSTOM_INSTRUCTION="$2"; shift ;;
  esac
  shift
done

# --- Division 목록 결정 ---
BRIEFS_DIR="${REPO_DIR}/${PROJECT}/division-briefs"
ALL_DIVISIONS=()
for brief in "${BRIEFS_DIR}"/*.md; do
  [ -f "$brief" ] || continue
  ALL_DIVISIONS+=("$(basename "$brief" .md)")
done

if [ -n "$TARGET_DIVISIONS" ]; then
  IFS=',' read -ra DIVISIONS <<< "$TARGET_DIVISIONS"
else
  DIVISIONS=("${ALL_DIVISIONS[@]}")
fi

NUM="${#DIVISIONS[@]}"
echo "프로젝트: ${PROJECT}, Phase: ${PHASE}, Division: ${NUM}개 (${DIVISIONS[*]})"

# --- Phase별 지시 생성 ---
generate_instruction() {
  local div="$1"
  local agent="${div}-lead"
  local base="${REPO_DIR}/${PROJECT}"

  case "$PHASE" in
    1)
      echo "claude ${AUTO_PERMISSIONS} --agent ${agent} '${base}/division-briefs/${div}.md를 읽고 Phase 1 리서치를 시작하라. 모든 출력은 반드시 ${base}/findings/${div}/ 에만 저장하라.'"
      ;;
    2)
      echo "claude ${AUTO_PERMISSIONS} --agent ${agent} '${base}/sync/round-1-briefing.md와 ${base}/sync/phase2-${div}.md를 읽고 Phase 2 심화 리서치를 수행하라. 결과를 ${base}/findings/${div}/에 업데이트하고 .done 파일의 phase를 2로 갱신하라.'"
      ;;
    feedback)
      echo "claude ${AUTO_PERMISSIONS} --agent ${agent} '${base}/sync/feedback-${div}.md를 읽고 피드백을 반영하여 리서치를 보강하라. 결과를 ${base}/findings/${div}/에 업데이트하라.'"
      ;;
    custom)
      echo "claude ${AUTO_PERMISSIONS} --agent ${agent} '${CUSTOM_INSTRUCTION}'"
      ;;
    *)
      # 숫자 Phase (2.5 등)
      echo "claude ${AUTO_PERMISSIONS} --agent ${agent} '${base}/sync/phase${PHASE}-${div}.md를 읽고 Phase ${PHASE} 리서치를 수행하라. 결과를 ${base}/findings/${div}/에 저장하라.'"
      ;;
  esac
}

# --- tmux 세션 생성 ---
SESSION="research-v2-p${PHASE}"
tmux kill-session -t "$SESSION" 2>/dev/null || true

PANE_MAP_FILE="/tmp/research-v2-pane-map-p${PHASE}.txt"
> "$PANE_MAP_FILE"

# 첫 Division
FIRST_DIV="${DIVISIONS[0]}"
FIRST_CMD=$(generate_instruction "$FIRST_DIV")

tmux new-session -d -s "$SESSION" -n "phase${PHASE}" -c "$REPO_DIR"
sleep 0.5
FIRST_PANE=$(tmux list-panes -t "${SESSION}:phase${PHASE}" -F '#{pane_id}' | head -1)
tmux send-keys -t "$FIRST_PANE" "$FIRST_CMD" Enter
echo "${FIRST_DIV}=${FIRST_PANE}" >> "$PANE_MAP_FILE"
echo "  ✅ ${FIRST_DIV}-lead → ${FIRST_PANE}"

# 나머지 Division
for ((i=1; i<NUM; i++)); do
  DIV="${DIVISIONS[$i]}"
  CMD=$(generate_instruction "$DIV")

  if (( i % 2 == 1 )); then
    NEW_PANE=$(tmux split-window -v -t "${SESSION}:phase${PHASE}" -c "$REPO_DIR" -P -F '#{pane_id}')
  else
    NEW_PANE=$(tmux split-window -h -t "${SESSION}:phase${PHASE}" -c "$REPO_DIR" -P -F '#{pane_id}')
  fi
  sleep 0.3
  tmux send-keys -t "$NEW_PANE" "$CMD" Enter
  echo "${DIV}=${NEW_PANE}" >> "$PANE_MAP_FILE"
  echo "  ✅ ${DIV}-lead → ${NEW_PANE}"
done

tmux select-layout -t "${SESSION}:phase${PHASE}" tiled

echo ""
echo "${NUM}개 Division Phase ${PHASE} 실행 완료!"
echo "접속: tmux attach -t ${SESSION}"
echo "pane 매핑: cat ${PANE_MAP_FILE}"

# --- checkpoint.yaml 자동 갱신 (#5) ---
CHECKPOINT="${REPO_DIR}/${PROJECT}/findings/checkpoint.yaml"
if [ -f "$CHECKPOINT" ]; then
  # current_phase 업데이트 (sed로 간이 갱신)
  sed -i '' "s/current_phase:.*/current_phase: \"phase-${PHASE}\"/" "$CHECKPOINT"
  sed -i '' "s/current_status:.*/current_status: in-progress/" "$CHECKPOINT"
  sed -i '' "s/last_updated:.*/last_updated: $(date -u +"%Y-%m-%dT%H:%M:%S")/" "$CHECKPOINT"
  echo "checkpoint.yaml 갱신: phase-${PHASE}, in-progress"
fi

# --- 완료 감지 ---
DIVISION_LIST=$(IFS=,; echo "${DIVISIONS[*]}")

(
  ERROR_LOG="/tmp/research-v2-error-p${PHASE}.log"
  > "$ERROR_LOG"
  POLL_COUNT=0
  MAX_POLLS=180  # 30분 (10초 × 180)

  while true; do
    COMPLETED=0
    ERRORS=0
    STATUS_LINE=""

    for div in "${DIVISIONS[@]}"; do
      DONE=false
      if [ "$PHASE" = "1" ]; then
        [ -f "${REPO_DIR}/${PROJECT}/findings/${div}/.done" ] && DONE=true
      else
        grep -q "phase: ${PHASE}" "${REPO_DIR}/${PROJECT}/findings/${div}/.done" 2>/dev/null && DONE=true
      fi

      if $DONE; then
        ((COMPLETED++))
        STATUS_LINE="${STATUS_LINE}  ${div}: ✅ |"
      else
        # .progress에서 리프 진행률 확인 (#6+#8)
        PROGRESS_FILE="${REPO_DIR}/${PROJECT}/findings/${div}/.progress"
        if [ -f "$PROGRESS_FILE" ]; then
          LEAF_DONE=$(grep -c "completed_at:" "$PROGRESS_FILE" 2>/dev/null || echo 0)
          STATUS_LINE="${STATUS_LINE}  ${div}: ⏳(${LEAF_DONE}leaf) |"
        else
          STATUS_LINE="${STATUS_LINE}  ${div}: ⏳ |"
        fi

        # pane 생존 체크 (#8 에러 감지)
        PANE_ID=$(grep "^${div}=" "$PANE_MAP_FILE" 2>/dev/null | cut -d= -f2)
        if [ -n "$PANE_ID" ]; then
          PANE_DEAD=$(tmux list-panes -t "$SESSION" -F '#{pane_id} #{pane_dead}' 2>/dev/null | grep "$PANE_ID" | awk '{print $2}')
          if [ "$PANE_DEAD" = "1" ]; then
            ((ERRORS++))
            echo "[$(date)] ${div}: pane ${PANE_ID} 비정상 종료" >> "$ERROR_LOG"
          fi
        fi
      fi
    done

    # 전체 완료
    if [ "$COMPLETED" -ge "$NUM" ]; then
      echo ""
      echo "✅ ${NUM}개 Division Phase ${PHASE} 완료!"
      echo "$STATUS_LINE"
      if [ -f "$CHECKPOINT" ]; then
        sed -i '' "s/current_status:.*/current_status: completed/" "$CHECKPOINT"
        sed -i '' "s/last_updated:.*/last_updated: $(date -u +"%Y-%m-%dT%H:%M:%S")/" "$CHECKPOINT"
      fi
      if command -v osascript &>/dev/null; then
        osascript -e "display notification \"Phase ${PHASE} 완료!\" with title \"Deep-Briefing\" sound name \"Glass\""
      fi
      break
    fi

    # 에러 감지 시 알림
    if [ "$ERRORS" -gt 0 ]; then
      echo "⚠️ ${ERRORS}개 Division에서 에러 감지. 로그: ${ERROR_LOG}"
      if command -v osascript &>/dev/null; then
        osascript -e "display notification \"${ERRORS}개 Division 에러 감지\" with title \"Deep-Briefing\" sound name \"Basso\""
      fi
    fi

    # 타임아웃
    ((POLL_COUNT++))
    if [ "$POLL_COUNT" -ge "$MAX_POLLS" ]; then
      echo "⚠️ 30분 타임아웃. ${COMPLETED}/${NUM} 완료. tmux 확인 필요."
      if command -v osascript &>/dev/null; then
        osascript -e "display notification \"30분 타임아웃. tmux 확인 필요.\" with title \"Deep-Briefing\" sound name \"Basso\""
      fi
      break
    fi

    sleep 10
  done
) &
echo "완료 감지 모니터 시작 (백그라운드, 에러 감지 포함)"
