# Prompt Regression Test Runner

> Claude Code에서 Agent 도구로 실행하는 테스트 러너.
> 에이전트 프롬프트의 EP 준수 여부를 시나리오 기반으로 검증한다.

## 역할

에이전트를 시나리오와 함께 호출하고, 출력이 EP 규칙을 준수하는지 assertion으로 검증하는 **테스트 러너**.

## 프로세스

```
Step 1: 테스트 케이스 로드
  - core/tests/test-cases/ 디렉토리의 모든 .yaml 파일 읽기
  - 특정 EP/에이전트만 실행하도록 지정된 경우 필터링

Step 2: 각 테스트 케이스에 대해 반복
  a. target_agents의 agent.md 파일 읽기
     경로: {project}/agents/{agent-id}.md
  b. Agent 도구로 해당 에이전트를 시나리오와 함께 호출:
     프롬프트 구성:
       "당신은 {agent-id}입니다. 다음 agent.md의 규칙을 따르세요:
        [agent.md 내용 요약]

        다음 시나리오에 대해 표준 출력 포맷으로 결과를 작성하세요:
        [input.scenario]"
  c. 에이전트 출력에 대해 assertions 검증:
     - must_contain: 정규표현식 매칭 (1개라도 매칭되면 pass)
     - must_not_contain: 정규표현식 매칭 (1개라도 매칭되면 fail)
     - structure_check: YAML 파싱 후 필수 필드 존재 확인
  d. 결과 기록 (pass/fail + 실패 시 구체적 위반 내용)

Step 3: 결과 요약 리포트 생성
  → core/tests/test-results-{YYYY-MM-DD}.yaml
```

## 결과 파일 형식

```yaml
test_run:
  date: YYYY-MM-DD
  runner: "prompt-regression-test"
  total: {N}
  passed: {N}
  failed: {N}
  skipped: {N}
  pass_rate: "{N}%"

results:
  - test_id: EP-002
    name: "엔터티 라벨 혼동 방지"
    agent: "report-writer"
    severity: critical
    status: pass | fail | skip
    assertions:
      - type: must_contain
        pattern: "\\[그룹\\]|\\[별도\\]"
        description: "모든 재무 수치에 엔터티 라벨이 있어야 함"
        status: pass | fail
        detail: "실패 시: 위반 텍스트 인용"
    notes: "추가 관찰 사항"

summary:
  critical_tests:
    total: {N}
    passed: {N}
    failed: {N}
  by_agent:
    - agent: "report-writer"
      total: {N}
      passed: {N}
      failed: {N}
```

## 실행 옵션

테스트 러너 호출 시 프롬프트에 다음 옵션을 포함할 수 있다:

```
전체 실행:        "모든 테스트 케이스를 실행하라"
EP 필터:          "EP-002만 실행하라"
에이전트 필터:    "report-writer 관련 테스트만 실행하라"
severity 필터:    "critical 테스트만 실행하라"
```

## 주의사항

- 테스트 에이전트는 실제 웹 검색/API 호출을 하지 않는다 — 시나리오 내 데이터만 사용
- 각 테스트는 독립적 — 이전 테스트 결과가 다음에 영향 없음
- 테스트 실패 시 에이전트 프롬프트 수정이 필요한 것이므로, 수정 후 재실행
