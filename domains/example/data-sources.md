# 범용 데이터 소스 정의

> 산업 독립적으로 사용 가능한 데이터 소스.
> 산업 특화 API는 도메인별 data-sources.md에서 추가 정의한다.

> 새 API 추가 방법: `scripts/ADDING-API.md` 참조

## API 소스

| API | 용도 | 인증 | 환경변수 | Division |
|-----|------|------|---------|----------|
| FRED | 미국 경제지표 (GDP, CPI, 환율) | API Key (무료) | `FRED_API_KEY` | Finance, Market |
| ECOS | 한국 경제지표 (GDP, CPI, 환율) | API Key (무료) | `ECOS_API_KEY` | Finance, Market |
| DART | 한국 상장사 재무/공시 | API Key (무료) | `DART_API_KEY` | Finance, Capability |
| SEC EDGAR | 미국 상장사 재무/공시 | 불필요 (User-Agent만) | — | Finance, Capability |

## 공개 데이터 소스

| 소스 | URL | 용도 | Division |
|------|-----|------|----------|
| Google Trends | trends.google.com | 검색 트렌드 분석 | Market |
| Statista (무료 범위) | statista.com | 시장 규모/통계 | Market, Finance |
| Crunchbase (무료 범위) | crunchbase.com | 기업/투자 정보 | Capability, Finance |
| LinkedIn | linkedin.com | 인력/조직 규모 추정 | People & Org |
| Glassdoor | glassdoor.com | 기업 문화/급여 벤치마크 | People & Org |

## 엔터티 규칙

| 규칙 | 예시 |
|------|------|
| 그룹사/자회사 구분 | [그룹] A그룹, [별도] A자회사 |
| 시점 표기 | YYYY 또는 YYYY-QN |
| 통화 표기 | 원문 통화 + 환산 병기 (예: $2.3B / ₩3.1조) |
| 회계 기준 명시 | K-IFRS / US-GAAP / IFRS |

## TTL 정책 (데이터 유효기간)

| 데이터 유형 | TTL | 근거 |
|------------|-----|------|
| 재무 데이터 | 90일 | 분기 보고 주기 |
| 시장 규모 | 180일 | 연간 보고서 기반 |
| 뉴스/이벤트 | 30일 | 빠르게 변화 |
| 매크로 지표 | 30일 | 월간 발표 |
| 기업 기초 정보 | 90일 | 안정적 |

### 활용 시나리오 (API별 필수 작성)

> 각 API에 대해 "에이전트가 어떤 리서치 질문에 어떤 순서로 호출하는가"를 명시한다.
> 작성 가이드: `scripts/ADDING-API.md` Step 5 참조

#### 시나리오 1: 매크로 환경 분석
> 대상: Finance Division, Market Division
> 트리거: 시장 전망에 매크로 요인 반영 필요 시

```
호출 순서:
1. FRED get_series("GDP", 5년) → 미국 GDP 추이
2. FRED get_series("CPIAUCSL", 5년) → 인플레이션 추이
3. FRED get_series("DEXKOUS", 1년) → 환율 (해당 시)
4. ECOS get_stat_data("200Y001", 5년) → 한국 GDP (해당 시)

결과 구조화:
  - 저장: findings/{division}/{agent-id}-macro.yaml
  - golden-facts 후보: GDP 성장률, CPI, 환율
  - 차트 후보: 시계열 추이 (꺾은선)
```

#### 시나리오 2: 대상 기업 재무 분석 (한국 상장사)
> 대상: Finance Division
> 트리거: Client Brief에 한국 기업 분석 포함 시

```
호출 순서:
1. DART search_company(기업명) → corp_code
2. DART get_financials(corp_code, 최근 3년, CFS) → 연결 재무제표
3. DART get_financials(corp_code, 최근 3년, OFS) → 별도 재무제표 (자회사 분석 시)
4. DART get_employees(corp_code) → 인력 현황

결과 구조화:
  - 저장: findings/finance/{agent-id}-dart.yaml
  - golden-facts 후보: 매출, 영업이익, 인당 매출
  - 차트 후보: 3개년 재무 추이 (막대), Peer 비교 (그룹 막대)
```
