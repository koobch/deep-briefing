#!/bin/bash
# setup-api-keys.sh — 대화형 API 키 설정 스크립트
# 사용법: ./scripts/setup-api-keys.sh
#
# 동작:
#   1. .env 파일이 없으면 .env.example에서 복사하여 생성
#   2. 필수/권장/선택 구분하여 API 키 입력 안내
#   3. 이미 설정된 키는 유지, 누락된 키만 입력
#   4. 입력 후 각 API 연결 테스트

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${REPO_DIR}/.env"
ENV_EXAMPLE="${REPO_DIR}/.env.example"

# --- 색상 정의 ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# --- 유틸리티 함수 ---
print_header() {
  echo ""
  echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════${NC}"
  echo -e "${BOLD}${BLUE}  Deep-Briefing — API 키 설정${NC}"
  echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════${NC}"
  echo ""
}

print_section() {
  echo ""
  echo -e "${BOLD}${CYAN}── $1 ──${NC}"
  echo ""
}

# 현재 .env에서 키 값 읽기 (없으면 빈 문자열)
get_current_value() {
  local key="$1"
  if [ -f "$ENV_FILE" ]; then
    local val
    val=$(grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2-)
    # 예시값이면 빈 문자열 반환
    if [[ "$val" == *"your_"*"_here"* ]] || [ -z "$val" ]; then
      echo ""
    else
      echo "$val"
    fi
  else
    echo ""
  fi
}

# .env 파일에 키 설정 (이미 있으면 교체, 없으면 추가)
set_env_value() {
  local key="$1"
  local value="$2"
  if grep -qE "^${key}=" "$ENV_FILE" 2>/dev/null; then
    # macOS/Linux 호환 sed
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    else
      sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    fi
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

# API 연결 테스트
test_api() {
  local name="$1"
  local test_url="$2"
  local expected="$3"  # HTTP 상태 코드 또는 응답 내 포함 문자열

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$test_url" 2>/dev/null || echo "000")

  if [ "$http_code" = "$expected" ] || [ "$http_code" = "200" ]; then
    echo -e "  ${GREEN}✓${NC} ${name}: 연결 성공 (HTTP ${http_code})"
    return 0
  elif [ "$http_code" = "000" ]; then
    echo -e "  ${RED}✗${NC} ${name}: 연결 실패 (타임아웃 또는 네트워크 오류)"
    return 1
  else
    echo -e "  ${YELLOW}△${NC} ${name}: HTTP ${http_code} (키 또는 URL 확인 필요)"
    return 1
  fi
}

# 키 입력 프롬프트
prompt_key() {
  local key="$1"
  local name="$2"
  local url="$3"
  local tier="$4"  # 필수/권장/선택
  local current
  current=$(get_current_value "$key")

  if [ -n "$current" ]; then
    local masked="${current:0:8}...${current: -4}"
    echo -e "  ${GREEN}✓${NC} ${name}: 이미 설정됨 (${masked})"
    read -rp "    변경하시겠습니까? [y/N] " change
    if [[ "$change" =~ ^[yY]$ ]]; then
      read -rp "    새 키 입력: " new_value
      if [ -n "$new_value" ]; then
        set_env_value "$key" "$new_value"
        echo -e "    ${GREEN}→ 업데이트 완료${NC}"
      fi
    fi
  else
    echo -e "  ${YELLOW}○${NC} ${name} [${tier}]"
    echo -e "    발급: ${url}"
    read -rp "    API 키 입력 (건너뛰려면 Enter): " new_value
    if [ -n "$new_value" ]; then
      set_env_value "$key" "$new_value"
      echo -e "    ${GREEN}→ 설정 완료${NC}"
    else
      echo -e "    ${YELLOW}→ 건너뜀${NC}"
    fi
  fi
}

# --- 메인 로직 ---
print_header

# .env 파일 초기화
if [ ! -f "$ENV_FILE" ]; then
  if [ -f "$ENV_EXAMPLE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo -e "${GREEN}.env.example에서 .env 파일을 생성했습니다.${NC}"
  else
    touch "$ENV_FILE"
    echo -e "${YELLOW}.env.example이 없어 빈 .env 파일을 생성했습니다.${NC}"
  fi
else
  echo -e "${BLUE}기존 .env 파일이 있습니다. 누락된 키만 추가합니다.${NC}"
fi

# --- 필수 API 키 ---
print_section "필수 API (리서치 품질에 직접 영향)"

prompt_key "DART_API_KEY" "DART Open API (한국 기업 공시)" \
  "https://opendart.fss.or.kr" "필수 — 무료"

prompt_key "EXA_API_KEY" "Exa.ai (고품질 웹 검색)" \
  "https://exa.ai" "필수 — 유료"

# --- 권장 API 키 ---
print_section "권장 API (특정 Division 분석 보강)"

prompt_key "STEAM_API_KEY" "Steam Web API" \
  "https://steamcommunity.com/dev/apikey" "권장 — 무료"

prompt_key "FRED_API_KEY" "FRED API (미국 매크로 지표)" \
  "https://fred.stlouisfed.org/docs/api/api_key.html" "권장 — 무료"

prompt_key "ECOS_API_KEY" "한국은행 ECOS API" \
  "https://ecos.bok.or.kr/api/" "권장 — 무료"

prompt_key "NEWSAPI_KEY" "NewsAPI (글로벌 뉴스)" \
  "https://newsapi.org" "권장 — 무료 tier"

# --- 선택 설정 ---
print_section "선택 설정"

current_ua=$(get_current_value "SEC_EDGAR_USER_AGENT")
if [ -z "$current_ua" ] || [[ "$current_ua" == *"example.com"* ]]; then
  echo -e "  ${YELLOW}○${NC} SEC EDGAR User-Agent (키 불필요, User-Agent만 설정)"
  echo -e "    형식: \"프로젝트명 이메일주소\""
  read -rp "    User-Agent 입력 (건너뛰려면 Enter): " ua_value
  if [ -n "$ua_value" ]; then
    set_env_value "SEC_EDGAR_USER_AGENT" "\"${ua_value}\""
    echo -e "    ${GREEN}→ 설정 완료${NC}"
  else
    echo -e "    ${YELLOW}→ 건너뜀 (기본값 사용)${NC}"
  fi
else
  echo -e "  ${GREEN}✓${NC} SEC EDGAR User-Agent: 이미 설정됨"
fi

# --- API 연결 테스트 ---
print_section "API 연결 테스트"

echo -e "연결 테스트를 실행하시겠습니까? [Y/n] "
read -rp "" run_test

if [[ ! "$run_test" =~ ^[nN]$ ]]; then
  echo ""

  # DART 테스트
  dart_key=$(get_current_value "DART_API_KEY")
  if [ -n "$dart_key" ]; then
    test_api "DART" "https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=${dart_key}" "200"
  else
    echo -e "  ${YELLOW}–${NC} DART: 키 미설정 (건너뜀)"
  fi

  # Exa 테스트
  exa_key=$(get_current_value "EXA_API_KEY")
  if [ -n "$exa_key" ]; then
    exa_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
      -X POST "https://api.exa.ai/search" \
      -H "x-api-key: ${exa_key}" \
      -H "Content-Type: application/json" \
      -d '{"query":"test","numResults":1}' 2>/dev/null || echo "000")
    if [ "$exa_code" = "200" ]; then
      echo -e "  ${GREEN}✓${NC} Exa.ai: 연결 성공 (HTTP ${exa_code})"
    elif [ "$exa_code" = "000" ]; then
      echo -e "  ${RED}✗${NC} Exa.ai: 연결 실패"
    else
      echo -e "  ${YELLOW}△${NC} Exa.ai: HTTP ${exa_code} (키 확인 필요)"
    fi
  else
    echo -e "  ${YELLOW}–${NC} Exa.ai: 키 미설정 (건너뜀)"
  fi

  # Steam 테스트
  steam_key=$(get_current_value "STEAM_API_KEY")
  if [ -n "$steam_key" ]; then
    test_api "Steam" "https://api.steampowered.com/ISteamApps/GetAppList/v2/?key=${steam_key}" "200"
  else
    echo -e "  ${YELLOW}–${NC} Steam: 키 미설정 (건너뜀)"
  fi

  # FRED 테스트
  fred_key=$(get_current_value "FRED_API_KEY")
  if [ -n "$fred_key" ]; then
    test_api "FRED" "https://api.stlouisfed.org/fred/series?series_id=GDP&api_key=${fred_key}&file_type=json" "200"
  else
    echo -e "  ${YELLOW}–${NC} FRED: 키 미설정 (건너뜀)"
  fi

  # ECOS 테스트
  ecos_key=$(get_current_value "ECOS_API_KEY")
  if [ -n "$ecos_key" ]; then
    test_api "ECOS" "https://ecos.bok.or.kr/api/StatisticTableList/${ecos_key}/json/kr/1/1/" "200"
  else
    echo -e "  ${YELLOW}–${NC} ECOS: 키 미설정 (건너뜀)"
  fi

  # NewsAPI 테스트
  news_key=$(get_current_value "NEWSAPI_KEY")
  if [ -n "$news_key" ]; then
    test_api "NewsAPI" "https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey=${news_key}" "200"
  else
    echo -e "  ${YELLOW}–${NC} NewsAPI: 키 미설정 (건너뜀)"
  fi

  # SEC EDGAR 테스트 (키 불필요)
  test_api "SEC EDGAR" "https://data.sec.gov/submissions/CIK0000712515.json" "200"
fi

# --- 완료 ---
print_section "설정 완료"

echo -e "API 키 상태를 확인하려면:"
echo -e "  ${BOLD}./scripts/check-api-keys.sh${NC}"
echo ""
echo -e "리서치 실행 전 .env를 로드하려면:"
echo -e "  ${BOLD}source .env${NC}"
echo ""
echo -e "spawn-leads.sh가 실행 시 .env를 자동으로 로드합니다."
echo ""
