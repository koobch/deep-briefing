# Phase 2~5: 교차 심화 + 보고서 + QA

## Sync Round 1

활성 Division 전체 .done 확인 후 PM CLI에서 자동 진행:

1. 활성 Division의 `division-synthesis.yaml` 읽기 (Layer 0만)
2. Cross-domain 라우팅 (질문/시사점 배포)
3. Tension 식별 (T-01, T-02, ...)
4. fact-verifier 스폰 (Agent) → VL-3 교차검증
5. Sync Briefing 작성 → `{project}/sync/round-1-briefing.md`

Interactive/Team 모드: 사용자에게 브리핑 제시 + 피드백 수집.

## Phase 2: 교차 반영 심화 리서치

### Step 2-A: Phase 2 지시서 작성

Sync Briefing + 사용자 피드백을 기반으로 각 Division용 Phase 2 지시서 작성:
```
{project}/sync/
├── phase2-market.md          # 핵심
├── phase2-product.md         # 핵심
├── phase2-capability.md      # 핵심
├── phase2-finance.md         # 핵심
├── phase2-people-org.md      # 확장 (활성화 시)
├── phase2-operations.md      # 확장 (활성화 시)
└── phase2-regulatory.md      # 확장 (활성화 시)
```

### Step 2-B: Lead CLI에 Phase 2 자동 전송

PM이 사용자 확인 후 **PM CLI에서 바로 전송**한다. 사용자가 tmux에 들어갈 필요 없음.

```
Auto 모드:
  PM이 사용자 확인 없이 즉시 실행.
  → ./scripts/send-phase2.sh {project-name} --auto

Interactive/Team 모드:
  PM → 사용자:
    Phase 2 지시서 작성 완료.
    N개 Lead CLI에 Phase 2 지시를 전송합니다.
    → 진행할까요? [Y/n]

  사용자: "응"

PM 실행 (Bash 도구):
  ./scripts/send-phase2.sh {project-name} --auto

  ※ tmux send-keys로 활성 Division pane에 자동 전송
  ※ Lead들이 Phase 2 지시서를 읽고 자동 실행 시작
```

### Step 2-C: .done 자동 폴링

Phase 1과 동일한 방식으로 PM이 .done 파일을 자동 폴링한다.
Lead들이 Phase 2 완료 후 .done 업데이트 → PM이 감지 → Sync Round 2 자동 진입.

```
PM 실행 (Bash 도구, 반복):
  .done 파일의 phase 값이 2로 업데이트되었는지 확인

전체 완료 → PM → 사용자:
  ✅ 활성 Division Phase 2 완료!
  Sync Round 2 + 사고 루프를 시작합니다.
  → 진행할까요? [Y/n]
```

## Sync Round 2 + 사고 루프

Lead CLI들은 Phase 2 완료 후 종료 가능. 이후는 PM CLI에서 진행:

1. cross-domain-synthesizer 스폰 (Agent) → Division 간 교차 인사이트
   - 확장 Division 활성화 시 핵심-확장 간 교차 패턴도 탐색
   - 상세: `core/protocols/fact-check-protocol.md` 교차검증 규칙 참조
2. logic-prober 스폰 (Agent) → Why Chain (수직 검증)
3. strategic-challenger 스폰 (Agent) → 5-레인 도전 (수평 검증)
4. red-team 스폰 (Agent) → 적대적 반론 구성 (Devil's Advocate)
   - Team/Interactive 모드: 기본 활성화
   - Auto 모드: `--deep` 옵션 시에만 활성화
   - 산출물: `{project}/thinking-loop/red-team-report.md`
5. insight-synthesizer 스폰 (Agent) → 도전 결과 + Red Team 결과 반영
6. PM 수렴 판정 (최대 2회 반복)

## Phase 3.7: External Review

Phase 3(사고 루프) 수렴 완료 후 자동 진입.

PM이 external-reviewer 에이전트를 스폰한다:

```
external-reviewer 스폰 (Agent 도구)
  입력: strategy-articulations.md + loop-convergence.md + cross-domain-synthesis.md
  출력: thinking-loop/self-critique.md (+ external-review.md 선택)
```

**실행 흐름:**

1. **약점 체크리스트** (항상): 확증 편향, 반증 부족, 집단 사고, 관점 고정, 대안 부족 — 5항목 PASS/FLAG
2. **자기 비판** (FLAG 2건+ 또는 Interactive/Team): 프레이밍/접근법/빠진 관점/강건성 비판
3. **외부 모델 리뷰** (선택): /ask codex, /ask gemini, 또는 사용자 직접 전달

**모드별:**
- Auto: 체크리스트만 (FLAG 2+시 자기비판 자동)
- Interactive: 체크리스트 + 자기비판 → 사용자에게 외부 모델 선택지 제시
- Team: 체크리스트 + 자기비판 필수 + 외부 모델 권장

**Phase 4 진입 조건:**
loop-convergence.md(converged: true) + strategy-articulations.md 존재 + self-critique.md 존재
(Auto 모드: FLAG 0~1건이면 self-critique.md 면제)

## Phase 4: 보고서 생성

1. report-writer 스폰 (Agent)
2. 산출물: `{project}/reports/report-docs.md`

상세: `sync-protocol.md` Phase 4 참조.

## Phase 5: QA + 자동 수정 루프

### Step 5-A: 초기 QA
1. qa-orchestrator 스폰 (Agent)
   - mechanical-validator → source-traceability-checker → report-auditor 순차 실행
2. **source-url-verifier 검증** (QA 파이프라인 내 자동 실행):
   - **L1 (접근성)**: 보고서 내 모든 URL에 HTTP HEAD 요청 → 200 OK 확인
   - **L2 (관련성)**: URL 페이지 내용이 인용 맥락과 실제로 관련되는지 검증
   - 실패한 URL은 `qa-report.md`에 `[URL-FAIL]` 태그로 기록
   - 상세: `/source-check` 스킬 또는 `core/protocols/fact-check-protocol.md` 참조
3. 산출물: `{project}/qa/qa-report.md`

### Step 5-B: 자동 수정 루프
1. Critical/Major 이슈 존재 시 → report-fixer 자동 스폰
2. 수정 → 재검증 → 판정 (최대 3회 반복)
3. Critical/Major 0건 = PASS → 루프 탈출 (최대 3회)
4. 3회 후 미해결 → PM 에스컬레이션
5. 산출물: `qa/qa-report-round{N}.md` + `qa/fix-log.md`

### Step 5-C: PM 최종 확인
- 핵심 질문 답변 완결성, unverified 0건, 가설(H-##) 검증 결과 반영 확인

상세: `sync-protocol.md` Phase 5 참조.

## Phase 5.5: 사용자 피드백 + 부분 재실행

### 트리거
Phase 5 완료 후, 사용자가 보고서를 검토하고 피드백 제공 시.
Auto 모드에서는 생략.

### 워크플로우
1. **피드백 수집**: 사용자에게 보고서 전달 + 피드백 유형 안내
2. **피드백 분류**: PM이 영향 범위 판정 (minimal / division / cross_division)
3. **부분 재실행**: 영향 범위에 따라 해당 Division만 또는 교차 Division 재실행
4. **재전달**: 수정된 보고서 + 변경 추적 마커([UPDATED]) 전달
5. **반복**: 최대 3회 피드백 라운드

### 영향 범위별 재실행
- **minimal**: report-fixer만 → QA 재실행
- **division**: 해당 Division Lead 재투입 → 합성 업데이트 → 보고서 수정 → QA
- **cross_division**: 복수 Division 재투입 → Sync Round 재실행 → 보고서 재작성 → QA

상세: `sync-protocol.md` Phase 5.5 참조.

## Phase 4.7: HTML/PDF 내보내기

### 트리거
Phase 5 QA PASS + Phase 5.5 피드백 확정 이후.
MD 정본이 최종 형태로 확정된 시점에서 **단 1회** 실행.

### 전제 조건
- `reports/report-docs.md` 존재 (Phase 4-A 산출)
- `reports/one-pager.md` 존재 (Phase 4-C 산출, 선택적)
- `findings/golden-facts.yaml` 존재 (Phase 0.5+)
- `qa/qa-report.md` PASS 판정 (Trust Badge용)

### 실행 순서

```
Step 1: HTML 3종 생성
  PM 실행 (Bash 도구):
    python3 scripts/render-report-html.py {project-name}

  산출:
    {project}/reports/report-docs.html  (본문 태그 → sources.html 딥링크)
    {project}/reports/one-pager.html    (태그 자동 제거, A4 1p)
    {project}/reports/sources.html      (Golden Facts + Source Index 통합)

Step 2: PDF 변환 (one-pager 한정)
  PM 실행 (Bash 도구):
    python3 scripts/render-onepager-pdf.py {project-name}

  산출:
    {project}/reports/one-pager.pdf     (Chrome headless, A4 1p)

Step 3: 사용자에게 산출물 경로 안내
  PM → 사용자:
    ✅ HTML/PDF 생성 완료
    - report-docs.html : 상세 보고서 (브라우저)
    - one-pager.html/pdf : 경영진 원페이퍼
    - sources.html : 출처 인덱스 (딥링크 지원)
```

### 옵션

```
# 특정 산출물만 생성
--only {docs|one-pager|sources}

# 태그 처리 모드 변경
--docs-tags {link|mark|strip}          # 기본: link
--one-pager-tags {link|mark|strip}     # 기본: strip

# PDF 변환 대상
--target {one-pager|docs|both}         # 기본: one-pager만
```

### 재실행 조건

아래 파일 중 하나라도 변경되면 HTML 재생성:
- `reports/report-docs.md`
- `reports/one-pager.md`
- `findings/golden-facts.yaml`
- `findings/**/*.yaml` (source_index 포함)
- `qa/qa-report.md` (Trust Badge 갱신)

**HTML 직접 수정 금지** — MD 정본 수정 후 재생성 원칙.

### 실패 처리

- MD 없음 → 해당 보고서만 SKIP (다른 보고서 진행)
- Chrome 미설치 → weasyprint fallback, 둘 다 없으면 PDF만 생략
- golden-facts.yaml 비어 있음 → sources.html 생성 생략

상세: `core/protocols/html-export-protocol.md` 참조.
