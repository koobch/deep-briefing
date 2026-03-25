# 도메인 에이전트 가이드

> 도메인 특화 에이전트 오버라이드를 이 디렉토리에 추가합니다.
> 기본 제공 도메인(example)은 범용 Leaf 정의(`.claude/agents/leaves/`)를 그대로 사용합니다.

## 에이전트 로딩 우선순위 (v4)

```
1. {project}/agents/{agent}.md          — 프로젝트별 오버라이드 (최우선)
2. domains/{domain}/agents/{agent}.md   — 도메인 특화 에이전트 (이 디렉토리)
3. .claude/agents/leaves/{division}/{leaf}.md — 범용 Leaf 역할 정의 (v4 기본)
4. 동적 스폰 — Lead가 프롬프트에 직접 기술 (폴백)
```

## 기본 구조

- **Division Lead** → `.claude/agents/{division}-lead.md` (도메인 독립)
- **Leaf Agent** → `.claude/agents/leaves/{division}/` (범용, 내부 MECE 분석 구조 포함)
- **Cross-cutting** → `.claude/agents/` (fact-verifier, logic-prober 등)

## 도메인 특화 에이전트 추가 방법

특정 산업에서 범용 Leaf의 분석 구조를 변경하거나, 산업 특화 Leaf를 추가할 때:

```bash
# 범용 Leaf를 복사하여 도메인 특화 버전 생성
cp .claude/agents/leaves/market/market-sizing.md domains/my-domain/agents/market-sizing.md
# → 산업 특화 분석 구조/데이터 소스로 수정
```

## 지식 시스템과의 관계

- 에이전트 .md 파일 = **역할 지식** (Layer 1: 어떻게 분석하는가)
- `domains/{domain}/knowledge/` = **도메인 지식** (Layer 2: 이 산업에서 뭘 봐야 하는가)
- 같은 Leaf가 다른 도메인 knowledge를 로드하면 다른 산업 전문가로 작동
