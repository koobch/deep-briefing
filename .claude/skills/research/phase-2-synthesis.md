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
