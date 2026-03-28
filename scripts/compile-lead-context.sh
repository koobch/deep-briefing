#!/bin/bash
# compile-lead-context.sh — Lead 부트스트랩 통합 컨텍스트 생성
#
# PM이 Phase 0 완료 후 자동 실행. 각 Division Lead에게 필요한 모든 컨텍스트를
# 1개 파일로 압축하여 토큰 소비를 ~85% 절감.
#
# 사용법: ./scripts/compile-lead-context.sh <project-name>
#
# 생성 파일: {project}/lead-context-{division}.md (Division별 1개)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PROJECT="${1:-}"
if [ -z "$PROJECT" ]; then
  echo "사용법: ./scripts/compile-lead-context.sh <project-name>"
  exit 1
fi

PROJECT_DIR="${REPO_DIR}/${PROJECT}"
if [ ! -d "$PROJECT_DIR" ]; then
  echo "오류: 프로젝트 디렉토리가 없습니다: ${PROJECT_DIR}"
  exit 1
fi

# 도메인 탐지
DOMAIN="example"
if [ -f "${PROJECT_DIR}/01-research-plan.md" ]; then
  DETECTED=$(grep "domain_knowledge:" "${PROJECT_DIR}/01-research-plan.md" 2>/dev/null | head -1 | sed 's/.*domains\///' | sed 's/\/.*//' || true)
  [ -n "$DETECTED" ] && DOMAIN="$DETECTED"
fi

DOMAIN_DIR="${REPO_DIR}/domains/${DOMAIN}"

# 활성 Division 감지 (division-briefs/ 기반)
DIVISIONS=()
for brief in "${PROJECT_DIR}"/division-briefs/*.md; do
  [ -f "$brief" ] || continue
  div=$(basename "$brief" .md)
  DIVISIONS+=("$div")
done

if [ ${#DIVISIONS[@]} -eq 0 ]; then
  echo "오류: division-briefs/에 파일이 없습니다."
  exit 1
fi

echo "=== Lead 통합 컨텍스트 생성 ==="
echo "  프로젝트: ${PROJECT}"
echo "  도메인: ${DOMAIN}"
echo "  Division: ${DIVISIONS[*]}"

# === 공통 섹션 생성 (모든 Division 공유) ===
COMMON_SECTION=$(cat << 'COMMON_EOF'
## 출력 규칙 (core/protocols/output-format.md 핵심)

- **4-Layer 피라미드**: Layer 0(Claim 한 문장) → Layer 1(Evidence 1~3개 + 소스) → Layer 2(구조화 데이터) → Layer 3(원본 소스)
- **ID 체계**: {Division}{SubDomain}-## (예: MSZ-01 = Market-Sizing-01)
- **필수 메타데이터**: agent, domain, parent, status(draft/researching/verified), timestamp, iteration
- **Claim 태깅**: 모든 Claim에 confidence(high/medium/low) + strategic_impact(high/medium/low) 필수
- **disconfirming 필드**: 빈 값 불가. "X 키워드로 검색 + Y 소스 확인 → 반증 미발견" 수준 필수
- **엔터티 라벨**: [그룹] A그룹, [별도] A자회사 구분. 동일 기업은 문서 전체에서 같은 라벨
- **시점 표기**: YYYY 또는 YYYY-QN. 통화는 원문 + 환산 병기
- **Golden Facts**: findings/golden-facts.yaml = 수치 SSOT. [GF-###] 태그로 참조
- **cross_domain 태깅**: 다른 Division 영향 → implications / 데이터 필요 → questions / urgency: must|should|nice
- **data_gaps**: 해결 불가 항목에 fallback 전략 기재

상세: core/protocols/output-format.md 참조 (필요 시 Read)

## 검증 규칙 (core/protocols/fact-check-protocol.md 핵심)

**VL-1 (Leaf 자가 검증)**:
- 최소 2개 독립 소스에서 확인 (confidence: high 기준)
- 소스 신뢰도: primary(공식 재무/정부 통계) > secondary(애널리스트/리서치) > tertiary(뉴스/블로그)
- 반증 검토: "이 Claim이 틀렸다면?" 능동 검색. 반증 없으면 검색 방법 기재
- Null Hypothesis Check: 가설의 정반대를 명시적으로 검증

**VL-1.5 (Lead 삼각 검증 + 스팟체크)**:
- Leaf 간 교차 가능 수치 식별 → 불일치 > 5%면 재확인 지시
- strategic_impact: high Claim 상위 3~5개 독립 검증 (Lead가 직접 원본 확인)
- Leaf 80%+ 동일 방향 → Groupthink 경고 + 반대 가능성 1건 서술

**VL-2 (정합성 검토)**:
- 수치 일관성: 부분합 = 전체, 비율 ≤ 100%
- 엔터티 일관성: 표기 라벨 통일
- 시점 일관성: 기준 시점 통일 또는 차이 명시
- 정의 일관성: 핵심 용어 정의 통일

상세: core/protocols/fact-check-protocol.md 참조 (필요 시 Read)

## 분석 원칙 (core/knowledge/common-sense.yaml 핵심)

- **So What 테스트**: 모든 Claim에 "의사결정에 어떤 의미인가?" 답할 수 있어야 함
- **MECE 체크**: 분석 범위 나눌 때 겹침/빠짐 확인
- **규모감 유지**: 숫자 제시 시 비교 대상 함께 제시
- **불확실성 인정**: 모르면 모른다고 명시. confidence 부풀리지 않음
- **반대 의견 포함**: 핵심 Claim에 반대 의견/반증 1건 이상

상세: core/knowledge/common-sense.yaml 참조 (필요 시 Read)

## API 사용 규칙 (core/protocols/api-usage-guide.md 핵심)

- **API 우선**: 설정된 API가 있으면 웹 검색보다 먼저 사용
- 수집 우선순위: API → Exa 검색 → WebSearch → WebFetch/Firecrawl
- 정부 API(DART/FRED/ECOS) = primary 소스, Exa/Firecrawl = secondary
- WebFetch 실패(403/차단) → Firecrawl API로 재시도
- API 결과: findings/{division}/api/ 에 저장, data-registry.csv에 등록
- API 미사용 시 confidence 상한 = medium (high 불가)

상세: core/protocols/api-usage-guide.md 참조 (필요 시 Read)
COMMON_EOF
)

# === Division별 컨텍스트 생성 ===
for div in "${DIVISIONS[@]}"; do
  CONTEXT_FILE="${PROJECT_DIR}/lead-context-${div}.md"

  # 헤더
  cat > "$CONTEXT_FILE" << HEADER_EOF
# ${div} Lead 부트스트랩 통합 컨텍스트
> 자동 생성됨 (compile-lead-context.sh). 수동 편집 금지.
> 프로젝트: ${PROJECT} | 도메인: ${DOMAIN}
> 상세가 필요하면 원본 파일을 Read하라.

HEADER_EOF

  # 공통 섹션
  echo "$COMMON_SECTION" >> "$CONTEXT_FILE"

  # 도메인 지식 요약 (있으면)
  echo "" >> "$CONTEXT_FILE"
  echo "## 도메인 지식 (domains/${DOMAIN}/)" >> "$CONTEXT_FILE"
  echo "" >> "$CONTEXT_FILE"

  if [ -f "${DOMAIN_DIR}/frameworks.md" ]; then
    echo "### 프레임워크 (요약)" >> "$CONTEXT_FILE"
    # 프레임워크 이름만 추출
    grep "^### " "${DOMAIN_DIR}/frameworks.md" 2>/dev/null | sed 's/### /- /' >> "$CONTEXT_FILE"
    echo "" >> "$CONTEXT_FILE"
    echo "상세: domains/${DOMAIN}/frameworks.md 참조" >> "$CONTEXT_FILE"
  fi

  if [ -f "${DOMAIN_DIR}/data-sources.md" ]; then
    echo "" >> "$CONTEXT_FILE"
    echo "### 데이터 소스 (요약)" >> "$CONTEXT_FILE"
    # API 이름만 추출
    grep "^| " "${DOMAIN_DIR}/data-sources.md" 2>/dev/null | head -10 >> "$CONTEXT_FILE"
    echo "" >> "$CONTEXT_FILE"
    echo "상세: domains/${DOMAIN}/data-sources.md 참조" >> "$CONTEXT_FILE"
  fi

  # 축적된 도메인 지식 (있고 비어있지 않으면)
  META_FILE="${DOMAIN_DIR}/knowledge/_meta.yaml"
  if [ -f "$META_FILE" ]; then
    MATURITY=$(grep "maturity:" "$META_FILE" 2>/dev/null | awk '{print $2}' | tr -d '"')
    if [ "$MATURITY" != "empty" ] && [ -n "$MATURITY" ]; then
      echo "" >> "$CONTEXT_FILE"
      echo "### 축적된 지식 (성숙도: ${MATURITY})" >> "$CONTEXT_FILE"
      echo "domains/${DOMAIN}/knowledge/ 아래 learned-*.yaml 파일 참조" >> "$CONTEXT_FILE"
    else
      echo "" >> "$CONTEXT_FILE"
      echo "### 축적된 지식: 없음 (첫 프로젝트)" >> "$CONTEXT_FILE"
    fi
  fi

  # Division Brief 전체 포함
  BRIEF_FILE="${PROJECT_DIR}/division-briefs/${div}.md"
  if [ -f "$BRIEF_FILE" ]; then
    echo "" >> "$CONTEXT_FILE"
    echo "---" >> "$CONTEXT_FILE"
    echo "" >> "$CONTEXT_FILE"
    echo "## Division Brief" >> "$CONTEXT_FILE"
    echo "" >> "$CONTEXT_FILE"
    cat "$BRIEF_FILE" >> "$CONTEXT_FILE"
  fi

  # Client Brief 포함
  CLIENT_BRIEF="${PROJECT_DIR}/00-client-brief.md"
  if [ -f "$CLIENT_BRIEF" ]; then
    echo "" >> "$CONTEXT_FILE"
    echo "---" >> "$CONTEXT_FILE"
    echo "" >> "$CONTEXT_FILE"
    echo "## Client Brief" >> "$CONTEXT_FILE"
    echo "" >> "$CONTEXT_FILE"
    cat "$CLIENT_BRIEF" >> "$CONTEXT_FILE"
  fi

  # --- User Context 스니펫 생성 ---
  USER_PROFILE="${PROJECT_DIR}/user-profile.yaml"
  if [ -f "$USER_PROFILE" ]; then
    echo "" >> "$CONTEXT_FILE"
    echo "---" >> "$CONTEXT_FILE"
    echo "" >> "$CONTEXT_FILE"
    echo "## User Context" >> "$CONTEXT_FILE"
    echo "" >> "$CONTEXT_FILE"
    # user-profile.yaml에서 핵심 필드 추출
    grep -A1 'level:' "$USER_PROFILE" | head -2 >> "$CONTEXT_FILE"
    grep -A1 'role:' "$USER_PROFILE" | head -2 >> "$CONTEXT_FILE"
    grep -A1 'tolerance:' "$USER_PROFILE" | head -2 >> "$CONTEXT_FILE"
    grep 'focus_areas:' "$USER_PROFILE" >> "$CONTEXT_FILE"
    grep 'evidence_threshold:' "$USER_PROFILE" >> "$CONTEXT_FILE"
    echo "" >> "$CONTEXT_FILE"
  fi

  LINES=$(wc -l < "$CONTEXT_FILE" | tr -d ' ')
  echo "  ✅ ${div}: lead-context-${div}.md (${LINES}줄)"
done

echo ""
echo "=== 완료 ==="
echo "Lead 스폰 시 각 Lead에게 다음을 전달하세요:"
echo "  '{project}/lead-context-{division}.md를 읽고 Phase 1 리서치를 시작하라.'"
echo ""
echo "이 파일 하나로 프로토콜, 도메인, Brief가 모두 포함됩니다."
echo "상세가 필요하면 원본 파일을 추가로 Read할 수 있습니다."
