# CLAUDE.md — Deep-Briefing

## 프로젝트 개요

컨설팅급 리서치를 **N-Division 병렬 실행**(핵심 4 + 확장 최대 3)으로 수행하는 에이전트 오케스트레이션 시스템.
에이전트가 4계층(PM → Lead → Leaf + Cross-cutting/QA)으로 작동.

## 첫 대화 자동 안내 (Claude 필수 행동)

**사용자가 이 프로젝트에서 처음 대화를 시작하면, Claude는 반드시 다음을 수행한다:**

1. `scripts/check-env.sh`를 실행하여 환경 상태를 확인
2. 결과의 `ACTION` 필드에 따라 안내:
   - `first_setup`: "환경 설정이 필요합니다. /setup 을 실행할까요?" 제안
   - `new_research`: "설정이 완료되어 있습니다. 어떤 주제를 리서치할까요?" 제안
   - `continue_or_new`: 진행 중 프로젝트 목록을 보여주고 "이어서 진행 / 새 리서치" 선택지 제시
3. 사용자가 별도 요청 없이 대화를 시작해도 (예: "안녕", "시작", 빈 입력) 위 안내를 먼저 수행

**원칙: 사용자가 다음에 뭘 해야 하는지 모르는 순간이 없어야 한다. Claude가 항상 먼저 제안한다.**

## 커스텀 가이드

이 프로젝트를 클론하여 사용할 때:
1. 이 CLAUDE.md를 본인의 조직/프로젝트 컨텍스트에 맞게 수정하세요
2. `domains/example/`을 복사하여 산업별 도메인 플러그인을 만드세요
3. `/setup`을 실행하면 인터랙티브하게 설정됩니다

## 핵심 아키텍처

- **실행 모델**: PM CLI 1개 + 활성 Division Lead CLI N개 (핵심 4 + 확장 최대 3)
- **CLI 간 통신**: 파일 시스템 기반 (직접 통신 없음). `findings/`, `sync/` 디렉토리 경유
- **오케스트레이션 흐름**: Phase 0 → **0-A.6(v4.11: analysis_type 판정)** → 0.5(가설+데이터갭, 타입별 분기) → 1(병렬 리서치, baseline_coverage 우선) → Sync 1 → 2(심화) → Sync 2(긴장해소) → 3(사고 루프+Red Team) → 3.7(External Review) → 4-A(세로 보고서 MD) → 4-C(원페이퍼 MD, 선택적) → 4.5(출처 레지스트리) → 5(QA 자동 루프) → 5.5(피드백) → 4.7(HTML/PDF 내보내기)

## 디렉토리 구조

```
core/                   → 도메인 독립 프레임워크 (재사용)
  orchestration/        → sync-protocol.md, escalation-protocol.md
  protocols/            → output-format.md (4-Layer), fact-check-protocol.md (VL-1~3), html-export-protocol.md (Phase 4.7)
  templates/            → 에이전트/리드 템플릿, learning-extraction-template 등
  knowledge/            → Layer 0 범용 분석 상식 (common-sense.yaml)
  style/                → report-templates/ (Phase 4.7 HTML/CSS/Jinja2 템플릿)
  tests/                → 프롬프트 테스트 케이스 (EP-001~033)

domains/                → 도메인 플러그인 (도메인별 지식 베이스)
  example/              → 스켈레톤 템플릿 (새 도메인 생성 시 복사)
    frameworks.md       → 수동 정의 프레임워크
    data-sources.md     → 수동 정의 데이터 소스
    knowledge/          → 학습 엔진 축적 지식 (Layer 2)
      learned-sources.yaml, learned-patterns.yaml, learned-terms.yaml
      learned-frameworks.yaml, learned-pitfalls.yaml, _meta.yaml
  {domain}/             → 산업 특화 지식 (같은 구조)

scripts/                → 자동화 스크립트 (아래 스크립트 테이블 참조)

.claude/agents/         → Division Lead 에이전트 정의 (핵심 4 + 확장 3)
  leaves/               → Leaf 에이전트 역할 정의 (내부 MECE 분석 구조 포함)
    market/             → market-sizing, customer-analysis, competitive-landscape 등
    product/            → product-offering, value-differentiation, go-to-market 등
    capability/         → technology-ip, human-capital, strategic-assets 등
    finance/            → revenue-growth, cost-efficiency, investment-returns 등
    people-org/         → org-design, talent-strategy, culture-engagement
    operations/         → process-excellence, supply-chain, infrastructure
    regulatory/         → compliance-status, regulatory-outlook, esg-governance
.claude/skills/setup    → /setup 스킬 (환경 점검 + 도메인 생성 + API 설정)
.claude/skills/research → /research 스킬 (PM 실행 시퀀스)

{project}/              → 프로젝트별 실행 결과 (1회성)
  00-client-brief.md, 01-research-plan.md, hypotheses.yaml
  division-briefs/, findings/, sync/, thinking-loop/, reports/, qa/
  learnings/            → 학습 엔진 추출 결과 ({division}-learnings.yaml)
```

## Division Pool (N-Division 선택 투입)

| 구분 | Division | 약자 | 활성화 기준 |
|------|----------|------|------------|
| 핵심 | Market | M | 거의 항상 |
| 핵심 | Product | P | 거의 항상 |
| 핵심 | Capability | C | 거의 항상 |
| 핵심 | Finance | F | 거의 항상 |
| 확장 | People & Organization | H | 조직/인력/문화 이슈 시 |
| 확장 | Operations | O | 프로세스/운영/인프라 이슈 시 |
| 확장 | Regulatory & Governance | R | 규제/법률/ESG 이슈 시 |

## 에이전트 인벤토리 (총 49: 비Leaf 23 + Leaf 26)

| 구분 | 에이전트 | 수 |
|------|---------|---|
| PM | research-pm | 1 |
| Division Lead | market, product, capability, finance, people-org, operations, regulatory | 7 |
| Leaf | Division별 MECE 분석가 (.claude/agents/leaves/) | 26 |
| Cross-cutting | fact-verifier, logic-prober, strategic-challenger, red-team | 4 |
| Review | external-reviewer | 1 |
| Synthesis | cross-domain-synthesizer, insight-synthesizer | 2 |
| Report | report-writer, brief-writer | 2 |
| QA | qa-orchestrator, audience-fit-checker, executability-checker, report-auditor, report-fixer | 5 |
| Utility | data-preprocessor | 1 |

### Leaf 인벤토리 (26개)

| Division | Leaves |
|----------|--------|
| Market (5) | market-sizing, customer-analysis, competitive-landscape, channel-landscape, market-dynamics |
| Product (4) | product-offering, value-differentiation, go-to-market, pricing-monetization |
| Capability (4) | technology-ip, human-capital, strategic-assets, execution-readiness |
| Finance (4) | revenue-growth, cost-efficiency, investment-returns, valuation-risk |
| People-Org (3) | org-design, talent-strategy, culture-engagement |
| Operations (3) | process-excellence, supply-chain, infrastructure |
| Regulatory (3) | compliance-status, regulatory-outlook, esg-governance |

### 지식 4-Layer 구조

```
Layer 0: Common Sense    → core/knowledge/common-sense.yaml (범용 분석 상식)
Layer 1: 역할 지식       → .claude/agents/*.md, leaves/**/*.md (분석 방법론)
Layer 2: 도메인 지식     → domains/{domain}/knowledge/ (산업별 축적, 학습 엔진)
Layer 3: 프로젝트 맥락   → {project}/ (일회성)
```

### 학습 엔진

- **시점**: Division Lead가 Phase 1/2 완료 후 자동 실행
- **추출**: 데이터 소스 신뢰도, 프레임워크 효과성, 분석 패턴, 용어, 함정
- **저장**: `{project}/learnings/` → `domains/{domain}/knowledge/`에 머지
- **효과**: 프로젝트를 거듭할수록 시스템이 해당 도메인에서 더 똑똑해짐

## 핵심 프로토콜

### Analysis Type (v4.11)
주제 성격에 따라 Phase 0.5/1 분기. 상세: `core/protocols/analysis-type-protocol.md`

| Type | 용도 | Phase 0.5 가설 | Division Brief |
|------|------|---------------|--------------|
| **decision** | 의사결정 지원 (기본값) | 필수 3~5개 | verification_plan |
| **profile** | 기업·시장 전방위 스터디 | 선택 0~2개 | **baseline_coverage 의무** |
| **exploration** | 기회 탐색 | 후보 5~8개 | exploration_space |
| **monitoring** | 지속 관찰 | 불필요 | monitoring_metrics |

- PM이 Phase 0-A.6에서 주제 키워드로 자동 판정 + Interactive/Team에서 사용자 확인
- `/research --type {type}` CLI 플래그로 명시 가능
- 기본값: 지정 없음 → **decision** (v4.10 역호환)

### 출력 포맷
- **4-Layer 피라미드**: Layer 0(Claim) → 1(Evidence) → 2(Data) → 3(Source)
- **ID 체계**: `{Division}{SubDomain}-##` (예: MGE-01 = Market-Geography-EastAsia)
- **Golden Facts**: `findings/golden-facts.yaml` = 수치 SSOT. fact-verifier만 수정 가능
- **SCR 스토리라인**: 보고서는 Situation→Complication→Resolution 구조
- **Action Title**: 모든 보고서 섹션 제목은 주장 문장형 (주제형 금지)
- **Implementation Playbook**: 전략 제안에 담당/마일스톤/KPI/의존성 포함
- **API 사용 가이드**: `core/protocols/api-usage-guide.md` — API 우선 원칙, 의사결정 매트릭스, Firecrawl 규칙
- **HTML 내보내기 (Phase 4.7)**: MD 정본 → HTML/PDF 변환. `core/protocols/html-export-protocol.md` 참조. 산출: `report-docs.html`, `one-pager.html`, `sources.html`, `one-pager.pdf`
  - **모드별 동작**:
    - Auto: Phase 5.5 생략 시 Phase 5 PASS 직후 자동 실행
    - Interactive: Phase 5.5 피드백 확정 후 "HTML/PDF 생성할까요?" 확인 → 승인 시 실행
    - Team: Interactive와 동일
  - **안전 장치**: `--require-qa-pass` (기본 활성, Critical/Major > 0 시 차단), `--allow-confidential-export` 없이 CONFIDENTIAL 내보내기 차단, 우회 사용 시 `qa/audit-log.md` 기록

### 검증 체계
- VL-1: Leaf 자가 검증 (2소스+, 반증 검토)
- VL-1.5: Lead 삼각 검증 + 스팟체크
- VL-2: Lead 정합성 (엔터티/시점/정의 일관)
- VL-3: fact-verifier 교차 검증 (Division 간)

### 사고 루프 (Phase 3)
- logic-prober: Why Chain 수직 검증
- strategic-challenger: 5-레인 도전 (수평 검증)
- **red-team**: 적대적 반론 — 핵심 전제 반증, 역 시나리오, 숨겨진 가정 노출
- insight-synthesizer: 도전 + 반론 결과 통합 → 전략 보강/수정

### External Review (Phase 3.7)
- 약점 탐지 체크리스트: 확증 편향, 반증 부족, Groupthink, 관점 고정, 대안 부족 (5항목 PASS/FLAG)
- external-reviewer: 전체 프레이밍/접근법 비판 (Red Team과 다름 — Claim 단위가 아닌 분석 전체 수준)
- 외부 모델 리뷰: 선택적 (/ask codex, /ask gemini, 사용자 직접 전달)
- 산출물: `{project}/thinking-loop/self-critique.md`, `{project}/thinking-loop/external-review.md`

### Phase 5 QA 게이트
- audience-fit-checker: Action Title + SCR 스토리라인 + 경영진 적합성 (6개 Check)
- executability-checker: Implementation Playbook 완전성 + 리소스 현실성 (5개 Check)
- report-auditor: 논리 완결성 + SCR 구조 + 미해소 긴장 반영

### Phase 0.5 가설 플로우
- Quick Scan(활성 Division 30분) → 가설 3~5개 도출 → 사용자 정렬 → Division Briefs에 반영
- Phase 1이 "가설 검증/반증" 중심으로 구동

### Phase 5 QA 자동 수정 루프
- report-fixer 자동 스폰 → 재검증 → 최대 3회 반복 → Critical/Major 0건 = PASS

### Phase 5.5 피드백 루프
- 사용자 피드백 분류 → 영향 범위 판정 (minimal/division/cross_division) → 부분 재실행

## 3-모드 체계

| 모드 | 특징 |
|------|------|
| Auto | 직행. 가설 자동 확정, 피드백 생략 |
| Interactive | 매 단계 사용자 게이트 + 가설 검토 + 피드백 |
| Team | Deep Discovery + 토론 + 전방위 되돌아가기 |

## 진입점

```bash
claude
```

**Claude가 자동으로 상태를 감지하고 다음 단계를 제안합니다:**

| 감지된 상태 | Claude의 제안 |
|------------|-------------|
| 도메인 미설정 (첫 사용) | `/setup` 실행을 제안 |
| 도메인 설정 완료, 프로젝트 없음 | `/research` 실행을 제안 + 모드 선택지 제시 |
| 진행 중 프로젝트 존재 | 이어서 진행할지, 새 프로젝트를 시작할지 선택지 제시 |

직접 시작하려면:
```bash
> /setup                                          # 환경 설정 (최초 1회)
> /research interactive {project-name} {주제}      # 리서치 시작
```

## 에이전트 스폰 규칙

- **Phase 1 Lead**:
  - **모드 A (tmux 병렬, 기본)**: tmux 독립 CLI (`spawn-leads.sh`). 완전 병렬 실행
  - **모드 B (Agent tool, tmux 불가 시)**: PM CLI 내에서 Agent tool로 Lead 스폰. 2개씩 순차-병렬 실행
  - tmux 가용 여부는 `/setup` Phase 1에서 자동 감지. 수동 선택도 가능
- **Phase 0.5/2~5**: PM CLI 내에서 Agent tool로 스폰
- **최대 네스팅**: Level 2 (PM → Lead → Leaf)

## 스크립트

| 스크립트 | 용도 |
|---------|------|
| `scripts/quickstart.sh` | 비인터랙티브 환경 점검 (CI/CD용) |
| `scripts/init-project.sh {name}` | 새 프로젝트 디렉토리 스캐폴딩 |
| `scripts/spawn-leads.sh {name} [--attach] [--auto]` | tmux N-pane Lead CLI 실행 (Division 동적 감지) + .done 자동 감지 |
| `scripts/spawn-phase.sh {name} {phase}` | 특정 Phase만 범용 스폰 |
| `scripts/send-phase2.sh {name}` | 활성 Lead CLI에 Phase 2 지시 자동 전송 |
| `scripts/send-to-leads.sh {name} {message}` | 활성 Lead CLI에 임의 메시지 전송 |
| `scripts/generate-charts.py {name}` | findings 데이터 → 차트 자동 생성 (matplotlib). 마리메꼬/하비볼 포함 |
| `scripts/api-caller.py --api {api} --action {action}` | 외부 API 호출 래퍼 (DART, FRED, ECOS 등) |
| `scripts/verify-facts.py {name}` | golden-facts.yaml 수치 교차 검증 |
| `scripts/generate-disconfirming.py {name}` | 반증 시나리오 자동 생성 |
| `scripts/merge-learnings.py {name} [--domain {d}] [--dry-run]` | 프로젝트 학습 결과를 도메인 지식 베이스에 머지 |
| `scripts/check-api-keys.sh` | .env API 키 유효성 일괄 점검 |
| `scripts/setup-api-keys.sh` | API 키 인터랙티브 설정 도우미 |
| `scripts/compile-lead-context.sh {name}` | Lead 부트스트랩 통합 컨텍스트 생성 (토큰 94% 절감) |
| `scripts/generate-source-registry.py {name}` | source_index + golden-facts + 보고서 통합 → source-registry.csv 생성 |
| `scripts/check-env.sh` | 세션 시작 시 환경 상태 JSON 점검 (SessionStart 훅, Lead CLI 자동 스킵) |
| `scripts/render-report-html.py {name}` | Phase 4.7: MD → HTML (report-docs.html, one-pager.html, sources.html). 태그 처리 모드 선택 가능 (link/mark/strip) |
| `scripts/render-onepager-pdf.py {name}` | Phase 4.7: HTML → PDF (Chrome headless 우선, weasyprint fallback). 기본 one-pager.pdf만 |
| `start.sh` | 환경 안내 + Claude 실행 래퍼 (Quick Start 진입점) |

## 권한 정책

settings.local.json의 WebFetch 권한이 프로젝트마다 개별 도메인으로 증가한다.
리서치 에이전트가 다양한 웹 소스에 접근해야 하므로, 다음 그룹 정책을 권장:

```
# 리서치에 자주 사용되는 도메인 그룹
# 한국 공시/뉴스: dart.fss.or.kr, namu.wiki, *.co.kr 계열
# 글로벌 데이터: 도메인별 data-sources.md에 정의된 외부 데이터 소스
# 기업 정보: 도메인별 data-sources.md에 정의된 기업 사이트

# spawn-leads.sh --auto 사용 시 모든 권한이 자동 승인됨
# 보안이 중요한 경우 --auto 없이 실행하여 도메인별 수동 승인
```

## 코딩 컨벤션

- 주석: 한국어
- 변수/함수명: 영어 camelCase
- 데이터 포맷: YAML (에이전트 출력), Markdown (브리핑/보고서)
- 응답 언어: 한국어 (기술 용어 영어 병기)
