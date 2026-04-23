#!/bin/bash
# init-project.sh — 새 리서치 프로젝트 디렉토리 스캐폴딩
#
# 사용법:
#   ./scripts/init-project.sh <project-name> [options]
#
# 옵션:
#   --all                        모든 Division (핵심 4 + 확장 3) 스캐폴딩
#   --divisions "div1,div2,..."  특정 확장 Division만 추가 (people-org, operations, regulatory)
#
# 예시:
#   ./scripts/init-project.sh my-research                         # 핵심 4개
#   ./scripts/init-project.sh my-research --all                   # 전체 7개
#   ./scripts/init-project.sh my-research --divisions "people-org,regulatory"  # 핵심 4 + 선택 2

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# === Division 정의 ===
CORE_DIVISIONS=("market" "product" "capability" "finance")
EXTENDED_DIVISIONS=("people-org" "operations" "regulatory")

# === 인자 파싱 ===
PROJECT=""
USE_ALL=false
EXTRA_DIVISIONS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      USE_ALL=true
      shift
      ;;
    --divisions)
      if [[ -z "${2:-}" ]]; then
        echo "오류: --divisions 뒤에 Division 목록이 필요합니다."
        exit 1
      fi
      IFS=',' read -ra EXTRA_DIVISIONS <<< "$2"
      shift 2
      ;;
    --*)
      echo "알 수 없는 옵션: $1"
      echo ""
      echo "사용법: ./scripts/init-project.sh <project-name> [options]"
      echo "옵션:"
      echo "  --all                        모든 Division (핵심 4 + 확장 3) 스캐폴딩"
      echo "  --divisions \"div1,div2,...\"  특정 확장 Division만 추가 (people-org, operations, regulatory)"
      exit 1
      ;;
    *)
      if [[ -z "$PROJECT" ]]; then
        PROJECT="$1"
      else
        echo "오류: 프로젝트명이 이미 지정되었습니다: $PROJECT"
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ -z "$PROJECT" ]]; then
  echo "사용법: ./scripts/init-project.sh <project-name> [options]"
  echo ""
  echo "옵션:"
  echo "  --all                        모든 Division (핵심 4 + 확장 3) 스캐폴딩"
  echo "  --divisions \"div1,div2,...\"  특정 확장 Division만 추가 (people-org, operations, regulatory)"
  echo ""
  echo "예시:"
  echo "  ./scripts/init-project.sh my-research                                      # 핵심 4개"
  echo "  ./scripts/init-project.sh my-research --all                                # 전체 7개"
  echo "  ./scripts/init-project.sh my-research --divisions \"people-org,regulatory\"  # 핵심 4 + 선택 2"
  exit 1
fi

PROJECT_DIR="${REPO_DIR}/${PROJECT}"

# === 활성 Division 목록 결정 ===
ACTIVE_DIVISIONS=("${CORE_DIVISIONS[@]}")

if [[ "$USE_ALL" == true ]]; then
  ACTIVE_DIVISIONS+=("${EXTENDED_DIVISIONS[@]}")
elif [[ ${#EXTRA_DIVISIONS[@]} -gt 0 ]]; then
  # 확장 Division 유효성 검증
  for div in "${EXTRA_DIVISIONS[@]}"; do
    # 공백 제거
    div="$(echo "$div" | xargs)"
    valid=false
    for ext in "${EXTENDED_DIVISIONS[@]}"; do
      if [[ "$div" == "$ext" ]]; then
        valid=true
        break
      fi
    done
    if [[ "$valid" == false ]]; then
      echo "오류: '$div'은(는) 유효한 확장 Division이 아닙니다."
      echo "사용 가능한 확장 Division: ${EXTENDED_DIVISIONS[*]}"
      exit 1
    fi
    ACTIVE_DIVISIONS+=("$div")
  done
fi

# --- 이미 존재하는지 확인 ---
if [ -d "$PROJECT_DIR" ]; then
  echo "⚠ 프로젝트 '${PROJECT}'가 이미 존재합니다: ${PROJECT_DIR}"
  read -r -p "덮어쓰지 않고 빠진 디렉토리만 추가할까요? [Y/n]: " choice
  case "$choice" in
    [nN]) echo "중단합니다."; exit 1 ;;
  esac
fi

echo "=== 프로젝트 '${PROJECT}' 스캐폴딩 시작 ==="
echo "  활성 Division: ${ACTIVE_DIVISIONS[*]}"

# --- 공통 디렉토리 생성 ---
mkdir -p "${PROJECT_DIR}"/{division-briefs,sync,thinking-loop,reports,qa,learnings,data/{user-provided},agents}

# --- Division별 디렉토리 생성 ---
for div in "${ACTIVE_DIVISIONS[@]}"; do
  # findings 하위 디렉토리
  if [[ "$div" == "market" ]]; then
    # market은 하위 세분화 디렉토리 포함
    mkdir -p "${PROJECT_DIR}/findings/market"/{geography,genre,platform,competitive}
  else
    mkdir -p "${PROJECT_DIR}/findings/$div"
  fi

  # data/processed 하위 디렉토리
  mkdir -p "${PROJECT_DIR}/data/processed/$div"

  # division-briefs 빈 파일 생성 (존재하지 않는 경우만)
  if [ ! -f "${PROJECT_DIR}/division-briefs/${div}.md" ]; then
    cat > "${PROJECT_DIR}/division-briefs/${div}.md" << BRIEF_EOF
# Division Brief — ${div}

## Decision Context
<!-- research-pm이 Decision Frame에서 자동 주입 -->
<!-- 이 Division이 답해야 할 의사결정과 그에 필요한 핵심 근거를 기술 -->

## 검증 대상 가설
<!-- Phase 0.5에서 hypotheses.yaml 기반으로 자동 주입됨 -->

## 분석 지시


## 초점 영역


## 데이터 소스 우선순위


## 산출물 기대치
<!-- 이 Division의 findings가 어떤 형태로 활용되는지 (go/no-go 근거, 비교 근거, 리스크 근거) -->

BRIEF_EOF
  fi
done

echo "  ✅ 디렉토리 트리 + division-briefs 생성 완료"

# --- 템플릿 파일 생성 (존재하지 않는 경우만) ---

# Feasibility Gate 템플릿
if [ ! -f "${PROJECT_DIR}/00-feasibility-gate.md" ]; then
  cat > "${PROJECT_DIR}/00-feasibility-gate.md" << 'FGATE'
# Feasibility Gate

## 판정
- verdict: GO | CONDITIONAL | SCOPE_CHANGE
- decision_type: go_no_go | strategic_choice | exploration

## 데이터 접근성
-

## 의사결정 타입
-

## 실행 가능성
- execution_owner:
- implementation_playbook_needed: true | false

## 시간 제약
- deadline:
- recommended_mode: auto | interactive | team

## Scope 조정 (해당 시)
-
FGATE
  echo "  ✅ Feasibility Gate 템플릿 생성"
fi

# Client Brief 템플릿
if [ ! -f "${PROJECT_DIR}/00-client-brief.md" ]; then
  cat > "${PROJECT_DIR}/00-client-brief.md" << 'TEMPLATE'
# Client Brief

> **프로젝트**: {project-name}
> **날짜**: YYYY-MM-DD
> **모드**: auto | interactive | team

## 핵심 리서치 질문

(Phase 0 Discovery에서 채워짐)

## 의사결정 컨텍스트

- **최종 의사결정**:
- **최종 소비자**:
- **검토 중인 방향**:
- **제외 방향**:

## 제약조건

- **예산**:
- **인력**:
- **타임라인**:

## 성공 기준

## 제공 데이터

TEMPLATE
  echo "  ✅ 00-client-brief.md (템플릿)"
fi

# Research Plan 템플릿
if [ ! -f "${PROJECT_DIR}/01-research-plan.md" ]; then
  cat > "${PROJECT_DIR}/01-research-plan.md" << 'TEMPLATE'
# Research Plan

> **프로젝트**: {project-name}
> **핵심 질문**:
> **모드**: auto | interactive | team

## Division 배치

(Phase 0-B에서 채워짐)

## 프레임워크 선택

## 에이전트 로스터

## 제약사항

TEMPLATE
  echo "  ✅ 01-research-plan.md (템플릿)"
fi

# hypotheses.yaml 템플릿
if [ ! -f "${PROJECT_DIR}/hypotheses.yaml" ]; then
  cat > "${PROJECT_DIR}/hypotheses.yaml" << 'TEMPLATE'
# 전략 가설 목록 — Phase 0.5에서 생성
# PM이 Quick Scan 결과를 합성하여 작성

project: {project-name}
phase: "0.5-hypothesis"
status: pending  # pending | user_review | confirmed

hypotheses: []
  # - id: H-01
  #   statement: "가설 1문장"
  #   type: opportunity | risk | assumption
  #   supporting_signals: []
  #   counter_signals: []
  #   verification_plan: []
  #   priority: must | should | nice
  #   verdict: pending | confirmed | revised | rejected

primary_data_gaps: []
  # - question: "공개 데이터로 답할 수 없는 질문"
  #   why_needed: "이 답이 없으면 어떤 가설이 검증 불가한지"
  #   ideal_source: "이상적 데이터 소스"
  #   fallback: "대안 접근법"
  #   impact_if_missing: high | medium | low

TEMPLATE
  echo "  ✅ hypotheses.yaml (템플릿)"
fi

# golden-facts.yaml 초기화 (#9)
if [ ! -f "${PROJECT_DIR}/findings/golden-facts.yaml" ]; then
  cat > "${PROJECT_DIR}/findings/golden-facts.yaml" << TEMPLATE
# golden-facts.yaml — 수치의 단일 진실 소스 (SSOT)
# 수정: fact-verifier만 수정 가능. 다른 에이전트는 읽기 전용.
# 보고서의 모든 수치는 [GF-###] 태그로 이 파일을 참조해야 함.

project: ${PROJECT}
last_verified: null
verified_by: null

facts: []
  # - id: GF-001
  #   category: "company-basic | market-size | financials | growth-rate | competitive"
  #   entity: "대상 엔터티명"
  #   entity_label: "[그룹] | [별도] | [부문]"
  #   metric: "지표명"
  #   value: 0
  #   unit: "단위"
  #   as_of: "YYYY | YYYY-QN"
  #   source_id: S##
  #   source_detail: "소스 상세 설명"
  #   confidence: "[확정] | [유력] | [가정] | [미확인]"
TEMPLATE
  echo "  ✅ findings/golden-facts.yaml (초기화)"
fi

# checkpoint.yaml 초기화
if [ ! -f "${PROJECT_DIR}/findings/checkpoint.yaml" ]; then
  cat > "${PROJECT_DIR}/findings/checkpoint.yaml" << TEMPLATE
project: ${PROJECT}
mode: pending
last_updated: $(date -u +"%Y-%m-%dT%H:%M:%S")

current_phase: "not-started"
current_status: pending

phases_completed: []
user_decisions: []
pending_escalations: []
backtracks: []
TEMPLATE
  echo "  ✅ findings/checkpoint.yaml (초기화)"
fi

# user-profile.yaml 초기화 (사용자 프로파일 SSOT)
if [ ! -f "${PROJECT_DIR}/user-profile.yaml" ]; then
  cat > "${PROJECT_DIR}/user-profile.yaml" << TEMPLATE
# 사용자 프로파일 — Phase 0에서 수집, Phase별 갱신
# PM이 관리하는 SSOT. Division Brief, compile-lead-context에서 참조.

domain_expertise:
  level: null          # expert | intermediate | novice
  focus_areas: []
  experience_summary: null
  previous_attempts: null

decision_context:
  role: null           # executor | decision_maker | reporter
  stakeholders: []
  implementation_capacity: null  # high | medium | low

risk_profile:
  tolerance: null      # aggressive | balanced | conservative
  key_constraints: []
  available_resources: null

evidence_threshold: null   # 어떤 근거면 결정을 바꾸는가
preferred_direction: null  # 이미 기운 방향 (편향 보정용)

# 갱신 이력
updates:
  - phase: "not-yet"
    updated_at: null
    changed_fields: []
TEMPLATE
  echo "  ✅ user-profile.yaml (초기화)"
fi

# execution-trace.yaml 초기화
if [ ! -f "${PROJECT_DIR}/findings/execution-trace.yaml" ]; then
  cat > "${PROJECT_DIR}/findings/execution-trace.yaml" << TEMPLATE
project: ${PROJECT}
created_at: $(date -u +"%Y-%m-%dT%H:%M:%S")

traces: []
TEMPLATE
  echo "  ✅ findings/execution-trace.yaml (초기화)"
fi

# sync/tension-resolution.yaml 초기화
if [ ! -f "${PROJECT_DIR}/sync/tension-resolution.yaml" ]; then
  cat > "${PROJECT_DIR}/sync/tension-resolution.yaml" << TEMPLATE
# tension-resolution.yaml — Division 간 긴장 해소 기록
# Sync Round 2에서 PM이 관리

project: ${PROJECT}

# v4.12: 스키마 통일 — \`tensions\`가 정본 (tension-resolution-rubric.md)
# 역호환: \`tension_resolution\` 키도 insight-synthesizer가 읽을 수 있음
tensions: []
  # - id: T-01
  #   type: 수치 모순 | 전망 모순 | 해석 모순 | 전제 모순 | 범위 모순
  #   divisions: [market, finance]
  #   description: "긴장 내용"
  #   resolution:                       # v4.12 rubric 적용
  #     verdict: a | b | c | d | e | unresolved
  #     winner: market | finance | both | neither
  #     applied_rule: "엔터티 라벨 일치 | 소스 강도 | 최신성 | 사용자 의도 | 양측 병기"
  #     rationale: "..."
  #     report_treatment: "단일 채택 | 각주 | 리스크 섹션 | 미해결 불확실성"
TEMPLATE
  echo "  ✅ sync/tension-resolution.yaml (초기화)"
fi

# data-registry.csv 초기화
if [ ! -f "${PROJECT_DIR}/data/data-registry.csv" ]; then
  echo "data_id,name,type,source,format,file_path,description,usage,collected_by,date,reliability,url,notes" > "${PROJECT_DIR}/data/data-registry.csv"
  echo "  ✅ data/data-registry.csv (초기화)"
fi

# API 쿼터 초기화
if [ ! -f "${PROJECT_DIR}/data/api-quota.yaml" ]; then
  cat > "${PROJECT_DIR}/data/api-quota.yaml" << 'QUOTA_EOF'
# API 일일 쿼터 관리 (api-caller.py에서 자동 갱신)
dart:
  daily_limit: 10000
  used_today: 0
  reset_at: ""
exa:
  daily_limit: 1000
  used_today: 0
  reset_at: ""
newsapi:
  daily_limit: 100
  used_today: 0
  reset_at: ""
fred:
  daily_limit: 120
  used_today: 0
  reset_at: ""
ecos:
  daily_limit: 1000
  used_today: 0
  reset_at: ""
steam:
  daily_limit: 100000
  used_today: 0
  reset_at: ""
QUOTA_EOF
  echo "  ✅ API 쿼터 파일 생성"
fi

# ARCHITECTURE.md 템플릿
if [ ! -f "${PROJECT_DIR}/ARCHITECTURE.md" ]; then
  cat > "${PROJECT_DIR}/ARCHITECTURE.md" << 'TEMPLATE'
# ARCHITECTURE — {project-name}

## 에이전트 토폴로지

(Phase 0-B에서 PM이 작성)

## EP 패턴 매핑

(프로젝트별 주의 EP 패턴)

## 데이터 소스 배분

(Division별 주요 데이터 소스)

TEMPLATE
  echo "  ✅ ARCHITECTURE.md (템플릿)"
fi

echo ""
echo "=== 스캐폴딩 완료 ==="
echo ""
echo "디렉토리 구조:"
find "${PROJECT_DIR}" -type d | sed "s|${REPO_DIR}/||" | head -30
echo ""
echo "다음 단계:"
echo "  1. PM CLI에서: /research interactive ${PROJECT} 주제"
echo "  2. 또는 내부 데이터가 있으면: ${PROJECT}/data/user-provided/ 에 복사 후 시작"
echo ""
