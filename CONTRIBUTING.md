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
domains/        → 도메인별 지식 베이스 (도메인 추가/수정)
scripts/        → 자동화 스크립트 (기능 추가/개선)
.claude/agents/ → 에이전트 정의 (새 Division/Lead 추가)
.claude/skills/ → 스킬 정의 (/research 등)
```

### 새 도메인 추가
1. `cp -r domains/example/ domains/{your-domain}/`
2. `frameworks.md`, `data-sources.md` 작성
3. 필요 시 `agents/` 디렉토리에 도메인 특화 에이전트 추가
4. API 추가 시 `scripts/ADDING-API.md` 참조

### 새 Division 추가
1. `.claude/agents/{division}-lead.md` 생성 (기존 Lead 패턴 참조)
2. `core/orchestration/sync-protocol.md` Research Plan 스키마에 추가
3. `core/protocols/output-format.md` ID 체계에 약자 추가
4. `scripts/init-project.sh` EXTENDED_DIVISIONS 배열에 추가

## 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.
