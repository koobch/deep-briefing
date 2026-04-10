# Changelog — Deep-Briefing

> 에이전트 오케스트레이션 시스템의 변경 이력.
> 카테고리: **Agents** (에이전트 프롬프트), **Protocols** (프로토콜/스키마), **Scripts** (자동화 스크립트), **Docs** (문서/대시보드/백서)

---

## v4.7 — 2026-04-10 (아키텍처 리뷰 + Codex 교차검증 4회)

### Agents
- **slide-writer.md 신규**: Phase 4-B 슬라이드 덱 생성 에이전트 (core/style/ 22개 유형 연결, slide-outline.yaml + slide-deck.html + slide-meta.yaml 산출)
- **finance-lead.md**: valuation-risk 2-Wave 의존성 순서 강제 (Wave 1: 3개 병렬 → Wave 2: valuation-risk)
- **strategic-challenger.md**: why-probe 의존성을 필수→선택적 보강으로 변경 (LP 병렬 실행 가능), Step 9 LP 보강 패스 추가
- **research-pm.md**: Phase 4→4-A/4-B 분리, 인터뷰 질문 16번(보고서 형식) 추가, Phase 3 LP+SC 병렬 스폰, Sync Round 1 Step 6(phase2 생성) 추가
- **qa-orchestrator.md**: Step 2에 verify-source-traceability.py 호출 + 산출물 경로 명시

### Protocols
- **agent-io-spec.yaml 신규**: 에이전트 간 I/O 인터페이스 6개 스키마 (Division Brief, Lead↔Leaf 계약, .done/.progress/.status, Cross-cutting 매트릭스)
- **sync-protocol.md**: Phase 4.5 전환표 등록, .done phase/status 분리 스키마, .progress Phase 공용 + leaves_in_progress 통일, .status 파일 규약, Phase 3 병렬화 (3단계 + SC 보강 패스), Sync R2 Step 번호 통일 (Step 3→4)
- **output-format.md**: (참조) golden-facts source_id/sources 양쪽 호환 인정

### Scripts
- **verify-source-traceability.py 신규**: QA Phase 5 Step 2 자동화 — [S##] + [GF-###] 태그 ↔ source_index 매칭, 제로패딩 정규화, YAML 결과 출력
- **generate-source-registry.py**: golden-facts source_id(단수)/sources(배열) 양쪽 호환, [GF-###] 태그 스캔 추가, golden_facts 필드 매핑
- **verify-facts.py**: L935-957 else/elif 구조 오류 + cp_checker 들여쓰기 수정
- **spawn-leads.sh**: --agent-file→--agent 재스폰 플래그 수정, tmux 세션명 동적화 (research-${PROJECT}), compile-lead-context.sh 자동 호출 (fallback 포함), lead-context-{div}.md 참조, checkpoint.yaml 보존 갱신, 모니터 status:success 체크, .status 기반 30분 stuck 감지, Lead 프롬프트에 status:success 기록 지시
- **send-phase2.sh**: tmux 세션명 동적화, 미완료 Division만 재스폰, .done phase/status 분리, .progress Phase 2 기존 진행분 보존, checkpoint.yaml 보존 갱신, 모니터 status:success 체크, Lead 프롬프트에 status:success 기록 지시
- **send-to-leads.sh**: tmux 세션명 동적화, SESSION 정의 위치 이동
- **spawn-phase.sh**: tmux 세션명 동적화, 모니터 status:success + phase 체크 강화, Lead 프롬프트에 status:success 기록 지시

### Docs
- **CLAUDE.md**: 오케스트레이션 흐름 Phase 4-A/4-B 반영, 에이전트 인벤토리 49개
- **ARCHITECTURE.md**: Phase 3 LP+SC 병렬 실행 표현 반영
- **whitepaper.html**: v4.7 changelog 항목 추가, 버전 번호 업데이트
- **index.html**: 에이전트 수 48→49

### Codex 교차검증 (4회)
1. 아키텍처 리뷰: verify-facts.py 문법 오류, --agent-file 플래그, 세션명 하드코딩 발견
2. P1 설계 검증: SC 입력 의존성, 산출물 경로 불일치, .done 스키마 충돌 발견
3. 프로세스+출처 검증: 모니터 오판 버그, source-registry 3중 실패, Phase 4.5 전환표 누락 발견
4. 최종 점검: Phase 2 .progress 무조건 리셋, [GF-###] 미파싱, checkpoint 덮어쓰기, SC Step 9 미반영 발견

---

## v4.6 — 2026-04-01

### Agents
- Division Lead 강화: 핵심 이슈 도출(조건부) + 분석 내 케이스 임베딩

### Protocols
- BCG 아티클 18개 패턴 차용: 반전 질문, Golden Insights, SCR+PCS 2계층, 3-Layer 시나리오
- 세로형 보고서 템플릿: vertical-report-template.md (인라인 KPI, Pull Quote, So What→Now What)

### Scripts
- generate-source-registry.py: 통합 출처 추적 (14컬럼 source-registry.csv)

---

## v4.5 — 2026-04-01

### Docs
- 시각 품질 개선: BCG 342 ref-spec 통계 기반 차트/도형/밀도 토큰 재설정
- element-catalog.md: 16개 PDF(322p) 이미지 기반 전수 분석 카탈로그
- 16축 루브릭: D1 공간 활용 축 추가
- visual-checker.js: Puppeteer 기반 자동 빈 공간 탐지

---

## v4.4 — 2026-04-01

### Docs
- 슬라이드 시스템 구축: 22유형 프로토타입, CSS 토큰, BCG 레퍼런스
- section-map.md, design-guide.md, 342개 ref-specs JSON

---

## v4.3 — 2026-03-28

### Agents
- 적응형 2-Pass 인터뷰 (Phase 0): Quick → Deep 동적 전환
- user-profile.yaml SSOT, 질문 예산 (Auto 3 / Interactive 10 / Team 무제한)

---

## v4.2 — 2026-03-28

### Agents
- Phase 3.7 External Review 추가 (external-reviewer 에이전트, 48개)

### Scripts
- merge-learnings.py: 학습 엔진 머지 스크립트

---

## v4.0 — 2026-03-23

### Agents
- Leaf 26개 파일화 (.claude/agents/leaves/)
- 4-Layer 지식 시스템 (common-sense.yaml + 도메인 플러그인)

### Scripts
- compile-lead-context.sh: Lead 부트스트랩 통합 컨텍스트 생성

---

## v3.0 — 2026 Q1

- 기본 아키텍처 확립: 4계층 에이전트, Phase 0~5, 4-Layer 검증
