# Prompt Regression Test

> 에이전트 프롬프트가 EP(Error Pattern) 규칙을 실제로 따르는지 검증하는 테스트 인프라.
> "프롬프트는 코드처럼 테스트해야 한다" — 행동 검증의 최소 단위.

## 목적

EP-001~027이 문서화되어 있지만 에이전트가 실행 시 실제로 따르는지 확인할 방법이 없었다.
이 테스트 인프라는 에이전트를 시나리오와 함께 호출하고, 출력이 EP 규칙을 준수하는지 assertion으로 검증한다.

## 구조

```
core/tests/
├── README.md                          # 이 파일
├── run-prompt-tests.md                # 테스트 러너 에이전트 프롬프트
└── test-cases/
    ├── ep-001-platform-verify.yaml    # 플랫폼 확인 검증
    ├── ep-002-entity-label.yaml       # 엔터티 라벨 혼동 방지
    ├── ep-023-source-traceability.yaml # 출처-데이터 추적성
    ├── ep-026-assumption-gate.yaml    # 전제 확신도 등급
    └── ep-027-art-genre-compat.yaml   # 제품-장르 적합도
```

## 테스트 케이스 형식

```yaml
test_id: EP-###
name: "테스트 이름"
target_agents: ["대상 에이전트 ID 목록"]
severity: critical | major | minor

input:
  scenario: |
    에이전트에게 주어질 시나리오 텍스트
  context_files: []  # 필요 시 참조 파일 경로

assertions:
  - type: "must_contain | must_not_contain | structure_check"
    pattern: "정규표현식 패턴"
    description: "이 assertion이 검증하는 내용"
```

## 실행 방법

### 1. 전체 테스트 (smoke test)
```
Claude Code에서:
Agent 도구로 run-prompt-tests.md를 실행
→ 모든 test-cases/*.yaml 실행
→ core/tests/test-results-{date}.yaml 생성
```

### 2. 특정 EP 테스트
```
Agent 도구로 run-prompt-tests.md를 실행
프롬프트에 "EP-002만 실행" 지정
```

### 3. 특정 에이전트 테스트
```
Agent 도구로 run-prompt-tests.md를 실행
프롬프트에 "report-writer 관련 테스트만 실행" 지정
```

## 실행 시점

| 시점 | 범위 | 목적 |
|------|------|------|
| 에이전트 프롬프트 수정 후 | 수정된 에이전트 관련 테스트만 | 회귀 방지 |
| 리서치 시작 전 (선택) | 전체 테스트 | smoke test |
| EP 추가 시 | 새 EP 테스트 케이스 | 새 규칙 검증 가능 확인 |

## 테스트 결과 형식

```yaml
test_run:
  date: YYYY-MM-DD
  total: {N}
  passed: {N}
  failed: {N}
  skipped: {N}

results:
  - test_id: EP-002
    agent: data-researcher
    status: pass | fail | skip
    assertions:
      - description: "assertion 설명"
        status: pass | fail
        detail: "실패 시 구체적 위반 내용"
```

## 새 테스트 케이스 작성 가이드

1. `test-cases/` 디렉토리에 `ep-{###}-{slug}.yaml` 파일 생성
2. 위 형식에 따라 작성
3. `assertions`는 에이전트 출력의 **관찰 가능한 행동**을 검증해야 함:
   - `must_contain`: 출력에 반드시 포함되어야 하는 패턴
   - `must_not_contain`: 출력에 포함되면 안 되는 패턴
   - `structure_check`: YAML 구조 검증 (필수 필드 존재 여부 등)
4. 시나리오는 EP 위반을 유도할 수 있는 현실적 상황 설계
