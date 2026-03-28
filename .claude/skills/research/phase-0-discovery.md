# Phase 0: Client Discovery + Research Plan

## Step 0-A: Intake Interview (필수)
`research-pm.md`의 Client Discovery 프로토콜에 따라 사용자 인터뷰 실행.
- Quick (7~10개 질문): Auto 모드
- Deep (15~20개 질문): Interactive/Team 모드
- **Data Intake 질문 필수**: 질문 5번 답변 후 후속 질문(5-a/b/c) 반드시 수행
- 산출물: `{project}/00-client-brief.md`

### 적응형 2-Pass 인터뷰 구조

질문은 **그룹 0(사용자 인터뷰)** → **그룹 1~4(기존)** 순서로 진행하되,
2-Pass 구조로 효율과 깊이를 모두 확보한다.

```
Pass 1 — Quick Profile + 리서치 범위:
  그룹 0 Quick 질문(Q0-1~Q0-3) + Codex 추가 질문 3개
  + 그룹 1(목적과 방향)
  → 사용자 프로파일 초안 생성 + gap 식별

Pass 2 — gap 기반 보완 (Interactive/Team만):
  2-A: Pass 1에서 식별된 gap 보완 질문 (자동 생성)
  2-B: 파악된 산업/도메인 기반 심층 질문 (Q0-4~Q0-7 + 그룹 2~4)

합산 최대 10개 (CLAUDE.md/메모리에 이미 있는 정보는 스킵).
Auto 모드: Pass 1만 실행 후 자동 진행.
```

### 그룹 0: 사용자 인터뷰 (그룹 1 앞에 실행)

기존 그룹 1~4 질문은 "무엇을 조사할 것인가"에 집중하지만,
그룹 0은 **"누가 왜 이 리서치를 필요로 하는가"**를 먼저 파악한다.
이 정보는 보고서 톤, 근거 수준, 프레임워크 선택에 직접 영향을 준다.

```
━━ 그룹 0/5: 사용자 인터뷰 ━━

Quick (모든 모드):
  Q0-1. 이 분야에서 본인의 역할과 경험은?
  Q0-2. 이 리서치 결과를 본인이 직접 실행하는가, 누군가에게 전달하는가?
  Q0-3. 이미 시도했거나 검토한 것이 있는가? 결과는?

Codex 교차검토 추가 질문 (Pass 1 Quick에 통합):
  Q0-C1. 이 리서치 결과로 누가 무엇을 결정/실행하나?
  Q0-C2. 어떤 수준의 근거면 현재 생각을 바꿀 수 있나?
  Q0-C3. 이미 마음이 기운 방향이 있다면?

Deep (Interactive/Team) 추가:
  Q0-4. 이 주제에서 특별히 잘 아는 세부 영역과 잘 모르는 영역은?
  Q0-5. 의사결정에서 가장 중요한 기준은?
  Q0-6. 리스크에 대한 태도는? 실패 시 감내 가능한 범위?
  Q0-7. 가용 리소스는? (시간, 예산, 인력, 인프라)
```

### Client Brief 산출물에 User Profile 포함

Step 0-A 완료 시, `{project}/00-client-brief.md`에 아래 구조를 **첫 번째 섹션으로** 포함한다.
그룹 0 답변을 구조화하여 이후 Phase 전체에서 참조한다.

```yaml
## 사용자 프로파일
domain_expertise:
  level: "expert | intermediate | novice"
  focus_areas: ["영역1"]
  experience_summary: "경험 요약"
  previous_attempts: "이미 시도한 것 + 결과"
decision_context:
  role: "직접 실행자 | 의사결정자 | 보고 대상자"
  stakeholders: ["이해관계자"]
  implementation_capacity: "high | medium | low"
risk_profile:
  tolerance: "aggressive | balanced | conservative"
  key_constraints: ["제약조건"]
  available_resources: "시간/예산/인력"
evidence_threshold: "어떤 수준의 근거면 결정을 바꾸는가"
preferred_direction: "이미 기운 방향 (편향 보정용)"
```

- `preferred_direction`은 Phase 3 Red Team에서 편향 보정 입력으로 활용
- `evidence_threshold`는 보고서 근거 수준(VL) 결정에 반영
- `domain_expertise.level`에 따라 보고서 설명 깊이 조정

## Step 0-A.5: 도메인 탐지 (Domain Discovery)

Client Discovery 완료 후, Research Plan 작성 전에 도메인을 탐지한다.

1. `domains/` 디렉토리 스캔 → 사용 가능한 도메인 목록 확인
   - `example/` 디렉토리는 제외
2. 도메인 선택:
   a. 1개만 있으면 자동 선택
   b. 2개 이상이면 Client Brief 주제와 매칭하여 선택
   c. 적합한 도메인 없으면 `core/` 프레임워크만 사용 (도메인 없이 진행)
3. 선택된 도메인의 `frameworks.md`, `data-sources.md` 존재 확인
4. Research Plan에 `domain`, `domain_path` 필드 기록

## Step 0-B: Research Plan (필수)
Client Brief 기반으로 리서치 설계.
- Division 활성화, Leaf 배치, 프레임워크 선택, EP 경고
- 산출물: `{project}/01-research-plan.md`

> **Research Plan에 Decision Frame 필수 포함**:
> `core/orchestration/sync-protocol.md`의 "Decision Frame" 섹션에 정의된 스키마를 따른다.
> Decision Questions 3~5개 + Decision Tree + Kill Criteria 2~3개를 01-research-plan.md에 기록.

### Division Pool 활성화 판정

Research Plan 작성 시, Client Brief 키워드/맥락 기반으로 확장 Division 활성화를 판정한다.

- 조직/인재/문화 키워드 → **People & Org (H)** 활성화
- 프로세스/운영/인프라 키워드 → **Operations (O)** 활성화
- 규제/법률/ESG 키워드 → **Regulatory (R)** 활성화

핵심 4개(Market, Product, Capability, Finance)는 기본 활성. 확장은 주제에 따라 PM이 판정.
Research Plan에 `active_divisions` 목록을 명시적으로 기록한다.

### 프로젝트 초기화 시 Division 옵션 반영

```
./scripts/init-project.sh {project} --divisions "{활성화된 확장 Division 약어, 쉼표 구분}"
# 예: ./scripts/init-project.sh my-project --divisions "people-org,regulatory"
# 확장 Division 없으면 옵션 생략 (핵심 4개만 생성)
```

## Step 0-B.5: API Readiness Check (필수)
Research Plan 기반으로 필요 API를 동적 판정. `check-api-keys.sh` 실행.
- 필수 키 미설정 시 사용자에게 발급 안내 또는 "키 없이 진행" 확인

## Step 0-C: Data Intake + 전처리 (조건부 필수)
- 사용자 데이터 **있음** → data-preprocessor 스폰 → 전처리 → 정합성 검증. **건너뛸 수 없다.**
- 사용자 데이터 **없음** → checkpoint에 `preprocessor_run: not_needed` 명시적 기록

## Step 0-C.5: 전처리 데이터 정합성 검증 (조건부 필수)
사용자 데이터가 있는 경우 반드시 수행:
- data-preprocessor 자체 검증 (VL-1): 합계 일치, 행 수 보존
- fact-verifier 교차 검증 (VL-1.5): 원본 vs 전처리 스팟체크 3건+
- PM 최종 확인: 핵심 수치 1~2개 직접 대조

## Phase 0 완료 게이트 (필수)
Division Briefs 작성 전, `research-pm.md`의 Phase 0 완료 게이트 체크리스트를 전수 확인.
하나라도 미완료이면 해당 단계로 돌아간다.

## Step 0.5: Factsheet + Golden Facts
- 대상 기업 팩트시트 확보 → 사용자 승인
- fact-verifier로 golden-facts.yaml 초기화
- **필수 게이트**: `findings/golden-facts.yaml` 파일이 존재하고 최소 1건의 fact가 등록되어야 Phase 0.5로 진행 가능
- golden-facts.yaml이 비어있으면 → fact-verifier 스폰하여 팩트시트 수치를 등록

## Phase 0.5: 가설 생성 + 사용자 정렬

Phase 0 완료 후, Phase 1 진입 전에 실행. `sync-protocol.md` Phase 0.5 참조.

### Step 0.5-A: Quick Scan
- 활성 Division Lead에 Quick Scan 지시 (Agent 병렬, 30분 제한)
- 각 Division이 `findings/{division}/quick-scan.yaml` 출력
- headlines + opportunities/threats Top 3

### Step 0.5-A.5: 1차 데이터 갭 식별 + 수집 가이드 (필수)
Quick Scan 결과를 바탕으로, **공개 데이터만으로는 답할 수 없는 질문**을 명시적으로 식별한다:

```yaml
# hypotheses.yaml 내 primary_data_gaps 섹션
primary_data_gaps:
  - question: "공개 데이터로 답할 수 없는 질문"
    why_needed: "이 답이 없으면 어떤 가설/전략이 검증 불가한지"
    ideal_source: "이상적 데이터 소스 (예: 내부 매출 데이터, 고객 인터뷰, 전문가 의견)"
    fallback: "대안 접근법 (예: 공시 데이터 역산, 유사 기업 벤치마크, 범위 추정)"
    impact_if_missing: high | medium | low
```

- Interactive/Team 모드: 사용자에게 갭 목록을 제시하고 추가 데이터 제공 가능 여부 확인
- Auto 모드: 갭 목록을 기록하고 fallback 전략으로 자동 진행
- 이 갭 목록은 최종 보고서의 "미해소 불확실성" 섹션에 자동 반영된다

1차 데이터 수집 가이드 생성 (Interactive/Team, ideal_source가 인터뷰/서베이인 경우):
```yaml
primary_research_guide:
  - gap_id: "PDG-01"
    method: interview | survey | expert_consultation
    target: "인터뷰 대상 (예: 사업부장, 현지 파트너, 업계 전문가)"
    key_questions:
      - "질문 1 — 이 질문으로 확인하려는 것"
      - "질문 2"
    expected_output: "이 데이터가 확보되면 어떤 가설이 검증되는지"
    deadline: "Phase 1 시작 전 / Phase 2 시작 전"
```
- PM이 자동 생성하여 사용자에게 제공
- 사용자가 인터뷰 결과를 제공하면 data/user-provided/에 저장 → data-preprocessor 처리
- Phase 2 시작 전까지 결과 미입수 시: fallback 전략으로 진행, 보고서에 "[1차 데이터 미확보]" 명시

### Step 0.5-B: 가설 공동 도출
- Auto: PM이 Quick Scan 합성 → 3~5개 가설 자동 생성 → 자동 확정
- Interactive/Team: **사용자와 함께** 가설을 도출하는 대화형 프로세스

```
Interactive/Team 가설 공동 도출:

1. PM이 Quick Scan 결과 요약을 공유:
   "각 Division의 Quick Scan 결과를 요약하면:
    - Market: {핵심 발견 1줄}
    - Product: {핵심 발견 1줄}
    - Capability: {핵심 발견 1줄}
    - Finance: {핵심 발견 1줄}"

2. PM이 사용자에게 먼저 물음:
   "이 결과를 보고 어떤 가설이 떠오르시나요?
    본인의 경험이나 직관에서 나오는 것도 좋습니다.
    저도 몇 가지 떠오르는 게 있습니다."

3. 사용자 가설 수렴 (0개~N개):
   - 사용자가 가설을 제시하면 → hypotheses.yaml에 [사용자 제안] 태깅
   - 사용자가 "없어" 또는 "잘 모르겠어" → PM이 주도
   - ★ 근거 수집 필수: 사용자 가설마다 "왜 그렇게 생각하시는지" 반드시 확인
     → hypotheses.yaml의 user_rationale 필드에 기록
     → 근거가 경험적이면 검증 우선순위 상승, 직관적이면 반증 검토 강화

4. PM이 보충 가설 제시:
   "저는 이런 가설들이 떠오릅니다:
    H-01: [opportunity] {가설}
    H-02: [risk] {가설}
    H-03: [assumption] {가설}

    사용자님이 제시한 가설과 합치면 총 {N}개입니다."

5. 겹치는 가설 병합 + 우선순위 공동 결정

6. 사용자 전문 영역 기반 추가 가설 유도:
   Client Brief의 domain_expertise.focus_areas를 참조하여,
   사용자가 잘 아는 영역에서 PM이 추가 가설을 유도한다:
   "이 영역에서 {focus_area} 경험이 있으시다고 하셨는데,
    혹시 {관련 패턴/트렌드}에 대해 가설이 있으신가요?"
   → 전문 영역에서 나오는 가설은 검증 가치가 높으므로 우선순위 boost

핵심: 에이전트가 "정답을 제시"하는 것이 아니라 "함께 생각"하는 대화.
사용자의 도메인 지식이 가설 단계에서부터 반영되어야 리서치 방향이 정확해진다.
```

- 가설 유형: opportunity / risk / assumption
- 각 가설에 verification_plan (Division별 검증 과제) 포함
- 산출물: `{project}/hypotheses.yaml`

#### hypotheses.yaml 사용자 가설 구조

사용자가 제시한 가설에는 반드시 `user_rationale` 필드를 포함한다:

```yaml
hypotheses:
  - id: H-01
    type: opportunity
    statement: "가설 내용"
    source: user          # user | pm | joint
    user_rationale: "사용자가 설명한 근거 — 경험, 데이터, 직관 등"
    rationale_type: experiential | data_based | intuitive
    verification_plan:
      - division: market
        task: "검증 과제"
```

- `rationale_type: experiential` → 검증 우선순위 상승 (현장 경험 기반)
- `rationale_type: intuitive` → 반증 검토 강화 (Phase 3 Red Team 우선 타겟)
- `rationale_type: data_based` → 데이터 재확인 후 fast-track

### Step 0.5-C: 사용자 가설 정렬
- Auto: PM이 자동 확정
- Interactive/Team: 사용자에게 구조화된 선택지 제시

```
━━ 전략 가설 검토 ━━

  H-01: [opportunity] "국내 B2B SaaS 시장의 ERP 카테고리가 포화 상태이나 버티컬 SaaS 전환 기회 존재"
  H-02: [risk] "경쟁사 3사의 동시 신규 서비스 출시로 마케팅 비용 급등 예상"
  H-03: [assumption] "글로벌 진출 시 동남아 시장이 가장 높은 ROAS를 보일 것"

  선택:
  1. 전체 채택 (이대로 진행)
  2. 특정 가설 수정 (예: "2번 수정: 경쟁사를 2사로 한정")
  3. 가설 추가 (예: "IP 라이선싱 기회도 검토해줘")
  4. 특정 가설 삭제 (예: "3번 삭제")
  5. 우선순위 변경 (예: "2번을 must로 올려줘")

  → 번호 + 내용을 입력하세요 (복수 가능):
```

Phase 3 Red Team 결과 검토 시에도 동일 패턴:
```
  Red Team 결과:
  - Strong 1건: "핵심 전제 X가 반증됨 — 근거: [GF-015]"
  - Moderate 2건: "숨겨진 가정 Y, Z"

  선택:
  1. 전략 수정 반영 (insight-synthesizer가 보강)
  2. Strong 반론에 대한 추가 데이터 수집 요청
  3. 현 전략 유지 (리스크 수용 — 보고서에 명시)
```

- 사용자가 "이대로 진행" 또는 "1" → Phase 1 진입
- 사용자가 수정 → hypotheses.yaml 갱신

### Step 0.5-D: Division Briefs에 가설 + User Context 반영
- 확정된 가설의 verification_plan을 Division Briefs에 삽입
- Leaf 출력의 iteration_log에 가설 ID(H-##) 태깅 지시

#### Division Brief User Context 섹션 (~100 tokens)

각 Division Brief에 **User Context** 섹션을 추가한다.
Client Brief의 사용자 프로파일에서 해당 Division과 관련된 정보를 압축 전달:

```yaml
## User Context
background: "사용자의 역할/경험 중 이 Division과 관련된 부분 1줄"
decision_role: "직접 실행자 | 의사결정자 | 보고 대상자"
risk_tolerance: "aggressive | balanced | conservative"
expertise_relevance: "이 Division 주제에 대한 사용자 전문성 수준 + 영역"
user_hypotheses:
  - "H-## 중 이 Division이 검증 담당인 사용자 가설 (user_rationale 포함)"
key_constraints: ["이 Division 분석에 영향을 주는 제약조건"]
```

- Lead가 분석 깊이/톤을 사용자 프로파일에 맞춰 조정하는 데 사용
- `expertise_relevance`가 높으면: 기초 설명 생략, 전문 용어 사용 가능
- `expertise_relevance`가 낮으면: 충분한 배경 설명 + 용어 해설 포함
- `user_hypotheses`의 `user_rationale`을 통해 Lead가 사용자 관점을 이해

### Phase 0.5 완료 게이트
- [ ] Quick Scan 활성 Division 전체 완료
- [ ] 1차 데이터 갭 식별 완료 + hypotheses.yaml에 primary_data_gaps 기록
- [ ] 가설 3~5개 도출 + hypotheses.yaml 저장
- [ ] 사용자 정렬 완료 (Auto: 자동 확정)
- [ ] Division Briefs에 가설 검증 지시 반영
- [ ] checkpoint.yaml에 phase: "0.5-hypothesis" 기록
