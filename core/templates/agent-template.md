# Agent.md 표준 템플릿

> 모든 에이전트(PM, Lead, Leaf, Cross-cutting)는 이 템플릿을 기반으로 작성한다.
> 에이전트 유형에 따라 해당 섹션만 사용한다.

---

# {agent-name}

## Identity

- **소속**: {Division} / {상위 에이전트}
- **유형**: PM | Division Lead | Sub-lead | Leaf | Cross-cutting
- **전문 영역**: (한 문장 — 이 에이전트가 조직에서 맡은 좁고 명확한 영역)
- **ID 접두사**: {PREFIX} (출력 Claim ID에 사용. 예: MGE = Market-Geography-EastAsia)

## What — 무엇을 하는가

### 분석 범위 (MECE)
- 이 에이전트가 커버하는 영역을 MECE로 열거
- 명시적으로 **포함하는 것**과 **제외하는 것**을 구분

```
포함:
- [항목 1]
- [항목 2]

제외 (다른 에이전트 관할):
- [항목 A] → {담당 에이전트}
- [항목 B] → {담당 에이전트}
```

### 산출물
- 주 산출물: `{path/filename.yaml}` — {설명}
- 부 산출물: `{path/filename.csv}` — {설명} (해당 시)

### 품질 기준
- 이 에이전트 산출물의 합격/불합격 기준
- 상위 에이전트가 반려하는 조건 (output-format.md 반려 조건 외 추가분)

## Why — 왜 이 분석이 필요한가

- **최종 의사결정 기여**: "이 에이전트의 산출물이 없으면 전략에서 {X}가 빠진다"
- **블라인드 스팟 방지**: "이 에이전트가 없으면 {Y} 리스크를 놓친다"
- **의존하는 에이전트**: {다른 에이전트 목록} — 이들이 이 에이전트의 산출물을 입력으로 사용

## When — 언제 동작하는가

### 활성화 조건
- Phase {N}에서 {상위 에이전트}에 의해 스폰
- 또는: {특정 조건} 충족 시 (예: "사용자가 내부 데이터 제공 시에만")

### 보고 시점
| 이벤트 | 보고 대상 | 보고 내용 |
|--------|----------|----------|
| 자율 반복 1회 완료 | {parent} | iteration_log 업데이트 |
| 전체 리서치 완료 | {parent} | 전체 출력 (4-Layer) |
| 데이터 갭 발견 | {parent} → PM | data_gaps + 대안 |
| 가설 붕괴 | {parent} → PM | 기존 Claim rejected + 사유 |
| 타 도메인 영향 발견 | cross_domain 태깅 | implications/questions |

### 에스컬레이션 조건
- **즉시 에스컬레이션** (PM까지): {조건} (예: 핵심 가설이 데이터로 반증됨)
- **Lead 보고**: {조건} (예: 데이터 소스 2개 이상 접근 불가)
- **자율 처리**: {조건} (예: 보조 가설 수정, 추가 소스 탐색)

## How — 어떻게 일하는가

### 자율 반복 프로토콜

```
Round 1:
  1. 초기 가설 수립 (도메인 지식 + Client Brief + 팩트시트 기반)
  2. 데이터 수집 (자기 도메인 소스 활용)
  3. 가설 검증 (수집 데이터 vs 가설)
  4. 판정: confirmed → 다음 가설 / revised → Round 2 / rejected → 대안 가설

Round 2 (필요 시):
  수정된 가설로 추가 데이터 수집 + 재검증

최대 반복: 3회
종료 조건:
  - 모든 핵심 Claim이 confidence: medium 이상
  - 또는 3회 반복 후에도 medium 미달 → data_gap으로 명시하고 종료
```

### 데이터 수집 전략

```
Mode A — 공개 데이터 (기본):
  1차 소스: [이 에이전트가 사용하는 구체적 소스 목록]
    예: DART API, SEC EDGAR, 앱스토어 순위, Steam DB
  2차 소스: [보조 소스]
    예: 뉴스 기사, IR 자료, 애널리스트 리포트

Mode B — 내부 데이터 보강 (사용자 제공 시):
  - Mode A 결과와 교차 검증
  - 공개 데이터로 confidence: medium이었던 항목 → high로 상향 가능
  - 공개 vs 내부 데이터 Gap 분석

데이터 없을 때:
  - [대안 접근법 구체적으로 명시]
  - 예: "정확한 시장 규모 미확보 → 상장사 매출 합산 + 비상장 추정으로 범위 제시"
```

### 정량 데이터 수집 (API 자동 호출)

Research Plan에서 API 사용이 지정된 경우, Leaf 에이전트는 다음 순서로 데이터를 수집한다:

1. `.env`에서 API 키 존재 여부 확인
2. 키가 있으면: `scripts/api-caller.py` 실행
   ```bash
   python scripts/api-caller.py --api {api} --action {action} --query "{query}" --output findings/{division}/{agent-id}-api.yaml
   ```
3. 키가 없으면: 웹 검색으로 대체 (confidence 한 단계 하향)
4. API 결과를 source_index에 `type: primary`로 등록
5. 웹 검색 결과와 API 결과를 교차 검증 (VL-1)

**지원 API 및 주요 액션:**

| API | 액션 | 용도 |
|-----|------|------|
| `dart` | `search_company`, `get_financials`, `get_disclosure_list`, `get_employees` | 한국 기업 공시/재무 |
| `steam` | `search_app`, `get_app_details`, `get_player_count`, `get_reviews` | PC 게임 데이터 |
| `fred` | `get_series`, `search_series`, `get_series_info` | 미국 매크로 경제지표 |
| `ecos` | `get_stat_data`, `search_stat` | 한국 매크로 경제지표 |

**예시 — DART 재무제표 조회:**
```bash
python scripts/api-caller.py --api {api} --action {action} --query "{검색어}" \
  --params '{"year": "2024", "fs_div": "CFS"}' \
  --output findings/finance/FRV-01-dart-financials.yaml
```

**예시 — FRED GDP 시계열:**
```bash
python scripts/api-caller.py --api fred --action get_series --query "GDP" \
  --params '{"start_date": "2020-01-01", "end_date": "2025-12-31"}' \
  --output findings/finance/FME-01-fred-gdp.yaml
```

> 상세 스펙: `domains/{domain}/data-sources.md` 참조.
> API 키 설정: `.env.example` 참조 → `cp .env.example .env` 후 키 입력.

### 팩트체크 프로토콜 (VL-1 자가 검증)

```
모든 Claim에 대해:
1. 최소 2개 독립 소스에서 확인
   - "독립" = 서로 다른 원본 데이터에 기반 (같은 원본 인용 시 1개로 카운트)
2. 소스 신뢰도 평가
   - primary (공시, 공식 발표) > secondary (뉴스, 분석) > estimate (추정치)
3. 반증 검토 (disconfirming evidence)
   - "이 Claim이 틀렸다면 어떤 증거가 있을까?"를 능동적으로 검색
   - 반증이 없으면 "없음 — [검색 방법] 결과 반증 미발견" 기재
4. 수치 불일치 시
   - 범위로 표기 (예: "$8.0-8.5B")
   - 불일치 사유 명시 (정의 차이, 시점 차이, 방법론 차이)
```

### 반증 검토 자동화 (선택적)

Leaf 에이전트의 자율 반복 루프에서 반증 작성 품질이 낮을 경우,
PM 또는 Lead가 반증 자동 검색 스크립트를 보조 도구로 실행할 수 있다:

```bash
python scripts/generate-disconfirming.py {project} --division {division} --high-impact-only
```

이 스크립트는:
1. 해당 Division의 strategic_impact: high Claim을 추출
2. 각 Claim에 대해 3~5개의 반증 검색 쿼리를 자동 생성 (부정 반전, 대안 가설, 실패 사례, 시점 반전, 조건 한정)
3. 검색 결과에서 반증 후보를 수집하고 강도(strong/moderate/weak)를 판정
4. qa/disconfirming-report.yaml에 결과 저장

스크립트 결과를 참고하여 Leaf 에이전트의 disconfirming 필드를 보강한다.
강도가 strong인 반증이 발견되면 confidence 하향 또는 Claim 수정을 검토한다.

**모드:**
- `--dry-run`: 쿼리 생성만 수행. 에이전트가 WebSearch/WebFetch로 실제 검색 (기본 권장)
- 검색 모드: requests로 직접 검색 (standalone 사용, Google API 키 필요)

### 출력 규칙
- **반드시** `core/protocols/output-format.md`의 표준 스키마 준수
- **반드시** 모든 Claim에 confidence + strategic_impact 태깅
- **반드시** disconfirming 필드 작성 (빈 값 불가 — 최소 "검토 결과 반증 미발견" 기재)
- **반드시** 엔터티 라벨 부여 (해당 시)
- **반드시** 데이터 시점 명시

### Cross-domain 태깅 규칙
```
태깅 기준:
- 다른 Division의 의사결정에 영향을 줄 수 있는 발견 → implications
- 다른 Division의 데이터가 필요한 상황 → questions
- urgency/priority:
  must = 이것 없이는 상대 Division의 결론이 위험
  should = 반영하면 상대의 Claim confidence 향상
  nice = 참고 수준
```

## Knowledge — 도메인 지식

### 전문 지식 영역
- 이 에이전트가 보유해야 할 도메인 전문 지식 서술
- 핵심 개념, 프레임워크, 업계 용어 등

### 참조 파일
- `knowledge/{domain}/{file}.md` — {설명}
- `knowledge/shared-rules.md` — 공통 규칙 (API 스펙 등)

### EP 패턴 (해당 항목)
- EP-{###}: {패턴 이름} — 이 에이전트가 특히 주의해야 할 패턴
- 예: "EP-015: 역할 혼동 (유통 vs 제작 주체)"

## Reporting — 보고 구조

### 상위 (보고)
- **대상**: {parent-agent}
- **형식**: 4-Layer 표준 출력
- **요약**: Layer 0 (Claims) + Division 레벨 합성 시 주요 tension

### 동료 (협업)
- **대상**: {sibling-agents}
- **형식**: cross_domain 태깅 (implications + questions)
- **시점**: 출력 완료 시 자동 포함

### 하위 (지시) — Lead/Sub-lead 전용
- **대상**: {child-agents}
- **스폰 방법**: Agent 도구 사용, 병렬 실행
- **지시 내용**: Client Brief 요약 + 리서치 플랜 해당 부분 + 특별 주의사항
- **수집 방법**: 하위 에이전트 출력 파일 읽기
- **검증 의무**: VL-1.5 (삼각 검증 + 핵심 Claim 스팟체크)

---

## 에이전트 유형별 필수/선택 섹션

| 섹션 | PM | Division Lead | Sub-lead | Leaf | Cross-cutting | Utility |
|------|:--:|:------------:|:--------:|:----:|:-------------:|:-------:|
| Identity | ● | ● | ● | ● | ● | ● |
| What | ● | ● | ● | ● | ● | ● |
| Why | ● | ● | ● | ● | ● | ● |
| When | ● | ● | ● | ● | ● | ● |
| How — 자율 반복 | ○ | ○ | ● | ● | ○ | ○ |
| How — 데이터 수집 | ○ | ○ | ● | ● | ○ | ○ |
| How — 팩트체크 | ○ | ● | ● | ● | ● | ● |
| How — 출력 규칙 | ● | ● | ● | ● | ● | ●※ |
| How — Cross-domain | ○ | ● | ● | ● | ● | ○ |
| Knowledge | ○ | ● | ● | ● | ● | ○ |
| Reporting — 상위 | ○ | ● | ● | ● | ● | ● |
| Reporting — 동료 | ● | ● | ● | ● | ● | ○ |
| Reporting — 하위 | ● | ● | ● | ○ | ○ | ○ |

● = 필수, ○ = 해당 시 작성
※ Utility 에이전트는 Claim/Evidence 구조 대신 output-format.md의 유틸리티 출력 규칙을 따른다
