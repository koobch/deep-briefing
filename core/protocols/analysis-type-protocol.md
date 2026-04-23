# Analysis Type Protocol (v4.11)

> 리서치 주제의 성격에 따라 Phase 0.5/1 흐름을 분기하는 프로토콜.
> 가설 중심 편향을 해소하고 기초 전방위 조사(baseline coverage)를 보장한다.

## 1. 배경 (Why)

v4.10까지 모든 리서치는 **Phase 0.5 가설 도출 → Division Brief의 `verification_plan` 주입** 경로로 수행되었다. 결과적으로:

- "네이버웹툰 분석" 같은 **기업·시장 프로파일** 요청에도 가설 검증 중심 파이프라인이 돌아
- 시장 규모, 실적 추이, IP 활용, 인력 구성 같은 **기초 조사 항목**이 "가설과 관련되지 않음"으로 스킵되는 일이 발생.

v4.11은 주제의 성격을 **4가지 analysis_type**으로 분류하고, 타입별로 Phase 0.5 가설 강제성과 Division Brief 구성을 다르게 적용한다.

## 2. Analysis Type 정의 (4가지)

| Type | 용도 | Phase 0.5 가설 | Division Brief 구성 | 전형적 주제 |
|------|------|---------------|--------------------|-----------|
| **decision** | 의사결정 지원 (진출 여부, M&A, 투자) | **필수** 3~5개 | `verification_plan` 중심 | "AI 사업 진출해야 할까?", "M&A 타당성", "2026 예산 배분" |
| **profile** | 기업·시장 전방위 스터디 | **선택적** 0~2개 | **`baseline_coverage` 의무** + `verification_plan` 보조 | "네이버웹툰 분석", "국내 핀테크 시장 개관", "경쟁사 A 프로파일" |
| **exploration** | 기회 탐색·트렌드 감지 | **후보** 5~8개 (Phase 1 중 확정) | 탐색 공간 광범위 + 약한 초점 | "최근 게임 AI 트렌드", "신성장 동력", "떠오르는 기술" |
| **monitoring** | 주기적 지표 업데이트 | 불필요 | **고정 지표 목록** + 최소 Division Brief | "분기별 시장 동향", "월간 경쟁사 업데이트", "주간 지표" |

### 2.1 decision (기본값, 역호환)

- v4.10과 동일한 경로. Phase 0.5에서 가설 3~5개 도출 필수.
- Division Brief의 `verification_plan`에 가설 검증 과제 주입.
- `analysis_type` 미지정 프로젝트는 **자동 decision**으로 판정(역호환).

### 2.2 profile (신규, 전방위 기초 조사)

- Phase 0.5에서 **baseline_coverage 주입이 주목적**. 가설은 부차적.
- Division Brief의 `baseline_coverage` 필드가 필수 영역 리스트를 명시.
- 기업 분석(`entity_type: company`)일 때 추가 커버리지 자동 포함.
- Leaf는 `baseline_coverage`를 먼저 수행, `verification_plan`은 보조로 처리.

### 2.3 exploration (신규, 탐색)

- 가설이 "후보"로 존재. Phase 1 진행 중 데이터로 확정·기각.
- Quick Scan 범위 확대 (30분 → 60분 권장).
- Division Brief의 `exploration_space`에 탐색 키워드·영역 명시.
- Phase 3 사고 루프에서 "후보 가설 → 확정 가설" 전환 판정.

### 2.4 monitoring (신규, 지속 관찰)

- Phase 0.5 가설 생략. 대신 **지표 목록 + 수집 주기** 확정.
- Division Brief 최소화 (지표별 데이터 소스만).
- Phase 2/3 사고 루프 대폭 축약 (변화 탐지·이상치만).
- 동일 스키마로 반복 실행 가능 → `{project}-YYYY-QN` 형태로 누적.

## 3. PM 판정 — 가중치 룰 (v4.11 Round 1 보정, research-pm:471-489 정본)

PM은 Phase 0-A.6에서 주제를 **가중치 룰**로 점수 계산 후 최고 점수 타입을 후보로 선정한다.
단순 키워드 매칭이 아니며, 한국어 경계 케이스 오분류 방지를 위한 설계이다.

**실행 순서**:
1. **Step 0-A.6-1**: CLI `--type` 플래그 우선 파싱. 있으면 휴리스틱 생략.
2. **Step 0-A.6-2**: 가중치 휴리스틱 판정 (아래 룰)

### 가중치 룰

```
━━ profile 점수 ━━ (기업·시장 전방위 스터디)
  +3: 특정 기업/제품 고유명사 (예: 네이버웹툰, Meta, 테슬라)
  +3: "분석", "프로파일", "현황", "개관", "비교", "파악"
  +2: "전략", "포지션", "사업 구조", "IP 활용", "조직"
  +1: "경쟁사", "플레이어"

━━ decision 점수 ━━ (의사결정 지원)
  +3: "~할까?", "~해야 하나?", "~해야 할까", "할지 말지"
  +3: "진출", "투자", "M&A", "인수", "합병", "철수"
  +2: "결정", "선택", "타당성"
  +1: "검토"

━━ exploration 점수 ━━ (기회 탐색·트렌드)
  +3: "트렌드", "신성장", "떠오르는", "차세대", "emerging"
  +3: "기회", "발굴", "탐색", "전망"
  +2: "최근", "앞으로", "2026", "2030", "미래"

━━ monitoring 점수 ━━ (지속 관찰·지표)
  +5: "분기별", "월간", "주간", "매일", "주기적"
  +4: "업데이트", "모니터", "추적", "트래킹", "대시보드"
  +2: "지표", "KPI", "변화"
```

### 판정 규칙

- **단독 최고 점수** → 그 타입으로 판정
- **동률 (2타입+)**: Interactive/Team은 사용자 확인 필수, Auto는 우선순위(monitoring > profile > exploration > decision)
- **모든 점수 ≤ 2**: decision 기본값 + Interactive/Team에서 사용자 확인
- **'분석/프로파일' 키워드 있음 + 고유명사 없음**: profile로 승격 (점수 +2)

### 경계 케이스 예시

- "엔씨소프트 IP 전략" → profile (고유명사 +3 + IP·전략 +2 = 5)
- "2026 게임 시장 전망" → exploration (전망 +3 + 2026 +2 = 5)
- "경쟁사 분석" → profile (분석 +3 + 경쟁사 +1 = 4, 고유명사 없어도 분석으로 승격)
- "클라우드 시장은 어떨까?" → 모호 (모든 점수 ≤ 2) → decision 기본값 + 사용자 확인

### Ambiguous 중간 상태 (v4.12 Issue #9)

최고 점수가 2 이하이거나 2타입+ 동률인 경우:

1. **Interactive/Team**: Research Plan에 `analysis_type: ambiguous`로 임시 기록, 사용자에게 타입 선택 요청 (필수)
2. **Auto**: Research Plan에 `analysis_type: decision`으로 판정하되 `ambiguous_fallback: true` 플래그 기록
   - Phase 5 audience-fit-checker가 이 플래그 존재 시 "타입 판정 확신도 낮음" warning 보고서 메타에 추가
   - 사용자가 보고서 수령 후 다른 타입으로 판정했다면 Phase 5.5 피드백으로 전체 재실행

**Ambiguous 실패 인정**: 어떤 타입으로도 판정 불가한 주제(예: 너무 광범위/비어있음)는 Phase 0-A에서 사용자에게 주제 재정의 요청. Research Plan 단계 진입 금지.

### 3.1 사용자 확인 방식

- **Auto 모드**: PM이 판정 → "이 주제는 `{type}`로 분류했습니다. Phase 0.5를 `{type}` 방식으로 진행합니다." 안내 후 자동 진행
- **Interactive/Team 모드**: PM이 판정 → "이 주제는 `{type}`로 보입니다. 맞나요? (다른 타입으로 변경 가능: decision/profile/exploration/monitoring)" 확인 후 진행
- **CLI 플래그로 명시**: `/research {mode} --type {type} {project} {주제}` → 사용자가 명시한 타입이 판정을 덮어씀

## 4. Baseline Coverage Catalog

**Profile 타입**에서 Division Brief에 자동 주입되는 필수 커버리지. 각 항목은 `baseline_coverage.required=true`로 마킹되어 `verification_plan`보다 우선 실행된다.

### 4.1 핵심 Division (4개)

> **영역명 정본 (v4.11 Round 7 보정)**: 아래 영역명은 각 Leaf의 `baseline_contract.area` 값과 **완전 일치**해야 한다. QA의 Check 9/Step 9.5가 iteration_log의 `baseline_area`와 이 catalog 영역명을 대조한다.

#### Market
| 영역 (정본) | 담당 Leaf | 필수 산출물 |
|------|----------|-----------|
| 시장 정의·규모 | market-sizing | TAM/SAM/SOM + 세분화(지역/세그먼트) + 성장률 5년 |
| 경쟁 구조·주요 플레이어 | competitive-landscape | 플레이어 맵 + 점유율 Top 5 + 진입장벽 |
| 채널 구조 | channel-landscape | 유통 경로 + 비중 + 동향 |
| 고객 세그먼트·JTBD | customer-analysis | Persona 3~5 + JTBD + 규모 |
| 매크로·기술·규제 동인 | market-dynamics | 매크로 트렌드 + 기술 변화 + 규제 영향 |

#### Product
| 영역 (정본) | 담당 Leaf | 필수 산출물 |
|------|----------|-----------|
| 제품·서비스 포트폴리오 | product-offering | 제품/서비스 라인업 + 포지셔닝 |
| 가치 제안·차별화 | value-differentiation | JTBD 매칭 + 차별화 요소 + PMF |
| 수익 모델·가격 | pricing-monetization | 가격 구조 + 수익 단위 + 탄력성 |
| GTM 전략 | go-to-market | 채널·영업·마케팅 믹스 |

#### Capability
| 영역 (정본) | 담당 Leaf | 필수 산출물 |
|------|----------|-----------|
| 기술·IP | technology-ip | R&D 역량 + 특허 + 기술 로드맵 |
| 전략 자산 + 공식 전략·비전 + IP 활용 사례 | strategic-assets | 브랜드 + IP + 데이터 + 파트너십 + 공식 전략 인용 + IP 사례 |
| 인재·조직 역량 | human-capital | 조직 규모 + 핵심 역할 + 스킬 갭 |
| 실행력·변화 수용력 | execution-readiness | 트랙레코드 + 변화 수용력 |

#### Finance
| 영역 (정본) | 담당 Leaf | 필수 산출물 |
|------|----------|-----------|
| 매출 구조·추이 | revenue-growth | 3년 추이 + 부문별 구조 + 성장 동인 |
| 비용 구조·수익성 | cost-efficiency | 원가·판관비 + 단위 경제학 |
| 투자·자본 배분 | investment-returns | CAPEX·OPEX + ROI·IRR |
| 밸류에이션·리스크 | valuation-risk | 가치 평가 + 민감도 + 시나리오 |

### 4.2 확장 Division (활성화 시)

#### People & Org
| 영역 (정본) | 담당 Leaf | 필수 산출물 |
|------|----------|-----------|
| 조직 구조·거버넌스 | org-design | 조직도 + 거버넌스 + 의사결정 체계 |
| 인재 전략 | talent-strategy | 확보/유지/육성/보상 |
| 조직 문화·몰입 | culture-engagement | 문화 지표 + 몰입도 + 변화 수용력 |

#### Operations
| 영역 (정본) | 담당 Leaf | 필수 산출물 |
|------|----------|-----------|
| 핵심 프로세스·효율성 | process-excellence | 핵심 프로세스 + 효율성 + 자동화 |
| 공급망 구조·리스크 | supply-chain | 소싱·물류·리스크 |
| 기술·물리 인프라 | infrastructure | 기술·물리 인프라 + 확장성 |

#### Regulatory
| 영역 (정본) | 담당 Leaf | 필수 산출물 |
|------|----------|-----------|
| 적용 규제·준수 현황 | compliance-status | 적용 규제 + 준수 현황 + 위반 리스크 |
| 규제 전망·대응 | regulatory-outlook | 입법 동향 + 정책 변화 + 대응 |
| ESG·지배구조 | esg-governance | ESG 성과 + 지배구조 + 공시 |

### 4.3 기업 Profile 특화 추가 (entity_type=company 시)

- **실적 추이 (3년+)** — revenue-growth 확장
- **공식 전략·비전** — strategic-assets (IR, 연차보고서, CEO 발표)
- **IP/자산 활용 사례** — strategic-assets (라이선싱, 미디어 믹스 사례 3+)
- **채널·유통 구조** — channel-landscape (자체 플랫폼, 파트너 채널, B2B/B2C)
- **주요 경쟁사 비교** — competitive-landscape (Top 3 정량 비교)

### 4.4 시장·제품·지역 Profile 특화 추가 (company 외 entity_type)

> **구현 주의 (v4.11 3회차 보정)**: 각 Leaf의 `baseline_contract`는 `company_profile_addons` 필드를 사용하지만,
> `entity_type=market`/`product`/`region` 프로젝트에서는 PM이 Division Brief 작성 시 이 §4.4 항목을
> `baseline_coverage` 리스트에 직접 주입해야 한다. Leaf contract의 `company_profile_addons` 필드명은
> 역호환을 위해 유지되며, 실제 의미는 **"entity_type별 추가 산출물"**이다 (필드명 리팩토링은 v4.12에서).

#### 4.4.1 entity_type=market

- **시장 라이프사이클** — market-dynamics (도입·성장·성숙·쇠퇴 단계 판정)
- **세부 카테고리 breakdown** — market-sizing (상위 5개 세그먼트 규모 + CAGR)
- **시장 구조적 변화** — market-dynamics (통합/분화, 플랫폼화, 규제 변화)
- **Top 10 플레이어 지도** — competitive-landscape (점유율 + 전략 포지션)
- **주요 수요 드라이버** — customer-analysis (3~5개 세그먼트 각 JTBD)

#### 4.4.2 entity_type=product

- **제품 카테고리 정의** — product-offering (기능 분류, 대체재, 보완재)
- **사용자 적합도** — customer-analysis (타겟 Persona 3~5)
- **가격 포지션** — pricing-monetization (경쟁 제품 대비 가격 분포)
- **주요 유사 제품 비교** — competitive-landscape (기능·가격·시장성 비교 표)
- **기술 성숙도** — technology-ip (R&D 수준, 특허 현황)

#### 4.4.3 entity_type=region

- **지역 시장 규모·성장** — market-sizing (해당 지역 TAM + CAGR)
- **지역 고객 특성** — customer-analysis (문화·언어·구매력 세분화)
- **지역 경쟁 구도** — competitive-landscape (로컬 플레이어 vs 글로벌)
- **진입 규제·장벽** — regulatory-outlook / compliance-status
- **채널·유통 특성** — channel-landscape (지역 특화 채널)

### 4.4 타입별 baseline_coverage 주입 규칙

| Type | 주입 범위 |
|------|----------|
| decision | 없음 (기존 verification_plan 중심) |
| **profile** | **활성 Division 전체 baseline** + 기업 특화 항목 (company인 경우) |
| exploration | 핵심 4 Division의 "시장 정의·규모" + "경쟁 구조"만 (광범위 탐색을 위한 최소 기준선) |
| monitoring | 지표 목록에서 직접 도출 (catalog 참조하지 않음) |

## 5. Division Brief 스펙 확장

Division Brief YAML 스키마에 다음 필드 추가:

```yaml
# 기존 필드 (유지)
division: market
user_context: {...}
primary_data_gaps: [...]
verification_plan:             # 가설 검증 과제 (decision/profile 보조)
  - hypothesis_id: H-01
    verification_tasks: [...]

# 신규 필드 (v4.11)
analysis_type: decision | profile | exploration | monitoring
baseline_coverage:             # 필수 커버리지 (profile/exploration에서 의무)
  - area: "시장 정의·규모"
    required: true
    leaf: market-sizing
    deliverables:
      - "TAM/SAM/SOM 산출"
      - "지역/세그먼트 세분화"
      - "5년 성장률 + 동인"
    reference: "core/protocols/analysis-type-protocol.md#4-1-market"

entity_target:                 # profile 타입에서 기업/시장 특화 분석 대상
  type: company | market | product | region
  name: "네이버웹툰"
  scope: "글로벌 웹툰 시장에서의 네이버웹툰 포지션"

exploration_space:             # exploration 타입에서 탐색 공간 정의
  keywords: [...]
  time_horizon: "2026-2028"
  signal_types: ["기술 변화", "규제", "소비자 행동"]

monitoring_metrics:            # monitoring 타입에서 추적 지표
  - metric: "국내 웹툰 시장 MAU"
    source: "data.ai, Sensor Tower"
    frequency: "monthly"
```

### 5.1 실행 우선순위

Division Lead가 Leaf를 스폰할 때:

1. **baseline_coverage.required=true** 항목을 먼저 배치 (필수 커버리지)
2. **verification_plan** 과제를 다음으로 배치 (가설 검증)
3. **exploration_space** 탐색 (exploration 타입)
4. **cross-domain** 교차 주제 (다른 Division의 질문에 응답)

## 6. Phase 0.5 분기 로직

```
Phase 0.5-A: Quick Scan (모든 타입 공통)
  ├─ 활성 Division 각자 30~60분 병렬
  └─ 산출: quick-scan.yaml (headlines + Top 3 기회/위협)

Phase 0.5-B: 타입별 분기
  ├─ decision:   가설 3~5개 확정 → verification_plan 주입
  ├─ profile:    baseline_coverage catalog에서 활성 Division 전체 항목 주입
  │              + (선택) 가설 0~2개 보강
  │              + entity_target 명시 (기업/시장/제품 특정)
  ├─ exploration: 가설 "후보" 5~8개 + exploration_space 정의
  │              + Phase 1 중 확정 판정 가이드라인
  └─ monitoring: 지표 목록 + 수집 주기 확정 (Division Brief 최소화)

Phase 0.5 완료 게이트: 타입별 조건
  ├─ decision:   [ ] 가설 3~5개 도출  [ ] 사용자 정렬  [ ] verification_plan 주입
  ├─ profile:    [ ] baseline_coverage 주입  [ ] entity_target 명시  [ ] (선택) 가설 정렬
  ├─ exploration: [ ] 후보 가설 리스트  [ ] 탐색 공간 정의  [ ] 확정 기준 명시
  └─ monitoring: [ ] 지표 목록 확정  [ ] 수집 주기 확정  [ ] 변화 임계값 설정
```

## 7. QA 연계

**audience-fit-checker** 보강: analysis_type에 맞는 보고서 구조 확인

- decision: Exec Summary에 Answer(Go/No-Go) + Confidence + Risk if Wrong 필수
- profile: baseline_coverage 항목 전체가 보고서 본문에 반영되었는지 검증
- exploration: 후보 가설 → 확정 가설 전환 이력 명시
- monitoring: 지표별 현황 + 변화 방향 + 이상치 명시

**report-auditor** 보강: baseline_coverage 미준수를 Major 이슈로 감지 (profile 타입).

## 8. 역호환성

- `analysis_type` 필드 **없으면 자동 decision**으로 간주 (v4.10 동작 유지)
- `baseline_coverage` 필드는 optional (decision에서 비어 있음)
- 기존 `verification_plan` 경로 완전 보존
- 기존 프로젝트 재실행 시 수정 불필요

## 8.5 실행 모델 — "에이전트 프롬프트 기반" (v4.11 명시)

### 주입 책임자

deep-briefing은 **에이전트 프롬프트 + 스크립트 자동화 병행** 시스템이다.
- 스크립트는 **인프라 오케스트레이션**을 담당: 환경 점검(`check-env.sh`), Lead 스폰(`spawn-leads.sh`), Phase 지시 전송(`send-phase2.sh`), 컨텍스트 컴파일(`compile-lead-context.sh`), 외부 API 호출(`api-caller.py`), fact 검증(`verify-facts.py`) 등
- **`analysis_type` 판정, `baseline_coverage` 주입, `--type` 플래그 해석**은 **에이전트(Claude)가 프롬프트 수준에서 수행**한다 — 이 부분은 스크립트 엔트리포인트가 없다.
- 스크립트는 에이전트가 생성한 파일(Division Brief, hypotheses.yaml 등)을 운반·실행하는 역할.

| 책임 | 수행 주체 | 시점 |
|------|----------|------|
| `analysis_type` 판정 | `research-pm` 에이전트 | Phase 0-A.6 (Step 0-A.6) |
| `baseline_coverage` catalog 조회 | `research-pm` 에이전트 | Phase 0.5-D (타입별 분기 단계) |
| `baseline_coverage` Division Brief 주입 | `research-pm` 에이전트 | Phase 0.5-D (Division Briefs 작성 시) |
| `--type` 플래그 해석 | `research-pm` 에이전트 | Phase 0-A.6 (판정보다 우선) |
| Leaf의 `baseline_contract` 준수 | 각 Leaf 에이전트 | Phase 1 실행 중 |

### CLI 플래그 파싱 방식

`/research auto --type profile 네이버웹툰 분석` 같은 명령은:
1. Claude Code의 `/research` 슬래시 커맨드가 인수 문자열을 research-pm에 전달
2. `research-pm`가 문자열에서 `--type {value}` 패턴을 **프롬프트 수준에서 파싱**
3. 파싱된 타입이 있으면 휴리스틱 판정을 덮어씀
4. 없으면 주제 키워드 기반 휴리스틱 판정 (Step 0-A.6)

**핵심**: 별도 스크립트 엔트리포인트 불필요. PM 프롬프트가 CLI를 해석한다.

### baseline_coverage catalog 조회 절차 (research-pm 수행)

```
Phase 0.5-D 실행 시:

1. Research Plan의 analysis_type 확인
2. analysis_type이 profile 또는 exploration이면:
   a. core/protocols/analysis-type-protocol.md §4 Baseline Coverage Catalog 참조
   b. 활성 Division 각각에 대해 catalog의 해당 Division 항목 전부 수집
   c. entity_target.type에 맞는 추가 항목 포함:
      - company: §4.3 기업 Profile 특화 추가
      - market: §4.4.1 시장 Profile 특화 추가
      - product: §4.4.2 제품 Profile 특화 추가
      - region: §4.4.3 지역 Profile 특화 추가
   d. 수집된 항목을 각 Division Brief의 baseline_coverage YAML 리스트로 작성
3. analysis_type이 monitoring이면:
   a. monitoring_metrics 리스트를 직접 정의 (catalog 참조 생략)
4. analysis_type이 decision이면:
   a. baseline_coverage 필드 생략 (기존 verification_plan 경로)
```

## 9. 구현 참조

| 파일 | 역할 |
|------|------|
| `.claude/agents/research-pm.md` | analysis_type 판정 + Research Plan 스키마 |
| `.claude/skills/research/phase-0-discovery.md` | Phase 0.5 타입별 분기 실행 |
| `.claude/skills/research/phase-1-parallel.md` | Division Brief 스키마 + 주입 로직 |
| `.claude/agents/{division}-lead.md` | baseline_coverage 체크 단계 |
| `.claude/agents/leaves/**/*.md` | "필수 커버리지" 헤더 (analysis_type 무관) |
| `core/knowledge/common-sense.yaml` | "전방위 기초 조사" 원칙 |

## 10. 변경 이력

- **v4.11 (2026-04-22)**: 프로토콜 신규. 4-Type Analysis Taxonomy 도입.
