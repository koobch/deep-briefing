# Phase 1: Division 병렬 리서치 — 독립 CLI 오케스트레이션

## Step 1-A: Division Briefs 작성

Research Plan 완료 후, 각 Division Lead를 위한 지시서를 파일로 작성한다.

```
{project}/division-briefs/
├── market.md          # 핵심
├── product.md         # 핵심
├── capability.md      # 핵심
├── finance.md         # 핵심
├── people-org.md      # 확장 (활성화 시)
├── operations.md      # 확장 (활성화 시)
└── regulatory.md      # 확장 (활성화 시)
```

각 지시서에 포함할 내용:
- Client Brief 요약 (해당 Division 관련 부분)
- Research Plan 중 해당 Division 배치 + 프레임워크
- **analysis_type** (v4.11): Research Plan의 `analysis_type` 전파
- **entity_target** (v4.11): profile 타입인 경우 분석 대상 엔터티
- 활성화할 Sub-lead/Leaf 목록 (agent_roster)
- EP 경고 + 제외 방향
- **baseline_coverage** (v4.11, profile/exploration 타입 시): 필수 커버리지 리스트. `core/protocols/analysis-type-protocol.md#4-baseline-coverage-catalog` 참조
- 가설 검증 지시 (decision 타입 주력, profile에서는 보조) — Phase 0.5 확정 가설의 verification_plan
- **exploration_space** (v4.11, exploration 타입 시): 탐색 키워드 + 시간 범위 + 신호 유형
- **monitoring_metrics** (v4.11, monitoring 타입 시): 추적 지표 + 수집 주기 + 임계값
- 사용자 데이터 경로 (해당 시)
- 출력 저장 경로: `findings/{division}/`

### Division Brief 실행 우선순위 (v4.11)

Division Lead가 Leaf를 스폰할 때 다음 순서로 배치:

1. **baseline_coverage.required=true** 항목 (필수 커버리지 — profile/exploration에서 의무)
2. **verification_plan** 과제 (가설 검증 — decision 주력)
3. **exploration_space** 탐색 (exploration 타입)
4. **cross-domain** 교차 주제 (다른 Division의 질문 응답)

analysis_type이 profile이면서 baseline_coverage 주입이 없으면, Lead는 PM에 즉시 에스컬레이션 (구성 오류 가능성).

## Step 1-B: Lead CLI 투입 (PM CLI에서 직접 실행)

지시서 작성 완료 후, PM이 사용자 확인을 받고 **PM CLI에서 바로 실행**한다.
사용자가 별도 터미널을 열거나 명령어를 입력할 필요 없음.

```
Auto 모드:
  PM이 사용자 확인 없이 즉시 실행.
  → ./scripts/spawn-leads.sh {project-name} --auto

Interactive/Team 모드:
  PM → 사용자:
    Division Briefs 작성 완료.
    활성 Division Lead CLI를 tmux로 투입합니다.
    → 진행할까요? [Y/n]

  사용자: "응" / "Y" / (아무 긍정 표현)

PM 실행 (Bash 도구):
  ./scripts/spawn-leads.sh {project-name} --auto

  ※ --auto: 리서치 에이전트의 파일 읽기/쓰기/웹 접근을 자동 허용
  ※ tmux 세션이 백그라운드에서 생성됨 (PM CLI는 그대로 유지)
  ※ --attach 생략: PM CLI를 떠나지 않기 위해 tmux에 자동 접속하지 않음
  ※ spawn-leads.sh는 Research Plan의 active_divisions를 참조하여 활성 Division만 스폰
```

## Step 1-C: .done 자동 폴링

PM이 Bash 도구로 .done 파일을 주기적으로 확인한다.
사용자가 직접 모니터링할 필요 없음.

```
PM 실행 (Bash 도구, 반복):
  # 활성 Division 전체의 .done 파일 존재 여부 확인
  # Research Plan의 active_divisions 목록 기준으로 폴링
  ls {project}/findings/{division}/.done 2>/dev/null | wc -l

  결과:
    N (= 활성 Division 수) → 전체 완료 → Step 1-D로 진행
    0~(N-1) → 30초~1분 후 재확인

PM → 사용자 (중간 보고, 활성 Division 전체 표시):

  Lead 진행 상황:
    Market:     ✅ 완료
    Product:    ✅ 완료
    Capability: ⏳ 진행 중
    Finance:    ✅ 완료
    (확장 Division이 활성화된 경우 해당 Division도 표시)

  Capability Lead 완료를 기다리고 있습니다...

폴링 제한:
  - 최대 30분 (30초 간격 × 60회)
  - 30분 초과 시 사용자에게 알림:
    "Lead CLI가 30분 이상 실행 중입니다. tmux 세션을 확인하시겠습니까?"
    → tmux attach -t research-v2
```

## Step 1-D: 전체 완료 → Sync Round 1 자동 진입

```
Auto 모드:
  전체 완료 감지 → 즉시 Sync Round 1 자동 진입. 사용자 확인 없음.

Interactive/Team 모드:
  PM → 사용자:

    ✅ N개 Division 리서치 완료!

      (각 Division headline 표시)

    Sync Round 1을 시작합니다.
    → 진행할까요? [Y/n]

  사용자: "응"

PM: Sync Round 1 실행 (phase-2-synthesis.md 참조)
```

## Lead CLI 직접 확인이 필요한 경우

```
tmux 세션에 접속하려면:
  tmux attach -t research-v2

pane 이동: Ctrl+b → 화살표
풀스크린: Ctrl+b → z
나가기:   Ctrl+b → d (PM CLI로 복귀)
```

## 방법 2: TeamCreate (단일 CLI 모드)

```
독립 CLI 대신 현재 세션에서 TeamCreate로 Division Lead를 스폰할 수도 있습니다.
이 경우 PM 컨텍스트를 공유하므로, 간단한 리서치에 적합합니다.
진행할까요?
```
