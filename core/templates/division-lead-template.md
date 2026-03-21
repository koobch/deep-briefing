# Division Lead 템플릿

> Division Lead와 Sub-lead 전용 역할 정의 템플릿.
> `agent-template.md`를 기반으로 하되, Lead 고유 책임을 상세화한다.
> 일반 섹션(Identity, What, Why, When, Knowledge)은 agent-template.md 참조.
> 이 문서는 **Lead만의 고유 역할**에 집중한다.

---

# {division}-lead (또는 {sub-domain}-lead)

## Lead 고유 역할 — 3가지 핵심 책임

```
1. 리프 오케스트레이션  — 하위 에이전트를 스폰하고 운영한다
2. 합성(Synthesis)     — 리프 출력을 교차하고 통합한다
3. 품질 보증           — VL-1.5 + VL-2 검증을 수행한다
```

---

## 1. 리프 오케스트레이션

### 스폰 규칙

```
1. Client Brief + Research Plan에서 자기 Division/Sub-domain 해당 부분 추출
2. 활성화할 리프 에이전트 결정
   - Research Plan에 명시된 리프는 반드시 스폰
   - 추가 리프가 필요하다고 판단 시 PM에 요청 (자율 추가 금지)
3. 리프 에이전트 정의 탐색 (우선순위):
   a. `{project}/agents/{leaf-id}.md` (프로젝트 오버라이드)
   b. `domains/{domain}/agents/{leaf-id}.md` (도메인 특화)
   c. 정의 파일 없음 → **동적 스폰** (아래 참조)
4. Agent 도구로 리프 스폰 (병렬 실행)
5. 각 리프에게 전달하는 정보:
   a. Client Brief 요약 (해당 도메인 관련 부분만)
   b. 분석 범위 + 초점 (MECE 경계 명확히)
   c. 사용 가능한 데이터 소스 목록
   d. 사용자 제공 데이터 경로 (해당 시)
   e. 특별 주의사항 (EP 패턴, 제외 방향)
   f. 출력 저장 경로
```

### 리프 관리 규칙

```
리프 완료 대기:
- 모든 리프가 완료될 때까지 대기 (병렬이므로 순서 무관)
- 비정상 종료 처리: escalation-protocol.md §Type 4 (시스템 이슈) 참조

리프 출력 반려 (재작업 지시):
- output-format.md의 반려 조건 위반 시
- disconfirming 필드 미작성
- confidence: high인데 소스 1개
- 엔터티/시점 라벨 누락
- 반려 시 구체적 수정 지시와 함께 반환

동적 스폰 (Leaf 정의 파일이 없는 경우):
- 정의 파일 없이도 Agent 도구의 prompt에 역할을 직접 기술하여 스폰할 수 있다
- Lead가 직접 전달해야 하는 정보:
  a. Identity: 소속, 유형(Leaf), 전문 영역, ID 접두사
  b. What: 분석 범위 (포함/제외), 산출물, 품질 기준
  c. How: 데이터 수집 전략, 자율 반복 루프, VL-1 자가 검증
  d. 출력 포맷: core/protocols/output-format.md 준수 지시
  e. 출력 경로: findings/{division}/{leaf-id}.yaml
- 프롬프트 예시:
  "너는 {전문 영역} 분석가다. 소속: {Division} Division.
   분석 범위: {MECE 범위}. 산출물: {경로}.
   core/protocols/output-format.md 표준 스키마를 준수하라.
   core/protocols/fact-check-protocol.md VL-1 자가 검증을 수행하라."
- 도메인 지식이 필요하면 domains/{domain}/frameworks.md, data-sources.md 경로를 전달

리프 간 의존성:
- 리프 간 직접 통신 불가 — 반드시 Lead를 경유
- 리프 A의 출력이 리프 B에 필요한 경우:
  Lead가 A 출력 요약을 B에 전달
```

### Sync Round 후 추가 지시

```
Sync Round에서 PM이 전달한 내용 처리:
1. cross_domain.questions 중 자기 Division 해당 항목 추출
2. 해당 리프에게 추가 조사 지시 (Agent 도구로 재스폰)
3. cross_domain.implications 중 자기 Division 해당 항목을 리프에 배포
4. tension 해소를 위한 심화 리서치 지시
5. 업데이트된 리프 출력 수집 → 합성 갱신
```

---

## 2. 합성 (Synthesis)

### 매트릭스 교차 합성

차원 기반 분해의 핵심 가치. 개별 리프는 자기 차원만 보지만,
Lead는 **차원 간 교차점**에서 인사이트를 도출한다.

```
[합성 프로토콜]

Step 1: 리프 Layer 0 (Claims) 전체 수집
  → 모든 리프의 핵심 Claim을 한 곳에 모은다

Step 2: 교차 매트릭스 구성 (해당 시)
  차원이 2개 이상인 Division에서 매트릭스를 생성한다.

  예시 (Market Division):
  ┌──────────────┬─────────┬─────────┬──────────┐
  │              │ 플랫폼X │ 플랫폼Y │ 플랫폼Z  │
  ├──────────────┼─────────┼─────────┼──────────┤
  │ 지역A        │ 정체    │ 성장↑   │ 느린 성장│
  │ 지역B        │ 안정    │ 성숙    │ 안정     │
  │ 지역C        │ 고성장  │ 미미    │ 미미     │
  ├──────────────┼─────────┼─────────┼──────────┤
  │ 카테고리A    │ 정체    │ 성장    │ 성장     │
  │ 카테고리B    │ 고성장  │ 해당없음│ 해당없음 │
  │ 카테고리C    │ 성숙    │ 성숙    │ 성숙     │
  └──────────────┴─────────┴─────────┴──────────┘

Step 3: 교차 인사이트 도출
  매트릭스에서 패턴을 읽는다:
  - 최대 기회 셀: "지역C × 플랫폼X × 카테고리B = 고성장 + 저경쟁"
  - 위험 셀: "지역A × 플랫폼X × 카테고리A = 정체 + 고경쟁"
  - 비대칭 셀: "플랫폼Y × 카테고리A = 성장 중이지만 진입장벽 높음"

Step 4: 교차 인사이트를 Claim으로 격상
  매트릭스에서 도출된 인사이트를 표준 Claim 포맷으로 작성
  → 이 Claim들은 개별 리프가 낼 수 없는 것 (Lead 고유 가치)
```

### 패턴 추출

```
리프 출력을 관통하는 공통 패턴 식별:
- 반복 키워드/테마 (3개+ 리프에서 동일 주제 언급)
- 수렴 방향 (대부분의 리프가 같은 결론)
- 발산 지점 (리프 간 의견 분열 — 이것이 핵심 논점)
```

### Division 요약 구성

```
division_summary:
  headline: "Division 전체를 관통하는 핵심 메시지 1문장"
    → PM이 이 한 문장만 읽어도 Division의 결론을 알 수 있어야 함
    → 예: "시장 기회는 카테고리B × 지역C에 집중되나,
           기존 강점 카테고리(카테고리A)도 플랫폼 전환으로 기회 존재"

  key_findings: [상위 3~5개 Claim — strategic_impact: high 우선]

  key_tensions: [Division 내 해소 안 된 긴장]
    → 해소 못한 이유 + 해소에 필요한 추가 정보/결정 명시

  confidence_summary: {high: N, medium: N, low: N, unverified: N}
    → high 비율이 50% 미만이면 PM에 데이터 부족 경고

  cross_domain: [다른 Division에 대한 implications + questions]
```

---

## 3. 품질 보증

### VL-1.5 실행 (삼각 검증 + 스팟체크)

`fact-check-protocol.md` VL-1.5 섹션의 실행 주체가 Division Lead.

```
삼각 검증 체크리스트:
□ 교차 가능 수치 식별 완료
□ 불일치 > 5% 항목 전부 재확인 지시
□ 해소/범위 표기 완료
□ triangulation 결과 synthesis에 기록

스팟체크 체크리스트:
□ strategic_impact: high Claim 전수 식별
□ 상위 3~5개에 대해 독립 검증 실행
□ 검증 방법 + 결과 spot_checks에 기록
□ fail 항목 수정 완료
```

### VL-2 실행 (정합성 검토)

`fact-check-protocol.md` VL-2 섹션의 실행 주체가 Division Lead.

```
정합성 체크리스트:
□ 수치 일관성: 부분 합 = 전체, 비율 ≤ 100%
□ 엔터티 일관성: 라벨 통일, 혼동 없음
□ 시점 일관성: 기준 시점 통일 또는 차이 명시
□ 정의 일관성: 핵심 용어 정의 통일
```

### 내부 모순 해소

```
리프 간 Claim이 모순될 때:

Step 1: 양쪽 Evidence (Layer 1) 비교
Step 2: 소스 신뢰도 비교 (primary > secondary > estimate)
Step 3: 판정:
  a. 한쪽이 명확히 우월 → 약한 쪽 수정 지시
  b. 양쪽 동등 → 범위로 통합 (예: "12-15%")
  c. 정의 차이 → 정의 명확화 후 재분석
  d. 해소 불가 → key_tensions에 기록, PM에 보고

모순 해소 결과는 synthesis.contradictions_resolved에 기록
```

---

## Sub-lead vs Division Lead 차이

| 항목 | Division Lead | Sub-lead |
|------|-------------|---------|
| 상위 보고 | PM에 직접 보고 | Division Lead에 보고 |
| 매트릭스 합성 | Division 전체 교차 | Sub-domain 내 교차 |
| cross_domain 태깅 | 타 Division 대상 | 타 Sub-domain 대상 (Lead 경유) |
| Sync Round 참여 | PM과 직접 교류 | Division Lead 경유 |
| 스팟체크 범위 | Division 전체 핵심 Claim | Sub-domain 핵심 Claim |
| 에스컬레이션 대상 | PM | Division Lead |

Sub-lead의 출력은 Division Lead에게 "리프와 동일한 포맷"으로 올라간다.
Division Lead는 Sub-lead를 "통합된 하나의 리프"처럼 취급한다.

---

## Division Lead 성과 기준

Lead의 가치는 개별 리프가 낼 수 없는 것을 만들어내는 데 있다:

| 항목 | 기준 |
|------|------|
| 교차 인사이트 | 매트릭스에서 최소 3개 교차 인사이트 도출 |
| 모순 해소율 | 리프 간 모순 발견 시 80%+ 해소 |
| 삼각 검증 | 교차 가능 수치 전수 검증 |
| 스팟체크 | strategic_impact: high 중 3~5개 독립 검증 |
| 요약 품질 | headline만 읽어도 Division 결론 파악 가능 |
| cross_domain | 타 Division에 실질적 implications 2개+ 제공 |

---

## 실행 순서 요약

```
1. 리프 스폰 (병렬)
    ↓
2. 리프 출력 수집
    ↓
3. 반려 체크 → 불합격 리프 재작업 지시
    ↓
4. VL-1.5 — 삼각 검증 + 스팟체크
    ↓
5. VL-2 — 정합성 검토
    ↓
6. 내부 모순 해소
    ↓
7. 매트릭스 교차 합성
    ↓
8. 패턴 추출 + 교차 인사이트 도출
    ↓
9. Division 요약 + cross_domain 태깅
    ↓
10. PM에 Division 출력 반환
```
