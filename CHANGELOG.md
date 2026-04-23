# Changelog — Deep-Briefing

> 에이전트 오케스트레이션 시스템의 변경 이력.
> 카테고리: **Agents** (에이전트 프롬프트), **Protocols** (프로토콜/스키마), **Scripts** (자동화 스크립트), **Docs** (문서/대시보드/백서)

---

## v4.12 — 2026-04-23 (품질 감사 후속 수정 + Codex 슬라이드 통합)

### 의사결정 기록
- **배경**: v4.11 완료 후 시스템 전반 품질 감사(Codex + Claude 병렬)에서 13건 이슈 발견. 핵심은 Critical 1건(소스 강도 게이트 형식적 검증), Major 10건(MECE 중복, 모순 해소 rubric 부재, 의도 보존 등). 사용자 요청으로 Codex 슬라이드 생성(Phase 4.8) 통합 포함.
- **접근**: 이슈 10건 + Phase 4.8을 단일 릴리스 v4.12로 묶고, Issue #1 우선 커밋(68800b8) 후 잔여 이슈 일괄 처리.

### Tier 1 — 필수 수정
- **Issue #1 (Critical)**: VL-3.5 Source Strength Gate
  - `scripts/verify-source-strength.py` 신규 — Claim confidence vs 소스 조합 매트릭스 검증
  - `core/protocols/fact-check-protocol.md` VL-3.5 섹션
  - `.claude/agents/qa-orchestrator.md` Step 2.5
- **Issue #2 (Major)**: Leaf MECE 경계 재정의
  - Market Division 5개 Leaf에 "수치 재산출 금지" 블록 추가
  - market-sizing을 **수치 SSOT**로 확정 — 다른 Leaf는 [GF-###] 재참조만
- **Issue #3 (Major)**: Division 모순 해소 rubric
  - `core/protocols/tension-resolution-rubric.md` 신규 — 4단계 우선순위 (엔터티→소스강도→최신성→사용자의도)
  - insight-synthesizer 수렴 판정 5조건으로 확장

### Tier 2 — 중요 수정
- **Issue #4 (Major)**: intent_coverage_matrix
  - Phase 0.5-D 산출물에 사용자 의도 coverage 추적 매트릭스 추가
  - Sync Layer 0 요약에서 의도 손실 방지
- **Issue #5 (Major)**: DQ Check 6~8 analysis_type 분기
  - audience-fit-checker Check 6/8을 decision/profile/exploration/monitoring 타입별 severity로 분기
  - profile에서 DQ 미답변이 Critical → Minor로 하향 (intent_coverage가 대체 기준)
- **Issue #6 (Major)**: Phase 5.5 feedback-impact 자동화
  - `scripts/feedback-impact.py` 신규 — 피드백 키워드 → minimal/division/cross_division/ambiguous 자동 판정
  - downstream HTML/PDF/thinking-loop 무효화 자동 감지

### Tier 3 — 문서 보강
- **Issue #7**: Leaf 출력에 `domain_knowledge_used` 필드 추가 (output-format.md)
- **Issue #9**: analysis_type 'ambiguous' 중간 상태 + Auto 모드 fallback 처리
- **Issue #10**: confidence 값에 `insufficient` 추가 — 실패 인정 경로 공식화

### Phase 4.8 신규 — Codex 슬라이드 통합
- **배경**: 사용자 요청으로 LinkedIn의 `gpt-slide-*` 4단계 스킬 아이디어 통합
- **원칙**: MD 정본 유지, 외부 도구 위임 (v4.9 슬라이드 제거 결정 존중)
- **신규 파일**:
  - `core/protocols/slide-export-protocol.md` — Phase 4.8 전체 프로토콜 명세
  - `scripts/render-slides-codex.py` — 4단계 파이프라인 (design → plan → prompt → generate)
- **4단계**:
  - Step 1: `core/style/report-templates/` CSS 토큰 → DESIGN.md 자동 생성
  - Step 2: Golden Insights + SCR → slide-outline.yaml (analysis_type별 5~20장)
  - Step 3: 페이지별 JSON 프롬프트 (layout, content, design_constraints, hint)
  - Step 4: `codex exec`로 이미지 렌더 → `{project}/slides/page_*.png`
- **Fallback**:
  - Codex 미설치 → Step 3까지만 생성, 프롬프트를 사용자가 직접 실행
  - Canva MCP 옵션은 v4.12.3에서 추가 예정

### 검증
- **Source Strength**: 스모크 테스트 4 케이스 모두 정상 판정 (OK/MISMATCH/INSUFFICIENT)
- **feedback-impact**: 4 케이스 (minimal/division/cross_division/ambiguous) 정상 분류
- **slide-render**: profile 타입 자동 인식 → 14장 프롬프트 생성 확인
- **Codex 교차 검증**: Issue #1에서 4 Major FAIL 수정 후 PASS

### 역호환
- 모든 신규 필드 optional
- Phase 4.8은 명시적 실행 시에만 동작
- `analysis_type` 미지정 → decision 기본값 (v4.10 이전 호환)
- confidence 'insufficient'는 새 값, 기존 high/medium/low/unverified 그대로 유효

### 예상 효과
- 경영진 발표용 슬라이드 이미지 자동 생성 가능 (Codex 환경)
- 소스 강도가 형식적 태그에서 실질 검증으로 강화
- 사용자 피드백 처리 시 자동 범위 판정으로 재실행 효율화
- Division 간 모순이 rubric 기반으로 일관되게 해소

### 예정된 후속 작업 (v4.13)
- Issue #8: Leaf 무작위 10~20% Layer 3 감사
- Issue #11: 재현성 · 토큰 예산 관리
- Phase 4.8-B: Canva MCP 경로
- 네이버웹툰 profile + 슬라이드 end-to-end 실증

---

## v4.11 — 2026-04-22 (Analysis Type 체계 도입 — 가설 중심 편향 해소)

### 의사결정 기록
- **발견된 문제**: "네이버웹툰 분석" 같은 기업·시장 프로파일 요청에도 Phase 0.5 가설 도출 → verification_plan 주입 파이프라인으로 진행되어 시장 규모, 실적 추이, IP 활용, 인력 구성 같은 **기초 전방위 조사**가 누락되는 사례 발생
- **근본 원인**: Phase 0.5 가설 게이트 강제화 + Division Brief 스펙에 `baseline_coverage` 필드 부재 + analysis_type 개념 부재
- **해결책**: 4-Type Analysis Taxonomy (decision / profile / exploration / monitoring) 도입. Profile 타입에서는 가설과 독립적으로 baseline_coverage를 Division Brief에 의무 주입

### Protocols (신규 1개)
- **core/protocols/analysis-type-protocol.md** 신규:
  - 4가지 Type 정의 + PM 판정 휴리스틱
  - Baseline Coverage Catalog (7 Division × 필수 항목 매트릭스)
  - Division Brief 스키마 확장 (`analysis_type`, `baseline_coverage`, `entity_target`, `exploration_space`, `monitoring_metrics`)
  - Phase 0.5/1 타입별 분기 규칙
  - 기업 Profile 특화 추가 항목 (실적 추이, 공식 전략, IP 활용 사례, 채널 구조, 경쟁사 비교)

### Agents
- **research-pm.md**:
  - Step 0-A.6 신규 — analysis_type 자동 판정 + 사용자 확인 로직
  - Research Plan YAML 스키마에 `analysis_type`, `analysis_type_rationale`, `entity_target` 필드 추가
- **market/product/capability/finance/people-org/operations/regulatory-lead.md (7개)**:
  - "v4.11 Analysis Type & Baseline Coverage 체크" 섹션 추가
  - Step 0-A: Division Brief에서 analysis_type + baseline_coverage 읽기
  - Step 0-B: 타입별 Leaf 스폰 우선순위 (baseline → verification → cross-domain)
  - Step 0-C: 구성 오류 에스컬레이션 조건
- **leaves/**/*.md (26개)**:
  - "필수 커버리지 (v4.11 Analysis Type 프로토콜)" 섹션 일괄 추가
  - analysis_type=profile/exploration 시 baseline_coverage 항목을 가설 유무와 무관하게 수행

### Skills
- **.claude/skills/research/phase-0-discovery.md**:
  - Phase 0.5 "v4.11: Analysis Type별 분기" 서두 추가
  - Step 0.5-B를 4타입 분기 구조로 확장 (decision/profile/exploration/monitoring)
  - Step 0.5-D에 baseline_coverage, exploration_space, monitoring_metrics 주입 분기 추가
  - Phase 0.5 완료 게이트를 타입별 조건으로 재구성
- **.claude/skills/research/phase-1-parallel.md**:
  - Division Brief 필수 포함 내용에 신규 필드 7개 추가
  - Leaf 스폰 실행 우선순위 규칙 명시
- **.claude/skills/research/SKILL.md**:
  - `/research --type {decision|profile|exploration|monitoring}` CLI 플래그 추가
  - PM 자동 판정 휴리스틱 안내

### Knowledge
- **core/knowledge/common-sense.yaml**:
  - `analysis_principles`에 "전방위 기초 조사" 신규 원칙 추가
  - 타입별 적용 조건 (`applies_when`) + 7개 baseline_checklist 항목 + 실패 모드 예시

### Docs
- **CLAUDE.md**:
  - 오케스트레이션 흐름에 Phase 0-A.6(analysis_type 판정) 반영
  - "Analysis Type (v4.11)" 섹션 추가 (4타입 요약표)

### 역호환성
- `analysis_type` 미지정 프로젝트 → 자동 **decision**으로 판정 (v4.10 동작 완전 유지)
- 모든 신규 필드는 optional
- 기존 `verification_plan` 경로 완전 보존
- v4.10 이전 프로젝트 재실행 시 수정 불필요

### 예상 효과
- "네이버웹툰 분석" 같은 profile 요청 → 시장 규모, 3년 매출 추이, 경쟁사 비교, IP 활용 사례, 미디어 믹스, 조직 구성 등 전방위 커버리지 자동 보장
- "M&A 타당성 검토" 같은 decision 요청 → v4.10과 동일한 가설 중심 경로
- "분기별 업데이트" 같은 monitoring → 지표 목록만 확정, Division Brief 최소화

### Codex 교차검증 반영 (3회차 완료 기준)

**1회차 수정 (A/D/G/H)**:
- research-pm 판정 휴리스틱을 단순 매칭에서 **가중치 룰**로 전환 (profile/decision/exploration/monitoring 각각 +1~+5 점수, 동률 시 사용자 확인)
- 핵심 Leaf 4개(revenue-growth, strategic-assets, channel-landscape, competitive-landscape)에 **baseline_contract** 블록 추가 (area, required_deliverables, company_profile_addons, iteration_log 기록 의무)
- 기업 Profile 특화 항목(§4.3)을 해당 Leaf의 필수 산출물로 승격
- audience-fit-checker **Check 9** + report-auditor **Step 9.5** 신규 (baseline_coverage 검증 로직)

**2회차 수정 (II/JJ/KK/LL/MM/NN/OO/PP)**:
- 나머지 **22개 Leaf** 전체에 baseline_contract 추가 (catalog 매핑 기반, 총 26/26 완비)
- **report-fixer**: baseline 누락 수정 매핑 추가 + "섹션 추가 허용 예외" 명시
- **output-format.md iteration_log**: `baseline_area`, `deliverable_status`, `company_profile_addons_status` 필드 추가
- **analysis-type-protocol.md §8.5**: "에이전트 프롬프트 + 스크립트 자동화 병행" 실행 모델 명시 + catalog 조회 절차 + `--type` 플래그 파싱 방식
- **phase-2-synthesis.md**: "Exploration 후보 가설 확정" 섹션 신규 (Step E-A~D, verdict 매트릭스)
- **analysis-type-protocol.md §4.4**: market/product/region entity_type별 특화 addon 추가
- **common-sense.yaml**: `applies_when` 해석 가이드 + `applies_when_check` 필드

**3회차 수정 (QQ/RR/TT/UU/VV/WW/XX)**:
- **market-dynamics**: 규제 항목을 "산업·매크로 영향"으로 축소 (regulatory-outlook 관할 충돌 해소)
- **report-fixer**: baseline 데이터가 결론 뒤집는 경우 `structural_conflict` 승격 규칙 추가
- **analysis-type-protocol.md**: "스크립트 자동화가 아닌" 표현을 "병행" 모델로 완화
- **§4.4 구현 주의**: Leaf contract의 `company_profile_addons` 필드명 역호환 해석 명시 (v4.12에서 리팩토링)
- **insight-synthesizer.md**: Exploration 후보 가설 확정 책임 명시 + `exploration-confirmation.yaml` 산출물
- **common-sense.yaml**: `applies_when_check`를 optional로 명확히 정의
- CHANGELOG(이 섹션) 업데이트

### 예정된 후속 작업
- Codex 교차검증 4~5회차 (잔여 FAIL 확인)
- 네이버웹툰 profile 재실행 (`deep-briefing-v4.10-test`)로 실증 검증

---


### Cross 검증 3회 + 추가 순차 검증 5회 반영 (총 40건+ FAIL 수정)

**Cross Round 1~3 (Codex + Claude 병렬)**:
- phase-2-synthesis에 analysis_type × 사고루프 매트릭스 추가 (decision 전체 / profile 선택적 / exploration 후보 확정 / monitoring 축약)
- report-writer + brief-writer에 타입별 Governing Thought + Step 0-pre 매트릭스
- audience-fit-checker + report-auditor 출력 스키마에 issue_id + baseline_area 필드 추가
- agent-io-spec Division Brief + Lead↔Leaf 계약에 analysis_type/entity_target/baseline_coverage/exploration_space/monitoring_metrics 전파 필수
- sync-protocol Research Plan 스키마 + Division Brief 주입 블록을 analysis_type별 분기로 업데이트
- Research Plan baseline_coverage_summary 스키마 정정 (divisions 객체형)

**Sequential Round 6~10 (추가 Codex 검증)**:
- common-sense.yaml: monitoring 타입은 baseline 생략 명시
- sync-protocol divisions leaves 중복/누락 정정 (capability에 human-capital 추가, finance에 cost-efficiency/valuation-risk 추가)
- research-pm YAML 구조 정정 (baseline_coverage_summary를 divisions + entity_specific_addons 객체로)
- Catalog §4 영역명 정본화 + Leaf baseline_contract.area / iteration_log.baseline_area 일관화
- analysis-type-protocol §3 판정 규칙을 가중치 룰로 상세 기술 (research-pm 본문과 동기화)
- 확장 Division (People-Org, Operations, Regulatory) 영역명도 Leaf와 일관화
- output-format.md iteration_log의 company_profile_addons_status → entity_specific_addons_status 명칭 변경 (역호환 주석)

**최종 판정**: Critical 0 / Major 0 (릴리스 승인)

## v4.10 — 2026-04-18 (Phase 4.7 HTML/PDF 내보내기 도입)

### 의사결정 기록
- **배경**: v4.9에서 슬라이드 시스템을 제거하면서 MD가 최종 산출물이 됨. 경영진/실무진이 브라우저·이메일·인쇄로 바로 소비할 수 있는 보조 산출물 필요
- **핵심 판단**: HTML/PDF는 MD 정본의 **파생물(derivative)** — 에이전트는 MD만 생성, 별도 변환 레이어(Phase 4.7)에서 HTML/PDF 렌더링
- **QA 불변**: Phase 5 QA 파이프라인은 MD만 검증 (audience-fit-checker, report-auditor 등 기존 로직 100% 유지). HTML 생성은 QA PASS 이후
- **외부 의존성 최소**: Python `markdown` + `jinja2`(이미 일반 의존성) + Chrome headless(macOS 기본 설치). 신규 의존성 0개(weasyprint는 선택적 fallback)

### Scripts (신규 2개)
- **scripts/render-report-html.py 신규**: Phase 4.7 MD → HTML 변환기
  - `reports/report-docs.md` → `report-docs.html` (좌측 TOC 사이드바 + 본문)
  - `reports/one-pager.md` → `one-pager.html` (A4 1p, 태그 자동 제거, 단일 컬럼 피라미드 레이아웃)
  - `findings/golden-facts.yaml` + `findings/**/*.yaml` 의 `source_index` → `sources.html` (탭 + 검색 + 딥링크 앵커)
  - 태그 처리 모드: `link` / `mark` / `strip` (CLI 플래그)
  - Financial Snapshot 표의 "출처"/"Source" 열 자동 제거 (원페이퍼 한정)
- **scripts/render-onepager-pdf.py 신규**: Phase 4.7 HTML → PDF 변환기
  - Chrome headless 우선 (macOS 기본 설치 경로 자동 탐지)
  - weasyprint fallback (설치된 경우)
  - Chrome 타임아웃 시 파일 존재 여부로 재판정 (일부 환경의 Chrome 종료 지연 대응)

### Protocols
- **core/protocols/html-export-protocol.md 신규**: Phase 4.7 전체 프로토콜 명세
  - 설계 원칙(MD 정본, QA 불변, 출처 분리, 인쇄 호환)
  - 실행 순서, 산출물 상세, 옵션, 실패 처리, 재실행 조건

### Style (신규 템플릿 디렉토리)
- **core/style/report-templates/ 신규**:
  - `shared/tokens.css` — 디자인 토큰 (McKinsey/BCG 컨설팅 팔레트: 딥 네이비 #003a70 + 블루 #0066cc)
  - `shared/base.css` — 본문 타이포그래피, 리셋, 테이블/리스트/코드
  - `shared/print.css` — @media print 공통 규칙
  - `report-docs/{report-docs.css, report-docs.html.j2}` — 세로형 상세 보고서 템플릿
  - `one-pager/{one-pager.css, one-pager.html.j2}` — A4 1페이지 단일 컬럼 레이아웃
  - `sources/{sources.css, sources.html.j2}` — 출처 인덱스 (탭 + 검색 + 딥링크)
  - `README.md` — 템플릿 사용 가이드

### Agents
- **report-writer.md**: "Phase 4.7 핸드오프" 섹션 추가 — MD만 생성, HTML/PDF는 Phase 4.7 담당
- **brief-writer.md**: 동일. 추가로 톤 가이드 "개조식(체언 종결)" 명시, Financial Snapshot 출처 열 자동 제거 규칙 안내, P0/P1/P2 액션 포맷 파서 규칙 명시

### Skills
- **.claude/skills/research/phase-2-synthesis.md**: Phase 4.7 섹션 추가 (Phase 5.5 이후 실행)
- **.claude/skills/research/SKILL.md**: 실행 시퀀스 + 사용자 개입 포인트 요약 테이블에 Phase 4.7 추가

### Docs
- **CLAUDE.md**:
  - 오케스트레이션 흐름에 Phase 4.7 추가
  - 디렉토리 구조 `core/style/report-templates/` 설명 추가
  - 핵심 프로토콜 "HTML 내보내기" 항목 추가
  - 스크립트 테이블에 render-report-html.py / render-onepager-pdf.py 추가

### Dependencies
- **requirements.txt**: `markdown>=3.5`, `jinja2>=3.1` 명시 (기존에 설치되어 있었으나 문서화)

### 검증
- 스모크 테스트: GF 17개 + Source 6개 샘플 → 링크 14개 모두 앵커 매칭 (Dangling 0)
- PDF 생성: Chrome headless A4 1페이지 강제 ✅
- 출처 열 자동 제거: Financial Snapshot 헤더에서 "출처" 열 탈락 확인 ✅
- BLUF 박스: 검은 글씨 가독성 이슈 → 흰색 통일 + 밑줄 강조로 해결
- 레이아웃: 2열 분할 → 단일 컬럼 수직 피라미드 (사용자 피드백 반영)

---

## v4.9 — 2026-04-11 (슬라이드 시스템 제거 — 보고서 2종 체계 확정)

### 의사결정 기록
- **제거 사유**: slide-writer(Phase 4-B)의 슬라이드 품질이 기대에 미달. v1(CSS+HTML), v2(자체 JS 렌더러), Marp CLI 연동 모두 시도했으나 만족스러운 결과를 얻지 못함
- **핵심 판단**: 이 프로젝트는 리서치 시스템이지 슬라이드 도구가 아님. 슬라이드 렌더링 엔진 구축은 범위 밖
- **Codex 교차검증**: "슬라이드 렌더러를 만들지 않고 구조화된 Markdown만 정본으로 출력하는 것이 제약조건을 가장 잘 만족" (D > B > A > E > C 순서 권고)
- **보존**: `core/style/` 하위 디자인 가이드/CSS/section-map은 레퍼런스로 보존 (git 히스토리에 전체 이력 존재)

### Agents
- **slide-writer.md 삭제**: Phase 4-B 에이전트 제거. 에이전트 49개
- **brief-writer.md 수정**: "Phase 4-B 병렬" 참조 제거

### Protocols
- **agent-io-spec.yaml**: slide-writer 항목 삭제, qa-orchestrator reads에서 slides/ 제거
- **sync-protocol.md**: Step 4-B 블록 삭제, 전환표에서 슬라이드 조건 제거

### Scripts
- **build-slides.sh 삭제**
- **core/style/v2-experimental/ 삭제**: 자체 렌더러 실험 코드 (slide-core.css, slide-parser.js, slide-renderer.js, slide-fit.js)

### Docs
- 모든 문서에서 slide-writer/Phase 4-B 참조 제거 (CLAUDE.md, research-pm.md, ARCHITECTURE.md, whitepaper.html, index.html, dashboard.js)
- 보고서 체계: 3종(세로+슬라이드+원페이퍼) → **2종(세로+원페이퍼)**

### 시도 이력 (레퍼런스)
- v1: CSS Grid + 고정 px (글자 겹침, 빈 공간)
- v2: 자체 JS 파서/렌더러 (더 심각한 렌더링 문제)
- Marp CLI: 품질 좋으나 외부 의존성/공급망 보안 우려
- Marp 패턴 차용 + 자체 렌더러: 외부 의존성 0이나 CSS 품질 미달
- 최종 결정: 슬라이드 렌더러를 내장하지 않음

---

## v4.8 — 2026-04-10 (경영진 원페이퍼 추가)

### Agents
- **brief-writer.md 신규**: Phase 4-C 경영진 원페이퍼 에이전트 (BLUF + Key Findings 3 + Recommended Actions + Risk Alert, 1~2페이지)
- **research-pm.md**: Phase 4-C 트리거 + brief-writer 스폰 로직, 인터뷰 질문 16번 원페이퍼 옵션 추가

### Protocols
- **agent-io-spec.yaml**: brief-writer I/O 매트릭스 추가
- **sync-protocol.md**: Phase 4→4.5 전환 게이트에 one-pager.md 포함

### Docs
- **CLAUDE.md**: 흐름 문자열 Phase 4-C 추가, 에이전트 50개 (비Leaf 24), Report 3개
- **ARCHITECTURE.md**: Phase 4-C 원페이퍼 단계 추가
- **whitepaper.html**: 에이전트 50개, brief-writer 카드/테이블/Phase 흐름
- **index.html**: 에이전트 50개, Phase 12개, brief-writer 칩
- **dashboard.js**: Phase 4-C 모델 추가

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
