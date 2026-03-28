---
name: research
description: 리서치 오케스트레이터 통합 진입점. N-Division Pool 기반 독립 CLI 병렬 실행을 오케스트레이션한다.
argument-hint: "[auto|interactive|team] [주제] [대상]"
---

# /research — 리서치 오케스트레이터

## Division Pool 구조

N-Division Pool 기반 병렬 실행. 도메인 및 프로젝트에 따라 에이전트 수 가변.

| 구분 | Division | 약어 | 설명 |
|------|----------|------|------|
| **핵심 4** | Market | M | 시장/경쟁/트렌드 |
| | Product | P | 제품/서비스/UX |
| | Capability | C | 역량/기술/자산 |
| | Finance | F | 재무/수익/밸류에이션 |
| **확장 3** | People & Org | H | 조직/인재/문화 |
| | Operations | O | 프로세스/운영/인프라 |
| | Regulatory | R | 규제/법률/ESG |

핵심 4개는 기본 활성. 확장은 Client Brief 주제에 따라 PM이 판정.

## 사용법
```
/research                                          → 모드 선택지 제시
/research auto [주제] [대상]                        → Auto 모드
/research auto --deep [주제] [대상]                 → Auto + Deep 검증
/research interactive [주제] [대상]                  → Interactive 모드
/research team [주제] [대상]                         → Team 모드
/research team --interactive [주제] [대상]           → Team + 사용자 게이트
/research status [project-name]                     → 프로젝트 진행 상태 조회
```

## 자동 Resume (세션 재개)

`/research` 실행 시 PM은 **기존 프로젝트 자동 감지**를 수행한다:

```
1. 루트 디렉토리에서 findings/checkpoint.yaml이 있는 프로젝트를 탐색
2. checkpoint.yaml의 current_phase가 "not-started" 또는 "completed"가 아닌 프로젝트 발견 시:

   📋 진행 중인 프로젝트 감지

   프로젝트: {project-name}
   현재 Phase: sync-round-1 (진행 중)
   마지막 업데이트: 2026-03-15 14:30:00
   완료된 Phase: Phase 0, Phase 0.5, Phase 1

   → 이어서 진행할까요? [Y/n]
   → 새 프로젝트를 시작하려면 'n'을 입력하세요.

3. 사용자가 Y → checkpoint.yaml 기반으로 해당 Phase부터 재개
4. 사용자가 N → 새 프로젝트 시작 (init-project.sh 자동 실행)
```

## /research status — 프로젝트 상태 조회

`/research status [project-name]` 실행 시 PM은 checkpoint.yaml을 파싱하여 상태를 표시한다.
project-name 생략 시 모든 프로젝트를 스캔.

```
📊 프로젝트 상태: {project-name}

  Phase 0   Client Discovery     ✅ 완료 (2026-03-15)
  Phase 0.5 가설 생성+정렬        ✅ 완료 (2026-03-15)
  Phase 1   Division 병렬 리서치  ✅ 완료 (2026-03-15)
    Market:     ✅  Product:    ✅  Capability: ✅  Finance: ✅
    (확장 Division이 활성화된 경우 해당 Division도 표시)
  Sync R1   교차 라우팅           ✅ 완료 (2026-03-15)
  Phase 2   교차 반영 심화        ✅ 완료 (2026-03-15)
  Sync R2   Cross-domain         ✅ 완료 (2026-03-15)
  Phase 3   사고 루프             ✅ 완료 (2026-03-15)
  Phase 3.7 External Review      ✅ 완료 (2026-03-15)
  Phase 4   보고서 생성           ✅ 완료 (2026-03-15)
  Phase 5   QA 자동 루프          ⚠️ CONDITIONAL PASS (Major 2건)
  Phase 5.5 사용자 피드백         ⏳ 대기 중

  사용자 결정 이력: 3건
  에스컬레이션: 0건 (미처리)

→ 이어서 진행하려면: /research interactive {project-name} {주제}
```

## 3-모드 체계

| 모드 | 사용자 역할 | 디스커버리 | 되돌아가기 | Lead CLI |
|------|-----------|----------|----------|---------|
| **Auto** | 클라이언트만 | Quick 자동 | 없음 | N개 병렬 |
| **Interactive** | 클라이언트→디렉터 | Quick/Deep 선택 | 사용자 트리거 | N개 병렬 + 게이트 |
| **Team** | 클라이언트→디렉터 | Deep 권장 | 전방위 | N개 병렬 + 게이트 + 토론 |

## 진입 흐름

### 모드 미지정 시

모드가 지정되지 않은 경우 (`/research {project-name} {주제}`로만 실행하거나, `/research`만 실행한 경우):
사용자에게 다음 선택지를 제시하세요:

```
리서치 모드를 선택해주세요:

1. **Interactive** (추천) — 매 단계 확인하며 함께 진행. 에이전트 작동 방식을 이해하기 좋음 (첫 사용자 추천) (약 1~2시간, 검증된 전략 보고서)
2. **Auto** — 전 과정을 자동 진행. 빠르지만 중간 개입 불가 (약 30분~1시간, 빠른 브리핑)
3. **Team** — 심층 토론 + 되돌아가기 지원. 복잡한 주제에 적합하지만 시간이 가장 오래 걸림 (약 2~3시간, 깊이 있는 전략 토론)

처음이시라면 Interactive를 추천합니다 — 에이전트가 어떻게 작동하는지 확인할 수 있습니다.
```

**파싱 분기 로직**:
- `/research` → 위 선택지 제시 (프로젝트명/주제 없음)
- `/research {project-name} {주제}` → 모드 없음 감지 → 위 선택지 제시 → 사용자 선택 후 해당 모드로 진행
- `/research auto|interactive|team {project-name} {주제}` → 모드 지정됨 → 바로 진행

모드 없이 주제만 입력한 경우에도 반드시 선택지를 먼저 보여준다. 이미 입력한 프로젝트명과 주제는 유지됩니다. 모드만 선택하면 바로 시작합니다.

**각 모드 상세 참고**:

| 모드 | 예상 시간 | 사용자 개입 | 과정 |
|------|----------|-----------|------|
| Interactive | 1~1.5시간 | 6~8회 | 인터뷰 → 가설 공동 수립 → 중간 리뷰 → 방향 수정 → 사고 루프 공유 → 보고서 |
| Auto | 30~45분 | 1~2회 | 인터뷰(5~7문) → 가설 자동 확정 → 병렬 리서치 → 보고서. `--deep`: Red Team 전체 실행 + Why Probe 강화 |
| Team | 2~3시간 | 10회+ | 심층 인터뷰(12~15문) → 가설 공동 도출 → 토론 → 되돌아가기 가능 → 보고서. `--interactive`: 매 Phase마다 추가 사용자 참여 |

※ 시간은 주제 복잡도에 따라 변동됩니다.

## PM 실행 시퀀스

Phase별 상세 워크플로우는 보조 파일 참조:

1. **Phase 0**: Client Discovery + Research Plan → [phase-0-discovery.md](phase-0-discovery.md)
2. **Phase 0.5**: 가설 생성 + 사용자 정렬 → [phase-0-discovery.md](phase-0-discovery.md)
3. **Phase 1**: Division 병렬 리서치 (가설 검증 중심) → [phase-1-parallel.md](phase-1-parallel.md)
4. **Phase 2~3**: 교차 심화 + 사고 루프 → [phase-2-synthesis.md](phase-2-synthesis.md)
5. **Phase 3.7**: External Review (약점 체크 + 자기 비판) → [phase-2-synthesis.md](phase-2-synthesis.md)
6. **Phase 4**: 보고서 생성 → [phase-2-synthesis.md](phase-2-synthesis.md)
7. **Phase 5**: QA 자동 수정 루프 → [phase-2-synthesis.md](phase-2-synthesis.md)
8. **Phase 5.5**: 사용자 피드백 + 부분 재실행 → [phase-2-synthesis.md](phase-2-synthesis.md)

## 사용자 개입 포인트 요약

**PM CLI 하나에서 모든 것을 진행한다. 터미널 전환/명령어 입력 불필요.**
사용자는 PM의 확인 요청에 "응"/"Y"만 답하면 됨.

| 시점 | 사용자가 할 일 | PM이 자동 처리하는 것 |
|------|-------------|---------------------|
| Phase 0 | Discovery 답변 + Factsheet 승인 | — |
| Phase 0.5 | 가설 검토 + 채택/수정 | Quick Scan 활성 Division Agent 스폰 |
| Phase 1 | **"투입할까요?" → "응"** | spawn-leads.sh 자동 실행 + .done 폴링 |
| Sync R1 | **"Sync 시작할까요?" → "응"** | Division 출력 수집 + 교차 라우팅 |
| Phase 2 | **"Phase 2 전송할까요?" → "응"** | send-phase2.sh 자동 실행 + .done 폴링 |
| Phase 2→3 | **"사고 루프 시작할까요?" → "응"** | Cross-domain + Thinking Loop (logic-prober → strategic-challenger → red-team → insight-synthesizer) |
| Phase 3 결과 | Red Team 결과 검토 (Interactive/Team) | Strong 반론 시 전략 수정 여부 판단 |
| Phase 3.7 | External Review 결과 검토 (Interactive/Team) | 약점 체크리스트 + 자기 비판 + 외부 모델 선택 |
| Phase 4 | 보고서 구성 확인 | 보고서 생성 |
| Phase 5 | PM 최종 확인 | QA 자동 루프 (mechanical + source + confidence + executability-checker + audience-fit-checker + report-auditor → report-fixer) |
| Phase 5.5 | 피드백 입력 → 확정 | 부분 재실행 + QA |
| Phase 6 | — | Post-mortem 자동 생성 |

## 사용자 도메인 지식 수집 프로토콜 (Interactive/Team)

모든 사용자 게이트에서 PM은 다음을 수행한다:

```
매 게이트에서 PM이 물어봐야 하는 것:
  1. "이 결과가 본인의 경험과 일치하나요?"
  2. "추가로 알고 계신 정보가 있나요?"
  3. "이 방향에 대한 직관적 판단은?"

수집된 정보 처리:
  - 정량 데이터 → data/user-provided/에 저장 + data-preprocessor 처리
  - 정성 판단 → Division Brief 또는 Phase 2 지시서에 "[사용자 인사이트]" 태깅
  - 방향 수정 → hypotheses.yaml 또는 Research Plan 업데이트

핵심: 사용자의 도메인 지식이 분석에 주입되어야 결과물 퀄리티가 올라간다.
에이전트만으로는 공개 데이터 기반의 피상적 분석이 될 수 있으며,
사용자의 경험/직관이 "이건 현실과 다르다" 교정을 제공한다.
```

## 되돌아가기 (어느 Phase에서든 가능)

Interactive/Team 모드에서 사용자가 자연어로 요청하면 PM이 자동 처리:

```
"가설을 바꾸고 싶어"           → Phase 0.5로 (영향 Division만 재실행)
"시장 분석이 틀렸어"           → Phase 1 해당 Division 재실행
"전제 자체가 틀렸어"           → Phase 0부터 전면 재설정
"이 가정을 바꿔서 다시 해봐"   → PM이 영향 범위 판정 후 최소 재실행
```

PM이 영향 분석 → 비용 추정 → 대안 제시(되돌아가기/현위치 보정/취소) → 사용자 선택 → 실행.
기존 산출물은 자동 백업. 영향 없는 Division은 유지.

상세: `sync-protocol.md` 되돌아가기 실행 프로토콜 참조.

## 참조
- `{project}/agents/research-pm.md` — PM 전체 지시사항
- `core/orchestration/sync-protocol.md` — Sync Round 프로토콜
- `core/orchestration/escalation-protocol.md` — 에스컬레이션
- `README.md` — 운용 매뉴얼
