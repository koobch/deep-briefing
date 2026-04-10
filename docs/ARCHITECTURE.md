# Deep-Briefing Architecture

## 에이전트 토폴로지

```
                              사용자
                                |
                          ┌─────┴─────┐
                          │ research-pm │  ← PM CLI (오케스트레이터)
                          └─────┬─────┘
                                |
              ┌─────────────────┼─────────────────┐
              |                 |                  |
     ┌────────┴────────┐  ┌────┴────┐   ┌────────┴────────┐
     │   Division Pool  │  │  사고   │   │     QA Layer     │
     │    (Phase 1~2)   │  │  루프   │   │    (Phase 5)     │
     └────────┬────────┘  │(Phase 3)│   └────────┬────────┘
              |           └────┬────┘            |
    ┌────┬────┼────┬────┐     |        ┌────┬───┼───┬────┐
    M    P    C    F  +확장    |        AFC  EXC  RA  RF  RW
    |    |    |    |           |
   Leaf Leaf Leaf Leaf    ┌───┼───┬───┐
                          LP  SC  RT  IS
```

### 범례

| 약어 | 에이전트 | 역할 |
|------|---------|------|
| **M/P/C/F** | market/product/capability/finance-lead | 핵심 4 Division Lead |
| **+확장** | people-org/operations/regulatory-lead | 확장 3 Division Lead |
| **Leaf** | 도메인별 전문 분석가 (동적 스폰) | 실제 데이터 수집 + 분석 |
| **LP** | logic-prober | Why Chain 수직 검증 |
| **SC** | strategic-challenger | 5-레인 수평 도전 |
| **RT** | red-team | 적대적 반론 (Devil's Advocate) |
| **IS** | insight-synthesizer | 도전 결과 통합 + 수렴 판정 |
| **AFC** | audience-fit-checker | Action Title + SCR + 경영진 적합성 |
| **EXC** | executability-checker | Implementation Playbook 검증 |
| **RA** | report-auditor | 논리 완결성 + SCR 구조 감사 |
| **RF** | report-fixer | 이슈 자동 수정 (최대 3회) |
| **RW** | report-writer | 보고서 + 슬라이드 생성 |

추가: **fact-verifier** (VL-3 교차 검증), **cross-domain-synthesizer** (Division 간 합성), **data-preprocessor** (데이터 전처리)

## Phase 흐름

```
Phase 0    Client Discovery + Research Plan
    |      PM이 사용자 인터뷰 → Client Brief → Research Plan → Division Briefs
    v
Phase 0.5  가설 수립 + 1차 데이터 갭 식별
    |      Quick Scan → 가설 3~5개 → 사용자 정렬 → primary_data_gaps
    v
Phase 1    Division 병렬 리서치 (tmux N-pane)
    |      각 Division Lead가 독립 CLI에서 Leaf 스폰 → 자율 반복 → .done 시그널
    v
Sync R1    교차 라우팅 + Tension 식별
    |      PM이 Division 출력 수집 → cross_domain 태깅 → tension(T-##) 식별 → fact-verifier VL-3
    v
Phase 2    교차 반영 심화 리서치
    |      각 Division이 다른 Division의 질문에 답변 + tension 해소 + 분석 심화
    v
Sync R2    Tension 해소 + Cross-domain Synthesis
    |      tension 3유형 분류 (data_error/perspective_gap/real_tension)
    |      cross-domain-synthesizer → 교차 인사이트 도출
    v
Phase 3    사고 루프 (Thinking Loop)
    |      Step 1: logic-prober (Why Chain) + strategic-challenger (5-레인 도전) [병렬 실행]
    |      Step 2: → red-team (적대적 반론) [Auto --deep / Interactive,Team 기본]
    |      Step 3: → insight-synthesizer (통합 + 수렴 판정)
    |      수렴 조건: 논리 단절 P1/P2 0 + Critical/Major 블라인드 스팟 0 + Strong 반론 대응 + BASE 자력 실현
    v
Phase 4-A  세로형 보고서 생성
    |      report-writer: SCR 스토리라인 → report-docs.md
    |      Trust Badge (검증 배지) 삽입 + Implementation Playbook
    v
Phase 4-B  슬라이드 덱 생성 (선택적)
    |      slide-writer: report-docs.md → slide-deck.html + slide-outline.yaml + slide-meta.yaml
    |      core/style/ 22개 슬라이드 유형 적용
    v
Phase 4-C  경영진 원페이퍼 (선택적, 4-B와 병렬 가능)
    |      brief-writer: report-docs.md → one-pager.md (1~2p BLUF 구조)
    |      Key Findings 3개 + Recommended Actions + Risk Alert
    v
Phase 4.5  출처 레지스트리
    |      generate-source-registry.py → source-registry.csv (14컬럼)
    v
Phase 5    QA 자동 수정 루프
    |      qa-orchestrator: 5개 내장 검증 + 3개 에이전트 스폰
    |      → verify-facts.py (수치 검증)
    |      → verify-source-traceability.py ([S##]/[GF-###] 태그 검증)
    |      → audience-fit-checker (Action Title + SCR)
    |      → executability-checker (Playbook 검증)
    |      → report-auditor (논리 감사)
    |      이슈 발견 → report-fixer → 재검증 (최대 3회)
    v
Phase 5.5  사용자 피드백 + 부분 재실행 (선택)
    |      피드백 분류 → 영향 범위 판정 → minimal/division/cross_division 재실행
    v
Phase 6    Post-mortem + 학습 전이 (자동)
```

## 데이터 플로우

### 파일 기반 통신 (CLI 간 직접 통신 없음)

```
PM CLI                    Division Lead CLI              QA Layer
  |                              |                          |
  |-- division-briefs/*.md ----->|                          |
  |                              |-- findings/{div}/*.yaml  |
  |                              |-- findings/{div}/.done -->|
  |<--- findings/ 수집 ----------|                          |
  |                                                         |
  |-- sync/round-1-briefing.md ->|                          |
  |-- sync/phase2-*.md --------->|                          |
  |                              |-- findings/ 업데이트 --->|
  |                                                         |
  |-- thinking-loop/*.md --------|------------------------->|
  |-- reports/*.md --------------|------------------------->|
  |                              |                          |
  |                              |         qa/qa-report.md  |
  |<---------------------------------------------------------|
```

### Golden Facts SSOT

```
fact-verifier (유일한 쓰기 권한)
      |
      v
findings/golden-facts.yaml  ←── 모든 에이전트 읽기
      |
      ├── report-writer: [GF-###] 태그로 인용
      ├── red-team: 전제 반증 시 참조
      ├── qa-orchestrator: mechanical-validator가 대조
      └── finance-lead: Scenario P&L 가정값 참조
```

## 검증 체계 (4단계)

```
VL-1   Leaf 자가 검증     2소스+, 반증 검토, confidence 태깅
  |
VL-1.5 Lead 삼각 검증     리프 간 교차 검증 + 스팟체크 3건+
  |
VL-2   Division 정합성    엔터티/시점/정의 일관성 (Lead 수준)
  |
VL-3   교차 검증          Division 간 모순 탐지 (fact-verifier)
  |
QA     보고서 검증         8+1단계 파이프라인 (내장4 + 에이전트3 + Decision Audit + 수정 루프)
```

## 에스컬레이션 체계

| Type | 범위 | 예시 |
|------|------|------|
| 1 | 데이터 이슈 | API 실패, 소스 접근 불가 |
| 2 | 가설/분석 이슈 | 핵심 가설 반증, Division 전제 붕괴 |
| 3 | Division 간 이슈 | Claim 모순, 전략 전제 검증 실패 |
| 4 | 사고 루프/QA 이슈 | Red Team Strong 2건+, Action Title 전수 위반 |
| 5 | 시스템 이슈 | CLI 크래시, API 쿼터 소진 |
| 6 | QA 최종 실패 | 3회 수정 후 Critical/Major 잔존 |

## 확장 포인트

| 확장 | 방법 |
|------|------|
| 도메인 추가 | `cp -r domains/example/ domains/{domain}/` → frameworks/data-sources/benchmarks 커스텀 |
| Division 추가 | `.claude/agents/{name}-lead.md` 생성 + CLAUDE.md Division Pool 테이블에 등록 |
| Leaf 에이전트 추가 | `domains/{domain}/agents/{name}.md` 또는 Lead 동적 스폰 |
| 차트 유형 추가 | `generate-charts.py`에 ChartData 플래그 + Selector 분기 + Renderer 메서드 |
| QA 모듈 추가 | `qa-orchestrator.md`의 Step에 모듈 추가 + 전용 에이전트 파일 생성 |
| API 추가 | `scripts/ADDING-API.md` 참조 → api-caller.py + data-sources.md |
