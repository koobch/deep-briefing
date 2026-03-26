# API 사용 가이드

> 에이전트가 데이터를 수집할 때 API를 언제, 어떻게 사용하는지 정의.
> Leaf 에이전트의 "데이터 수집 전략"에서 이 가이드를 참조한다.

## 원칙

- **API 우선**: 설정된 API가 있으면 웹 검색보다 먼저 사용. API가 더 정확하고 구조화됨
- API 키 미설정 시에만 웹 검색으로 대체 (confidence 한 단계 하향)
- 웹 크롤링이 막히는 사이트는 Firecrawl API로 대체

## 데이터 수집 우선순위

```
1순위: 설정된 API 호출 (가장 정확, 구조화된 데이터)
2순위: Exa 검색 (AI 최적화 웹 검색, 일반 검색보다 정확)
3순위: 일반 WebSearch (범용)
4순위: WebFetch 직접 접근 → 실패 시 Firecrawl API (크롤링 차단 사이트)
```

## 의사결정 매트릭스

| 리서치 질문 유형 | 1순위 (API) | 2순위 (웹) | API 없으면 confidence |
|-----------------|-----------|-----------|-------------------|
| 기업 재무제표 (한국) | **DART API** | dart.fss.or.kr WebFetch | medium (high 불가) |
| 기업 재무제표 (미국) | SEC EDGAR WebFetch | Exa 검색 | medium |
| 매크로 경제지표 (미국) | **FRED API** | 웹 검색 | medium |
| 매크로 경제지표 (한국) | **ECOS API** | 웹 검색 | medium |
| 시장 규모/성장률 | **Exa 검색** | 일반 WebSearch | low~medium |
| 경쟁사 웹사이트 | **Firecrawl** | WebFetch (차단 시 Firecrawl 필수) | medium |
| 기업 IR/뉴스 크롤링 | **Firecrawl** | WebFetch | medium |
| 게임 데이터 | **Steam API** | SteamDB WebFetch | medium |

## API 호출 시점

- **Leaf 부트스트랩 시**: .env에서 설정된 API 확인 → 사용 가능 API 목록 파악
- **Round 1 데이터 수집**: 설정된 API부터 호출 → API 결과 기반 분석 → 부족한 부분만 웹 검색 보충
- **Round 1.5 Null Hypothesis**: 반증 검색 시 Exa 우선 사용
- **Round 2 교차 검증**: API 결과 + 웹 검색 결과 교차 비교

## Firecrawl 사용 규칙

- WebFetch로 접근 시도 → 403/차단/불완전한 HTML → Firecrawl API로 재시도
- 가격 페이지, 경쟁사 제품 스펙, 유료 뉴스 사이트 등에 특히 유용
- 결과: 정제된 마크다운/텍스트로 반환 → Leaf가 바로 분석 가능

## API 결과 저장

- 파일: `findings/{division}/api/{api-name}-{query}.yaml`
- Layer 2 `data_files`에 경로 참조
- `source_index`에 `type: "api"`, `api_name: "{name}"` 태깅
- `data/data-registry.csv`에 행 추가 (data_id, name, type=api, source, url, reliability)

## API별 호출 방법

```bash
python scripts/api-caller.py --api {dart|fred|ecos|steam} --action {action} --query {params} --output {path}
```

- 상세 액션 목록: `python scripts/api-caller.py --api {name} --help`
- 쿼터 관리: `data/api-quota.yaml`에서 일일 사용량 자동 추적

## API 결과의 소스 분류

| API 유형 | source type | 근거 |
|---------|------------|------|
| 정부/기관 (DART, FRED, ECOS) | primary | 1차 공식 데이터 |
| 웹 검색 (Exa) | secondary | 2차 가공 검색 결과 |
| 크롤링 (Firecrawl) | secondary | 원본 소스의 신뢰도를 따름 |
| 산업 특화 (Steam) | primary | 플랫폼 공식 데이터 |
