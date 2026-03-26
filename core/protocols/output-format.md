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
  - id: S05
    type: estimate
    name: "업계 리서치 기관 Annual Report 2025"
    url: null                        # 유료 보고서 — URL 없음
    accessed: 2026-03-01
    reliability: medium
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

## 슬라이드 매핑 (PPT 생성용)

### report-slides.md의 slide_meta 메타데이터

report-writer가 `report-slides.md` 작성 시, 각 슬라이드 섹션에 YAML 프론트매터 형태의 매핑 정보를 포함한다.

### Action Title 규칙

슬라이드 title은 반드시 **주장 문장(Action Title)**이어야 한다:
- ✗ 금지: 주제형 타이틀 ("시장 규모 분석", "경쟁 현황", "재무 전망")
- ✓ 필수: 주장형 타이틀 ("국내 시장은 연 12% 성장 중이나 수익성은 상위 3사에 집중")
- 타이틀만 순서대로 읽으면 보고서의 전체 스토리라인이 완성되어야 한다
- qa-orchestrator의 audience-fit-checker가 주제형 타이틀을 감지하면 반려한다

```yaml
# report-slides.md 내 각 슬라이드 섹션 앞에 삽입
<!-- slide_meta
  slide_id: 1
  title: "타이틀 — 반드시 Action Title(주장 문장형)"
  layout: title_slide | content | two_column | chart | table | summary
  content_blocks:
    - id: CB-01
      type: text | table | chart | bullet_list | quote
      source_section: "report-docs.md Section 1.2"    # 상세 보고서 원본 위치
      source_claims: [MGN-02, FRV-01]                  # 관련 Claim ID
      data: |
        블록 콘텐츠 (마크다운)
    - id: CB-02
      type: table
      source_section: "report-docs.md Section 3.1"
      source_claims: [PGD-01, PGD-03]
      data: |
        | 열1 | 열2 |
        |-----|-----|
        | ... | ... |
  design_notes: "디자인 힌트 (색상 강조, 아이콘 등)"
-->
```

### 사용자 슬라이드 커스텀

Phase 4 Step 4-B에서 사용자가 슬라이드 구성을 변경할 수 있다:
- **순서 변경**: 슬라이드 번호 재배치
- **블록 이동**: content_block을 다른 슬라이드로 드래그
- **블록 추가/삭제**: report-docs.md에서 추가 콘텐츠 선택 또는 불필요 블록 제거
- **레이아웃 변경**: layout 타입 변경 (예: content → two_column)

### PPT 생성 경로별 매핑 활용

| 경로 | slide_meta 활용 방법 |
|------|---------------------|
| Canva MCP | content_blocks → Canva editing operations로 변환. layout → 템플릿 매칭 |
| python-pptx | content_blocks → python-pptx 슬라이드 객체 생성. layout → 마스터 레이아웃 선택 |
| 수동 | content_blocks를 참조하여 사용자가 직접 PPT 작성 |

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
| `confidential` | 기밀 데이터 (M&A, 인사, 미공개 전략) | "[기밀]" 태깅 필수, Executive Summary/슬라이드 사용 시 사용자 확인 |

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
