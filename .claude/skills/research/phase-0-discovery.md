# Phase 0: Client Discovery + Research Plan

## Step 0-A: Intake Interview (필수)
`research-pm.md`의 Client Discovery 프로토콜에 따라 사용자 인터뷰 실행.
- Quick (5~7개 질문): Auto 모드
- Deep (12~15개 질문): Interactive/Team 모드
- **Data Intake 질문 필수**: 질문 5번 답변 후 후속 질문(5-a/b/c) 반드시 수행
- 산출물: `{project}/00-client-brief.md`

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
# 예: ./scripts/init-project.sh my-project --divisions "H,R"
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

### Step 0.5-B: 가설 도출
- PM이 Quick Scan 합성 → 3~5개 전략 가설 생성
- 가설 유형: opportunity / risk / assumption
- 각 가설에 verification_plan (Division별 검증 과제) 포함
- 산출물: `{project}/hypotheses.yaml`

### Step 0.5-C: 사용자 가설 정렬
- Interactive/Team: 사용자에게 가설 목록 제시 → 채택/수정/추가
- Auto: PM이 자동 확정
- 사용자가 "이대로 진행" → Phase 1 진입
- 사용자가 수정 → hypotheses.yaml 갱신

### Step 0.5-D: Division Briefs에 가설 반영
- 확정된 가설의 verification_plan을 Division Briefs에 삽입
- Leaf 출력의 iteration_log에 가설 ID(H-##) 태깅 지시

### Phase 0.5 완료 게이트
- [ ] Quick Scan 활성 Division 전체 완료
- [ ] 가설 3~5개 도출 + hypotheses.yaml 저장
- [ ] 사용자 정렬 완료 (Auto: 자동 확정)
- [ ] Division Briefs에 가설 검증 지시 반영
- [ ] checkpoint.yaml에 phase: "0.5-hypothesis" 기록
