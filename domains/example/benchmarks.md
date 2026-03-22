# 벤치마크 프레임워크 (Benchmarks)

> 피어 비교 및 산업 벤치마크 분석을 위한 템플릿.
> **선택적 활성화**: 모든 리서치에 벤치마크가 필요하진 않다.
> PM이 Research Plan에서 `benchmarks: active | inactive`로 활성화 여부를 판정한다.

## 활성화 기준

| 기준 | 활성화 | 비활성화 |
|------|--------|---------|
| Client Brief에 "경쟁사 대비", "업계 수준", "피어 그룹" 언급 | ✅ | — |
| 대상이 특정 기업/사업부 | ✅ | — |
| 시장 진입/M&A/투자 의사결정 | ✅ | — |
| 산업 전체 트렌드 조사 (특정 기업 없음) | — | ✅ |
| 기술/제품 탐색 리서치 | — | ✅ |
| 정책/규제 분석 | — | ✅ |

## 피어 그룹 정의

### Step 1: 피어 그룹 선정 기준

Research Plan 또는 Phase 0.5에서 피어 그룹을 정의한다:

```yaml
peer_group:
  primary:                          # 직접 경쟁사 (3~5개)
    selection_criteria: "동일 시장, 유사 규모, 동일 비즈니스 모델"
    companies: []                   # PM이 Client Brief 기반으로 선정
  aspirational:                     # 벤치마크 대상 (1~3개)
    selection_criteria: "업계 Best-in-class 또는 타 산업 혁신 사례"
    companies: []
  emerging:                         # 신흥 위협 (0~2개)
    selection_criteria: "빠르게 성장하는 신규 진입자"
    companies: []
```

### Step 2: 피어 선정 가이드라인

- **규모 범위**: 대상 기업 매출의 0.3x ~ 3x 범위
- **지역 범위**: Client Brief의 관심 지역 우선, 글로벌 리더 1~2개 추가
- **비즈니스 모델 유사성**: 매출 구조, 고객 유형, 가치 사슬 상 위치
- 사용자 확인: Interactive/Team 모드에서 피어 그룹을 사용자에게 제시하고 승인받는다

## 벤치마크 지표 카탈로그

### 재무 벤치마크 (Finance Division)

| 지표 | 산출식 | 단위 | 소스 |
|------|--------|------|------|
| 매출 성장률 | (당기 매출 - 전기 매출) / 전기 매출 | % | DART, SEC |
| 영업이익률 | 영업이익 / 매출 | % | DART, SEC |
| EBITDA 마진 | EBITDA / 매출 | % | DART, SEC |
| ROE | 순이익 / 자기자본 | % | DART, SEC |
| R&D 집중도 | R&D 비용 / 매출 | % | DART, SEC |
| 인당 매출 | 매출 / 임직원 수 | 백만원/$M | DART, LinkedIn |
| FCF 마진 | 잉여현금흐름 / 매출 | % | DART, SEC |

### 역량 벤치마크 (Capability Division)

| 지표 | 측정 방법 | 단위 | 소스 |
|------|----------|------|------|
| 인력 규모 | 총 임직원 수 | 명 | DART, LinkedIn |
| 기술 인력 비율 | 개발/엔지니어 / 전체 인력 | % | LinkedIn, 채용공고 |
| 특허 건수 | 최근 3년 등록 특허 | 건 | KIPRIS, USPTO |
| 글로벌 거점 수 | 해외 법인/지사 수 | 개 | IR 자료 |
| 파트너십 네트워크 | 전략적 제휴 건수 | 건 | 뉴스, IR |

### 제품/시장 벤치마크 (Product/Market Division)

| 지표 | 측정 방법 | 단위 | 소스 |
|------|----------|------|------|
| 시장 점유율 | 매출 / TAM | % | 산업 보고서 |
| 고객 만족도 | NPS 또는 리뷰 평점 | 점 | 앱스토어, 설문 |
| 제품 포트폴리오 폭 | 제품/서비스 라인 수 | 개 | IR, 웹사이트 |
| 신제품 출시 빈도 | 연간 신제품/업데이트 수 | 건/년 | 뉴스, 릴리스 노트 |

### 인사/조직 벤치마크 (People & Org Division)

| 지표 | 측정 방법 | 단위 | 소스 |
|------|----------|------|------|
| 평균 근속연수 | — | 년 | DART, Glassdoor |
| 급여 수준 | 평균 보수 | 백만원 | DART, Glassdoor |
| 이직률 | 연간 퇴사자 / 평균 인원 | % | DART, LinkedIn |
| 직원 만족도 | Glassdoor 평점 | /5.0 | Glassdoor |

## 벤치마크 출력 포맷

```yaml
benchmarks:
  peer_group: {피어 그룹 정의 참조}
  comparison_date: "YYYY 또는 YYYY-QN"

  metrics:
    - category: "financial | capability | product | people"
      metric: "지표명"
      unit: "단위"
      values:
        - entity: "대상 기업"
          value: 0
          rank: 1
          source_id: S##
        - entity: "피어 A"
          value: 0
          rank: 2
          source_id: S##
      industry_avg: 0              # 산업 평균 (가용 시)
      best_in_class: 0             # 업계 최고 수준
      gap_analysis: "대상 vs 피어 그룹 평균 대비 갭 + 시사점"
```

## 피어 비교 매트릭스 (시각화)

벤치마크 결과를 요약하는 1페이지 매트릭스:

```
               대상기업   피어A   피어B   피어C   업계평균
매출 성장률      ◕        ●       ◑       ◔       ◑
영업이익률       ●        ◕       ◕       ◑       ◑
R&D 집중도      ◕        ◑       ●       ◔       ◑
인당 매출        ◑        ◕       ◕       ●       ◑
시장 점유율      ◕        ●       ◑       ◔       —
```

- ● 상위 20% | ◕ 상위 40% | ◑ 중간 | ◔ 하위 40% | ○ 하위 20%
- 이 매트릭스는 `generate-charts.py`의 하비볼 차트로 자동 렌더링 가능

## 커스텀 가이드

산업별 도메인에서 이 파일을 복사한 후:
1. **지표 추가/교체**: 산업 특화 KPI 추가 (예: 게임 → DAU, ARPU, D30 리텐션)
2. **피어 선정 기준 세분화**: 산업 특성에 맞는 선정 기준
3. **소스 특화**: 산업별 데이터 소스 (예: 게임 → SensorTower, Steam DB)
