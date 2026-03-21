# 새 API 추가 가이드

> 도메인 개발 시 새로운 데이터 소스 API를 추가하는 프로세스.
> 3곳을 수정하면 완료된다.

## 체크리스트

```
☐ Step 1: data-sources.md에 API 스펙 정의
☐ Step 2: .env.example + .env에 API 키 추가
☐ Step 3: api-caller.py에 클라이언트 클래스 추가
☐ Step 4: (선택) Research Plan API 판정 테이블 업데이트
☐ Step 5: data-sources.md에 활용 시나리오 작성
```

---

## Step 1: 도메인 data-sources.md에 API 스펙 정의

`domains/{your-domain}/data-sources.md`에 새 API 섹션을 추가한다.

```markdown
## N. {API 이름} ({용도 한 줄})

- **Base URL**: `https://api.example.com/v1`
- **인증**: API Key 필요 (무료/유료). 환경변수 `{API}_API_KEY` 사용
- **발급**: https://example.com/developers
- **Rate Limit**: 100 req/min
- **사용 Division**: Market, Finance

### 주요 엔드포인트

| 용도 | 엔드포인트 | 파라미터 |
|------|-----------|---------|
| 데이터 조회 | `GET /data` | `query`, `start_date`, `end_date` |
| 검색 | `GET /search` | `keyword`, `limit` |

### 응답 예시

```yaml
{
  "data": [...],
  "meta": { "total": 100, "page": 1 }
}
```
```

**핵심**: 에이전트가 이 문서를 읽고 API를 사용하므로, 엔드포인트/파라미터/응답 구조를 명확히 작성한다.

---

## Step 2: .env.example + .env에 API 키 추가

`.env.example`:
```bash
# {API 이름} — {용도}
# 발급: https://example.com/developers
{API}_API_KEY=your_{api}_api_key_here
```

`.env`에 실제 키 설정:
```bash
{API}_API_KEY=실제_키_값
```

### 네이밍 규칙
- 환경변수: `{API}_API_KEY` (대문자, 언더스코어)
- 예: `DART_API_KEY`, `STEAM_API_KEY`, `FRED_API_KEY`

---

## Step 3: api-caller.py에 클라이언트 클래스 추가

`scripts/api-caller.py`에 새 클래스를 추가한다.

### 3-A. 클라이언트 클래스 작성

```python
# ============================================================
# {API 이름} API
# ============================================================

class {API}Client(APICallerBase):
    """{API 이름} 클라이언트 — {용도}"""

    API_NAME = "{api}"                    # 소문자, CLI --api 값
    ENV_KEY_NAME = "{API}_API_KEY"        # .env 키 이름
    REQUIRES_KEY = True                   # 키 필수 여부
    BASE_URL = "https://api.example.com"

    def action_name(self, param1: str, param2: str = None) -> dict:
        """액션 설명"""
        url = f"{self.BASE_URL}/endpoint"
        params = {
            "key": self.api_key,
            "param1": param1,
        }
        if param2:
            params["param2"] = param2

        resp = self.call_with_retry(url, params=params)
        resp.raise_for_status()
        return resp.json()
```

### 3-B. 클라이언트 레지스트리에 등록

파일 하단의 `API_CLIENTS` 딕셔너리에 추가:

```python
API_CLIENTS = {
    "dart": DARTClient,
    "steam": SteamClient,
    "fred": FREDClient,
    "ecos": ECOSClient,
    "{api}": {API}Client,        # ← 추가
}
```

### 3-C. 테스트

```bash
# 키 확인
python scripts/api-caller.py --api {api} --action action_name --query "test" --output /tmp/test.yaml

# 키 없이 실행 (SKIP 확인)
unset {API}_API_KEY
python scripts/api-caller.py --api {api} --action action_name --query "test" --output /tmp/test.yaml
# → status: skipped로 저장되어야 함
```

---

## Step 4: (선택) Research Plan API 판정 테이블 업데이트

`research-pm.md`의 Step 0-B.5 "API Readiness Check" 판정 테이블에 새 API를 추가한다:

```
│ {조건}                        │ {API}_API_KEY      │ 필수/권장/선택 │
```

이 테이블은 PM이 Research Plan 수립 시 "이번 리서치에 어떤 API가 필요한지" 판정하는 데 사용된다.

---

## Step 5: 활용 시나리오 작성 (필수)

API 스펙만으로는 에이전트가 "언제, 어떤 순서로, 어떻게" API를 사용할지 알 수 없다.
각 API에 대해 최소 1개 이상의 활용 시나리오를 `data-sources.md`에 작성한다.

### 활용 시나리오 템플릿

```markdown
### 활용 시나리오

#### 시나리오 N: {리서치 질문 한 줄}
> 대상: {어떤 Division / Leaf가 사용하는가}
> 트리거: {Client Brief에 어떤 내용이 있을 때 이 시나리오를 실행하는가}

호출 순서:
1. {action_name}({파라미터}) → {결과}
   - 주의사항 또는 조건부 분기

2. {action_name}({이전 결과 활용}) → {결과}
   - ...

결과 구조화:
  - 저장 경로: findings/{division}/{agent-id}-{api}.yaml
  - golden-facts 후보: {어떤 수치를 GF 후보로 태깅}
  - source_index: type: primary, reliability: {high/medium}
  - 차트 후보: {어떤 데이터가 차트로 변환 가능한지}
```

### 좋은 활용 시나리오의 기준

1. **리서치 질문에서 시작**: "재무 분석"이 아닌 "한국 게임사의 영업이익률 비교"처럼 구체적
2. **호출 순서가 명확**: 1→2→3 의존관계 + 조건부 분기
3. **결과 활용이 명시**: "이 데이터로 무엇을 판단하는가"
4. **에러 대응 포함**: API 실패 시 대체 경로 (웹 검색, 다른 API)
5. **엔터티 규칙 참조**: 그룹/별도 구분 등 도메인 규칙 리마인드

---

## 핵심 원칙

1. **API 키가 없어도 리서치는 진행된다** — 웹 검색으로 대체, confidence 한 단계 하향
2. **모든 API 결과는 primary 소스** — source_index에 `type: primary`로 등록
3. **TTL 정책 준수** — data-sources.md에 정의된 유효기간 내에서만 캐시 재사용
4. **에러는 에스컬레이션이 아닌 대체** — API 실패 시 웹 검색 전환, critical이 아닌 이상 계속 진행

---

## 현재 등록된 API

| API | 환경변수 | 용도 | 도메인 |
|-----|---------|------|--------|
| DART | `DART_API_KEY` | 한국 기업 공시/재무 | 범용 (한국 기업 분석 시) |
| Steam | `STEAM_API_KEY` | PC 게임 데이터 | 범용 (PC 게임 분석 시) |
| FRED | `FRED_API_KEY` | 미국 경제지표 | 범용 |
| ECOS | `ECOS_API_KEY` | 한국 경제지표 | 범용 |
