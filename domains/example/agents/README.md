# 범용 에이전트 가이드

> 기본 제공 도메인(example)은 `core/templates/`의 범용 템플릿을 그대로 사용합니다.
> 산업 특화 에이전트가 필요하면 이 디렉토리에 추가하세요.

## 에이전트 로딩 우선순위

1. `{project}/agents/{agent}.md` — 프로젝트별 오버라이드 (최우선)
2. `domains/{domain}/agents/{agent}.md` — 도메인 범용 에이전트 (이 디렉토리)
3. `core/templates/agent-template.md` — 기본 템플릿 (폴백)

## 기본 제공 도메인에서는

- Division Lead → `.claude/agents/{division}-lead.md` (도메인 독립)
- Leaf Agent → PM이 Research Plan 기반으로 동적 배치
- Cross-cutting → `.claude/agents/research-pm.md`가 직접 스폰

**추가 에이전트가 필요하면:**
```bash
# 예: 특화 Leaf 에이전트 추가
cp core/templates/agent-template.md domains/example/agents/my-analyst.md
# my-analyst.md를 편집하여 역할 정의
```
