#!/bin/bash
# spawn-leads.sh — tmux로 Division Lead CLI를 자동 생성 (4~N개 동적 대응)
#
# 사용법:
#   ./scripts/spawn-leads.sh <project-name> [--attach] [--auto]
#
# 옵션:
#   --attach   실행 후 tmux 세션에 자동 접속
#   --auto     권한 확인 없이 자동 실행 (dangerously-skip-permissions)
#              ⚠ 모든 파일 읽기/쓰기/웹 접근을 자동 허용합니다
#
# Division 자동 감지:
#   {project}/division-briefs/*.md 파일에서 Division 이름을 자동 추출.
#   파일명 = Division 이름, 에이전트 = {파일명}-lead
#   예: market.md → market-lead, people-org.md → people-org-lead
#   ⚠ people-culture-lead는 deprecated → people-org-lead 사용
#
# 예시:
#   ./scripts/spawn-leads.sh my-research --attach         # 4 Division
#   ./scripts/spawn-leads.sh my-other-research --attach --auto   # 5 Division

set -euo pipefail

# --- .env 로드 ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ -f "${REPO_DIR}/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_DIR}/.env"
  set +a
  echo "API 키 로드 완료: .env"
else
  echo "⚠ 경고: .env 파일이 없습니다. API 키 없이 실행됩니다."
  echo ""
fi

# --- 인자 파싱 ---
PROJECT="${1:?사용법: ./scripts/spawn-leads.sh <project-name> [--attach] [--auto]}"
ATTACH=""
AUTO_PERMISSIONS=""

shift
for arg in "$@"; do
  case "$arg" in
    --attach) ATTACH="--attach" ;;
    --auto) AUTO_PERMISSIONS="--dangerously-skip-permissions" ;;
  esac
done

# --- --auto 미지정 시 사용자에게 선택 안내 ---
if [ -z "$AUTO_PERMISSIONS" ]; then
  echo ""
  echo "권한 모드를 선택하세요:"
  echo ""
  echo "  1) 자동 승인 (--auto)"
  echo "     → 파일 읽기/쓰기, 웹 검색 등 모든 권한을 자동 허용"
  echo ""
  echo "  2) 수동 승인 (기본)"
  echo "     → 각 Lead CLI에서 권한 요청마다 승인/거부 선택"
  echo ""
  read -r -p "선택 [1/2, 기본=1]: " choice
  case "$choice" in
    2) AUTO_PERMISSIONS="" ;;
    *) AUTO_PERMISSIONS="--dangerously-skip-permissions" ;;
  esac
  echo ""
fi

SESSION="research-${PROJECT}"

# --- Division 자동 감지 (division-briefs/*.md에서) ---
BRIEFS_DIR="${REPO_DIR}/${PROJECT}/division-briefs"
if [ ! -d "$BRIEFS_DIR" ]; then
  echo "❌ ${PROJECT}/division-briefs/ 디렉토리가 없습니다."
  exit 1
fi

DIVISIONS=()
AGENTS=()
DEPRECATED_AGENTS=("people-culture")  # deprecated Division 목록

for brief in "${BRIEFS_DIR}"/*.md; do
  [ -f "$brief" ] || continue
  div=$(basename "$brief" .md)

  # deprecated 에이전트 감지
  for dep in "${DEPRECATED_AGENTS[@]}"; do
    if [[ "$div" == "$dep" ]]; then
      echo "  ⚠️  ${div}-lead는 deprecated. people-org-lead를 사용하세요."
      echo "      division-briefs/${div}.md → division-briefs/people-org.md로 변경 필요"
      continue 2  # 이 Division 건너뛰기
    fi
  done

  DIVISIONS+=("$div")
  AGENTS+=("${div}-lead")
done

NUM_DIVISIONS=${#DIVISIONS[@]}

if [ "$NUM_DIVISIONS" -eq 0 ]; then
  echo "❌ division-briefs/*.md 파일이 없습니다."
  exit 1
fi

echo "감지된 Division: ${NUM_DIVISIONS}개 — ${DIVISIONS[*]}"
echo ""

# --- Pre-flight Check ---
echo "=== Pre-flight Check ==="
PREFLIGHT_FAIL=0

# 1. 에이전트 파일 존재 확인
for agent in "${AGENTS[@]}"; do
  if [ ! -f "${REPO_DIR}/.claude/agents/${agent}.md" ]; then
    echo "  ⚠️  .claude/agents/${agent}.md 없음 (에이전트 미등록)"
  fi
done

# 2. API 키 확인
if [ -f "${REPO_DIR}/.env" ]; then
  source "${REPO_DIR}/.env" 2>/dev/null
  if [ -z "${DART_API_KEY:-}" ] || [ "${DART_API_KEY:-}" = "your_dart_api_key_here" ]; then
    echo "  ⚠️  DART_API_KEY 미설정"
  fi
else
  echo "  ⚠️  .env 파일 없음"
fi

# 3. 사용자 데이터 전처리 확인
USER_DATA_DIR="${REPO_DIR}/${PROJECT}/data/user-provided"
PROCESSED_DIR="${REPO_DIR}/${PROJECT}/data/processed"
if [ -d "$USER_DATA_DIR" ] && [ "$(ls -A "$USER_DATA_DIR" 2>/dev/null)" ]; then
  if [ ! -d "$PROCESSED_DIR" ] || [ -z "$(ls -A "$PROCESSED_DIR" 2>/dev/null)" ]; then
    echo "  ❌ 사용자 데이터가 있으나 data-preprocessor 미실행"
    PREFLIGHT_FAIL=1
  else
    echo "  ✅ 전처리 데이터 확인됨"
  fi
fi

# 4. findings 디렉토리 확인/생성
for div in "${DIVISIONS[@]}"; do
  mkdir -p "${REPO_DIR}/${PROJECT}/findings/${div}"
done

if [ "$PREFLIGHT_FAIL" -eq 1 ]; then
  echo ""
  read -r -p "Pre-flight 실패. 강제 실행하시겠습니까? [y/N]: " force
  case "$force" in
    [yY]) echo "강제 실행합니다..." ;;
    *) echo "중단합니다."; exit 1 ;;
  esac
fi

echo ""
echo "프로젝트: ${PROJECT}"
echo "Division: ${NUM_DIVISIONS}개"
echo ""

# --- 기존 세션 정리 ---
tmux kill-session -t "$SESSION" 2>/dev/null || true

# --- tmux 세션 생성 + N-pane 구성 ---
# 핵심: 첫 pane에 바로 명령 전송 후, 나머지는 split + 즉시 전송
# 이 방식은 pane ID 밀림 문제를 원천 차단한다.

echo "tmux 세션 '${SESSION}' 생성 중..."

# 첫 번째 Division: 세션 생성과 동시에 명령 전송
FIRST_DIV="${DIVISIONS[0]}"
FIRST_AGENT="${AGENTS[0]}"
FIRST_CMD="claude ${AUTO_PERMISSIONS} --agent ${FIRST_AGENT} '${REPO_DIR}/${PROJECT}/division-briefs/${FIRST_DIV}.md를 읽고 Phase 1 리서치를 시작하라. 모든 출력은 반드시 ${REPO_DIR}/${PROJECT}/findings/${FIRST_DIV}/ 에만 저장하라. 완료 시 .done 파일에 phase: 1과 status: success를 기록하라.'"

# pane ID를 명시적으로 캡처하여 매핑 (밀림 원천 차단)
PANE_MAP_FILE="/tmp/research-${PROJECT}-pane-map.txt"
> "$PANE_MAP_FILE"

tmux new-session -d -s "$SESSION" -n "leads" -c "$REPO_DIR"
sleep 0.5

# 첫 pane ID 캡처
FIRST_PANE=$(tmux list-panes -t "${SESSION}:leads" -F '#{pane_id}' | head -1)
tmux send-keys -t "$FIRST_PANE" "$FIRST_CMD" Enter
echo "${FIRST_DIV}=${FIRST_PANE}" >> "$PANE_MAP_FILE"
echo "  ✅ ${FIRST_AGENT} → ${FIRST_PANE}"

# 나머지 Division: split 시 -P로 새 pane ID를 직접 캡처
for ((i=1; i<NUM_DIVISIONS; i++)); do
  DIV="${DIVISIONS[$i]}"
  AGENT="${AGENTS[$i]}"
  CMD="claude ${AUTO_PERMISSIONS} --agent ${AGENT} '${REPO_DIR}/${PROJECT}/division-briefs/${DIV}.md를 읽고 Phase 1 리서치를 시작하라. 모든 출력은 반드시 ${REPO_DIR}/${PROJECT}/findings/${DIV}/ 에만 저장하라. 완료 시 .done 파일에 phase: 1과 status: success를 기록하라.'"

  # split + pane ID 캡처 (-P -F로 생성된 pane ID를 반환)
  if (( i % 2 == 1 )); then
    NEW_PANE=$(tmux split-window -v -t "${SESSION}:leads" -c "$REPO_DIR" -P -F '#{pane_id}')
  else
    NEW_PANE=$(tmux split-window -h -t "${SESSION}:leads" -c "$REPO_DIR" -P -F '#{pane_id}')
  fi
  sleep 0.3

  # 캡처된 pane ID로 직접 전송 (활성 pane 의존 제거)
  tmux send-keys -t "$NEW_PANE" "$CMD" Enter
  echo "${DIV}=${NEW_PANE}" >> "$PANE_MAP_FILE"
  echo "  ✅ ${AGENT} → ${NEW_PANE}"
done

# 타일 레이아웃 적용
tmux select-layout -t "${SESSION}:leads" tiled

echo ""
echo "${NUM_DIVISIONS}개 Division Lead CLI 실행 완료!"
echo ""

# pane 매핑 표시
PANE_LIST=$(tmux list-panes -t "${SESSION}:leads" -F '#{pane_index}: #{pane_id}')
echo "pane 매핑:"
echo "$PANE_LIST"
echo ""

echo "tmux 조작법:"
echo "  Ctrl+b → 화살표  pane 이동"
echo "  Ctrl+b → z       현재 pane 풀스크린 토글"
echo "  Ctrl+b → d       tmux에서 빠져나오기"
echo ""
echo "접속: tmux attach -t ${SESSION}"
echo "종료: tmux kill-session -t ${SESSION}"
echo ""

# --- 완료 대기 모니터 안내 ---
echo ".done 파일 모니터링:"
echo "  watch -n 5 'ls -la ${REPO_DIR}/${PROJECT}/findings/*/.done 2>/dev/null || echo \"아직 완료된 Division 없음\"'"
echo ""

# --- 완료 감지 백그라운드 프로세스 ---
# Division 목록을 환경변수로 전달하여 동적 대응
DIVISION_LIST=$(IFS=,; echo "${DIVISIONS[*]}")

MONITOR_SCRIPT=$(cat << 'MONITOR_EOF'
#!/bin/bash
PROJECT_DIR="$1"
SESSION_NAME="$2"
IFS=',' read -ra DIVS <<< "$3"
TOTAL=${#DIVS[@]}
COMPLETED=0
ELAPSED=0
TIMEOUT=7200  # 2시간 타임아웃 (초)
CHECK_INTERVAL=10
HEALTH_CHECK_INTERVAL=60  # 1분마다 pane 상태 확인
LAST_HEALTH_CHECK=0

# pane 매핑 파일
PANE_MAP="/tmp/research-${PROJECT}-pane-map.txt"

while [ "$COMPLETED" -lt "$TOTAL" ]; do
  COMPLETED=0
  STALLED_DIVS=()

  for div in "${DIVS[@]}"; do
    if [ -f "${PROJECT_DIR}/findings/${div}/.done" ] && grep -q "status: success" "${PROJECT_DIR}/findings/${div}/.done" 2>/dev/null; then
      ((COMPLETED++))
    else
      STALLED_DIVS+=("$div")
    fi
  done

  if [ "$COMPLETED" -lt "$TOTAL" ]; then
    # 타임아웃 체크
    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
      echo ""
      echo "⚠️ 타임아웃 (${TIMEOUT}초) 초과. 미완료 Division: ${STALLED_DIVS[*]}"
      echo "   수동 확인 필요: tmux attach -t ${SESSION_NAME}"
      if command -v osascript &>/dev/null; then
        osascript -e "display notification \"Division 리서치 타임아웃: ${STALLED_DIVS[*]}\" with title \"Deep-Briefing ⚠️\" sound name \"Basso\""
      fi
      exit 1
    fi

    # pane 생존 + .status stuck 확인 (1분마다)
    if [ -f "$PANE_MAP" ] && [ $((ELAPSED - LAST_HEALTH_CHECK)) -ge "$HEALTH_CHECK_INTERVAL" ]; then
      LAST_HEALTH_CHECK=$ELAPSED
      for div in "${STALLED_DIVS[@]}"; do
        PANE_ID=$(grep "^${div}=" "$PANE_MAP" 2>/dev/null | cut -d= -f2)
        if [ -n "$PANE_ID" ]; then
          # .status 기반 stuck 감지 (pane 살아있어도 30분 무변경이면 경고)
          STATUS_FILE="${PROJECT_DIR}/findings/${div}/.status"
          if [ -f "$STATUS_FILE" ]; then
            STATUS_MTIME=$(stat -f %m "$STATUS_FILE" 2>/dev/null || stat -c %Y "$STATUS_FILE" 2>/dev/null || echo 0)
            NOW_TS=$(date +%s)
            STALE_SECS=$((NOW_TS - STATUS_MTIME))
            if [ "$STALE_SECS" -gt 1800 ]; then
              echo "⚠️ [${div}] .status 파일 ${STALE_SECS}초 무변경 — stuck 의심"
              if command -v osascript &>/dev/null; then
                osascript -e "display notification \"${div} stuck 의심 (${STALE_SECS}초 무변경)\" with title \"Deep-Briefing ⚠️\" sound name \"Basso\"" 2>/dev/null
              fi
            fi
          fi

          # pane이 존재하는지 확인
          if ! tmux list-panes -t "$SESSION_NAME" -F '#{pane_id}' 2>/dev/null | grep -Fxq "$PANE_ID"; then
            echo "⚠️ [${div}] pane ${PANE_ID} 사망 감지 (경과: ${ELAPSED}초)"

            # .done 파일이 없으면 비정상 종료
            if [ ! -f "${PROJECT_DIR}/findings/${div}/.done" ]; then
              # 크래시 기록
              echo "division: ${div}" > "${PROJECT_DIR}/findings/${div}/.crash"
              echo "pane_id: ${PANE_ID}" >> "${PROJECT_DIR}/findings/${div}/.crash"
              echo "detected_at: $(date -u +%Y-%m-%dT%H:%M:%S)" >> "${PROJECT_DIR}/findings/${div}/.crash"

              # 자동 재스폰 시도 (1회)
              CRASH_COUNT_FILE="/tmp/research-${PROJECT}-crash-${div}"
              CRASH_COUNT=0
              if [ -f "$CRASH_COUNT_FILE" ]; then
                CRASH_COUNT=$(cat "$CRASH_COUNT_FILE")
              fi

              if [ "$CRASH_COUNT" -lt 1 ]; then
                echo "🔄 ${div} 자동 재스폰 시도 (1/1)..."
                echo $((CRASH_COUNT + 1)) > "$CRASH_COUNT_FILE"
                # 실제 재스폰: 새 tmux pane 생성 + Division Lead CLI 재실행
                NEW_PANE=$(tmux split-window -t "$SESSION" -v -P -F '#{pane_id}' "claude ${AUTO_PERMISSIONS} --agent ${div}-lead '${PROJECT_DIR}/findings/${div}/.progress를 읽고 미완료 Leaf만 재실행하라.'" 2>/dev/null)
                if [ -n "$NEW_PANE" ]; then
                  tmux select-layout -t "$SESSION" tiled 2>/dev/null
                  # pane 매핑 갱신
                  sed -i'' -e "s/^${div}=.*/${div}=${NEW_PANE}/" "$PANE_MAP"
                  echo "✅ ${div} 재스폰 성공 (new pane: $NEW_PANE)"
                else
                  echo "⚠️  ${div} tmux pane 재생성 실패"
                fi
                if command -v osascript &>/dev/null; then
                  osascript -e "display notification \"${div} 자동 재스폰 완료\" with title \"Deep-Briefing\" sound name \"Submarine\""
                fi
              else
                echo "❌ ${div} 재스폰 실패 (최대 1회 초과). PM에 에스컬레이션 필요."
                if command -v osascript &>/dev/null; then
                  osascript -e "display notification \"${div} 재스폰 실패 — PM 확인 필요\" with title \"Deep-Briefing ⚠️\" sound name \"Basso\""
                fi
              fi
            fi
          fi
        fi
      done
    fi

    sleep "$CHECK_INTERVAL"
    ELAPSED=$((ELAPSED + CHECK_INTERVAL))
  fi
done

echo ""
echo "============================================"
echo "  ✅ ${TOTAL}개 Division 리서치 완료! (소요: ${ELAPSED}초)"
echo "  PM CLI에서 Sync Round 1을 시작하세요."
echo "============================================"
echo ""

if command -v osascript &>/dev/null; then
  osascript -e "display notification \"${TOTAL}개 Division 리서치 완료. PM CLI에서 Sync Round 1을 시작하세요.\" with title \"Deep-Briefing\" sound name \"Glass\""
fi
MONITOR_EOF
)

echo "$MONITOR_SCRIPT" > "/tmp/research-${PROJECT}-monitor.sh"
chmod +x "/tmp/research-${PROJECT}-monitor.sh"
bash "/tmp/research-${PROJECT}-monitor.sh" "${REPO_DIR}/${PROJECT}" "$SESSION" "$DIVISION_LIST" &
MONITOR_PID=$!
echo "완료 감지 모니터 시작 (PID: ${MONITOR_PID})"
echo "  ${NUM_DIVISIONS}개 Division .done 파일이 모두 생성되면 알림이 표시됩니다."
echo ""

# --- 자동 접속 ---
if [ "$ATTACH" = "--attach" ]; then
  tmux attach -t "$SESSION"
fi
