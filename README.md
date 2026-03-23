# Deep-Briefing

**AI 멀티 에이전트가 수행하는 컨설팅급 전략 리서치.**
22개 에이전트가 병렬로 분석하고, 교차 검증하고, 반증하고, 보고서를 작성합니다.

```
주제 하나를 던지면 → 22개 에이전트가 → 컨설팅 펌 수준의 전략 보고서를 생성합니다.
```

### 왜 Deep-Briefing인가?

| | 일반 AI 리서치 | Deep-Briefing |
|---|---|---|
| **분석 구조** | 단일 에이전트 반복 검색 | 7개 Division이 독립 CLI로 병렬 분석 (최대 1,400K 컨텍스트) |
| **검증** | 없음 | 4단계 교차 검증 (VL-1→VL-3) + Red Team 반증 |
| **스토리** | 정보 나열 | SCR 스토리라인 + Action Title (MBB 방법론) |
| **실행력** | "~하세요" 수준 제안 | Implementation Playbook (담당/KPI/마일스톤/의존성) |
| **수치 신뢰** | 출처 불명 | Golden Facts SSOT + 소스 추적 ([GF-###], [S##]) |
| **반증** | 없음 | Red Team: 핵심 전제 반증 + 역 시나리오 + 숨겨진 가정 노출 |

### 30초 Quick Start

```bash
git clone https://github.com/{owner}/deep-briefing.git
cd deep-briefing
claude            # Claude Code 실행
> /setup          # 환경 자동 설정 (Express: 2분)
> /research interactive my-project 한국 SaaS 시장 진출 전략
```

끝. PM 에이전트가 인터뷰 → 가설 수립 → 병렬 리서치 → 보고서 생성까지 자동으로 진행합니다.

---

## 핵심 기능

| 기능 | 설명 |
|------|------|
| **22개 전문 에이전트** | PM, Division Lead 7, Cross-cutting 6(Red Team 포함), QA 6, Report, Utility |
| **SCR 스토리라인** | Situation→Complication→Resolution + 모든 슬라이드 Action Title 필수 |
| **Red Team (Devil's Advocate)** | 핵심 전제 반증, 역 시나리오, 숨겨진 가정 노출, 조기 경보 지표 |
| **Implementation Playbook** | 담당/마일스톤/KPI/의존성 + Impact×Feasibility 우선순위 매트릭스 |
| **Scenario P&L + 민감도 분석** | BASE/UPSIDE/DOWNSIDE 3-시나리오 + 핵심 가정 ±변동 영향 |
| **4단계 검증** | VL-1(자가) → VL-1.5(삼각) → VL-2(정합) → VL-3(교차) + QA 자동 수정 루프 |
| **벤치마크** | 피어 비교 매트릭스 + 하비볼 시각화 (선택적 활성화) |
| **컨설팅급 차트** | 마리메꼬, 하비볼, 워터폴, 시나리오 등 자동 생성 |
| **3가지 모드** | Auto(직행) / Interactive(공동작업) / Team(토론+되돌아가기) |
| **도메인 플러그인** | 산업별 프레임워크/데이터소스를 플러그인으로 확장 |

## Quick Start

### 1. 클론 + 초기 설정

```bash
git clone https://github.com/{owner}/deep-briefing.git
cd deep-briefing
claude
```

Claude Code에서:
```
> /setup
```

`/setup`이 환경 점검 → 도메인 생성 → API 설정을 인터랙티브하게 안내합니다.
설명서를 읽을 필요 없이 대화하면서 설정이 완료됩니다.

### 2. 첫 리서치

```bash
./scripts/init-project.sh my-first-research
```

Claude Code에서:
```
> /research interactive my-first-research {리서치 주제}
```

### 수동 설치 (CI/CD 또는 /setup 없이 설정할 경우)

<details>
<summary>수동 설치 단계 펼치기</summary>

#### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI 설치 필요
- Python 3.8+ (스크립트 실행용)
- tmux (Division 병렬 실행용)

#### 환경 설정

```bash
# Python 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (선택 — API 키가 없어도 웹 검색으로 리서치 가능)
cp .env.example .env
# 필요한 API 키를 .env에 입력 (DART, FRED 등)
```

#### 도메인 설정

```bash
# 방법 A: 기본 제공 도메인 사용 (범용 전략 분석)
# domains/example/이 그대로 사용 가능 — 추가 설정 불필요

# 방법 B: 커스텀 도메인 생성
cp -r domains/example/ domains/my-domain/
# domains/my-domain/frameworks.md, data-sources.md를 도메인에 맞게 수정
```

비인터랙티브 환경 점검만 하려면:
```bash
./scripts/quickstart.sh
```

</details>

PM이 자동으로 다음을 수행합니다:
1. Client Discovery (질문 5~15개)
2. 도메인 탐지 + Research Plan 수립
3. Division Briefs 작성

PM이 "Division Briefs 작성 완료"를 알리면, **새 터미널**에서:
```bash
./scripts/spawn-leads.sh my-first-research --attach
```

### 4. 결과 확인

리서치 완료 후 산출물:
```
my-first-research/
├── reports/report-docs.md      ← 상세 보고서
├── reports/report-slides.md    ← 경영진 요약 슬라이드
├── reports/charts/             ← 자동 생성 차트
├── findings/                   ← Division별 분석 결과
└── qa/                         ← 품질 검증 리포트
```

## 아키텍처 개요

```
사용자
  │
  ├── PM CLI (메인)           ← /research 명령으로 시작
  │     │
  │     ├── Phase 0: Client Discovery + Research Plan
  │     ├── Phase 0.5: 가설 생성 + 사용자 정렬 (Quick Scan → 가설 3~5개 → 확정)
  │     ├── Phase 1: Division 병렬 리서치 (가설 검증/반증 중심)
  │     ├── Sync Round 1: 교차 라우팅 + Tension 식별
  │     ├── Phase 2: 교차 반영 심화 리서치
  │     ├── Sync Round 2: Cross-domain Synthesis
  │     ├── Phase 3: 사고 루프 (Why Chain + 5-레인 도전)
  │     ├── Phase 4: 보고서 생성 + PPT 매핑 (Canva MCP / python-pptx)
  │     ├── Phase 5: QA 자동 수정 루프 (Critical/Major 0건 = PASS, 최대 3회)
  │     └── Phase 5.5: 사용자 피드백 + 부분 재실행 (선택)
  │
  ├── Market Lead CLI         ← 독립 200K 컨텍스트
  ├── Product Lead CLI        ← 독립 200K 컨텍스트
  ├── Capability Lead CLI     ← 독립 200K 컨텍스트
  ├── Finance Lead CLI        ← 독립 200K 컨텍스트
  │
  │   # 확장 Division (주제에 따라 선택 투입)
  ├── People & Org Lead CLI   ← 독립 200K 컨텍스트
  ├── Operations Lead CLI     ← 독립 200K 컨텍스트
  └── Regulatory Lead CLI     ← 독립 200K 컨텍스트
```

**핵심**: 각 CLI가 독립 프로세스로 실행되어 **최대 1,400K 컨텍스트**를 활용 (핵심 4 + 확장 최대 3).
CLI 간 통신은 **파일 시스템**을 통해 이루어짐 (직접 통신 없음).

## 에이전트 구성 (도메인에 따라 가변)

| 계층 | 에이전트 | 수 |
|------|---------|---|
| PM | research-pm | 1 |
| Division Lead | market-lead, product-lead, capability-lead, finance-lead | 4 |
| Sub-lead | geography-lead, segment-lead, channel-lead, competitive-lead | 4 |
| Leaf | 20개 전문 분석가 | 20 |
| Cross-cutting | fact-verifier, logic-prober, strategic-challenger, **red-team**, insight-synthesizer, cross-domain-synthesizer | 6 |
| QA | report-writer, qa-orchestrator, **audience-fit-checker**, **executability-checker**, report-auditor, report-fixer | 6 |
| Utility | data-preprocessor (동적 스폰) | 1 |

상세 구성: 프로젝트 실행 시 `{project}/ARCHITECTURE.md`가 자동 생성됩니다.

## 모드별 운용 차이

| 단계 | Auto | Interactive | Team |
|------|------|-------------|------|
| Client Discovery | Quick 자동 | Quick/Deep 선택 | Deep 권장 |
| Lead CLI | 4개 병렬 | 4개 병렬 + 사용자 게이트 | 4개 병렬 + 게이트 + 토론 |
| Sync Round 1 후 | 바로 Phase 2 | 사용자에게 briefing 제시 | briefing + 토론 |
| 사고 루프 | 1회 | 1~2회 | 2회 (최대) |
| 되돌아가기 | 없음 | 사용자 트리거 | 자동+사용자 |

## 사용자 개입 포인트

**PM CLI 하나에서 전부 진행. 터미널 전환 / 명령어 입력 불필요.**

| 시점 | 사용자가 할 일 | PM이 자동 처리 | 예상 소요 |
|------|-------------|-------------|----------|
| Phase 0 | Discovery 답변 + Factsheet 승인 | — | 10~15분 |
| Phase 0.5 | 가설 검토 + 채택/수정 | Quick Scan Agent 스폰 | 5~10분 |
| Phase 1 | **"투입?" → "응"** | spawn-leads.sh + .done 폴링 | 5초 |
| Sync R1 | **"Sync?" → "응"** | 교차 라우팅 자동 | 5초 |
| Phase 2 | **"전송?" → "응"** | send-phase2.sh + .done 폴링 | 5초 |
| Phase 2→3 | **"사고루프?" → "응"** | Thinking Loop 자동 | 5초 |
| Phase 4 | PPT 슬라이드 구성 확인 | PPT 생성 | 5분 |
| Phase 5 | PM 최종 확인 | QA 자동 수정 루프 | 5분 |
| Phase 5.5 | 피드백 → 확정 | 부분 재실행 | 임의 |
| Phase 6 | — | Post-mortem 자동 | 자동 |

**능동적 개입: ~25분 (대부분 "응" 한 번)**

## 파일 기반 조율 프로토콜

모든 CLI 간 통신은 파일 시스템을 통해 이루어집니다.

```
{project}/
├── 00-client-brief.md              ← PM 작성, Lead 참조
├── 01-research-plan.md             ← PM 작성, Lead 참조
├── 00-company-factsheet.md         ← PM 작성, Lead 참조
│
├── division-briefs/                ← PM → Lead (Phase 1 지시)
│   ├── market.md
│   ├── product.md
│   ├── capability.md
│   └── finance.md
│
├── findings/                       ← Lead → PM (결과)
│   ├── market/
│   │   ├── division-synthesis.yaml
│   │   ├── opportunity-matrix.yaml
│   │   └── .done                   ← 완료 시그널
│   ├── product/
│   ├── capability/
│   └── finance/
│
├── sync/                           ← PM ↔ Lead (Sync Round)
│   ├── round-1-briefing.md
│   ├── phase2-market.md
│   ├── phase2-product.md
│   ├── phase2-capability.md
│   ├── phase2-finance.md
│   ├── round-2-briefing.md
│   └── cross-domain-synthesis.md
│
├── thinking-loop/                  ← Cross-cutting (사고 루프)
│   ├── why-probe.md
│   ├── strategic-challenge.md
│   ├── red-team-report.md
│   └── loop-convergence.md
│
├── reports/                        ← 최종 산출물
│   ├── report-docs.md
│   └── report-slides.md
│
└── qa/                             ← QA 결과
    ├── mechanical-validation.md
    ├── source-traceability.md
    └── audit-log.md
```

## 도메인 지식 베이스

리서치 도메인별 지식(프레임워크, 데이터 소스)을 플러그인으로 관리합니다.

```
domains/
├── example/           ← 범용 전략 분석 도메인 (바로 사용 가능)
│   ├── README.md
│   ├── frameworks.md
│   ├── data-sources.md
│   └── agents/
└── {your-domain}/     ← 도메인별 지식 베이스
```

새 도메인 생성:
```bash
cp -r domains/example/ domains/{your-domain}/
```

## 커스텀 도메인으로 사용하기

이 프레임워크는 도메인 독립적입니다. 어떤 산업/분야에도 적용 가능합니다.

1. `domains/example/`을 복사하여 도메인 생성
2. `frameworks.md`에 분석 프레임워크 정의
3. `data-sources.md`에 데이터 소스 정의
4. (선택) `agents/`에 도메인 특화 에이전트 정의
5. `/research` 실행 시 자동으로 도메인 탐지

## 상세 사용법

### Lead CLI 수동 투입

터미널 탭 4개를 열고 각각:
```bash
# 탭 1 — Market
cd ~/deep-briefing
claude --agent market-lead "my-research/division-briefs/market.md를 읽고 Phase 1 리서치를 시작하라."

# 탭 2 — Product
cd ~/deep-briefing
claude --agent product-lead "my-research/division-briefs/product.md를 읽고 Phase 1 리서치를 시작하라."

# 탭 3 — Capability
cd ~/deep-briefing
claude --agent capability-lead "my-research/division-briefs/capability.md를 읽고 Phase 1 리서치를 시작하라."

# 탭 4 — Finance
cd ~/deep-briefing
claude --agent finance-lead "my-research/division-briefs/finance.md를 읽고 Phase 1 리서치를 시작하라."
```

### Lead 완료 대기 (.done 모니터링)

각 Lead가 완료되면 `findings/{division}/.done` 파일을 생성합니다.

모니터링:
```bash
watch -n 5 'ls -la my-research/findings/*/.done 2>/dev/null'
```

### Sync Round 1 — PM CLI

4개 `.done` 파일이 모두 확인되면 PM CLI로 돌아옵니다:

```
> 4개 Division 리서치가 완료됐다. Sync Round 1을 진행해.
```

### Phase 2 — Lead CLI 재활용

PM이 Phase 2 지시서를 작성하면, 자동 전송:
```bash
./scripts/send-phase2.sh my-first-research   # 활성 Division 전체에 Phase 2 지시
```

또는 임의 메시지 전송:
```bash
./scripts/send-to-leads.sh my-first-research "추가 분석 요청 메시지"
./scripts/send-to-leads.sh my-first-research --div market "Market만 추가 분석"
```

### Sync Round 2 + 사고 루프 + 보고서 — PM CLI

Phase 2 완료 후 Lead CLI는 종료해도 됩니다. PM CLI에서 순차 진행:

```
> Phase 2가 완료됐다. Sync Round 2 + 사고 루프를 진행해.
> 보고서를 작성해.
```

### 대안: TeamCreate 모드 (단일 CLI)

독립 CLI 대신 PM CLI 하나에서 TeamCreate로 Division Lead를 스폰할 수도 있습니다.

```
장점: 셋업 간편 (터미널 1개)
단점: 200K 컨텍스트를 전체가 공유 → 대규모 리서치 시 한계
적합: 간단한 리서치, 특정 Division만 활성화할 때
```

PM CLI에서 `/research` 실행 시 "TeamCreate 모드로 진행" 옵션을 선택하면 됩니다.

## tmux 기본 조작법

| 조작 | 단축키 |
|------|--------|
| pane 이동 | `Ctrl+b` → 방향키 |
| pane 확대/축소 | `Ctrl+b` → `z` |
| 세션 분리 (백그라운드) | `Ctrl+b` → `d` |
| 세션 재접속 | `tmux attach -t research-v2` |
| 세션 종료 | `tmux kill-session -t research-v2` |
| 스크롤 | `Ctrl+b` → `[` → 방향키/PgUp → `q`로 탈출 |

## 트러블슈팅

### Lead CLI가 시작 안 됨
```bash
# 에이전트 등록 확인
claude agents
# market-lead, product-lead, capability-lead, finance-lead가 보여야 함

# division-briefs 존재 확인
ls {project}/division-briefs/
```

### .done 파일이 생성 안 됨
Lead CLI에서 직접 확인:
```
> findings/{division}/ 디렉토리에 어떤 파일이 있어?
> .done 파일을 작성해줘.
```

### Sync Round에서 division-synthesis.yaml을 못 읽음
```bash
# 파일 존재 확인
ls {project}/findings/*/division-synthesis.yaml
```

### tmux 세션이 안 보임
```bash
tmux ls                          # 세션 목록
tmux attach -t research-v2      # 재접속
```

### Lead CLI가 중간에 크래시됨
- PM CLI로 돌아가서 해당 Division의 `.done` 파일 확인:
  ```bash
  ls {project}/findings/{division}/.done
  ```
- `.done`이 없으면 해당 Division만 재스폰:
  ```bash
  claude --agent {division}-lead "{project}/division-briefs/{division}.md를 읽고 Phase 1을 이어서 진행하라."
  ```
- `findings/{division}/`에 부분 결과가 있으면 Lead가 자동으로 이어서 진행

### API 호출 실패
- `.env`의 API 키 확인:
  ```bash
  ./scripts/check-api-keys.sh
  ```
- 특정 API만 실패 시: 해당 API 없이 웹 검색으로 대체 (confidence 한 단계 하향)
- 전체 네트워크 문제: PM에게 "API 없이 웹 검색만으로 진행해" 지시

### 컨텍스트 초과 (Compacting 반복)
- Division Lead CLI에서 발생 시: 리프 에이전트 수를 줄이거나 배치 처리
- PM CLI에서 발생 시: Division 출력의 Layer 0만 읽기 (Context 관리 규칙 참조)
- 해결 안 되면: TeamCreate 대신 독립 CLI 모드로 전환

### Phase 중간에 세션이 끊김
- PM CLI 재시작 → 자동으로 `checkpoint.yaml` 읽기 → 이전 Phase부터 재개
- "이전 세션에서 {phase}까지 완료. 이어서 진행합니다" 메시지 확인

### QA에서 반복 FAIL
- `qa/qa-report.md` 확인 → Critical/Major 이슈 목록 확인
- report-fixer가 3회 반복 후에도 해결 못하면 수동 수정 필요
- 수동 수정 후: `/research` 세션에서 "QA를 다시 실행해" 지시

### 차트 생성 실패
- matplotlib 설치 확인:
  ```bash
  pip install matplotlib
  ```
- 데이터 없는 Division은 차트 자동 스킵 (에러 아님)
- 한국어 폰트 문제: `brew install font-pretendard` 또는 시스템 폰트 폴백 자동 적용

## 참조 문서

| 문서 | 위치 | 설명 |
|------|------|------|
| ARCHITECTURE.md | `docs/` | 에이전트 토폴로지, Phase 흐름, 데이터 플로우 |
| sync-protocol.md | `core/orchestration/` | Sync Round 프로토콜 |
| output-format.md | `core/protocols/` | 4-Layer 출력 포맷 |
| fact-check-protocol.md | `core/protocols/` | VL 검증 체계 |
| frameworks.md | `domains/{domain}/` | 도메인별 프레임워크 카탈로그 |
| research-pm.md | `.claude/agents/` | PM 전체 지시사항 |
