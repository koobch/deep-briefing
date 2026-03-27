# Contributing

Deep-Briefing에 기여해 주셔서 감사합니다.

## 기여 방법

### 이슈 등록
- 버그 리포트, 기능 제안, 질문은 GitHub Issues에 등록해 주세요.
- 이슈 템플릿이 없으면 자유 형식으로 작성해 주세요.

### Pull Request
1. 이 저장소를 Fork합니다.
2. 기능 브랜치를 생성합니다: `git checkout -b feature/my-feature`
3. 변경사항을 커밋합니다: `git commit -m "Add my feature"`
4. 브랜치를 Push합니다: `git push origin feature/my-feature`
5. Pull Request를 생성합니다.

### 코딩 컨벤션
- 주석: 한국어
- 변수/함수명: 영어 camelCase
- 데이터 포맷: YAML (에이전트 출력), Markdown (브리핑/보고서)
- Python: 3.8+ 호환, 외부 패키지 최소화

### 디렉토리 구조
```
core/           → 도메인 독립 프레임워크 (수정 시 모든 도메인에 영향)
  templates/    → 에이전트/리드/리프 템플릿, learning-extraction
  protocols/    → output-format, fact-check-protocol
  orchestration/→ sync-protocol, escalation-protocol
  tests/        → EP-001~033 프롬프트 테스트 케이스
domains/        → 도메인별 지식 베이스 (도메인 추가/수정)
scripts/        → 자동화 스크립트 (기능 추가/개선)
.claude/agents/ → 에이전트 정의 (PM 1, Lead 7, Leaf 26, Cross-cutting 4, Synthesis 2, QA 5, Report 1, Utility 1)
  leaves/       → Leaf 에이전트 역할 정의 (Division별 MECE 분석 구조)
.claude/skills/ → 스킬 정의 (/setup, /research)
docs/           → 아키텍처 문서
```

전체 아키텍처: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** 참조.

### 새 도메인 추가
1. `cp -r domains/example/ domains/{your-domain}/`
2. `frameworks.md`, `data-sources.md`, `benchmarks.md` 작성
3. 필요 시 `agents/` 디렉토리에 도메인 특화 에이전트 추가 (`core/templates/leaf-agent-template.md` 참조)
4. API 추가 시 `scripts/ADDING-API.md` 참조

### 새 Division 추가
1. `.claude/agents/{division}-lead.md` 생성 — 기존 확장 Lead(`people-org-lead.md`, `operations-lead.md`, `regulatory-lead.md`) 패턴 참조
2. `core/orchestration/sync-protocol.md` Research Plan 스키마에 추가
3. `core/protocols/output-format.md` ID 체계에 약자 추가
4. `scripts/init-project.sh` EXTENDED_DIVISIONS 배열에 추가
5. `CLAUDE.md` Division Pool 테이블 + 에이전트 인벤토리 업데이트
6. `README.md` 에이전트 구성 테이블 업데이트

## 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.
