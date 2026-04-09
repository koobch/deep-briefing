# Sync 프로토콜 (Orchestration Protocol)

> PM이 Division 간 교차 검증과 맥락 공유를 운영하는 규칙.
> 모든 리서치 프로젝트에서 동일하게 적용된다.

## 전체 오케스트레이션 플로우

```
Phase 0: Client Discovery + Research Plan
    │
Phase 0.5: 가설 생성 + 사용자 정렬
    │   ├── Quick Scan (활성 Division × 30분 기초 스캔)
    │   ├── 전략 가설 3~5개 도출
    │   └── 사용자 가설 채택/수정/추가 → 가설 확정
    │
Phase 1: Division 병렬 리서치 (가설 검증/반증 중심)
    │
    ├── [Division 내부] Lead가 리프 스폰 → 리프 자율 반복 → Lead 합성
    │
Sync Round 1: PM이 Division 출력 수집 + 교차 라우팅
    │
Phase 2: 교차 반영 심화 리서치 (각 Division 독립)
    │
Sync Round 2: PM이 전체 취합 → Cross-domain Synthesis
    │
Phase 3: 사고 루프 (Thinking Loop)
    │
Phase 4: 전략 도출 + 보고서
    │
Phase 5: QA + 자동 수정 루프
    │
Phase 5.5: 사용자 피드백 + 부분 재실행 (선택적)
    │
Phase 6: Post-mortem + 학습 전이 (자동)

※ 어느 Phase에서든 사용자가 "되돌아가기" 요청 가능 (Interactive/Team)
  → PM이 영향 범위 분석 → 최소 범위 재실행 → 원래 Phase로 복귀
```

## Phase 0-pre: Feasibility Gate

리서치 시작 전 실행 가능성 + 전략적 당위성을 사전 판단한다. 불가능/비효율적인 프로젝트의 조기 식별이 목적.

### 필수 판정 항목 (3분 이내)

1. **데이터 접근성 판정**
   - 핵심 질문에 답하기 위해 필요한 데이터 유형 식별
   - 공개 데이터로 충분 → GO
   - 기밀/유료 데이터 필요 → CONDITIONAL (범위 축소 또는 대체 접근법 명시)
   - 접근 불가 데이터에 핵심 의존 → SCOPE_CHANGE

2. **의사결정 타입 판별**
   - Go/No-Go (이진 판단) → 핵심 1~2개 가설에 집중, lean 분석
   - Strategic Choice (다지선다) → 선택지별 비교 프레임 필요
   - Exploration (탐색적) → 열린 구조, 가설 도출 중심

3. **실행 가능성**
   - 리서치 결과를 실행할 주체 확인: 있음 → Implementation Playbook 필수 / 없음 → Playbook 축소

4. **시간 제약**
   - 1주 이내 → Auto + Quick Scan 중심
   - 2~4주 → Interactive 권장
   - 1개월+ → Team 가능

### 산출물: 00-feasibility-gate.md

```yaml
feasibility:
  verdict: GO | CONDITIONAL | SCOPE_CHANGE
  decision_type: go_no_go | strategic_choice | exploration
  data_constraints: []
  timeline: "YYYY-MM-DD까지"
  execution_owner: "있음 | 없음 | 확인 필요"
  scope_adjustments: ""
  recommended_mode: auto | interactive | team
```

### 모드별 차이
| | Auto | Interactive | Team |
|---|---|---|---|
| Feasibility Gate | 1분 자동 판정 | 3분 사용자 확인 | 5분+ 토론 |
| CONDITIONAL 처리 | scope 자동 축소 | 사용자 선택 | 팀 합의 |

---

## Phase 0: Client Discovery + Research Plan

### Step 0-A: Intake Interview

PM이 사용자와 직접 대화하여 리서치 맥락을 확보한다.
질문은 2개 Pass로 구성된다. Pass 1(사용자 인터뷰)은 모든 모드에서 실행하며, Pass 2(리서치 질문)는 모드별로 Quick/Deep을 선택한다.

**Pass 1: 사용자 인터뷰 (모든 모드)**
사용자의 도메인 전문성, 의사결정 맥락, 증거 기준을 파악하여 `{project}/user-profile.yaml`에 기록한다.
이 프로필은 리서치 전체에서 SSOT로 사용되며, Phase 진행 중 갱신된다 (갱신 시점은 아래 "user-profile.yaml SSOT 갱신 시점" 참조).

Quick (3개) — Auto 모드:
1. 이 분야에서의 역할과 경험은? (전문가 / 의사결정자 / 탐색 중)
2. 리서치 결과를 직접 실행하는가, 다른 의사결정자에게 전달하는가?
3. 이미 시도하거나 검토한 것이 있는가? (결과와 교훈 포함)

Full (6~10개) — Interactive/Team 모드:
Quick 3개 + 추가:
4. 리서치 결과를 받은 후 어떤 행동을 취할 계획인가? (사용 후 행동)
5. 결론을 수용하려면 어떤 수준의 증거가 필요한가? (정량 필수 / 정성 OK / 혼합)
6. 선호하거나 기피하는 전략 방향이 있는가?
Deep 추가 (Interactive/Team):
7. 전문 영역과 비전문 영역은? (PM이 비전문 영역에 더 상세한 설명 제공)
8. 분석 항목 간 우선순위가 있는가? (시장 > 재무 등)
9. 리스크 허용도는? (공격적 / 보수적 / 상황에 따라)
10. 이 리서치에 투입 가능한 리소스(시간, 예산, 인력)는?

산출물: `{project}/user-profile.yaml`

```yaml
user_profile:
  role: "역할 (예: 전략기획팀 리드)"
  domain_expertise: high | medium | low
  expert_areas: ["전문 영역"]
  non_expert_areas: ["비전문 영역"]
  decision_role: executor | advisor | explorer
  evidence_standard: quantitative | qualitative | mixed
  risk_tolerance: aggressive | conservative | situational
  preferred_directions: ["선호 방향"]
  avoided_directions: ["기피 방향"]
  prior_attempts: ["이전 시도 요약"]
  post_research_action: "결과 수신 후 계획된 행동"
  priority_order: ["우선순위 순서"]
  updated_at: "YYYY-MM-DD"
  update_log:
    - phase: "0"
      changes: "초기 프로필 생성"
      timestamp: "YYYY-MM-DD HH:MM"
```

**Pass 2: 리서치 질문**

**Quick (5~7개 질문)** — Auto 모드 또는 시간 제약 시:
1. 이 리서치의 최종 의사결정은 무엇인가?
2. 최종 소비자는 누구인가? (경영진, 이사회, 실무팀)
3. 이미 검토 중인 방향이 있는가?
4. 반드시 제외해야 할 방향이 있는가?
5. 제공 가능한 내부 데이터가 있는가?
6. 예산/인력/시간 제약이 있는가?
7. 보고서 톤/형식 선호가 있는가?

**Deep (12~15개 질문)** — Interactive/Team 모드:
Quick 7개 + 추가:
8. 이전에 유사 리서치를 한 적이 있는가? 결과는?
9. 조직 내 이해관계자 간 의견 차이가 있는가?
10. 경쟁사 중 특별히 벤치마킹 대상이 있는가?
11. 기술적 제약 (엔진, 플랫폼, 기술 스택)이 있는가?
12. 타임라인 제약 (출시 목표 시점)이 있는가?
13. 최근 조직 변화 (인수, 구조조정, 핵심 인력 이동)가 있는가?
14. 성공 기준은 무엇인가? (매출 목표, 시장 점유율, MAU 등)
15. 리서치 결과에 따라 "안 한다"도 옵션인가?

**산출물**: `{project}/00-client-brief.md`

### Step 0-B: Research Plan

PM이 Client Brief를 기반으로 리서치 설계:

```yaml
research_plan:
  project: {project-name}
  question: "핵심 리서치 질문 1문장"
  mode: auto | interactive | team

  divisions:
    market:
      active: true
      leaves: [market-sizing, customer-analysis, competitive-landscape, channel-landscape, market-dynamics]
      priority_focus: "Client Brief에서 도출된 시장 분석 초점"

    product:
      active: true
      leaves: [product-offering, value-differentiation, go-to-market, pricing-monetization]
      priority_focus: "..."

    capability:
      active: true
      leaves: [technology-ip, technology-ip, execution-readiness, strategic-assets]
      priority_focus: "..."

    finance:
      active: true
      leaves: [revenue-growth, investment-returns]
      priority_focus: "..."

    # === 확장 Division (주제에 따라 선택 투입) ===
    people-org:
      active: false          # PM이 주제 기반으로 결정
      activation_criteria: "조직 변화, 인력 전략, 문화 전환, HR 이슈가 핵심 질문에 포함될 때"
      leaves: [talent-strategy, org-design, culture-engagement]
      priority_focus: ""

    operations:
      active: false
      activation_criteria: "프로세스 효율화, 운영 최적화, 서비스 운영, 공급망이 핵심일 때"
      leaves: [process-excellence, supply-chain, infrastructure]
      priority_focus: ""

    regulatory:
      active: false
      activation_criteria: "규제 환경, 법적 리스크, ESG, 정부 정책이 전략에 중대한 영향을 줄 때"
      leaves: [compliance-status, regulatory-outlook, esg-governance]
      priority_focus: ""

  frameworks:                          # domains/{domain}/frameworks.md 참조
    selection_rationale: "이 조합을 선택한 이유 (핵심 질문과의 연결)"
    market:
      primary: {프레임워크명}
      secondary: {프레임워크명}          # 필요 시
      rationale: "적용 목적"
    product:
      primary: {프레임워크명}
      secondary: {프레임워크명}
      rationale: "적용 목적"
    capability:
      primary: {프레임워크명}
      secondary: {프레임워크명}
      rationale: "적용 목적"
    finance:
      primary: {프레임워크명}
      secondary: {프레임워크명}
      rationale: "적용 목적"
    cross_cutting:
      primary: {프레임워크명}            # 거의 항상 3C
      secondary: {프레임워크명}          # 거의 항상 SWOT
      optional: {프레임워크명}
      rationale: "적용 목적"
    # === 확장 Division 프레임워크 (활성화 시) ===
    people_org:
      primary: {프레임워크명}
      rationale: "적용 목적"
    operations:
      primary: {프레임워크명}
      rationale: "적용 목적"
    regulatory:
      primary: {프레임워크명}
      rationale: "적용 목적"

  data_intake:
    user_provided: [데이터 목록]
    preprocessing_needed: true | false

  # 에이전트 선별 투입 (PM agent.md의 agent_roster 참조)
  agent_roster:
    required: [항상 투입되는 인프라 에이전트]
    active:
      # 핵심 Division (거의 항상 활성화)
      market: { lead, leaves }
      product: { lead, leaves }
      capability: { lead, leaves }
      finance: { lead, leaves }
      # 확장 Division (활성화 시)
      # people-org: { lead, leaves }
      # operations: { lead, leaves }
      # regulatory: { lead, leaves }
    skipped: [{ agent-id: "제외 사유" }]  # 예: { market-dynamics: "신흥국 미포함" }
    total_active: {N}

  constraints:
    excluded_directions: [Client Brief에서 제외된 방향]
    must_include: [반드시 포함할 분석]
    timeline: "리서치 완료 목표"

  # 도메인 특화 확장 필드 (PM agent.md에서 정의)
  ep_warnings:                         # EP 패턴 사전 경고 (도메인별)
    - ep: EP-027                       # EP 번호
      target: [agent-id-1, agent-id-2] # 경고 대상 에이전트
      message: "주의사항 메시지"         # 구체적 경고 내용
```

**산출물**: `{project}/01-research-plan.md`

### Step 0-C: Data Intake (해당 시)

사용자가 내부 데이터를 제공한 경우:

```
1. PM이 data-preprocessor (유틸리티 에이전트) 스폰
2. data-preprocessor가 데이터 구조 탐색 → 정제 → 분할
3. 분할된 데이터를 활성 Division에 배포:
   # 활성화된 Division에 대해 동적으로 생성
   {project}/data/processed/{division}/   ← 각 활성 Division별 관련 데이터
   예: market/, product/, capability/, finance/, people-org/, operations/, regulatory/
4. 데이터 품질 보고서 작성: {project}/00.5-data-quality-report.md
```

### Decision Frame (의사결정 프레임) — Research Plan 필수 구성요소

Research Plan 작성 시 아래 Decision Frame을 반드시 포함한다. 이것이 리서치 전체의 **나침반** 역할을 한다.

#### Decision Questions (DQ) — 3~5개 제한
리서치가 답해야 할 핵심 의사결정 질문. Yes/No 또는 A vs B 형태로 작성.

```yaml
decision_frame:
  decision_questions:
    - id: DQ-01
      question: "{구체적 의사결정 질문}"
      judgment_criteria: "{어떤 데이터/근거가 있으면 답할 수 있는가}"
      related_divisions: [market, finance]
      min_confidence: high
    - id: DQ-02
      question: "{...}"
      ...

  decision_tree:
    - condition: "H-01 = true AND H-02 = true"
      action: "선택지 A: {전략 방향}"
    - condition: "H-01 = true AND H-02 = false"
      action: "선택지 B: {대안 방향}"
    - condition: "H-01 = false"
      action: "No-Go 또는 Pivot"

  kill_criteria:          # 2~3개 제한
    - id: KC-01
      condition: "{이 조건 발견 시 프로젝트 방향 전면 재검토}"
      threshold: "{구체적 수치 기준}"
      example: "TAM < $1B이면 진출 재고"
```

#### hypotheses.yaml 확장 스키마
기존 가설 스키마에 전략적 중량감 필드를 추가:

```yaml
hypotheses:
  - id: H-01
    statement: "..."
    type: opportunity | risk | assumption
    decision_it_serves: "DQ-01"       # Decision Question 참조
    strategic_weight: critical | supporting | contextual
    # critical = 거짓이면 전체 전략 무너짐
    # supporting = 세부 전략 변경
    # contextual = 배경 이해용
    kill_trigger: true | false        # 검증 실패 시 Kill Criteria 활성
    user_rationale: ""               # 사용자가 이 가설을 채택/수정/추가한 이유 (Step 0.5-C에서 기록)
                                     # 빈 문자열 = PM 자동 생성 가설, 사용자 미개입
    verification_plan: [...]
```

---

## Phase 0.5: 가설 생성 + 사용자 정렬

### 목적

전 방위 리서치 전에 **전략 가설을 먼저 세워** 조사 범위를 좁히고, 사용자와 방향을 정렬한다.
Phase 1이 "가설 검증/반증" 구조로 전환되어 리소스 효율과 논리 깊이가 동시에 개선된다.

### 트리거
Phase 0 완료 — Client Brief + Research Plan + Factsheet 확정 후.

### Step 0.5-A: Quick Scan (기초 스캔)

```
실행 방법: PM CLI에서 Agent 도구로 Research Plan에 정의된 Division Lead를 병렬 스폰.
  (Quick Scan은 30분 이내 경량 작업이므로 tmux 독립 CLI 불필요.
   PM 컨텍스트 내에서 Agent 도구로 충분.)

1. PM이 각 Division에 Quick Scan 지시 (Agent 도구, 병렬)
   - 각 Division Lead에게 Client Brief + Research Plan 전달
   - 지시: "30분 이내, 기초 데이터만 수집. 상세 분석 불필요.
            findings/{division}/quick-scan.yaml에 결과 저장."
   - 출력: Division별 1페이지 요약 (headlines + 기회/위협 Top 3)

2. Quick Scan 출력 경로:
   {project}/findings/{division}/quick-scan.yaml

3. Quick Scan 출력 스키마:
   agent: {lead-id}
   phase: "0.5-quick-scan"
   headlines:
     - "Division 관점에서 본 핵심 시장/역량/재무 시그널"
   opportunities:
     - id: OPP-01
       description: "기회 요약"
       confidence: high | medium | low
       rationale: "근거 1~2문장"
   threats:
     - id: THR-01
       description: "위협 요약"
       confidence: high | medium | low
       rationale: "근거 1~2문장"
```

### Step 0.5-B: 가설 도출

```
PM이 Quick Scan 결과를 합성하여 3~5개 전략 가설을 생성한다.

가설 구조:
  hypotheses:
    - id: H-01
      statement: "가설 1문장 (검증/반증 가능한 형태)"
      type: opportunity | risk | assumption
      supporting_signals:
        - division: market
          signal: "Quick Scan에서 발견된 근거"
        - division: capability
          signal: "Quick Scan에서 발견된 근거"
      counter_signals:
        - "이 가설이 틀릴 수 있는 이유"
      verification_plan:
        - division: market
          task: "이 가설을 검증하기 위해 Market Division이 조사할 것"
        - division: capability
          task: "이 가설을 검증하기 위해 Capability Division이 조사할 것"
      priority: must | should | nice

가설 유형별 예시:
  opportunity: "제품 카테고리A가 현재 역량으로 12~18개월 내 출시 가능한 유일한 옵션이다"
  risk: "기존 주력 제품 매출이 연 -35% 이상 급감하여 2027년 조직 유지 최소 매출에 미달한다"
  assumption: "자사 IP를 신규 카테고리에 적용하면 UA 비용을 30% 절감할 수 있다"

산출물: {project}/hypotheses.yaml
```

### Step 0.5-C: 사용자 가설 정렬

```
PM이 사용자에게 가설 목록을 제시:

📋 전략 가설 목록 (Quick Scan 기반)

[필수 검증]
  H-01: "카테고리A가 현재 역량으로 실현 가능한 유일한 옵션이다"
        근거: 자체 실증 1건 (Capability) + 시장 $400M/CAGR 4.9% (Market)
        반론: 세그먼트B도 소규모 프로토로 검증 가능 (Product)

  H-02: "2027년 매출 공백이 $40M+ 발생하여 신작 없이는 사업 지속 불가"
        근거: 주력 제품 매출 -61% 급감 (Finance) + 파이프라인 0건 (Capability)

[선택 검증]
  H-03: "자사 IP 활용 시 UA 비용 30% 절감 + D1 리텐션 5%p 상승"
        근거: 업계 벤치마크 (Market)
        반론: 제품-시장 미스매치 리스크 (Product)

→ 가설을 수정/추가/삭제하시겠습니까? 아니면 이대로 진행?

사용자 응답 유형:
  "이대로 진행" → 가설 확정, Phase 1 진입
  "H-03 삭제, H-04 추가: ..." → 가설 수정 후 확정
  "가설 방향 자체를 바꿔야 해" → Step 0.5-B 재실행
```

### Step 0.5-D: Division Briefs에 가설 반영

```
가설 확정 후, Division Briefs에 가설 검증 지시를 추가:

각 Division Brief에 추가되는 섹션:
  ## 가설 검증 지시
  이 Division이 담당하는 가설 검증:
    - H-01: [검증] "카테고리A 실현 가능성" → 구체적 조사 항목
    - H-02: [반증 탐색] "매출 공백 규모" → 주력 제품 외 매출원 가능성도 탐색

  검증 결과 출력:
    각 Leaf 출력의 iteration_log에 가설 ID(H-##)를 태깅하여
    어떤 가설의 검증/반증에 기여하는 데이터인지 추적 가능하게 한다.
```

### Phase 0.5 완료 게이트

```
□ Quick Scan 전체 Division 완료
□ 가설 3~5개 도출 완료
□ 사용자 가설 정렬 완료 (확정 또는 수정 반영)
□ hypotheses.yaml 저장 완료
□ Division Briefs에 가설 검증 지시 반영 완료
□ checkpoint.yaml에 phase: "0.5-hypothesis" 기록
```

### 모드별 차이

| 단계 | Auto | Interactive | Team |
|------|------|-------------|------|
| Quick Scan | 자동 실행 | 자동 실행 | 자동 실행 |
| 가설 도출 | PM 자동 | PM 자동 | PM 자동 |
| 사용자 정렬 | 생략 (자동 확정) | 사용자 검토 + 수정 | 사용자 검토 + 토론 |
| 가설 추가 | 불가 | 사용자 추가 가능 | 팀 토론 후 추가 |

### Phase 0.5 자동화 플로우 (4-Step)

#### Step 0.5-A: Quick Scan
- PM이 각 활성 Division Lead를 Agent 도구로 스폰 (Quick Scan 모드)
- 각 Lead는 30분 이내로 기초 스캔 수행
- 산출물: `findings/{division}/quick-scan.yaml`

#### Step 0.5-B: 가설 도출
- PM이 전체 quick-scan.yaml을 수집
- 3~5개 가설을 `{project}/hypotheses.yaml`에 자동 생성:
  ```yaml
  hypotheses:
    - id: H-01
      statement: "가설 내용"
      validation_method: "검증 방법"
      related_divisions: [market, product]
      initial_confidence: low | medium
  ```

#### Step 0.5-C: 사용자 정렬
- Auto 모드: 가설 자동 확정 → Step 0.5-D 즉시 진행
- Interactive/Team: 사용자에게 가설 목록 제시 → 채택/수정/추가/삭제 가능
- 사용자 확정 후 hypotheses.yaml 갱신

#### Step 0.5-D: Division Brief 자동 주입
- 확정된 가설을 `division-briefs/{div}.md`에 자동 삽입
- 삽입 위치: "## 검증 대상 가설" 섹션 (init-project.sh에서 템플릿에 포함)
- 각 Division에 관련 가설만 배분 (related_divisions 필드 기반)

---

## Phase 1: Division 병렬 리서치

### PM의 역할

```
1. TeamCreate로 Research Plan에 정의된 Division Lead를 스폰 (병렬)
2. 각 Lead에게 전달:
   - Client Brief (00-client-brief.md)
   - Research Plan 중 해당 Division 부분
   - 사용자 데이터 (해당 시)
   - 특별 주의사항 (EP 패턴, 제외 방향 등)
3. Division 완료 대기
```

### .status 파일 (실시간 진행 상태 — Lead 필수 갱신)

Lead는 Leaf 시작/완료마다 `findings/{division}/.status`를 갱신한다.
PM의 spawn-leads.sh 모니터가 이 파일의 `updated_at`을 확인하여 stuck 상태를 감지한다.

```yaml
# findings/{division}/.status
division: {division}
phase: 1                              # 현재 Phase
status: running                       # running | completed | error
updated_at: YYYY-MM-DDTHH:MM:SS      # 마지막 갱신 시각
current_leaf: market-sizing           # 현재 실행 중인 Leaf (없으면 synthesis 등)
leaves_done: 2                        # 완료된 Leaf 수
leaves_total: 5                       # 전체 Leaf 수
last_event: "market-sizing 완료"      # 최근 이벤트 (사람 읽기용)
```

**갱신 규칙:**
- Leaf 스폰 시: `current_leaf` 갱신, `status: running`
- Leaf 완료 시: `leaves_done` 증가, `current_leaf`을 다음 Leaf로 갱신
- 전체 완료 시: `status: completed`
- 에러 발생 시: `status: error`, `last_event`에 에러 요약

**stuck 감지 (spawn-leads.sh 모니터):**
- `.status`의 `updated_at`이 30분 이상 무변경 → stuck 의심 경고 발송
- `.status`가 없으면 `.done`만 확인 (하위 호환)

### Division Lead의 역할

```
0. 재투입 시 .progress 확인 (부분 완료 복구)
   → findings/{division}/.progress 파일이 존재하면 읽어서 완료된 Leaf를 건너뛴다.
   → .progress 파일이 없으면 처음부터 실행.

1. Agent 도구로 Sub-lead 또는 Leaf 스폰 (병렬)
2. 각 하위 에이전트에게 전달:
   - Client Brief 요약 (해당 도메인 관련 부분)
   - 분석 범위 + 초점
   - 사용 가능한 데이터 소스
3. 하위 에이전트 출력 수집
4. VL-1.5 검증 (삼각 검증 + 스팟체크)
5. VL-2 검증 (리프 간 정합성)
6. Division 합성 (매트릭스 교차, 패턴 추출)
7. Division 출력 작성 (표준 출력 포맷)
```

### Leaf Agent의 역할

```
1. 자율 반복 프로토콜 실행 (최대 3회)
   가설 수립 → 데이터 수집 → 검증 → 판정
2. VL-1 자가 검증 (2소스+, 반증 검토)
3. 표준 출력 포맷으로 결과 작성
4. cross_domain 태깅 (다른 도메인 영향 식별)
5. 완료 → 상위 에이전트(Lead)에 반환
```

### .progress 파일 (부분 완료 추적 — Phase 1/2 공용)

Lead가 각 Leaf 완료 시 `findings/{division}/.progress`를 갱신한다.
토큰 제한/세션 중단 시 재투입하면 이 파일을 읽어 완료된 Leaf를 건너뛴다.

**Phase 전환 규칙:**
- Phase 2 시작 시 `send-phase2.sh`가 `.progress`를 Phase 2용으로 리셋 (Phase 1 이력은 `.progress.phase1-backup`에 백업)
- `phase` 필드는 현재 활성 Phase를 나타냄 (1 또는 2)
- Lead는 재투입 시 `phase` 필드를 확인하여 현재 Phase에 맞는 Leaf만 건너뜀

```yaml
# findings/{division}/.progress
division: {division}
phase: 2              # 1 또는 2 — 현재 활성 Phase
updated_at: YYYY-MM-DDTHH:MM:SS

leaves_completed:
  - agent: market-dynamics
    file: findings/market/market-dynamics.yaml
    completed_at: YYYY-MM-DDTHH:MM:SS
  - agent: competitive-landscape
    file: findings/market/competitive-landscape.yaml
    completed_at: YYYY-MM-DDTHH:MM:SS

leaves_pending:
  - agent: market-dynamics
    reason: "세션 중단으로 미완료"

synthesis_status: pending  # pending | in-progress | completed
```

### .done 파일 Phase 전환 관리

`.done` 파일의 `phase` 필드로 PM이 각 Division의 Phase 완료 상태를 판단한다.

```yaml
# findings/{division}/.done — Phase 상태 추적
division: {division}
phase: 2                   # 완료된 Phase 번호 (1 또는 2)
                           # Phase 2 시작 시: "2-in-progress"
                           # Phase 2 완료 시: 2
completed_at: YYYY-MM-DDTHH:MM:SS
```

**Phase 전환 시나리오:**
- Phase 1 완료: `.done`에 `phase: 1` 기록
- Phase 2 시작: `send-phase2.sh`가 미완료 Division의 `.done`을 `phase: 2-in-progress`로 갱신
- Phase 2 완료: Lead가 `.done`을 `phase: 2`로 갱신
- Phase 2 재실행: `send-phase2.sh`가 `phase: 2` Division은 건너뛰고, 나머지만 재스폰

**Lead 재투입 프로토콜:**
```
1. .progress 파일 존재 확인
2. .progress의 phase 필드가 현재 Phase와 일치하는지 확인
   - 불일치: 이전 Phase 이력 → 처음부터 실행
   - 일치: 부분 완료 상태 → 아래 3번으로
3. leaves_completed 목록의 파일이 실제 존재하는지 검증
4. leaves_pending만 Agent 도구로 스폰
5. 모든 Leaf 완료 → synthesis 실행 → .done 작성 (phase: {현재 Phase})
6. .progress 파일은 .done 작성 후에도 유지 (이력용)
```

## Sync Round 1

### 트리거
Phase 1 완료 — 모든 Division Lead 출력이 도착.

### PM이 수행하는 작업

```
Step 1: Division 출력 수집
  - 각 Division의 Layer 0 (Claims) 읽기
  - division_summary.headline 수집

Step 2: Cross-domain 라우팅
  - 각 Division의 cross_domain.questions 수집
  - 해당 Division에 라우팅:
    "market→product 질문: 세그먼트B Top 10 제품의 설계 패턴은?"
    → product-lead에게 전달
  - 각 Division의 cross_domain.implications 수집
  - 해당 Division에 배포:
    "market의 발견이 capability에 미치는 영향: 현지화 역량 확인 필요"
    → capability-lead에게 전달

Step 3: Tension 식별
  - Division 간 모순 또는 긴장 식별:
    "Market: 세그먼트B가 기회"
    vs "Capability: 세그먼트B 관련 경험 0건"
    → tension으로 태깅

Step 4: fact-verifier 투입
  - VL-3 교차 검증 실행
  - Division 간 수치 정합성 확인
  - 방법론 감사

Step 5: Sync Briefing 작성
  → {project}/sync/round-1-briefing.md
```

### Sync Briefing 구조

```yaml
sync_round: 1
timestamp: YYYY-MM-DD

division_headlines:
  # 활성 Division별 headline (핵심 4개 + 활성화된 확장 Division)
  market: "Division headline"
  product: "Division headline"
  capability: "Division headline"
  finance: "Division headline"
  # 확장 Division (활성화 시)
  # people-org: "Division headline"
  # operations: "Division headline"
  # regulatory: "Division headline"

routed_questions:
  - from: market
    to: product
    question: "..."
    priority: must
  - from: capability
    to: finance
    question: "..."
    priority: should

routed_implications:
  - from: market
    to: capability
    implication: "..."
    urgency: must

tensions:
  - id: T-01
    description: "시장 기회 vs 역량 부재"
    between:
      - division: market
        claim: MGN-02
        position: "세그먼트B CAGR 15%"
      - division: capability
        claim: CDP-01
        position: "세그먼트B 관련 경험 0건"
    resolution_needed_by: "Phase 2 종료 시"

fact_verification:
  cross_division_issues: [{이슈 목록}]
  methodology_flags: [{플래그 목록}]

action_items:
  - division: product
    action: "세그먼트B Top 10 제품 설계 패턴 조사"
    source: "market cross_domain question"
  - division: capability
    action: "현지화 역량 현황 + 파트너십 옵션 심화"
    source: "market implication + tension T-01"
```

### Interactive/Team 모드: 사용자 게이트

Interactive 또는 Team 모드에서는 Sync Round 1 후 사용자에게 브리핑:

```
📋 Sync Round 1 결과

[Division별 핵심 발견 요약]

⚠️ 식별된 긴장:
- T-01: 시장 기회(세그먼트B) vs 역량 부재(경험 0건)
- T-02: IP 가치 vs 제품-시장 미스매치

❓ 방향 확인이 필요한 사항:
1. 역량 부재 해결 방법 선호: 자체 육성 / 외부 영입 / 공동개발 / M&A?
2. 아트 스타일 전환 수용 가능?

🔍 맥락 체크인 (user-profile.yaml 기반):
3. 이 결과가 [사용자 역할/경험]에서의 경험과 맞는가? 예상과 다른 부분은?
4. 빠져 있다고 느끼는 관점이나 데이터가 있는가?
5. [사용자 전문 영역]에서 추가로 제공할 수 있는 정보가 있는가?

→ 피드백 반영 + user-profile.yaml 갱신 후 Phase 2 진행
```

## Phase 2: 교차 반영 심화 리서치

### PM의 역할

```
1. Sync Briefing + 사용자 피드백을 각 Division Lead에 전달
2. 각 Division이 다음을 수행하도록 지시:
   a. 다른 Division에서 온 질문에 답변
   b. implications 반영하여 분석 심화
   c. tension 해소를 위한 추가 리서치
3. Division 완료 대기
```

### Division Lead의 역할

```
1. Sync Briefing에서 자기 Division 해당 항목 추출
2. 필요 시 추가 리프 스폰 또는 기존 리프에 추가 지시
3. 질문 응답 + 심화 분석
4. 업데이트된 Division 출력 작성
```

## Sync Round 2 + Cross-domain Synthesis

### PM이 수행하는 작업

```
Step 1: 업데이트된 Division 출력 수집
Step 2: Tension 해소 프로토콜
  각 Tension(T-##)에 대해 순차적으로 판정:

  2-a. 원인 분류:
    - data_error: 수치/시점/정의 불일치 → fact-verifier 재검증으로 해소
    - perspective_gap: 같은 데이터를 다른 관점에서 해석 → 양쪽 관점 병기
    - real_tension: 실제 전략적 트레이드오프 → 선택지로 명시

  2-b. 해소 프로세스:
    - data_error: fact-verifier에 해당 Claim 재검증 → 오류 측 수정
    - perspective_gap: cross-domain-synthesizer가 양쪽 관점을 통합 서술
    - real_tension: 사용자 결정 필요 항목으로 에스컬레이션
      Interactive/Team: 선택지 제시 + 각 선택의 trade-off 명시
      Auto: "미해소 전략적 긴장"으로 보고서에 명시적 기록

  2-c. 해소 기록 — PM이 직접 작성 (sync/tension-resolution.yaml):
    ※ 이 파일은 init-project.sh에서 스캐폴딩됨. PM이 Sync Round 2에서 내용을 채운다.
    ※ report-writer, report-auditor가 이 파일을 입력으로 소비한다.
    tension_resolution:
      - id: T-01
        type: data_error | perspective_gap | real_tension
        resolution: "해소 방법 + 결과"
        resolved_by: "fact-verifier | cross-domain-synthesizer | 사용자"
        status: resolved | escalated | accepted_as_tradeoff

  2-d. 미해소 긴장 처리:
    - 미해소 tension → 보고서 "리스크 및 미해소 불확실성" 섹션에 반드시 반영
    - report-writer에 미해소 목록 전달 → 보고서에도 명시
    - 미해소 real_tension 3건+ → PM이 Phase 1 부분 재실행 제안

Step 2.5: fact-verifier 재투입
  - Phase 2에서 변경/추가된 Claim에 대해 VL-3 교차 검증 재실행
  - tension 해소 과정에서 새로 생성된 Claim 검증
  - Sync Round 1의 methodology_flags 해소 여부 확인
Step 3: cross-domain-synthesizer 스폰
```

### cross-domain-synthesizer의 역할

```
1. 모든 Division의 division_summary + key_findings 읽기 (전체 출력이 아닌 요약만)
2. 교차 인사이트 도출:
   "Division A의 Claim X + Division B의 Claim Y → 새로운 인사이트 Z"
3. tension 기반 전략적 선택지 구조화
4. 핵심 불확실성 식별 (사고 루프 입력)
5. 산출물: {project}/sync/cross-domain-synthesis.md
```

### Interactive/Team 모드: Sync R2 맥락 체크인

Sync Round 2 완료 후, tension 해소 결과와 cross-domain synthesis를 사용자에게 브리핑하며 맥락 체크인을 수행한다:

```
📋 Sync Round 2 결과 + Cross-domain Synthesis

[Tension 해소 결과 요약]
[교차 인사이트 요약]

🔍 맥락 체크인 (user-profile.yaml 기반):
1. 이 긴장(tension)에 대한 직관적 판단은? 데이터와 다른 감각이 있는가?
2. 해소된 긴장 중 "실제로는 다른 방향"이라고 느끼는 것이 있는가?
3. real_tension으로 남은 항목 중, 현실적으로 어느 쪽이 더 가능성 높은가?

→ 피드백 반영 + user-profile.yaml 갱신 후 Phase 3 진행
```

## Phase 3: 사고 루프 (Thinking Loop)

### 순서 (고정)

```
Step 1: logic-prober (수직 검증)
  - cross-domain-synthesis의 핵심 인사이트/전략에 Why Chain
  - 각 Division의 strategic_impact: high Claim에 Why Chain
  - "이 결론의 근거는?" → "그 근거의 근거는?" (재귀)
  - 논리 단절 발견 시: 해당 Division에 재검증 요청

Step 2: strategic-challenger (수평 도전)
  - 대안 전략 생성 (최소 2개)
  - 실패 시뮬레이션 ("이 전략이 실패하는 시나리오는?")
  - 경쟁자 대응 ("경쟁사가 같은 기회를 본다면?")
  - 비대칭 사고 ("완전히 다른 접근은?")
  - 포트폴리오 자기모순 탐지 ("A 전략과 B 전략이 충돌하지 않는가?")
  - 산출물: {project}/thinking-loop/strategic-challenge.md

Step 2.5: red-team (적대적 반론 — Devil's Advocate)
  - 활성화: Team/Interactive 기본. Auto는 --deep 시에만
  - 핵심 전제 반증 시도 (Falsification)
  - 역 시나리오 모델링 (시장/경쟁/기술이 반대로 움직이면?)
  - 숨겨진 가정 노출 (명시되지 않은 전제 식별)
  - 최악의 경우 구성 (트리거 → 연쇄 반응 → 실패 경로)
  - 반론 강도 판정: Strong(전략 재검토) / Moderate(보강) / Weak(참고)
  - Strong 2건+ → PM 에스컬레이션 (escalation-protocol Type 4)
  - 산출물: {project}/thinking-loop/red-team-report.md

Step 3: insight-synthesizer (통합 반영)
  - logic-prober의 논리 보강 반영
  - strategic-challenger의 도전 결과 반영
  - red-team의 반론 대응 (Strong → 전략 수정, Moderate → 보강)
  - 전략 보강/수정
  - 산출물: {project}/thinking-loop/loop-convergence.md

PM 수렴 판정:
  - 논리 단절 0건 + Critical 블라인드 스팟 0건 + Strong 반론 전수 대응 + BASE 시나리오 자력 실현 가능 → 수렴
  - 미수렴 → Step 1~3 반복 (최대 2회)
```

**산출물**: `{project}/thinking-loop/`
- `why-probe.md`
- `strategic-challenge.md`
- `loop-convergence.md`

> **Multi-round 파일명 관례**: 미수렴 시 Round 2+ 산출물은 `{basename}-round{N}.md` (예: `why-probe-round2.md`, `strategic-challenge-round2.md`, `loop-convergence-round2.md`). Round 1은 접미사 없음.

## Phase 3.5: Strategy Articulation

사고 루프 수렴 후, 보고서 작성 전에 **전략을 의사결정 형태로 구조화**하는 단계.

- **실행 주체**: insight-synthesizer (수렴 판정 Step 5로 통합)
- **입력**: loop-convergence.md + 01-research-plan.md의 Decision Frame
- **산출물**: strategy-articulations.md
- **내용**:
  - 각 Decision Question(DQ)에 대한 명시적 Answer + Confidence + Risk if Wrong
  - Kill Criteria 점검 (TRIGGERED/NOT TRIGGERED)
  - Unresolved Uncertainties (영향받는 DQ + 추가 검증 방법)
- **전달**: report-writer가 strategy-articulations.md를 보고서의 뼈대로 사용

## Phase 3.7: External Review

전략 구조화 후, 보고서 작성 전에 **분석의 약점과 편향을 체계적으로 점검**하는 단계.
Red Team이 Claim 단위 반론이라면, External Review는 **전체 프레이밍/접근법** 수준의 비판.

### Step 1: 자동 약점 탐지 체크리스트 (항상 실행, 모델 불필요)

PM이 strategy-articulations.md + loop-convergence.md + 전체 Division 출력을 기반으로 아래 5개 항목을 점검한다.

```
약점 탐지 체크리스트:
  ☐ 확증 편향: 반증 없이 주장을 뒷받침하는 증거만 수집하지 않았는가?
  ☐ 반증 부족: 각 핵심 주장에 반증 시도가 있었는가?
  ☐ Groupthink: 모든 Division이 같은 방향을 가리키고 있다면, 이것이 진짜인가 아니면 단일 소스 의존인가?
  ☐ 관점 고정: 초기 가설이 후반 분석을 과도하게 지배하고 있지 않은가?
  ☐ 대안 부족: 핵심 전략에 진정한 대안(not strawman)이 제시되었는가?

결과: 각 항목 PASS/FLAG + 근거 문장
판정: FLAG 2건 이상 → Step 2(자기 비판) 필수 실행
```

**산출물**: `{project}/thinking-loop/weakness-checklist.yaml`

### Step 2: 자기 비판 (기본 실행, 외부 모델 불필요)

PM이 external-reviewer 에이전트를 스폰한다. Red Team과의 차이점: Claim 단위가 아닌 **전체 프레이밍/접근법**을 비판.

```
external-reviewer 스폰 (Agent 도구)
  역할: "이 분석을 처음 보는 외부 비판자"
  입력:
    - strategy-articulations.md
    - loop-convergence.md
    - cross-domain-synthesis.md
    - weakness-checklist.yaml (Step 1 결과)
  비판 관점:
    1. 프레이밍: 문제 정의 자체가 올바른가? 다른 프레이밍이 가능한가?
    2. 접근법: 분석 방법론 선택이 적절했는가?
    3. 빠진 관점: 어떤 이해관계자/시각이 누락되었는가?
    4. 결론의 강건성: 핵심 가정 1~2개가 틀렸을 때 결론이 유지되는가?
  산출물:
    - {project}/thinking-loop/self-critique.md
```

### Interactive/Team 모드: Phase 3.7 맥락 체크인

self-critique 완료 후, 외부 리뷰 진행 전에 사용자에게 약점 분석 결과를 브리핑하며 맥락 체크인을 수행한다:

```
📋 Phase 3.7 약점 분석 결과

[weakness-checklist FLAG 항목 요약]
[self-critique 핵심 지적 요약]

🔍 맥락 체크인 (user-profile.yaml 기반):
1. 지적된 약점 중 보완할 수 있는 정보나 데이터를 갖고 있는가?
2. 빠진 이해관계자 관점이나 시각이 있는가?
3. 보고서에 반드시 추가해야 할 관점이 있는가?

→ 피드백 반영 + user-profile.yaml 갱신 후 외부 리뷰(또는 Phase 4) 진행
```

### Step 3: 외부 모델 리뷰 (선택적)

PM이 사용자에게 외부 모델 리뷰 옵션을 제시한다.

```
옵션:
  A. /ask codex — Codex에게 self-critique.md + strategy-articulations.md 전달하여 피드백 요청
  B. /ask gemini — Gemini에게 동일 자료 전달
  C. 사용자 직접 전달 — ChatGPT 등에서 받은 피드백을 붙여넣기
  D. 스킵 — 자기 비판만으로 충분

산출물: {project}/thinking-loop/external-review.md (선택 시)
```

### 모드별 적용

| 모드 | Step 1 (약점 체크리스트) | Step 2 (자기 비판) | Step 3 (외부 모델) |
|------|------------------------|-------------------|-------------------|
| Auto | 항상 실행 | FLAG 2건+ 시 자동 실행 | 스킵 |
| Interactive | 항상 실행 | 항상 실행 + 결과 공유 | 사용자에게 선택지 제시 |
| Team | 항상 실행 | 필수 실행 + 결과 토론 | 권장 (사용자에게 제안) |

### Phase 4 진입 조건 (업데이트)

```
필수:
  ☐ loop-convergence.md (converged: true)
  ☐ strategy-articulations.md 존재
  ☐ self-critique.md 존재
    예외: Auto 모드에서 약점 체크리스트 FLAG 0~1건이면 self-critique.md 면제

선택:
  ☐ external-review.md (있으면 report-writer가 참조)
```

## Phase 4: 전략 도출 + 보고서

### Step 4-A: 보고서 생성

```
1. PM이 report-writer 스폰
2. 입력: cross-domain-synthesis + thinking-loop 결과 + 전체 Division 출력
3. 보고서 구조: 피라미드 원칙 (결론 먼저 → 근거 전개)
4. 산출물:
   - {project}/reports/report-docs.md (전략 보고서)
```

## 세션 Checkpoint 관리

### checkpoint.yaml 업데이트 규칙

PM은 Phase 전환마다 `findings/checkpoint.yaml`을 자동 업데이트한다.

```yaml
# findings/checkpoint.yaml — 세션 연속성을 위한 구조화된 상태 파일
project: {project-name}
mode: auto | interactive | team
last_updated: YYYY-MM-DDTHH:MM:SS

# 현재 상태
current_phase: "phase-id"           # 예: "0-client-discovery", "1-division-research", "sync-round-1", "3.7-external-review"
current_status: pending | in-progress | gate-pending | completed

# Phase 완료 이력
phases_completed:
  - phase: "phase-id"
    completed_at: YYYY-MM-DDTHH:MM:SS
    output_files: ["파일 경로 목록"]
    user_approved: true | false      # 사용자 승인 게이트 결과
    divisions_completed: []          # Phase 1/2에서 Division 완료 목록 (해당 시)

# 사용자 의사결정 이력 (재개 시 재확인 불필요)
user_decisions:
  - decision: "의사결정 내용"
    phase: "phase-id"
    timestamp: YYYY-MM-DDTHH:MM:SS

# 복구 이력 (A3 자동 복구 메커니즘)
recovery_history: []
  # - tier: 1 | 2 | 3
  #   division: "{division}"
  #   timestamp: YYYY-MM-DDTHH:MM:SS
  #   trigger: "pane crash detected"
  #   result: success | failed

# 반복 카운트 (A4 반복 예산 정책)
iteration_counts:
  leaf_retry: {}        # {division: {leaf: count}}
  thinking_loop: 0
  qa_fix_loop: 0
  feedback_loop: 0

# 에스컬레이션 미처리 건
pending_escalations:
  - id: "ESC-###"
    from: "agent-id"
    description: "이슈 설명"
    status: awaiting-user | in-progress

# 되돌아가기 이력
backtracks: []
```

### Sync Round 전후 checkpoint 업데이트

```
Sync Round 시작 시:
  1. checkpoint.yaml의 current_phase를 "sync-round-{N}"으로 업데이트
  2. current_status를 "in-progress"로 설정

Sync Round 완료 시:
  1. phases_completed에 해당 Sync Round 추가
  2. output_files에 sync briefing 파일 경로 기록
  3. 사용자 게이트가 필요한 경우 user_approved: false로 기록
  4. 사용자 승인 후 user_approved: true로 갱신
  5. current_phase를 다음 Phase로 업데이트
  6. current_status를 "pending"으로 설정
```

### execution-trace.yaml 업데이트

PM이 에이전트 호출 전후에 `findings/execution-trace.yaml`을 업데이트한다.

```
Sync Round에서 fact-verifier 스폰 시:
  호출 전: execution-trace에 새 항목 추가 (id, agent: "fact-verifier", phase: "sync-round-{N}")
  호출 후: completed_at, duration_min, status, metrics 업데이트
    metrics (fact-verifier용):
      claims_produced: 0          # fact-verifier는 Claim을 생성하지 않으므로 0
      checks_performed: {N}       # 검증 수행 건수
      checks_passed: {N}
      checks_failed: {N}
      escalations: {N}

cross-domain-synthesizer 스폰 시:
  동일한 trace 기록 규칙 적용

상세 스키마: research-pm.md §에이전트 호출 추적 참조.
```

## Phase 5: QA + 자동 수정 루프

### 개요

보고서 품질을 기계적으로 보장하는 **자동 수정 루프**. Critical/Major 0건 달성 시 PASS로 루프 탈출한다 (최대 3회).

### Step 5-A: 초기 QA 실행

```
1. PM이 qa-orchestrator 스폰
2. qa-orchestrator가 6개 검증기를 순차 실행:

   === Layer 1: 기계적 검증 (기존) ===
   a. mechanical-validator: 수치 정합성 (합계, 비율, 환율)
   b. source-traceability-checker: [GF-###]/[S##] 태그 → 원본 대조
   c. report-auditor: 시맨틱 감사 (피라미드 구조, So What, Executive Summary 정합)

   === Layer 2: 신뢰도·공정성 검증 (신규) ===
   d. confidence-prominence-checker: confidence vs 배치 위치 정합성
      - confidence: low/medium 수치가 Executive Summary, 보고서 핵심 섹션, 핵심 논거에 사용되면 FAIL
      - 규칙: Executive Summary/보고서 서두 핵심 섹션의 수치는 confidence: high만 허용
      - confidence: low 수치 사용 시 반드시 "(추정치, confidence: low)" 주의문구 동반
      - 체크: "보수에서도 X" 같은 낙관적 프레이밍이 실제 데이터와 일치하는지
        (예: "보수에서도 원금 회수" → 실제 보수 하단이 적자이면 FAIL)

      구체적 알고리즘 (golden-facts.yaml 연동):
      ```
      Step 1: 보고서에서 수치 추출
        report-docs.md에서 숫자+단위 패턴 추출
        (예: "156~312억", "ROI 171~286%", "$41~81M")

      Step 2: golden-facts.yaml 매칭
        추출된 수치를 golden-facts.yaml의 facts[]와 대조
        매칭 기준: entity + metric + value 범위 일치
        매칭 실패(golden-facts에 없는 수치) → WARNING: 출처 불명 수치

      Step 3: confidence × 배치 위치 교차
        위치 분류:
          A등급 (고노출): Executive Summary, 핵심 결론 1~3번
          B등급 (중노출): 본문 섹션 제목, 테이블 헤더
          C등급 (저노출): 본문 상세, 부록, 별첨

        판정:
          confidence: high → A/B/C 모두 OK
          confidence: medium → B/C OK, A는 WARNING (주의문구 필수)
          confidence: low → C만 OK, A/B는 FAIL (격하 또는 주의문구 필수)
          confidence: unverified → 보고서 사용 금지 (FAIL)

      Step 4: 프레이밍 편향 검출
        패턴 매칭:
          "보수에서도 X" / "최악에서도 Y" → 실제 보수/최악 데이터의 하단과 대조
          "최소 X" → 해당 수치가 실제 최소값인지 검증
          "확실히/반드시/분명히" + confidence: low → FAIL (과신 표현)
      ```

   e. executability-checker: 실행 가능성 검증
      - 실행 카드(태스크)의 담당 인원 × 기간 vs 실제 가용 리소스 비교
      - 동시 진행 태스크 수가 담당 조직 규모 대비 현실적인지
      - 선후 의존관계가 있는 태스크의 시점이 맞는지
        (예: "데이터 엔지니어 필요"인 태스크가 "DE 채용" 태스크보다 앞에 오면 FAIL)

   f. audience-fit-checker: 청중 적합성 검증
      - 보고서 분량이 청중 유형 대비 적절한지
      - 전문용어가 정의 없이 본문에서 사용되면 FAIL (부록 정의만으로 불충분)
      - 내부 데이터 vs 외부 추정치의 비율을 명시하는지
      - 경영진이 반드시 물어볼 질문 3개에 대한 답이 있는지:
        · "비용 대비 효과가 확실한가?" → ROI 근거의 정직한 불확실성 명시
        · "경쟁사가 더 많이 쓰는데 우리는 괜찮은가?" → 규모 대비 비율 논리
        · "안 하면 어떻게 되는가?" → 비전환 비용의 confidence 명시

3. 산출물: {project}/qa/qa-report.md (이슈 목록 + 심각도)

Layer 2 검증기 도입 배경:
  Layer 1만으로는 "숫자가 맞는가"만 검증하고, "숫자를 정직하게 전달하는가"는 검증하지 못한다.
  confidence: low 수치를 핵심 논거로 사용하면 경영진 신뢰가 비가역적으로 훼손된다.
  cherry-picking(유리한 수치만 전면 배치)은 기계적 검증으로 잡을 수 없으므로 별도 검증기가 필요.
```

### Step 5-B: 자동 수정 루프

```
루프 조건: qa-report에 Critical 또는 Major 이슈가 1건 이상

  ┌──────────────────────────────────────────┐
  │  Round {N}                                │
  │                                           │
  │  1. report-fixer 스폰                      │
  │     - 입력: qa-report.md (이슈 목록)       │
  │     - 입력: report-docs.md                    │
  │     - 지시: "Major 이상 이슈만 최소 수정.   │
  │       Minor는 수정하되 의미 변경 금지."      │
  │     - 수정 원칙:                            │
  │       · 수치 불일치 → golden-facts.yaml 기준으로 통일 │
  │       · 소스 태그 불일치 → 매핑 테이블 기준 통일 │
  │       · So What 박스 누락 → 해당 섹션 말미에 추가 │
  │       · Executive Summary ↔ 본문 불일치 → 본문 기준으로 수정 │
  │                                           │
  │  2. 수정된 보고서 재검증                    │
  │     - mechanical-validator + source-traceability 재실행 │
  │     - 새로운 qa-report-round{N}.md 생성     │
  │                                           │
  │  3. 판정:                                  │
  │     - Critical/Major 0건 → PASS (루프 탈출) │
  │     - 이슈 잔존 → 다음 Round 진행           │
  │                                           │
  │  최대 반복: 3회                             │
  │  3회 후에도 미해결 → PM 에스컬레이션        │
  └──────────────────────────────────────────┘

산출물:
  - {project}/qa/qa-report.md (최종)
  - {project}/qa/qa-report-round{N}.md (각 라운드)
  - {project}/qa/fix-log.md (수정 이력)
```

### Step 5-C: PM 최종 확인

```
QA PASS 후 PM이 확인하는 체크리스트:
  □ 핵심 리서치 질문에 대한 명확한 답변이 보고서에 있는가?
  □ Client Brief의 제외 방향이 보고서에 포함되지 않았는가?
  □ 사용자 의사결정에 필요한 정보가 빠짐없이 제시되었는가?
  □ 가설(H-##) 검증 결과가 보고서에 반영되었는가?
  □ unverified Claim이 0건인가? (또는 명시적으로 [미확인] 태깅)

모두 통과 → Phase 5 완료, Phase 5.5(사용자 피드백) 또는 최종 전달로 진행
```

---

## 범용 피드백 수신 (모든 Phase에서 활성)

PM은 **Phase 5.5(보고서 완료 후)뿐 아니라 모든 Phase에서** 사용자의 변경 요청을 수신할 수 있다.

### 수신 규칙

```
1. 사용자 입력이 "변경 요청"으로 판단되면:
   - 현재 진행 중인 작업 일시 중단
   - L0~L3 피드백 분류 수행 (research-pm.md § 인터랙티브 피드백 분류 참조)
   - L0: 즉시 반영, 작업 재개
   - L1+: cascade 영향 분석 → 옵션+추천 제시 → 사용자 확인 후 실행

2. Division 병렬 실행 중(Phase 1/2) 피드백 수신 시:
   - 실행 중인 Division의 완료를 대기하지 않음
   - 영향받지 않는 Division은 계속 실행
   - 영향받는 Division만 중단/재실행 대상

3. Interactive/Team 모드: PM이 각 Phase 전환 시점에 능동적으로:
   "현재까지 결과를 보셨는데, 방향이나 전제를 수정하고 싶은 부분이 있으신가요?
    지금 바꾸면 영향 최소화가 가능합니다."
```

### 기존 피드백 체계와의 관계

| 기존 체계 | 역할 | 변경 사항 |
|----------|------|----------|
| Mid-Research 체크인 | 지정된 Phase 전환 시 사용자 게이트 | 그대로 유지 |
| 되돌아가기 프로토콜 (Type 1/2/3) | Phase 수준 되돌아가기 실행 | L0~L3 분류가 Type을 트리거 |
| Phase 5.5 피드백 루프 | 보고서 완료 후 피드백 | L0~L3 level 필드 추가 |
| **범용 피드백 수신 (신규)** | 모든 Phase에서 변경 요청 수신 + 분류 | **신규 추가** |

---

## Phase 5.5: 사용자 피드백 + 부분 재실행

### 목적

보고서 전달 후 사용자 피드백을 받아 **부분적으로 재실행**하여 보고서를 정제한다.
전체 파이프라인을 다시 돌리지 않고, 피드백 대상 영역만 선택적으로 업데이트한다.

### 트리거
Phase 5 완료 후, 사용자가 보고서를 검토하고 피드백을 제공할 때.
Auto 모드에서는 생략 가능.

### Step 5.5-A: 피드백 수집

```
PM이 사용자에게 보고서를 전달하며 구조화된 피드백을 요청:

📋 최종 보고서 전달

[보고서 파일]
  - report-docs.md (전략 보고서)

[피드백 가이드]
  아래 유형 중 해당하는 것을 선택하고 구체적으로 알려주세요:

  ① 사실 오류   — "Section X의 Y 수치가 Z여야 한다"
                   → 해당 Division 재검증
  ② 깊이 부족   — "Section X의 Y 분석이 부족하다. Z 관점을 추가해야"
                   → 해당 Division 추가 리서치
  ③ 방향 수정   — "A 전략 대신 B를 검토해야 한다"
                   → 새 가설 추가 후 부분 재실행
  ④ 형식/톤    — "Executive Summary가 너무 길다" / "톤을 더 공식적으로"
                   → report-writer 재실행
  ⑤ 승인       — "이대로 확정"
                   → 최종 확정, Phase 6(post-mortem)으로 진행

  예시 입력:
    "② Section 3.2 신규 카테고리 분석이 얕다.
     벤치마크 사례 3개 이상 + 성공/실패 요인을 추가해줘."

→ 유형 번호 + 대상 섹션 + 구체적 내용을 입력해주세요.
→ 여러 건이면 번호별로 나눠서 입력하시면 됩니다.
```

### Step 5.5-B: 피드백 분류 + 영향 범위 판정

```
PM이 피드백을 분류하고 재실행 범위를 결정:

feedback_analysis:
  - id: FB-01
    type: factual_error | depth_needed | direction_change | format_change
    level: L0 | L1 | L2 | L3    # 피드백 계층 분류 (아래 매핑 참조)
    description: "사용자 피드백 원문"
    affected_divisions: [market, finance]   # 영향받는 Division
    affected_claims: [MGN-02, FRV-01]       # 영향받는 Claim ID
    action: re_verify | deep_dive | new_hypothesis | rewrite
    scope: minimal | division | cross_division

영향 범위별 재실행 경로:
  minimal:        report-fixer만 재실행 (형식/톤 변경)
  division:       해당 Division Lead만 부분 재실행 → 합성 업데이트 → 보고서 수정
  cross_division: 해당 Division + 교차 영향 Division 재실행 → Sync Round 재실행 → 보고서 재작성

L계층 ↔ 기존 type 매핑:
  L0 (표현) → format_change → scope: minimal
  L1 (사실) → factual_error → scope: division
  L2 (가설) → direction_change → scope: division 또는 cross_division
  L3 (전제) → direction_change → scope: cross_division (Phase 0 되돌아가기 후보)

산출물: {project}/sync/feedback-analysis.yaml
```

### Step 5.5-C: 부분 재실행

```
scope: minimal 경우:
  1. report-fixer 스폰 → 피드백 반영 수정
  2. QA 재실행:
     - 기본: mechanical-validator + source-traceability 재실행
     - Action Title/SCR 관련 피드백 시: audience-fit-checker 재스폰
     - Playbook 관련 피드백 시: executability-checker 재스폰
     - 대량 Action Title 이슈 (5건+): report-fixer 배치 수정 → audience-fit-checker 재검증 → 잔여 시 2회차

scope: division 경우:
  1. 해당 Division Lead에 추가 지시서 작성
     → {project}/sync/feedback-{division}.md
  2. Lead CLI 재투입 (해당 Division만)
  3. Lead 완료 → 업데이트된 division-synthesis.yaml
  4. report-writer 재실행 (변경된 부분만 업데이트)
  5. QA 재실행

scope: cross_division 경우:
  1. 영향받는 Division들에 추가 지시서 작성
  2. Lead CLI 재투입 (해당 Division들)
  3. cross-domain-synthesizer 재실행
  4. 사고 루프 재실행 (해당 가설 관련만)
  5. Phase 3.7 External Review 재실행 (self-critique.md 갱신)
  6. report-writer 재실행
  7. QA 재실행
```

### Step 5.5-D: 재전달 + 반복

```
수정된 보고서를 사용자에게 재전달:

📋 보고서 업데이트 (피드백 반영)

[변경 사항]
  - FB-01: "주력 제품 감소율 -61% → -58%로 수정 (최신 데이터 반영)"
  - FB-02: "신규 카테고리 분석 심화 추가 (Section 3.2)"

[변경 추적]
  - 수정된 섹션에 [UPDATED] 마커 표시
  - 이전 버전: reports/report-docs-v1.md (자동 백업)

→ 추가 피드백이 있으시면 계속 입력해주세요.
→ "확정"이면 최종 보고서로 확정합니다.

최대 피드백 라운드: 3회 (초과 시 PM이 수렴 판정)
```

### 모드별 차이

| 단계 | Auto | Interactive | Team |
|------|------|-------------|------|
| Phase 5.5 | 생략 (바로 확정) | 1~2회 피드백 | 최대 3회 피드백 + 토론 |
| 재실행 범위 | N/A | 사용자 결정 | 팀 합의 |
| 버전 관리 | N/A | v1, v2 자동 백업 | v1, v2, v3 자동 백업 |

---

## Phase 6: Post-mortem + 학습 전이 (자동)

### 목적

프로젝트 완료 후 **자동으로** 교훈을 추출하여 다음 프로젝트에 전이한다.
PM이 사용자 확정(Phase 5.5 ⑤승인) 직후 자동 실행.

### Step 6-A: Post-mortem 자동 생성

```
PM이 프로젝트 전체를 회고하여 post-mortem.yaml을 자동 작성:

{project}/post-mortem.yaml:

project: {project-name}
completed_at: YYYY-MM-DD
mode: auto | interactive | team

# 실행 통계
stats:
  total_phases: 8                    # 0 ~ 5.5 + QA 라운드
  total_agents_spawned: {N}
  total_claims: {N}
  verification_pass_rate: "{N}%"
  qa_rounds: {N}
  feedback_rounds: {N}
  escalations: {N}
  backtracks: {N}
  elapsed_days: {N}

# 잘 된 것
what_worked:
  - category: process | data | agent | framework
    description: "설명"
    reusable: true | false           # 다음 프로젝트에서 재사용 가능한지

# 문제가 된 것
what_failed:
  - category: process | data | agent | framework
    description: "설명"
    root_cause: "근본 원인"
    resolution: "해결 방법"
    preventable: true | false        # EP 패턴으로 등록할 수 있는지

# 새로 발견된 EP 패턴 후보
new_ep_candidates:
  - description: "패턴 설명"
    trigger: "어떤 상황에서 발생하는지"
    prevention: "어떻게 방지하는지"

# 다음 프로젝트 추천 사항
recommendations:
  - "유사 주제 리서치 시 이 Division에 더 많은 리소스 배분"
  - "이 데이터 소스는 신뢰도가 낮으므로 대체 필요"
```

### Step 6-B: 학습 전이

```
다음 프로젝트의 Phase 0에서 PM이 자동으로 수행:

1. 모든 프로젝트의 post-mortem.yaml 스캔
2. 현재 프로젝트와 유사한 주제/도메인의 post-mortem 발견 시:
   - what_failed + recommendations를 Research Plan에 반영
   - new_ep_candidates를 EP 경고에 추가
3. 사용자에게 참고 정보로 제시:

   📋 이전 프로젝트 교훈 참고

   [{project-name}] (2026-03-15)
   - 주의: Finance Division의 주력 제품 매출 데이터가 3가지 기준선으로 혼용됨
     → 매출 기준선을 Phase 0에서 사전 합의 권장
   - 추천: 신규 카테고리는 벤치마크 데이터가 제한적
     → 사용자 내부 데이터 제공 시 품질 크게 향상
```

---

## Cascade 영향 분석 (L1+ 피드백 시 필수)

사용자 피드백이 L1 이상으로 분류되면, PM은 변경 사항의 cascade 영향을 추적한다.

### 산출물 의존 체인

```
Client Brief (00-client-brief.md)
    ↓
Research Plan (01-research-plan.md) + hypotheses.yaml
    ↓
Division Briefs (division-briefs/{div}.md)
    ↓
Division Findings (findings/{div}/division-synthesis.yaml)
    ↓
Cross-domain Synthesis (sync/cross-domain-synthesis.md)
    ↓
Thinking Loop (thinking-loop/*.md)
    ↓
Strategy Articulations (thinking-loop/strategy-articulations.md)
    ↓
External Review (thinking-loop/self-critique.md)
    ↓
Report (reports/report-docs.md)
```

### 분석 절차

```
Step 1: 변경 시작점 식별
  - 사용자 피드백이 위 체인의 어느 노드에 해당하는가?
  - L1(사실): findings 노드
  - L2(가설): hypotheses.yaml 노드
  - L3(전제): Client Brief 노드

Step 2: 하류 영향 추적
  - 변경 시작점부터 하류의 각 노드를 순회
  - 각 노드에서: "이 변경이 해당 산출물을 무효화하는가?" (Yes/No)
  - Yes이면: 해당 노드 + 이후 모든 노드가 재검증/재생성 대상
  - No이면: 해당 노드에서 cascade 중단

Step 3: Division 영향 범위
  - 무효화된 노드에 관련된 Division 목록 생성
  - 해당 Division의 Claim 중 영향받는 Claim ID 식별

Step 4: 영향 보고서 생성
  PM → 사용자:
    "이 변경의 cascade 영향:
     - 변경 시작점: {노드명}
     - 무효화되는 산출물: {목록}
     - 영향받는 Division: {목록}
     - 영향받는 Claim: {ID 목록}
     - 유지 가능한 산출물: {목록}
     - 재실행 필요 범위: {시작 Phase} → {현재 Phase}"
```

---

## 되돌아가기 (Backtrack) 실행 프로토콜

> 되돌아가기의 판단 기준, 유형, 비용 계산은 `escalation-protocol.md` 참조.
> 이 섹션은 **사용자 트리거 → PM 실행 → 복귀**의 구체적 UX와 실행 메커니즘을 정의한다.

### 사용자 트리거 방법

```
어느 Phase에서든 사용자가 자연어로 되돌아가기를 요청할 수 있다:

  "가설을 바꾸고 싶어"           → Phase 0.5로 되돌아가기
  "시장 분석이 잘못됐어"         → Phase 1 Market Division 재실행
  "전제 자체가 틀렸어"           → Phase 0 Client Brief 재설정
  "Merge 분석을 더 깊이 해줘"    → 해당 Division 부분 재실행
  "이 가정을 바꿔서 다시 해봐"   → 영향받는 Phase부터 재실행

PM은 자연어를 분석하여 되돌아가기 유형과 범위를 자동 판정한다.
```

### PM의 되돌아가기 처리 흐름

```
사용자 요청 접수
    ↓
Step 1: 영향 분석
  PM이 요청을 분석하여 다음을 판정:
    - 되돌아갈 Phase: 0 | 0.5 | 1 | Sync1 | 2 | Sync2 | 3 | 3.7 | 4 | 5
    - 영향받는 Division: [market, product, ...] 또는 all
    - 영향받는 가설: [H-01, H-03, ...] (해당 시)
    - 영향받는 Claim: [MGN-02, FRV-01, ...] (해당 시)
    ↓
Step 2: 비용 추정 + 사용자 확인
  PM → 사용자:

    📋 되돌아가기 분석

    [요청] "가설 H-01을 바꾸고 싶다"

    [영향 분석]
      되돌아갈 Phase: Phase 0.5 (가설 생성)
      영향받는 Division: Market, Capability (H-01 검증 담당)
      재실행 범위: Phase 0.5 → Phase 1(해당 Division만) → Sync R1 → Phase 2 → ... → 보고서
      기존 산출물: 자동 백업 (findings-backup-{timestamp}/)

    [비용 추정]
      재작업 에이전트: ~12개 (2 Division × 6 에이전트)
      예상 소요: Phase 1 대기 시간 + PM 처리 15분
      유지되는 것: Product, Finance Division 산출물 (영향 없음)

    [대안]
      A. 되돌아가기 — H-01 수정 후 영향 Division 재실행
      B. 현재 위치에서 보정 — 보고서에서 H-01 관련 부분만 수정 (한계 명시)
      C. 취소 — 되돌아가기 안 함

    → 어떻게 할까요? [A/B/C]

    ↓
Step 3: 실행 (사용자가 A 선택 시)
```

### 되돌아가기 유형별 실행 절차

#### Type 1: Phase 0.5 되돌아가기 (가설 변경)

```
트리거: "가설을 바꾸고 싶어" / "다른 방향을 검토하고 싶어"

실행:
  1. 기존 산출물 백업
     mkdir {project}/findings-backup-{timestamp}/
     cp -r {project}/findings/ {project}/findings-backup-{timestamp}/

  2. hypotheses.yaml 수정
     - 사용자와 가설 수정/추가/삭제
     - 변경된 가설의 verification_plan 갱신

  3. 영향 Division 판정
     - 변경된 가설의 verification_plan에 포함된 Division만 재실행
     - 영향 없는 Division은 기존 산출물 유지

  4. Division Briefs 갱신
     - 영향 Division의 briefs에 새 가설 검증 지시 반영

  5. 영향 Division만 재실행
     PM (Bash): spawn-leads.sh 대신 해당 Division만 개별 스폰
     tmux send-keys로 해당 pane에만 재지시 (기존 세션 활용 가능)
     또는 새 tmux 세션 생성 (기존 종료된 경우)

  6. .done 폴링 → Sync Round 재실행 → 이후 Phase 순차 진행

checkpoint.yaml 업데이트:
  backtracks:
    - id: BT-001
      from_phase: "3-thinking-loop"    # 되돌아가기 시점
      to_phase: "0.5-hypothesis"        # 되돌아간 Phase
      reason: "H-01 가설 변경"
      affected_divisions: [market, capability]
      backup_path: "findings-backup-20260319T143000/"
```

#### Type 2: Phase 1 되돌아가기 (Division 재실행)

```
트리거: "시장 분석이 틀렸어" / "이 데이터가 잘못됐어"

실행:
  1. 기존 산출물 백업 (해당 Division만)
     cp -r {project}/findings/{division}/ {project}/findings/{division}-backup-{timestamp}/

  2. 문제 원인 반영
     - 데이터 오류 → data-registry 수정 + 해당 소스 제외/교체
     - 분석 오류 → Division Brief에 수정 지시 추가
     - 범위 부족 → Division Brief에 추가 분석 지시

  3. 해당 Division만 재실행
     PM (Bash):
       # 기존 tmux 세션이 있으면 해당 pane에 재지시
       tmux send-keys -t research-v2:{pane} "division-briefs/{division}.md를 다시 읽고 Phase 1을 재실행하라. 수정사항: ..." Enter

       # tmux 세션이 없으면 개별 스폰
       claude --agent {division}-lead --dangerously-skip-permissions "{project}/division-briefs/{division}.md를 읽고 Phase 1을 재실행하라."

  4. 다른 Division은 유지 (영향 없으면)

  5. .done 폴링 → Sync Round부터 재실행
```

#### Type 3: Phase 0 되돌아가기 (전면 재설정)

```
트리거: "전제 자체가 틀렸어" / "리서치 방향을 완전히 바꿔야 해"

실행:
  1. 전체 산출물 백업
     mv {project}/findings/ {project}/findings-backup-{timestamp}/
     # 활성화된 Division에 대해 동적으로 생성
     mkdir -p {project}/findings/{활성 Division 목록}

  2. Client Brief 재작성
     PM이 사용자와 재인터뷰 (변경 부분만)

  3. Research Plan 재수립

  4. Phase 0.5부터 전체 재실행
     (init-project.sh는 불필요 — 디렉토리 구조는 유지)

  5. 전체 파이프라인 재실행

checkpoint.yaml: 전체 리셋 + backtrack 이력 기록
```

### tmux Lead 재투입 (종료된 경우)

```
Phase 2 이후에 되돌아가기 시, 기존 Lead CLI가 이미 종료되었을 수 있다.

PM의 재투입 전략:

  Case A: tmux 세션 'research-v2'가 살아있는 경우
    → 해당 Division pane에 tmux send-keys로 재지시
    → 전체 재실행이면 spawn-leads.sh --auto 재실행

  Case B: tmux 세션이 없는 경우
    → spawn-leads.sh 재실행 (전체) 또는
    → 개별 Division만 새 tmux pane으로 스폰:

    PM (Bash):
      tmux new-session -d -s research-v2-rerun -n "rerun"
      tmux send-keys -t research-v2-rerun "claude --dangerously-skip-permissions --agent {division}-lead '{project}/division-briefs/{division}.md를 읽고 Phase 1을 재실행하라.'" Enter

  PM이 Bash 도구로 자동 실행하므로 사용자는 "응"만 답하면 됨.
```

### 산출물 버전 관리

```
되돌아가기 시 기존 산출물은 항상 백업한다:

  전체 백업: {project}/findings-backup-{YYYYMMDD}T{HHMMSS}/
  Division 백업: {project}/findings/{division}-backup-{YYYYMMDD}T{HHMMSS}/

  보고서 백업: {project}/reports/report-docs-v{N}.md (기존 Phase 5.5과 동일)

백업 정리:
  - 프로젝트 완료(Phase 6) 후 PM이 사용자에게 백업 삭제 확인
  - 최신 백업 1개는 유지 권장
```

### checkpoint.yaml 되돌아가기 업데이트

```
되돌아가기 시 checkpoint.yaml 업데이트:

  1. current_phase를 되돌아간 Phase로 변경
  2. current_status를 "in-progress"로 설정
  3. backtracks 배열에 되돌아가기 이력 추가:
     - id: BT-{###}
       timestamp: YYYY-MM-DDTHH:MM:SS
       type: hypothesis | division | full
       from_phase: "되돌아가기 시점의 Phase"
       to_phase: "되돌아간 Phase"
       affected_divisions: [division 목록]
       reason: "사유"
       backup_path: "백업 경로"
  4. phases_completed에서 되돌아간 Phase 이후를 제거하지 않음
     (이력 보존 — 재완료 시 새로운 항목이 추가됨)
```

### 모드별 되돌아가기 UX

| 동작 | Auto | Interactive | Team |
|------|------|-------------|------|
| 사용자 트리거 | 불가 | "가설 바꾸고 싶어" → PM 처리 | 동일 |
| PM 자동 감지 | 불가 | 불가 | PM이 모순 감지 시 되돌아가기 제안 |
| 영향 분석 | — | PM 자동 | PM 자동 + 사용자에게 상세 제시 |
| 실행 확인 | — | "A/B/C?" → 사용자 선택 | 동일 + 비용/대안 상세 토론 |
| 부분 재실행 | — | 영향 Division만 | 영향 Division만 |

---

## Context 관리 규칙

에이전트 간 맥락 전달 시 컨텍스트 윈도우 초과를 방지하기 위한 규칙.

### 원칙

```
1. 파일 기반 전달: 에이전트 간 데이터는 YAML/MD 파일로 전달한다 (프롬프트 내 임베딩 금지)
2. 레이어별 접근: 상위 에이전트는 하위 출력의 Layer 0만 읽는다 (필요 시에만 드릴다운)
3. 요약 우선: Division 출력 전체가 아닌 division_summary + key_findings만 전달
```

### 역할별 읽기 범위

| 역할 | 읽는 범위 | 드릴다운 조건 |
|------|----------|-------------|
| PM | Division Lead의 `division_summary` + `key_findings` | tension/모순 발견 시 Layer 1 |
| cross-domain-synthesizer | 전체 Division의 `division_summary` + `key_findings` | 교차 인사이트 도출 시 해당 Claim의 Layer 1 |
| Division Lead | 리프/Sub-lead의 Layer 0 (Claims) 전체 | VL-1.5/VL-2 시 Layer 1~2 |
| Sub-lead | 리프의 Layer 0 (Claims) 전체 | 삼각 검증 시 Layer 1~2 |
| fact-verifier | 검증 대상 Claim의 Layer 1~3 | 항상 전체 드릴다운 |

### Agent 호출 시 프롬프트 크기 제한

```
Lead → Sub-lead 스폰 시 전달하는 정보:
  - Client Brief 요약 (해당 Division 관련 부분만, ~300 tokens)
  - 분석 범위 + 초점 (~200 tokens)
  - 지정 프레임워크 + 적용 목적 (~100 tokens)
  - 데이터 소스 목록 (~100 tokens)
  - EP 경고 (~100 tokens)
  - 출력 저장 경로
  합계: ~800 tokens 이내
  ※ 현재 Market Division만 Sub-lead 레이어 사용. 다른 Division은 Lead→Leaf 직접 구조.

Lead → Leaf 스폰 시 전달하는 정보:
  - Client Brief 요약 (해당 도메인 부분만, ~500 tokens)
  - 분석 범위 + 초점 (~200 tokens)
  - 데이터 소스 목록 (~100 tokens)
  - EP 경고 (~100 tokens)
  - 출력 저장 경로
  합계: ~1,000 tokens 이내

PM → Division Lead 스폰 시 전달하는 정보:
  - Client Brief 파일 경로 (내용은 에이전트가 직접 읽기)
  - Research Plan 해당 Division 부분 (~300 tokens)
  - 사용자 데이터 경로
  - EP 경고 + 제외 방향 (~200 tokens)
  합계: ~700 tokens 이내 (파일 경로 전달, 내용은 에이전트가 Read)
```

### Data Registry 프로토콜

모든 프로젝트에서 `{project}/data/data-registry.csv`를 운영한다. 리서치 과정에서 수집/제공/전처리된 모든 데이터의 메타데이터 카탈로그.

```
템플릿: core/templates/data-registry-template.csv
초기화: PM이 Phase 0에서 복사 생성

ID 체계:
- U-###: 사용자 제공 데이터 (PM이 등록)
- D-###: 크롤링/API/웹 수집 데이터 (Leaf 에이전트가 등록)
- P-###: 전처리 산출물 (data-preprocessor가 등록)

필수 필드:
  data_id, name, type, source, format, file_path,
  description, usage, collected_by, date, reliability

선택 필드:
  url, notes

등록 책임:
- PM: 레지스트리 초기화 + U-### 등록 + 완전성 점검
- Leaf 에이전트: 웹/API 데이터 수집 시 D-### 행 추가
  → findings/{division}/{sub}/{agent}.yaml 저장과 동시에 레지스트리 등록
- data-preprocessor: 전처리 CSV 생성 시 P-### 행 추가
- Lead: Sub-lead/Leaf가 누락한 등록이 있으면 합성 시 보완

type 값: user-provided | crawled | api | preprocessed | report | reference
reliability 값: High | Medium | Low | Unverified
```

### 대용량 출력 처리

```
Division 출력이 클 때:
  1. 리프 출력은 findings/{division}/{sub-domain}/{agent}.yaml 파일로 저장
  2. Lead는 파일을 읽어서 합성 — 합성 결과만 상위에 전달
  3. PM은 division-synthesis.yaml의 Layer 0만 읽음
  4. 드릴다운 필요 시 해당 파일을 직접 Read
```

---

## 실행 깊이 관리

### Agent 네스팅 규칙

```
에이전트 계층(Tier)과 실행 네스팅 깊이(Level)를 구분한다.

에이전트 계층 (Tier) — 조직 구조상 위치:
  Tier 0: PM
  Tier 1: Division Lead
  Tier 2: Sub-lead
  Tier 3: Leaf

실행 네스팅 깊이 (Level) — Agent 도구 호출 깊이:
  Level 0: PM (TeamCreate로 Division Lead 스폰)
  Level 1: Division Lead (Agent로 Sub-lead 또는 Leaf 스폰)
  Level 2: Sub-lead (Agent로 Leaf 스폰) ← 최대 깊이

  최대 실행 깊이: Level 2 (Agent 호출 2단계까지 허용)
  Level 3 이상의 네스팅은 금지한다.
```

### Sub-lead 실행 전략

Sub-lead(Level 2)가 리프를 스폰할 때, 컨텍스트 깊이 문제를 완화하기 위해:

```
전략 A — Agent 직접 스폰 (기본):
  Sub-lead가 Level 2에서 Agent 도구로 리프를 병렬 스폰
  적용: 리프 수 3개 이하, 각 리프의 예상 출력이 작은 경우

전략 B — 파일 기반 핸드오프 (대규모):
  1. Sub-lead가 리프별 지시서를 파일로 작성
     → findings/{division}/{sub-domain}/instructions/{leaf}.md
  2. Division Lead가 해당 리프를 Level 1에서 직접 스폰 (네스팅 1단계 절약)
  3. 리프 출력을 Sub-lead가 파일로 읽어서 합성
  적용: 리프 수 4개 이상이거나, 각 리프의 예상 출력이 큰 경우

판단 주체: Division Lead가 Sub-lead 스폰 시 전략을 지정
```

### 깊이별 도구 사용

| 실행 Level | 에이전트 (Tier) | 하위 스폰 도구 | 비고 |
|-----------|----------------|-------------|------|
| Level 0 | PM (Tier 0) | TeamCreate | Division Lead N명 병렬 (Research Plan 기준) |
| Level 1 | Division Lead (Tier 1) | Agent | Sub-lead + Leaf |
| Level 2 | Sub-lead (Tier 2) | Agent | Leaf (전략 A) |
| Level 1 | Division Lead (Tier 1) | Agent | Leaf (전략 B — Sub-lead 대신 직접) |

---

## 모드별 차이

| 단계 | Auto | Interactive | Team |
|------|------|------------|------|
| Client Discovery | Quick (5~7) | Quick/Deep 선택 | Deep 권장 |
| **Phase 0.5 가설 정렬** | 자동 확정 | 사용자 검토+수정 | 사용자 검토+토론 |
| Phase 1 종료 후 | 바로 Sync 1 | 사용자 게이트 | 사용자 게이트 |
| Sync Round 1 후 | 바로 Phase 2 | 사용자 피드백 | 사용자 피드백 + 토론 |
| Sync Round 2 후 | 바로 사고 루프 | 사용자 확인 | 사용자 확인 |
| 사고 루프 후 | 바로 External Review | 사용자 확인 | 사용자 확인 |
| **Phase 3.7 External Review** | 체크리스트만 (FLAG 2+시 자기비판) | 체크리스트+자기비판+외부모델 선택 | 체크리스트+자기비판 필수+외부모델 권장 |
| **Phase 4 보고서** | 자동 생성 | 보고서 구성 확인 | 보고서 구성 토론 |
| EP-026 게이트 | 보고서에 🔶 플래그 | 사용자 확인 | 사용자 확인 |
| **Phase 5 QA** | 자동 수정 루프 (3회) | 자동 수정 + 사용자 확인 | 자동 수정 + 사용자 확인 |
| **Phase 5.5 피드백** | 생략 | 1~2회 피드백 | 최대 3회 + 토론 |
| 되돌아가기 | 없음 | 사용자 트리거만 | 전방위 (자동+팀+사용자) |
| Mid-Research 체크인 | 없음 | Sync R1, R2, Phase 3.7 후 | Sync R1, R2, Phase 3.7 후 + 토론 |

### user-profile.yaml SSOT 갱신 시점

`{project}/user-profile.yaml`은 사용자의 도메인 전문성, 증거 기준, 선호/기피 방향 등을 기록하는 SSOT이다.
PM이 아래 시점에서 갱신하며, 갱신 시 `update_log`에 변경 내역과 타임스탬프를 기록한다.

| 시점 | 갱신 내용 | 트리거 |
|------|----------|--------|
| Phase 0 (Pass 1) | 초기 프로필 생성 | Intake Interview 완료 |
| Phase 0.5 (가설 정렬) | 사용자 가설 채택/수정/추가 시 선호 방향, 우선순위 반영 | Step 0.5-C 사용자 응답 |
| Sync R1 후 체크인 | 사용자 피드백에서 드러난 전문 영역, 추가 맥락 반영 | 맥락 체크인 응답 |
| Sync R2 tension 해소 시 | real_tension에 대한 사용자 직관/판단 반영, 리스크 허용도 갱신 | 맥락 체크인 응답 |
| Phase 3.7 후 체크인 | 보완 정보, 추가 관점 반영 | 맥락 체크인 응답 |
| Phase 5.5 피드백 | 보고서 피드백에서 드러난 증거 기준, 선호 변화 반영 | 피드백 수집 |

**Auto 모드**: Phase 0에서 생성 후 갱신 없음. 사용자 응답을 기반으로 `inferred` 프로필 + 보수적 기본값 적용.
**Interactive 모드**: Phase 0, 0.5, Sync R1, Sync R2, Phase 3.7 — 최대 5회 갱신.
**Team 모드**: Interactive와 동일 + 토론 기반 심층 갱신.

## 파일 구조 (프로젝트별)

```
{project}/
├── 00-client-brief.md
├── 00.5-data-quality-report.md       (해당 시)
├── 01-research-plan.md
├── hypotheses.yaml                    (Phase 0.5: 전략 가설 목록)
│
├── data/                              (사용자 데이터 + 전처리 결과)
│   ├── raw/
│   └── processed/
│       ├── market/
│       ├── product/
│       ├── capability/
│       ├── finance/
│       ├── people-org/          (확장 Division, 활성화 시)
│       ├── operations/          (확장 Division, 활성화 시)
│       └── regulatory/          (확장 Division, 활성화 시)
│
├── findings/                          (에이전트 출력)
│   ├── market/
│   │   ├── quick-scan.yaml            (Phase 0.5: 기초 스캔)
│   │   ├── market-sizing.yaml
│   │   ├── customer-analysis.yaml
│   │   ├── competitive-landscape.yaml
│   │   ├── channel-landscape.yaml
│   │   ├── market-dynamics.yaml
│   │   ├── opportunity-matrix.yaml   (market-lead: 지역×세그먼트×채널 기회 매트릭스)
│   │   └── division-synthesis.yaml   (market-lead)
│   ├── product/
│   │   ├── quick-scan.yaml            (Phase 0.5)
│   │   ├── product-offering.yaml
│   │   ├── value-differentiation.yaml
│   │   ├── go-to-market.yaml
│   │   ├── pricing-monetization.yaml
│   │   ├── product-competitiveness-matrix.yaml  (product-lead)
│   │   └── division-synthesis.yaml              (product-lead)
│   ├── capability/
│   │   ├── quick-scan.yaml            (Phase 0.5)
│   │   ├── technology-ip.yaml
│   │   ├── technology-ip.yaml
│   │   ├── execution-readiness.yaml
│   │   ├── strategic-assets.yaml
│   │   ├── capability-gap-matrix.yaml           (capability-lead)
│   │   └── division-synthesis.yaml              (capability-lead)
│   ├── finance/
│   │   ├── quick-scan.yaml            (Phase 0.5)
│   │   ├── revenue-growth.yaml
│   │   ├── investment-returns.yaml
│   │   ├── financial-viability-matrix.yaml      (finance-lead)
│   │   └── division-synthesis.yaml              (finance-lead)
│   │
│   │   # === 확장 Division (활성화 시 생성) ===
│   ├── people-org/                    (People & Organization, 활성화 시)
│   │   ├── quick-scan.yaml
│   │   ├── talent-strategy.yaml
│   │   ├── org-design.yaml
│   │   ├── culture-engagement.yaml
│   │   └── division-synthesis.yaml
│   ├── operations/                    (Operations, 활성화 시)
│   │   ├── quick-scan.yaml
│   │   ├── process-excellence.yaml
│   │   ├── supply-chain.yaml
│   │   ├── infrastructure.yaml
│   │   └── division-synthesis.yaml
│   └── regulatory/                    (Regulatory & Governance, 활성화 시)
│       ├── quick-scan.yaml
│       ├── compliance-status.yaml
│       ├── regulatory-outlook.yaml
│       ├── esg-governance.yaml
│       └── division-synthesis.yaml
│
├── sync/
│   ├── round-1-briefing.md
│   ├── round-2-briefing.md
│   ├── cross-domain-synthesis.md
│   └── feedback-analysis.yaml         (Phase 5.5: 피드백 분류)
│
├── thinking-loop/                    (V1: 05.5-thinking-loop/)
│   ├── why-probe.md                  (V1: why-probe-insights.md)
│   ├── strategic-challenge.md
│   └── loop-convergence.md
│
├── reports/
│   ├── report-docs.md
│   └── report-docs-v{N}.md           (Phase 5.5: 버전 백업)
│
├── qa/
│   ├── qa-report.md                   (최종)
│   ├── qa-report-round{N}.md          (자동 수정 라운드별)
│   ├── fix-log.md                     (수정 이력)
│   ├── mechanical-validation.md
│   ├── source-traceability.md
│   └── audit-log.md
│
└── post-mortem.yaml                   (Phase 6: 프로젝트 회고 + 학습 전이)
```

---

## 자동 복구 메커니즘 (3-Tier Recovery)

Phase 실행 중 에이전트 장애 발생 시 아래 3단계 복구를 순차 시도한다.

### Tier 1: Leaf 재스폰 (Lead 자율)
- Leaf 비정상 종료 감지 → Lead가 1회 자동 재스폰
- 재스폰 후 재실패 → Lead → PM 에스컬레이션

### Tier 2: Division 재스폰 (PM 자율)
- Division Lead CLI 크래시 → PM이 tmux pane 상태 확인
- 해당 Division만 `spawn-phase.sh --divisions {div}` 로 재스폰
- checkpoint.yaml에 recovery 이력 기록:
  ```yaml
  recovery_history:
    - tier: 2
      division: {division}
      timestamp: YYYY-MM-DDTHH:MM:SS
      trigger: "pane crash detected"
      result: success | failed
  ```

### Tier 3: 세션 복구 (PM → 사용자)
- PM CLI 자체 크래시 → `/research` 재실행 시 checkpoint.yaml 자동 감지
- 미완료 Phase의 구체적 재개 포인트 제시:
  - 어떤 Division이 어디까지 완료했는지 (.done 파일 기반)
  - 어떤 Cross-cutting 에이전트가 실행/미실행인지
  - 마지막 checkpoint 상태에서 이어서 진행 가능 여부 판정

### 복구 제한
- Tier 1: Division당 최대 2회 (동일 Leaf)
- Tier 2: 프로젝트당 최대 3회 (모든 Division 합산)
- Tier 2 초과 → PM이 사용자에게 "시스템 안정성 경고" + 수동 재시작 권고

---

## 반복 예산 정책 (Iteration Budget)

시스템 전체의 반복 횟수를 관리하여 무한 루프를 방지한다.

| 루프 | 최대 반복 | 초과 시 처리 | 독립/누적 |
|------|----------|------------|---------|
| Leaf 자율 반복 (VL-1 반려→재작업) | 3회 | confidence: low 태깅 후 반환 | 독립 (Phase 1/2 각각 리셋) |
| VL-1.5 재확인 (Lead→Leaf) | 1회 | 범위 표기 후 합성 진행 | 독립 |
| 사고 루프 (Phase 3) | 2회 | PM → 사용자 에스컬레이션 | 독립 |
| QA 수정 루프 (Phase 5) | 3회 | PM → 사용자 에스컬레이션 (unfixable_after_3rounds) | 독립 |
| 피드백 루프 (Phase 5.5) | Interactive 2회 / Team 3회 | 사용자에게 추가 반복 확인 | 독립 |

### 규칙
- 각 루프는 **독립적**으로 카운트 (사고 루프 2회 + QA 3회를 합산하지 않음)
- Leaf 자율 반복은 Phase 1과 Phase 2에서 각각 리셋
- checkpoint.yaml에 `iteration_counts` 섹션으로 현재 각 루프의 반복 횟수 추적:
  ```yaml
  iteration_counts:
    leaf_retry: {division: {leaf: count}}
    thinking_loop: N
    qa_fix_loop: N
    feedback_loop: N
  ```
- 전체 프로젝트의 되돌아가기(Backtrack) 횟수: Auto=0, Interactive=최대 2회, Team=최대 3회

---

## Phase 전환 조건 테이블

PM은 아래 조건을 확인하여 Phase 전환을 판정한다. 모드에 따라 자동 진입 또는 사용자 게이트를 적용한다.

| 전환 | 진입 조건 | Auto 모드 | Interactive/Team 모드 |
|------|----------|----------|---------------------|
| **Phase 0.5 → Phase 1** | hypotheses.yaml 확정 + division-briefs/*.md 전부 생성 | 자동 진입 → spawn-leads.sh 실행 | 사용자에게 가설 확인 후 진입 |
| **Phase 1 → Sync Round 1** | 모든 활성 Division의 `.done` 파일 존재 (phase: 1) | 자동 진입 | "Phase 1 완료. Sync Round 1 진입?" 사용자 게이트 |
| **Sync Round 1 → Phase 2** | `sync/round-1-briefing.md` + 모든 `sync/phase2-{div}.md` 생성 완료 | spawn-phase.sh 2 자동 실행 | 사용자 게이트 |
| **Phase 2 → Sync Round 2** | 모든 활성 Division의 `.done` 파일 존재 (phase: 2) | 자동 진입 | 사용자 게이트 |
| **Sync Round 2 → Phase 3** | `sync/cross-domain-synthesis.md` + `sync/tension-resolution.yaml` 생성 | 자동 진입 | 사용자 게이트 |
| **Phase 3 → Phase 3.7** | `thinking-loop/loop-convergence.md`의 `converged: true` + `strategy-articulations.md` 존재 | 자동 진입 | 사용자 게이트 |
| **Phase 3.7 → Phase 4** | `self-critique.md` 존재 (Auto: FLAG 0~1건이면 면제) | 자동 진입 | 사용자 게이트 |
| **Phase 3 미수렴** | 사고 루프 2회 반복 후에도 `converged: false` | PM이 사용자에게 에스컬레이션 | 사용자에게 선택지 제시 (강제 수렴/추가 반복/방향 전환) |
| **Phase 4 → Phase 5** | `reports/report-docs.md` 생성 완료 | 자동 진입 | 사용자 게이트 |
| **Phase 5 → Phase 5.5** | QA PASS (P1 0건 + P2 0건) | 생략 — 바로 확정 (§모드별 차이 참조) | 사용자 게이트 → 피드백 수집 |
| **Phase 5.5 → 완료** | 사용자 확정 (또는 Auto 생략 시 QA PASS 즉시) | 자동 확정 | 사용자 승인 후 확정 |

### 전환 감지 메커니즘
- **Phase 1/2 완료 감지**: `spawn-leads.sh` 백그라운드 모니터가 `.done` 파일 폴링 → PM에 알림
- **Phase 3~5 완료 감지**: PM CLI 내에서 Agent tool 실행 후 출력 파일 존재 확인
- **checkpoint.yaml 자동 갱신**: 각 Phase 전환 시 `current_phase`, `current_status`, `last_updated` 업데이트
