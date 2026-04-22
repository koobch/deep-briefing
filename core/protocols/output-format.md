# 표준 출력 포맷 (Standard Output Format)

> 모든 에이전트가 준수하는 유일한 출력 규격.
> 이 포맷을 따르지 않는 출력은 상위 에이전트가 반려한다.

## 설계 원칙

1. **Progressive Disclosure** — 상위 에이전트는 Layer 0만 읽어도 전체 그림 파악 가능
2. **Self-descriptive** — 출력만 보고 맥락, 근거, 원본까지 추적 가능
3. **Machine-parseable** — YAML 구조로 프로그래매틱 처리 가능
4. **Drillable** — 어떤 레이어에서든 하위 레이어로 즉시 드릴다운 가능

## 4-Layer 피라미드 구조

```
Layer 0: Claim (한 문장 — 결론)
Layer 1: Evidence (1~3개 근거 — 각 1문단 + 소스)
Layer 2: Data (구조화된 상세 데이터 — YAML/CSV 파일 레퍼런스)
Layer 3: Raw Source (원본 URL, API 응답, 스크린샷)
```

### 계층별 용도

| Layer | 내용 | 주 독자 | 분량 기준 |
|-------|------|--------|----------|
| 0 | 결론 한 문장 | PM, 다른 Division Lead | 1문장 |
| 1 | 근거 1~3개 + 소스 태그 | 상위 Lead, 교차 검증 | 각 근거 1문단 이내 |
| 2 | 상세 데이터, 테이블, 시계열 | 같은 Division 리프, fact-verifier | 파일 단위 |
| 3 | 원본 URL, API 응답, raw CSV | 스팟체크, 감사 시 | 파일/URL 레퍼런스 |

## 표준 출력 스키마

### Leaf Agent 출력

**필수/조건부 필드 구분:**
- ● 필수: 모든 Leaf 출력에 반드시 포함
- ○ 조건부: 해당 상황에서만 작성 (없으면 섹션 자체 생략 가능)

| 섹션 | 필수 | 비고 |
|------|:----:|------|
| META | ● | agent, domain, parent, status, timestamp, iteration |
| LAYER 0: CLAIMS | ● | 최소 1개 Claim |
| LAYER 1: EVIDENCE | ● | 모든 Claim에 대해 supports + disconfirming |
| LAYER 2: DATA | ○ | 상세 데이터 파일이 있는 경우만 |
| LAYER 3: RAW SOURCES | ● | 모든 소스에 대해 source_index |
| CROSS-DOMAIN | ○ | 타 도메인 영향/질문이 있는 경우만 |
| DATA GAPS | ○ | 데이터 공백이 있는 경우만 (없으면 생략) |
| NULL HYPOTHESIS CHECK | ● | Round 1.5 반대 가설 검증 결과 (Leaf 필수) |
| ITERATION LOG | ○ | 자율 반복 2회 이상 시 필수, 1회 완료 시 생략 가능 |

```yaml
# ============================================================
# META
# ============================================================
agent: {agent-id}                    # 예: market-sizing
domain: {division}/{sub-domain}      # 예: market/geography/east-asia
parent: {parent-agent-id}            # 예: market-lead
status: draft | researching | verified | revised
timestamp: YYYY-MM-DD
iteration: {N}                       # 자율 반복 회차

# ============================================================
# LAYER 0: CLAIMS (결론)
# ============================================================
claims:
  - id: {PREFIX}-{##}               # 예: MGE-01 (Market-Geography-EastAsia)
    claim: "한 문장 결론"
    confidence: high | medium | low | unverified
    # EP-026 확신도 등급 매핑:
    #   high = [확정] — 1차 소스 2개+ 교차 검증 완료
    #   medium = [유력] — 1차 소스 1개 + 보조 소스 뒷받침
    #   low = [가정] — 추정/간접 근거 기반. BASE 핵심 전제인 경우 사용자 확인 필수
    #   unverified = [미확인] — 검증 미실시
    strategic_impact: high | medium | low
    # high = 이 Claim이 틀리면 전체 전략 방향이 바뀜
    # medium = 일부 세부 전략에 영향
    # low = 참고 수준

# ============================================================
# LAYER 1: EVIDENCE (근거)
# ============================================================
evidence:
  - claim_id: MGE-01
    supports:
      - id: MGE-01-E1
        summary: "근거 요약 1문단"
        sources: [S01, S03]          # source_index 참조
      - id: MGE-01-E2
        summary: "근거 요약 1문단"
        sources: [S05]
    disconfirming:                   # 반증 — 필수 필드
      - id: MGE-01-D1
        summary: "이 Claim에 반하는 증거 또는 '독립 검토 결과 반증 없음'"
        sources: [S07]
        assessment: "반증의 무게와 이에 대한 판단"

# ============================================================
# LAYER 2: DATA (상세 데이터)
# ============================================================
data_files:
  - file: findings/market/geography/market-sizing-detail.yaml
    description: "지역별 시장 규모, 성장률, 카테고리 분포 상세"
  - file: findings/market/geography/market-sizing-timeline.csv
    description: "주요 시장(아시아/북미/유럽) 연도별 추이 (2020-2025)"

# ============================================================
# LAYER 3: RAW SOURCES
# ============================================================
source_index:
  - id: S01
    type: primary                    # primary | secondary | estimate
    name: "DART {기업명} 사업보고서 2025"
    url: "https://dart.fss.or.kr/..."
    accessed: 2026-03-11
    reliability: high                # high | medium | low
    summary: "핵심 정보 1~2줄 요약"    # Phase 4.5 source-registry 생성 시 사용
  - id: S05
    type: estimate
    name: "업계 리서치 기관 Annual Report 2025"
    url: null                        # 유료 보고서 — URL 없음
    accessed: 2026-03-01
    reliability: medium
    summary: "핵심 정보 1~2줄 요약"    # Phase 4.5 source-registry 생성 시 사용
    note: "추정치 기반. 다른 독립 소스와 교차 검증 필요"

# ============================================================
# CROSS-DOMAIN (타 도메인 연결)
# ============================================================
cross_domain:
  implications:
    - to: {division}/{sub-domain}
      content: "이 발견이 해당 도메인에 미치는 영향"
      related_claim: {CLAIM-ID}
      urgency: must | should | nice  # 반드시 반영 | 반영 권장 | 참고
  questions:
    - to: {division}/{sub-domain}
      content: "해당 도메인에 대한 질문"
      context: "왜 이 질문이 필요한지"
      priority: must | should | nice

# ============================================================
# DATA GAPS (데이터 공백)
# ============================================================
data_gaps:
  - description: "확인할 수 없는 정보"
    impact: "이 데이터가 없으면 어떤 Claim의 confidence가 제한되는지"
    alternative: "대안 접근법 또는 사용자 데이터 요청"
    required_for: {CLAIM-ID}

# ============================================================
# NULL HYPOTHESIS CHECK (반대 가설 검증 — Leaf 필수)
# ============================================================
null_hypothesis_check:
  - claim_id: {CLAIM-ID}
    hypothesis: "원래 가설"
    null_hypothesis: "정반대 가설"
    search_method: "검색 키워드/소스/방법"
    evidence_found: "반대 증거 또는 미발견 상세"
    strength: strong | moderate | weak    # 반대 증거의 강도
    impact: "반대 증거가 원래 가설에 미치는 영향"

# ============================================================
# ITERATION LOG (자율 반복 기록)
# ============================================================
iteration_log:
  - round: 1
    hypothesis: "초기 가설"
    action: "수행한 리서치"
    evidence_found: "발견한 증거 요약"
    verdict: confirmed | revised | rejected | insufficient
    next_action: "다음 라운드에서 할 일 (해당 시)"

    # v4.11 신규 — analysis_type in [profile, exploration] 시 필수
    # 상세: core/protocols/analysis-type-protocol.md#6-phase-0-5-분기-로직
    baseline_area: "담당 baseline 영역 (예: '시장 정의·규모')"    # Leaf의 baseline_contract.area 참조 (catalog §4 정본명과 일치)
    deliverable_status:                                          # 각 required_deliverable의 수행 상태
      "TAM/SAM/SOM 산출": complete | partial | unavailable
      "지역·세그먼트 세분화": complete | partial | unavailable
      # ... (Leaf의 required_deliverables 리스트와 1:1 매칭)
    entity_specific_addons_status:                               # v4.11 Round 7 명칭 변경 (company_profile_addons_status → entity_specific)
      "부문별 매출 breakdown": complete | partial | unavailable  # entity_type=company/market/product/region별 Leaf baseline_contract 참조
      # Leaf의 company_profile_addons 필드는 역호환을 위해 이름 유지 (실제 의미는 entity_specific)
```

### Lead Agent 출력 (Division Lead / Sub-lead)

Leaf 출력 스키마에 다음이 추가된다:

```yaml
# ============================================================
# SYNTHESIS (리프 합성 — Lead 전용)
# ============================================================
synthesis:
  method: "합성 방법론 (매트릭스 교차, 패턴 추출, 가중 평균 등)"
  child_agents: [agent-id-1, agent-id-2, ...]

  # Groupthink 탐지 (Lead 필수)
  groupthink_check:
    leaf_agreement_rate: 0          # Leaf 결론 동일 방향 비율 (0~100%)
    flag: false                     # true = 80%+ 동일 방향 (경고)
    counter_perspective: ""         # flag=true 시: Lead가 서술한 반대 가능성
    rationale: ""                   # flag=true 시: 왜 Leaf들이 같은 방향인지 분석

  # 리프 간 교차 매트릭스 (해당 시)
  matrix:
    dimensions: ["지역", "세그먼트"]
    highlights:
      - cell: "지역A × 세그먼트B"
        finding: "YoY +28%, 가장 빠른 성장 셀"
      - cell: "지역C × 카테고리C"
        finding: "사용자 급증, 수익화는 미성숙"

  # 리프 간 모순 해소 기록
  contradictions_resolved:
    - agents: [agent-id-1, agent-id-2]
      issue: "모순 내용"
      resolution: "해소 방법과 결론"

  # 리프 간 삼각 검증 결과
  triangulation:
    - metric: "국내 시장 규모"
      values:
        - agent: market-sizing
          value: "$8.0B"
          source: S01
        - agent: channel-landscape
          value: "$8.03B"
          source: S12
        - agent: customer-analysis
          value: "$8.0B (세그먼트 합산)"
          source: S05, S06, S07
      verdict: "일치 (범위 내)"

  # 핵심 Claim 스팟체크 결과
  spot_checks:
    - claim_id: MGN-03
      original_agent: {agent-id}
      verifier: market-sizing
      method: "독립 데이터로 역산"
      result: pass | fail | adjusted
      detail: "검증 상세 내용"

# ============================================================
# DIVISION SUMMARY (Division Lead 전용)
# ============================================================
division_summary:
  headline: "Division 전체를 관통하는 핵심 메시지 1문장"
  key_findings:                      # 상위 3~5개
    - claim_id: {ID}
      one_liner: "요약"
  key_tensions:                      # Division 내 해소 안 된 긴장
    - description: "긴장 내용"
      between: [claim-id-1, claim-id-2]
  confidence_summary:
    high: {N}건
    medium: {N}건
    low: {N}건
    unverified: {N}건
```

## ID 체계

```
Claim ID: {Division 약자}{Sub-domain 약자}-{##}

Division 약자:
  M = Market, P = Product, C = Capability, F = Finance
  H = People & Organization, O = Operations, R = Regulatory & Governance

Sub-domain 약자 (예시):
  Market:     GE(Geography-EastAsia), GW(Geography-Western), GM(Geography-eMerging),
              SG(SeGment-core), SC(Segment-Casual/niche),
              CH(CHannel), CD(Competitive-Domestic), CG(Competitive-Global)
  Product:    PS(ProductStrategy), CX(CustomerExperience), BR(BRand-IP), UR(UserResearch)
  Capability: DP(DevPortfolio), TC(Tech), OR(Org), PA(Partnership)
  Finance:    RV(Revenue), IV(Investment)
  People&Org: TS(TalentStrategy), OD(OrgDesign), CC(CultureChange), WA(WorkforceAnalytics)
  Operations: PR(PRocess), SC(SupplyChain), IO(InfraOps), QO(QualityOps)
  Regulatory: LC(LegalCompliance), IL(IPLegal), ES(ESG), PO(POlicy)

예: MGE-01 = Market, Geography, East Asia, Claim #01
    MGM-03 = Market, Geography, Emerging, Claim #03
    MCD-01 = Market, Competitive, Domestic, Claim #01
    PPS-03 = Product, ProductStrategy, Claim #03
    HTS-01 = People&Org, Talent Strategy, Claim #01
    OPR-03 = Operations, Process, Claim #03
    RLC-01 = Regulatory, Legal Compliance, Claim #01
```

## Golden Facts 참조 규칙

### golden-facts.yaml — 수치의 단일 진실 소스 (SSOT)

모든 에이전트가 수치 인용 시 `findings/golden-facts.yaml`에서 직접 참조해야 한다.

```yaml
# findings/golden-facts.yaml
# 규칙: 보고서/인사이트의 모든 수치는 이 파일의 ID를 참조해야 함
# 수정: fact-verifier만 수정 가능. 다른 에이전트는 읽기 전용

last_verified: YYYY-MM-DDTHH:MM:SS
verified_by: "fact-verifier"

facts:
  - id: GF-001
    category: "company-basic | market-size | financials | growth-rate | competitive"
    entity: "대상 엔터티명"
    entity_label: "[그룹] | [별도] | [부문]"  # 해당 시
    metric: "지표명"
    value: 0
    unit: "단위"
    as_of: "YYYY | YYYY-QN"
    source_id: S##                           # source_index 참조
    source_detail: "소스 상세 설명"
    confidence: "[확정] | [유력] | [가정] | [미확인]"  # EP-026
```

### Layer 2 data_files에서의 golden-facts 참조

Lead Agent 또는 report-writer가 Layer 2 (data_files)에서 수치를 참조할 때:

```yaml
data_files:
  - file: findings/golden-facts.yaml
    description: "핵심 수치 SSOT — 보고서 수치 인용 시 [GF-###] 태그 필수"
    referenced_facts: [GF-001, GF-010, GF-020]  # 이 산출물에서 참조하는 GF ID 목록
```

### [GF-###] 태그 사용 규칙

1. **Division Lead synthesis, report-writer 보고서**에서 수치 사용 시 `[GF-###]` 태그 필수
2. **[GF-###] 없이 수치를 서술하면** qa-orchestrator가 반려
3. golden-facts에 없는 수치는 해당 Claim의 source_index `[S##]`로 참조 (기존 규칙 유지)
4. **수정 권한**: fact-verifier만 golden-facts.yaml 수정 가능. 다른 에이전트가 오류 발견 시 fact-verifier에 에스컬레이션

### golden-facts 생성/갱신 시점

| 시점 | 책임자 | 행동 |
|------|--------|------|
| Phase 0.5 (팩트시트) 완료 후 | fact-verifier | 핵심 수치를 golden-facts.yaml에 초기 등록 |
| Phase 1 (Division 리서치 완료) 후 | fact-verifier | 새로 확보된 수치 추가, 기존 수치 업데이트 |
| Sync Round | fact-verifier | VL-3 검증 결과 반영, 오류 수정 |
| 보고서 QA | qa-orchestrator | 보고서 내 모든 수치를 golden-facts.yaml과 대조 |

---

## 드릴다운 규칙

| 상황 | 읽는 레이어 |
|------|------------|
| 기본 (합성, 브리핑) | Layer 0 (Claims) |
| Claim이 놀랍거나 의심스러울 때 | Layer 1 (Evidence) |
| confidence가 medium 이하일 때 | Layer 1 + disconfirming |
| cross_domain question 응답 시 | Layer 2 (Data files) |
| 스팟체크 / 삼각 검증 시 | Layer 2 + Layer 3 (Raw Source) |
| 감사 / QA 시 | Layer 3까지 전체 |

## 유틸리티 에이전트 출력 규칙

data-preprocessor 등 유틸리티 에이전트는 Claim/Evidence 구조 대신 도메인별 출력 포맷을 사용한다.
단, 다음 meta 필드는 동일하게 포함해야 한다:

```yaml
agent: {agent-id}
domain: utility/{function}
status: draft | processing | completed
timestamp: YYYY-MM-DD

output_files:
  - file: {path}
    description: "산출물 설명"
    target_division: {division}    # 이 파일을 사용할 Division

quality_report:
  total_records: {N}
  issues_found: [{이슈 목록}]
  actions_taken: [{처리 내역}]
```

## Action Title 규칙

보고서 섹션 제목은 반드시 **주장 문장(Action Title)**이어야 한다:
- ✗ 금지: 주제형 타이틀 ("시장 규모 분석", "경쟁 현황", "재무 전망")
- ✓ 필수: 주장형 타이틀 ("국내 시장은 연 12% 성장 중이나 수익성은 상위 3사에 집중")
- 섹션 제목만 순서대로 읽으면 보고서의 전체 스토리라인이 완성되어야 한다
- qa-orchestrator의 audience-fit-checker가 주제형 타이틀을 감지하면 반려한다

---

## 세로형 보고서 출력 규칙 (BCG 아티클 패턴 차용)

### 보고서 구조

1. 목차 (장 3개 이상 시)
2. Executive Summary — Golden Insights 5개 + SCR 요약
3. 본문 장별 — 섹션 헤더(주장형) + 데이터 앵커링 + So What
4. Implementation Playbook (해당 시)
5. Appendix / 연구 방법론

### 스토리라인 프레임워크 (SCR + PCS 2계층)

보고서는 **SCR과 PCS를 계층적으로 결합**하여 사용한다:

| 계층 | 프레임 | 적용 범위 | 적용 조건 |
|------|-------|---------|---------|
| **보고서 전체** | SCR (Situation→Complication→Resolution) | Exec Summary + 장 순서 | ✅ 항상 적용 |
| **개별 장 내부** | PCS (Problem→Challenges 3~5개→Solution) | 장별 분석 구조 | 📋 PM이 "도전형" 지정 시 |

- **SCR**: 독자를 "동의→긴장→해결"로 이끄는 설득 흐름. 보고서 전체 스토리라인의 뼈대
- **PCS**: 문제를 구조적으로 분해하여 도전 3~5개를 나열하고 각각에 해결책을 매핑. "기회형" 주제에서는 "기회 3~5개 → 실행 방안"으로 변형
- PM이 Phase 0에서 `issue_type: "도전형"/"기회형"`으로 PCS 적용 여부를 결정

### 작성법 규칙

- **데이터 앵커링**: 문단 → 데이터 포인트 → 해석 → 시사점 3단 구조
- **인라인 KPI**: 문단당 bold 수치 1~2개 (예: "**60%**의 기업이 AI에서 가치를 얻지 못하고 있다")
- **대비 프레이밍**: 주요 주장에 비교군 제시 (예: "선도 기업은 3배 높은 비용 절감 달성")
- **Key Findings**: Exec Summary에 핵심 발견 5개 불릿
- **So What → Now What**: 각 장 말미에 행동 제안

### 조건부 규칙 (PM 판단)

- **Pull Quote**: 경영진 보고서 → `> **"핵심 인사이트"**` 형태로 장 시작에 배치
- **장 전환 문장**: 3장 이상 → "다음 장에서는 [주제]를 분석한다" 형태
- **시나리오 섹션**: 불확실성 높은 주제 → 3-Layer 시나리오 표 포함

---

## 보고서 출처 섹션 포맷 (Source Index)

보고서 말미(부록)에 Source Index 섹션을 포함한다:

```
## Source Index

| ID | 소스명 | 유형 | 시점 | URL | 신뢰도 |
|----|--------|------|------|-----|--------|
| [S01] | DART {기업명} 사업보고서 | primary | 2025 | https://dart.fss.or.kr/... | high |
| [S05] | 업계 리서치 기관 Annual Report | estimate | 2025 | 유료 보고서 | medium |
```

필수 필드: ID, 소스명, 유형(primary/secondary/estimate), 시점, URL(없으면 "유료 보고서"), 신뢰도(high/medium/low)

## 데이터 기밀성 등급

모든 데이터와 보고서에 기밀성 등급을 적용한다:

| 등급 | 설명 | 보고서 처리 규칙 |
|------|------|-----------------|
| `public` | 공개 데이터 (공시, 뉴스, 산업 보고서) | 제한 없이 보고서에 포함 |
| `internal` | 내부 데이터 (사용자 제공, 비공개 매출) | 수치만 표기, 원본 경로 미노출 |
| `confidential` | 기밀 데이터 (M&A, 인사, 미공개 전략) | "[기밀]" 태깅 필수, Executive Summary 사용 시 사용자 확인 |

보고서 상단에 기밀 등급 + 배포 범위 표기:
```
기밀 등급: PUBLIC | INTERNAL | CONFIDENTIAL
배포 범위: 전사 | 경영진 | 프로젝트팀만
```

## 반려(Reject) 조건

상위 에이전트는 다음 경우 하위 출력을 반려하고 재작업을 지시한다:

1. `disconfirming` 필드가 비어있음 (반증 검토 누락)
2. `confidence: high`인데 소스가 1개뿐
3. `strategic_impact: high`인데 소스가 `estimate` 타입만
4. `source_index`에 URL/원천이 누락된 항목 존재
5. Claim과 Evidence 사이 논리적 비약
6. 엔터티 라벨 (`[그룹]`/`[별도]`) 누락
7. 데이터 시점 미표기

---

## Division Synthesis 표준 스키마

Lead가 Phase 1/2 완료 후 findings/{division}/division-synthesis.yaml에 저장하는 표준 포맷.
PM이 Sync Round에서 이 파일을 읽고 교차 분석을 수행한다.

```yaml
division: "{division}"
lead: "{division}-lead"
phase: 1
completed_at: "YYYY-MM-DDTHH:MM:SS"

headline: "Division 전체를 관통하는 핵심 메시지 1문장"

key_findings:
  - id: "{ID}"
    claim: "..."
    confidence: "high | medium | low"
    strategic_impact: "high | medium | low"
    so_what: "이 사실이 의사결정에 미치는 영향"

key_tensions:
  - tension: "해소 안 된 긴장 설명"
    between: ["leaf-a", "leaf-b"]
    resolution_needed: true | false

leaf_results:
  "{leaf-id}":
    status: "verified | draft | revised"
    claims_count: {high: N, medium: N, low: N}
    top_claim: "가장 중요한 Claim 1문장"

cross_domain:
  implications:
    - target: "{other-division}"
      finding: "전달할 발견"
      urgency: "must | should | nice"
  questions:
    - target: "{other-division}"
      question: "확인 필요한 질문"
      urgency: "must | should | nice"

source_summary:
  total: N
  by_type: {primary: N, secondary: N, estimate: N}
  by_reliability: {high: N, medium: N, low: N}
  api_used: ["API 이름 목록"]

confidence_summary:
  high: N
  medium: N
  low: N
  unverified: N
```

---

## Phase 3.7 산출물 포맷

Phase 3(사고 루프) 이후, Phase 4(보고서) 이전에 실행되는 자기 비판 + 외부 리뷰 단계의 산출물.

### weakness-checklist (self-critique.md의 첫 섹션)

```yaml
weakness_checklist:
  - id: WC-01
    item: "확증 편향 (Confirmation Bias)"
    verdict: PASS | FLAG
    evidence: "판정 근거"
    remediation: "FLAG인 경우 보완 방안"
  - id: WC-02
    item: "반증 부족 (Insufficient Disconfirmation)"
    verdict: PASS | FLAG
    evidence: "판정 근거"
    remediation: "..."
  - id: WC-03
    item: "집단 사고 (Groupthink)"
    verdict: PASS | FLAG
    evidence: "판정 근거"
    remediation: "..."
  - id: WC-04
    item: "관점 고정 (Anchoring)"
    verdict: PASS | FLAG
    evidence: "판정 근거"
    remediation: "..."
  - id: WC-05
    item: "대안 부족 (Alternative Deficit)"
    verdict: PASS | FLAG
    evidence: "판정 근거"
    remediation: "..."
summary:
  total_flags: N
  proceed_to_self_critique: true | false  # FLAG 2건+ → true
```

### self-critique.md (전체 구조)

```
# Self-Critique — External Review (Phase 3.7)

## 약점 체크리스트
(weakness-checklist 포맷 참조)

## 프레이밍 비판
- 현재 프레이밍: {요약}
- 대안 프레이밍 1~2개 + trade-off

## 접근법 비판
- Division 구성 적절성
- 데이터 소스 편향 여부
- 프레임워크 선택 영향

## 빠진 관점
| 누락 관점 | 영향 | 보완 방안 |

## 결론 강건성 테스트
- 시나리오별: 가정 변경 → 결론 변화 여부 → 강건/취약

## report-writer 전달 사항
```

### external-review.md (선택적)

```
# External Review — 외부 모델 피드백

## 피드백 소스
- provider: codex | gemini | user_provided
- timestamp: YYYY-MM-DDTHH:MM:SS

## 피드백 분류
| 항목 | 유형 | 내용 | PM 판정 |
| --- | 동의/보완/반박 | 피드백 상세 | 반영/보류/기각 |

## 반영 사항
- 보완 항목: [...]
- 반박 항목: [양쪽 근거 대비]
```

---

## 소스 추적 규칙

### 신뢰도 정량화

| 소스 조합 | confidence 상한 |
|----------|---------------|
| primary 2개+ 일치 | high |
| primary 1개 + secondary 1개+ | high |
| secondary 2개+ 독립 확인 | high |
| secondary 1개만 | medium |
| estimate/tertiary만 | low |
| API 미사용 + 웹 검색만 | medium (high 불가) |

### API 결과의 소스 분류

- 정부/기관 API (DART, FRED, ECOS): type: primary
- 상업 API (Exa, Firecrawl): type: secondary (원본 소스의 신뢰도를 따름)
- 크롤링 데이터: type: secondary

### 소스 변동 대응

- URL 접근 실패: source-url-verifier가 탐지 → 해당 Claim confidence 한 단계 하향
- 대체 소스 확보: 원본 URL + 아카이브 URL 병기 권장
- API 데이터 시점: 반드시 as_of 필드에 데이터 기준 시점 명시

### data-registry.csv 연동

모든 데이터 수집 결과를 `{project}/data/data-registry.csv`에 등록:
- data_id: {Leaf ID}-D## (예: MSZ-D01)
- type: api | web | report | internal
- reliability: high | medium | low
- collected_by: 수집한 agent-id
이 레지스트리가 최종 보고서의 소스 테이블 원천이 됨.
