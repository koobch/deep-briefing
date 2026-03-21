#!/bin/bash
# check-api-keys.sh — API 키 설정 상태 확인
# 사용법: ./scripts/check-api-keys.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${REPO_DIR}/.env"

# --- 색상 정의 ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# --- 유틸리티 함수 ---
get_value() {
  local key="$1"
  if [ -f "$ENV_FILE" ]; then
    local val
    val=$(grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2-)
    if [[ "$val" == *"your_"*"_here"* ]] || [ -z "$val" ]; then
      echo ""
    else
      echo "$val"
    fi
  else
    echo ""
  fi
}

check_key() {
  local key="$1"
  local name="$2"
  local tier="$3"  # 필수/권장/선택
  local tier_color

  case "$tier" in
    "필수") tier_color="${RED}" ;;
    "권장") tier_color="${YELLOW}" ;;
    "선택") tier_color="${CYAN}" ;;
    *) tier_color="${NC}" ;;
  esac

  local val
  val=$(get_value "$key")

  if [ -n "$val" ]; then
    local masked
    if [ ${#val} -gt 12 ]; then
      masked="${val:0:8}...${val: -4}"
    else
      masked="(설정됨)"
    fi
    echo -e "  ${GREEN}✓ 설정됨${NC}  [${tier_color}${tier}${NC}]  ${name}  ${BOLD}${masked}${NC}"
    return 0
  else
    echo -e "  ${RED}✗ 미설정${NC}  [${tier_color}${tier}${NC}]  ${name}"
    return 1
  fi
}

# --- 메인 ---
echo ""
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${BLUE}  Deep-Briefing — API 키 상태${NC}"
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════${NC}"
echo ""

if [ ! -f "$ENV_FILE" ]; then
  echo -e "${RED}.env 파일이 없습니다.${NC}"
  echo -e "설정하려면: ${BOLD}./scripts/setup-api-keys.sh${NC}"
  echo ""
  exit 1
fi

# 카운터 초기화
total=0
configured=0
required_total=0
required_ok=0

# --- 필수 ---
echo -e "${BOLD}[필수] 리서치 품질에 직접 영향${NC}"
total=$((total + 2))
required_total=$((required_total + 2))

if check_key "DART_API_KEY" "DART Open API (한국 기업 공시)" "필수"; then
  configured=$((configured + 1))
  required_ok=$((required_ok + 1))
fi

if check_key "EXA_API_KEY" "Exa.ai (고품질 웹 검색)" "필수"; then
  configured=$((configured + 1))
  required_ok=$((required_ok + 1))
fi

echo ""

# --- 권장 ---
echo -e "${BOLD}[권장] 특정 Division 분석 보강${NC}"
total=$((total + 4))

if check_key "STEAM_API_KEY" "Steam Web API" "권장"; then
  configured=$((configured + 1))
fi

if check_key "FRED_API_KEY" "FRED API (미국 매크로 지표)" "권장"; then
  configured=$((configured + 1))
fi

if check_key "ECOS_API_KEY" "한국은행 ECOS API" "권장"; then
  configured=$((configured + 1))
fi

if check_key "NEWSAPI_KEY" "NewsAPI (글로벌 뉴스)" "권장"; then
  configured=$((configured + 1))
fi

echo ""

# --- 선택 ---
echo -e "${BOLD}[선택] 키 불요 또는 대체 가능${NC}"
total=$((total + 1))

ua_val=$(get_value "SEC_EDGAR_USER_AGENT")
if [ -n "$ua_val" ] && [[ "$ua_val" != *"example.com"* ]]; then
  echo -e "  ${GREEN}✓ 설정됨${NC}  [${CYAN}선택${NC}]  SEC EDGAR User-Agent"
  configured=$((configured + 1))
else
  echo -e "  ${YELLOW}△ 기본값${NC}  [${CYAN}선택${NC}]  SEC EDGAR User-Agent (example.com → 변경 권장)"
fi

echo -e "  ${GREEN}✓ 불필요${NC}  [${CYAN}선택${NC}]  Yahoo Finance (비공식 API, 키 불필요)"
echo -e "  ${GREEN}✓ 불필요${NC}  [${CYAN}선택${NC}]  Google Trends (pytrends, 키 불필요)"
echo -e "  ${YELLOW}– 미지원${NC}  [${CYAN}선택${NC}]  IGDB (Twitch 인증 필요 — 대체 가능)"

# --- 요약 ---
echo ""
echo -e "${BOLD}────────────────────────────────────────────────────${NC}"
echo -e "  전체: ${configured}/${total} 설정됨"

if [ "$required_ok" -eq "$required_total" ]; then
  echo -e "  필수: ${GREEN}${required_ok}/${required_total} 완료${NC}"
else
  echo -e "  필수: ${RED}${required_ok}/${required_total} (미완료 — 리서치 품질 저하 가능)${NC}"
fi

echo ""

if [ "$required_ok" -lt "$required_total" ]; then
  echo -e "${YELLOW}필수 API 키를 설정하려면:${NC}"
  echo -e "  ${BOLD}./scripts/setup-api-keys.sh${NC}"
  echo ""
fi
