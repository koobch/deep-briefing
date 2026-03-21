# CLAUDE.md — Deep-Briefing

## 프로젝트 개요

컨설팅급 리서치를 **N-Division 병렬 실행**(핵심 4 + 확장 최대 3)으로 수행하는 에이전트 오케스트레이션 시스템.
에이전트가 5계층(PM → Lead → Sub-lead → Leaf + Cross-cutting/QA)으로 작동.

## 핵심 아키텍처

- **실행 모델**: PM CLI 1개 + 활성 Division Lead CLI N개 (핵심 4 + 확장 최대 3)
- **CLI 간 통신**: 파일 시스템 기반 (직접 통신 없음). `findings/`, `sync/` 디렉토리 경유
- **오케스트레이션 흐름**: Phase 0 → 0.5(가설) → 1(병렬 리서치) → Sync 1 → 2(심화) → Sync 2 → 3(사고 루프) → 4(보고서+PPT) → 5(QA 자동 루프) → 5.5(피드백)

## 디렉토리 구조

```
core/                   → 도메인 독립 프레임워크 (재사용)
  orchestration/        → sync-protocol.md, escalation-protocol.md
  protocols/            → output-format.md (4-Layer), fact-check-protocol.md (VL-1~3)
  templates/            → 에이전트/리드 템플릿, source-url-verifier 등
  tests/                → 프롬프트 테스트 케이스 (EP-001~027)

domains/                → 도메인 플러그인 (도메인별 지식 베이스)
  example/              → 스켈레톤 템플릿 (새 도메인 생성 시 복사)
  {domain}/             → 산업 특화 지식 (frameworks.md, data-sources.md, agents/)

scripts/                → 자동화 스크립트 (아래 스크립트 테이블 참조)

.claude/agents/         → Division Lead 에이전트 정의 (핵심 4 + 확장 3)
.claude/skills/setup    → /setup 스킬 (환경 점검 + 도메인 생성 + API 설정)
.claude/skills/research → /research 스킬 (PM 실행 시퀀스)

{project}/              → 프로젝트별 실행 결과 (1회성)
  00-client-brief.md, 01-research-plan.md, hypotheses.yaml
  division-briefs/, findings/, sync/, thinking-loop/, reports/, qa/
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

## 핵심 프로토콜

### 출력 포맷
- **4-Layer 피라미드**: Layer 0(Claim) → 1(Evidence) → 2(Data) → 3(Source)
- **ID 체계**: `{Division}{SubDomain}-##` (예: MGE-01 = Market-Geography-EastAsia)
- **Golden Facts**: `findings/golden-facts.yaml` = 수치 SSOT. fact-verifier만 수정 가능

### 검증 체계
- VL-1: Leaf 자가 검증 (2소스+, 반증 검토)
- VL-1.5: Lead 삼각 검증 + 스팟체크
- VL-2: Lead 정합성 (엔터티/시점/정의 일관)
- VL-3: fact-verifier 교차 검증 (Division 간)

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

# 처음 사용: 환경 점검 + 도메인 생성 + API 설정
> /setup

# /setup 완료 후 리서치 시작 (프로젝트 초기화 포함)
# /setup Phase 3에서 "바로 리서치 시작" 선택 시 자동 전환됨
> /research interactive {project-name} {주제}
```

## 에이전트 스폰 규칙

- **Phase 1 Lead**: 반드시 tmux 독립 CLI (`spawn-leads.sh`). Agent tool 사용 금지
- **Phase 0.5/2~5**: PM CLI 내에서 Agent tool로 스폰
- **최대 네스팅**: Level 2 (PM → Lead → Sub-lead/Leaf)

## 스크립트

| 스크립트 | 용도 |
|---------|------|
| `scripts/quickstart.sh` | 비인터랙티브 환경 점검 (CI/CD용) |
| `scripts/init-project.sh {name}` | 새 프로젝트 디렉토리 스캐폴딩 |
| `scripts/spawn-leads.sh {name} [--attach] [--auto]` | tmux N-pane Lead CLI 실행 (Division 동적 감지) + .done 자동 감지 |
| `scripts/spawn-phase.sh {name} {phase}` | 특정 Phase만 범용 스폰 |
| `scripts/send-phase2.sh {name}` | 활성 Lead CLI에 Phase 2 지시 자동 전송 |
| `scripts/send-to-leads.sh {name} {message}` | 활성 Lead CLI에 임의 메시지 전송 |
| `scripts/generate-ppt.py {name}` | report-slides.md → PPTX 변환 (python-pptx) |
| `scripts/generate-charts.py {name}` | findings 데이터 → 차트 자동 생성 (matplotlib) |
| `scripts/api-caller.py --api {api} --action {action}` | 외부 API 호출 래퍼 (DART, FRED, Steam 등) |
| `scripts/verify-facts.py {name}` | golden-facts.yaml 수치 교차 검증 |
| `scripts/generate-disconfirming.py {name}` | 반증 시나리오 자동 생성 |
| `scripts/check-api-keys.sh` | .env API 키 유효성 일괄 점검 |
| `scripts/setup-api-keys.sh` | API 키 인터랙티브 설정 도우미 |

## 권한 정책

settings.local.json의 WebFetch 권한이 프로젝트마다 개별 도메인으로 증가한다.
리서치 에이전트가 다양한 웹 소스에 접근해야 하므로, 다음 그룹 정책을 권장:

```
# 리서치에 자주 사용되는 도메인 그룹
# 한국 공시/뉴스: dart.fss.or.kr, namu.wiki, *.co.kr 계열
# 글로벌 데이터: sensortower.com, steamdb.info, newzoo.com
# 기업 정보: 도메인별 data-sources.md에 정의된 기업 사이트

# spawn-leads.sh --auto 사용 시 모든 권한이 자동 승인됨
# 보안이 중요한 경우 --auto 없이 실행하여 도메인별 수동 승인
```

## 코딩 컨벤션

- 주석: 한국어
- 변수/함수명: 영어 camelCase
- 데이터 포맷: YAML (에이전트 출력), Markdown (브리핑/보고서)
- 응답 언어: 한국어 (기술 용어 영어 병기)
