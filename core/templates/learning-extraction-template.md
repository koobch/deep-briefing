# 학습 추출 템플릿

> Division Lead가 Phase 1/2 완료 후, PM에 결과를 반환하기 직전에 실행하는 학습 추출 프로세스.
> 목적: 이번 프로젝트에서 배운 것을 도메인 지식으로 축적하여 다음 프로젝트에서 활용.

## 실행 시점

- Phase 1 완료 후 (findings 제출 직전)
- Phase 2 완료 후 (업데이트된 findings 제출 직전)

## 추출 프로세스

### Step 1: 회고 질문 (Lead가 자문)

```
1. 데이터 소스
   - 어떤 소스가 유용했는가? 왜?
   - 어떤 소스가 무용했는가? 왜? (접근 불가, 데이터 부정확, 범위 부족 등)
   - 예상치 못한 좋은 소스를 발견했는가?
   - 소스 접근에 어떤 어려움이 있었는가?

2. 프레임워크
   - 사용한 프레임워크가 이 산업에 적합했는가?
   - 프레임워크를 수정/적응해야 했다면 어떻게?
   - 더 적합한 프레임워크가 있었을까?

3. 분석 패턴
   - 이 산업 특유의 분석 패턴을 발견했는가?
     (예: "이 산업은 X 축으로 분해하는 게 Y 축보다 인사이트가 큼")
   - Leaf 간 교차에서 예상치 못한 인사이트가 나온 곳이 있는가?
   - 어떤 분석이 의사결정에 가장 큰 영향을 줬는가?

4. 용어
   - 이 산업에서 용어 혼동이 있었는가?
   - 같은 용어가 다른 의미로 쓰이는 곳이 있었는가?
   - 새로 정의해야 할 용어가 있었는가?

5. 함정
   - 분석 중 실수하거나 잘못된 방향으로 간 적이 있는가?
   - Leaf 에이전트가 반복적으로 틀린 패턴이 있는가?
   - 데이터 해석에서 주의해야 할 점을 발견했는가?
```

### Step 2: 학습 항목 추출

회고 결과를 아래 카테고리로 분류:

```yaml
# {project}/learnings/{division}-learnings.yaml

division: "{division}"
domain: "{domain}"
project: "{project-name}"
phase: 1  # 또는 2
extracted_at: "YYYY-MM-DDTHH:MM:SS"

learnings:
  sources:
    - name: "소스 이름"
      type: "market_data | financial | ..."
      url: "접근 URL (해당 시)"
      reliability: "high | medium | low"
      cost: "free | freemium | paid"
      divisions: ["market"]
      access_method: "API | 웹 스크래핑 | 직접 다운로드 | 수동 확인"
      notes: "유용했던/무용했던 이유"
      pitfall: "이 소스 사용 시 주의할 점 (해당 시)"

  frameworks:
    - name: "프레임워크 이름"
      division: "market"
      effectiveness: "high | medium | low"
      context: "적용 상황"
      adaptation: "수정한 부분 (해당 시)"
      limitation: "한계 (해당 시)"
      alternative: "더 나은 대안 (해당 시)"

  patterns:
    - id: "XX-001"  # 도메인 약자 + 번호
      pattern: "패턴 설명"
      confidence: "high | medium | low"
      divisions: ["market"]
      implication: "분석에 미치는 시사점"
      counter_example: "이 패턴이 적용되지 않는 경우 (해당 시)"

  terms:
    - term: "용어"
      definition: "이 산업에서의 정의"
      common_confusion: "혼동되는 점"
      measurement: "측정 방법/단위 (해당 시)"
      divisions: ["market", "product"]
      notes: "사용 시 주의사항"

  pitfalls:
    - pitfall: "함정 설명"
      severity: "critical | major | minor"
      context: "발생 상황"
      consequence: "이 함정에 빠지면 어떤 오류가 발생하는가"
      prevention: "방지 방법"
      divisions: ["finance"]
```

### Step 3: 도메인 지식에 머지

추출한 학습 항목을 `domains/{domain}/knowledge/`에 머지:

```
머지 규칙:
1. 기존 항목 발견 (name/term/pattern이 유사):
   → confirmed_by_projects[] 배열에 현재 프로젝트명 추가 (중복 시 무시)
   → notes 보강 (새로운 정보 추가)
   → reliability/effectiveness 조정 (여러 프로젝트 경험 반영)

2. 신규 항목:
   → 추가
   → first_learned에 현재 프로젝트명 기록
   → confirmed_by_projects: [현재 프로젝트명]

3. 기존 항목과 모순:
   → 기존 항목 유지 + conflict 필드 추가
   → 양쪽 증거를 모두 기록
   → 다음 프로젝트에서 검증 대상으로 표시

4. 같은 프로젝트의 Phase 2 머지:
   → 기존 항목 update/overwrite (새 항목으로 추가하지 않음)
   → confirmed_by_projects[]에 이미 프로젝트명 있으면 추가하지 않음
   → Phase 2에서 갱신된 reliability/effectiveness/notes 등은 덮어쓰기

5. _meta.yaml 갱신:
   → projects_seen[] 배열에 현재 프로젝트명 추가 (중복 시 무시)
   → last_project, last_updated 갱신
   → counts 갱신
   → maturity 재판정
```

### Step 4: 머지 후 검증

```
☐ 중복 항목 없는가 (같은 소스/패턴이 두 번 기록되지 않았는가)
☐ 스키마 준수 (각 항목이 정해진 필드를 가지고 있는가)
☐ _meta.yaml과 실제 항목 수가 일치하는가
```

## Lead가 실행하는 전체 흐름

```
Phase 1/2 분석 완료
  ↓
Step 1: 회고 질문 자문
  ↓
Step 2: 학습 항목 추출 → {project}/learnings/{division}-learnings.yaml 저장
  ↓
Step 3: domains/{domain}/knowledge/*.yaml에 머지
  ↓
Step 4: 머지 후 검증
  ↓
PM에 findings 반환 (.done 시그널)
```

## Leaf의 학습 기여

Leaf는 직접 knowledge에 쓰지 않지만, Lead에게 학습 재료를 제공:

```
Leaf 출력의 _learning_notes 필드 (선택적):
  useful_sources: ["이 소스가 특히 유용했음: ..."]
  data_issues: ["이 데이터에 이런 문제가 있었음: ..."]
  terminology_note: ["이 용어는 이 맥락에서 이런 의미였음: ..."]

Lead는 Leaf의 _learning_notes를 수집하여 자신의 학습 추출에 통합.
```
