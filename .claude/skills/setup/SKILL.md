---
name: setup
description: 환경 설치 + 도메인 설정 인터랙티브 가이드. 새 사용자가 처음 실행하는 명령.
user_invocable: true
---

# /setup — Deep-Briefing 초기 설정

새 사용자를 위한 인터랙티브 설정 가이드.

## Express Mode (2분 완료)

사용자가 "빨리 시작하고 싶어", "Express", "바로 시작" 등을 입력하면:
1. Phase 1(환경 점검)만 실행 (필수 의존성만 확인)
2. 도메인 = example (범용 전략) 자동 선택 (Phase 2 스킵)
3. API = 전부 스킵 (웹 검색만으로 진행)
4. 바로 "/research를 시작할까요?" 제안

```
━━ Express Setup ━━
  환경 점검 → ✅ Claude Code, Python, tmux 확인
  도메인 → example (범용 전략 분석) 자동 선택
  API → 스킵 (웹 검색만으로 리서치 가능)

  준비 완료! /research interactive {project} {주제} 로 시작하세요.
  → 바로 시작할까요? [Y/n]
```

Express가 아닌 경우 기존 3단계 진행:

## Standard Mode (3단계)

환경 점검 → 도메인 생성 → API 설정 → 리서치 준비 완료.

## 실행 플로우

### Phase 1: 환경 점검

자동으로 실행한다. 사용자에게 결과만 보여준다.

```
━━ Phase 1/3: 환경 점검 ━━
```

다음 항목을 순서대로 Bash 도구로 점검한다. 각 항목에 대해 **있는지 → 없으면 어떻게 설치하는지 → 설치 후 확인**까지 완결한다.

1. **OS 확인**:
   `uname -s` 실행 → macOS(Darwin) / Linux 판별.
   이후 설치 명령을 OS에 맞게 분기한다.

2. **Homebrew (macOS만)**:
   `which brew` 실행.
   - ✅ 있음 → "Homebrew $(brew --version | head -1) 설치됨" 표시, 다음으로
   - ❌ 없음 → 사용자에게 설명:
     ```
     Homebrew는 macOS 패키지 관리자입니다. tmux 등 도구 설치에 필요합니다.

     설치 방법: 아래 명령을 실행합니다 (약 1~2분 소요)
     설치할까요? (Y/n)
     ```
     - Y: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` 실행
     - 설치 후 `which brew`로 재확인 → 성공하면 ✅, 실패하면 에러 표시 + 수동 설치 안내
     - n: "brew 없이 계속합니다. tmux를 수동으로 설치해야 합니다." 안내

3. **tmux**:
   `which tmux` 실행.
   - ✅ 있음 → "tmux $(tmux -V) 설치됨" 표시, 다음으로
   - ❌ 없음 → 사용자에게 설명:
     ```
     tmux는 터미널 멀티플렉서입니다. Division Lead를 병렬로 실행할 때 사용합니다.
     없으면 TeamCreate 모드(단일 CLI)로도 리서치 가능하지만, 성능이 제한됩니다.

     설치 방법:
       macOS: brew install tmux
       Ubuntu/Debian: sudo apt install tmux
       기타 Linux: sudo yum install tmux

     설치할까요? (Y/n)
     ```
     - Y: OS에 맞는 명령 실행 → 설치 후 `tmux -V`로 확인
     - n: "⏭️ tmux 없이 계속합니다. TeamCreate 모드로 리서치 가능합니다." 안내

4. **Python 3.8+**:
   `python3 --version` 실행.
   - ✅ 3.8 이상 → "Python {버전} 설치됨" 표시, 다음으로
   - ⚠️ 버전 낮음 → "Python {현재버전}이 설치되어 있지만 3.8 이상이 필요합니다."
   - ❌ 없음 → 사용자에게:
     ```
     Python 3.8 이상이 필요합니다 (스크립트 실행용).

     설치 방법:
       macOS: brew install python3
       Ubuntu/Debian: sudo apt install python3
       또는: https://www.python.org/downloads/ 에서 직접 다운로드

     Python은 자동 설치가 어려울 수 있어서, 직접 설치 후 /setup을 다시 실행해 주세요.
     ```
     → Python 없으면 pip 의존성 설치를 건너뛴다.

5. **pip 의존성**:
   Python이 있는 경우만 실행.
   `pip3 install -r requirements.txt` 또는 `pip install -r requirements.txt` 실행.
   - ✅ 성공 → "의존성 설치 완료 (requests, pyyaml, matplotlib, python-dotenv)" 표시
   - ❌ 실패 → 에러 메시지 표시 + "수동 설치: pip install -r requirements.txt" 안내

6. **.env 파일**:
   `.env` 파일 존재 + 내용 확인.
   - ✅ 있고, 실제 키가 1개 이상 설정됨 → "기존 .env 파일 유지 (설정된 키 N개)" 표시
   - ⚠️ 있지만 모든 키가 기본값(your_*_here) → ".env 파일이 있지만 키가 미설정입니다. Phase 2에서 설정합니다."
   - ❌ 없음 → `cp .env.example .env` 실행 → ".env 파일 생성 완료. Phase 2에서 키를 설정합니다."

   .env 파일 위치 안내: "API 키는 프로젝트 루트의 `.env` 파일에 저장됩니다. 이 파일은 .gitignore에 포함되어 git에 커밋되지 않습니다."

7. **Claude Code**:
   이미 실행 중이므로 확인만.
   - ✅ Claude Code: 실행 중

모든 결과를 요약 테이블로 출력:

```
  ✅ OS: macOS (Darwin 22.6.0)
  ✅ Homebrew: 4.2.0
  ✅ tmux: 3.4
  ✅ Python: 3.11.5
  ✅ 의존성: 설치 완료
  ✅ .env: 생성됨 (키 미설정 — Phase 2에서 설정)
  ✅ Claude Code: 실행 중
```

→ "환경 준비 완료. 도메인 설정으로 넘어갑니다."

**⚠️ 항목이 있으면**: "위 항목을 해결한 후 /setup을 다시 실행하면 빠르게 통과됩니다." 안내.
**전부 ✅이면**: 자동으로 Phase 2 진입.

---

### Phase 2: 도메인 설정 (인터랙티브)

사용자와 대화하면서 도메인을 생성한다.

```
━━ Phase 2/3: 도메인 설정 ━━
```

**도메인 선택** — 사용자에게 아래 선택지를 보여주세요:

```
도메인을 선택해주세요:

1. example (범용 전략 분석) — 산업 무관, 바로 시작 가능 (추천)
2. 직접 입력 — 분석할 산업을 입력해주세요 (예: gaming, healthcare, fintech)

산업 특화 도메인은 나중에 추가/변경할 수 있습니다.
```

- 1 또는 example 선택 시 → Step 2-A~D 전체 스킵, Step 2-E 요약만 출력 후 Phase 3 진행
- 산업명 입력 시 → 아래 Step 2-A부터 정상 진행 (입력한 산업 기반으로 도메인 생성)

#### Step 2-A: 산업/분야 파악

먼저 기존 도메인을 확인한다. `domains/` 디렉토리를 읽어 `example` 외에 도메인이 있는지 체크.

- **기존 도메인이 있으면**:
  "기존 도메인이 있습니다: {domain_list}. 새 도메인을 추가할까요, 기존 도메인을 수정할까요?"
  - 새 도메인 추가 → 아래 플로우
  - 기존 수정 → Step 2-B로 바로 이동 (기존 도메인 파일 기반)

- **기존 도메인이 없으면** (example만 존재):
  사용자에게 질문:
  "어떤 산업 또는 분야의 리서치를 주로 하실 건가요?
   예: 핀테크, 헬스케어, 이커머스, SaaS, 게임, 제조업, 미디어..."

사용자 답변을 기반으로:
1. 도메인명 제안: "'{industry}' 도메인을 생성하겠습니다. 도메인명: {industry} (변경 가능)"
2. `domains/example/` 구조를 기반으로 `domains/{industry}/` 디렉토리에 파일들을 생성한다:
   - `README.md` — example/README.md를 해당 산업에 맞게 수정
   - `frameworks.md` — 범용 + 산업 특화 프레임워크
   - `data-sources.md` — 범용 + 산업 특화 데이터 소스
   - `agents/README.md` — 에이전트 커스텀 가이드

#### Step 2-B: 프레임워크 커스터마이징

기본 제공 프레임워크를 보여주고 산업 특화 프레임워크를 추가한다:

"현재 범용 프레임워크가 포함되어 있습니다:

 Market: Porter's Five Forces, TAM/SAM/SOM
 Product: Value Proposition Canvas, JTBD
 Capability: VRIO, McKinsey 7S
 Finance: DCF, Unit Economics
 Cross-cutting: 3C, SWOT

 {industry} 산업에 특화된 프레임워크를 추가하겠습니다."

산업에 따라 추천하는 프레임워크 예시:

| 산업 | 추천 프레임워크 |
|------|----------------|
| 게임 | 게임 라이프사이클 분석, 장르-플랫폼 매트릭스, IP 가치 평가, Live-Service 메트릭스 |
| 미디어 | 콘텐츠 수명 주기, 플랫폼-크리에이터 역학, ARPU/구독 전환 모델 |
| 이커머스 | 퍼널 분석, 카테고리 매트릭스, 풀필먼트 모델 비교, GMV-Take Rate 구조 |
| 제조업 | 밸류체인 분석, 공급망 리스크 매핑, OEE(설비 종합 효율), 스마트팩토리 성숙도 |
| 핀테크 | 규제 샌드박스 분석, CAC/LTV 핀테크 특화, 결제 밸류체인, 임베디드 파이낸스 매핑 |
| 헬스케어 | 임상 파이프라인 분석, 보험 청구 프로세스, 규제 승인 경로(FDA/MFDS), 의료기기 분류 |
| SaaS | SaaS 메트릭스(MRR, NRR, Churn), PLG vs SLG 분석, 코호트 리텐션 |

위 목록에 없는 산업이면 Claude가 산업 맥락에 맞는 프레임워크 3~5개를 자체 추천한다.

사용자 확인 후 `domains/{industry}/frameworks.md`에 추가 프레임워크를 작성한다.
작성 형식은 `domains/example/frameworks.md`와 동일한 구조를 따른다:

```markdown
### {프레임워크 이름}
- **목적**: {한 줄}
- **적용 방법**: {구체적 방법}
- **출력**: {산출물}
```

#### Step 2-C: 데이터 소스 + API 설정

사용자에게 아래 선택지를 먼저 보여주세요:

```
API 키를 설정하시겠습니까?

1. 지금 설정 — 데이터 품질이 향상됩니다 (DART, FRED 등 무료 API)
2. 나중에 설정 — API 없이도 웹 검색만으로 리서치 가능합니다
3. Express 스킵 — API 전부 건너뛰고 바로 리서치 시작

추천: 처음이라면 2번으로 시작해보고, 필요할 때 /setup으로 돌아와 추가하세요.
```

- 1 선택 시 → 아래 API 추천 + 설정 플로우 진행
- 2 또는 3 선택 시 → Step 2-C 전체 스킵, Phase 3 진행

**1을 선택한 경우:**

"이 산업에서 자주 사용하는 데이터 소스와 API를 추천합니다:"

**공통 추천 (모든 산업)**:
- FRED — 미국 매크로 경제지표 (무료)
- ECOS — 한국 매크로 경제지표 (무료)
- DART — 한국 기업 공시/재무 (무료)
- Exa.ai — 고품질 웹 검색 (유료)

**산업별 추가 추천**:

| 산업 | 추천 API | 필수도 |
|------|---------|-------|
| 게임 | Steam API, IGDB, Sensor Tower, App Annie | 중간 (PC/모바일 게임 시) |
| 미디어 | YouTube Data API, Nielsen (유료), Chartmetric | 중간 |
| 이커머스 | Google Trends, Amazon Product API, Naver DataLab | 중간 |
| 제조업 | 관세청 수출입 API, KOSIS, UN Comtrade | 중간 |
| 핀테크 | 금감원 API, PSD2/Open Banking API | 높음 (한국 시) |
| 헬스케어 | ClinicalTrials.gov, FDA/MFDS API, PubMed | 높음 |
| SaaS | Crunchbase API, G2 API, BuiltWith | 중간 |

각 추천 API에 대해 **3단계 점검**을 순서대로 수행한다:

**Step 1: 이미 설정되어 있는지 확인**

`.env` 파일에서 해당 환경변수를 읽는다 (Read 도구).
- 값이 있고 `your_*_here`가 아님 → "✅ {API} — 이미 설정됨"
  - (선택) 키 유효성 테스트: `python scripts/api-caller.py --api {api} --action {test_action}` 실행
  - 성공 → "✅ 키가 정상 동작합니다" → 다음 API로
  - 실패 → "⚠️ 키가 설정되어 있지만 동작하지 않습니다. 만료되었거나 잘못된 키일 수 있습니다. 재설정할까요?"
- 값이 없거나 기본값 → Step 2로

**Step 2: 발급 방법 상세 안내**

```
━━ {API 이름} 설정 ━━

용도: {이 API가 리서치에서 하는 역할 1줄}
필수도: {높음/중간/낮음} — {필수도 이유}
비용: {무료/유료} {유료면 가격 정보}

발급 방법:
  1. {발급 사이트 URL} 접속
  2. {회원가입/로그인 방법}
  3. {키 발급 메뉴 위치}
  4. {발급된 키 형태 예시: "abc123def456..." 같은 영숫자 문자열}

발급까지 소요 시간: {즉시/1~2분/승인 필요}

키가 있으면 입력해 주세요.
아직 없으면 'n'을 입력하면 스킵합니다 (나중에 /setup으로 재설정 가능).
```

API별 상세 발급 가이드:

| API | 발급 URL | 발급 절차 | 소요 시간 |
|-----|---------|----------|----------|
| DART | https://opendart.fss.or.kr | 회원가입 → 마이페이지 → 인증키 신청 → 이메일 수신 | 즉시~수분 |
| FRED | https://fred.stlouisfed.org/docs/api/api_key.html | 가입 → Request API Key → 즉시 발급 | 즉시 |
| ECOS | https://ecos.bok.or.kr/api/ | 회원가입 → 마이페이지 → 인증키 신청 | 즉시~수분 |
| Steam | https://steamcommunity.com/dev/apikey | Steam 로그인 → 도메인 입력 → 즉시 발급 | 즉시 |
| Exa | https://exa.ai | 가입 → Dashboard → API Keys | 즉시 |
| NewsAPI | https://newsapi.org | 가입 → 즉시 발급 (무료 tier 100건/일) | 즉시 |

**Step 3: 키 입력 + 저장 + 확인**

사용자가 키를 입력하면:
1. `.env` 파일에서 해당 환경변수 줄을 찾아 값을 교체 (Edit 도구)
   - 예: `DART_API_KEY=your_dart_api_key_here` → `DART_API_KEY=실제키값`
2. `.env.example`에 해당 키가 없으면 추가 (새 API인 경우)
3. 키 동작 테스트: `python scripts/api-caller.py --api {api} --action {간단한_테스트}` 실행
   - 성공 → "✅ {API} 키 설정 + 동작 확인 완료"
   - 실패 → "⚠️ 키가 저장되었지만 테스트 호출이 실패했습니다. 키를 다시 확인해 주세요."
     - 재입력 기회 제공 또는 "일단 스킵하고 나중에 확인" 선택지

사용자가 스킵('n')하면:
- "⏭️ {API} — 스킵됨"
- "이 API 없이도 리서치 가능합니다. 웹 검색으로 대체되며, 해당 데이터의 confidence가 한 단계 낮아집니다."
- "나중에 키를 발급받으면 /setup을 다시 실행하거나, .env 파일을 직접 편집하세요."
- ".env 파일 위치: {프로젝트 루트}/.env"

#### Step 2-D: API 활용 시나리오 작성

각 활성화된 API(키가 설정된 API)에 대해, 산업에 맞는 활용 시나리오를 자동 생성한다.

"각 API를 리서치에서 어떻게 사용할지 시나리오를 작성합니다..."

시나리오 작성 규칙:
- `domains/example/data-sources.md`의 시나리오 형식을 따른다
- 각 시나리오에 포함: 대상 Division, 트리거 조건, 호출 순서, 결과 구조화
- `scripts/ADDING-API.md` Step 5 기준을 충족

생성된 시나리오를 `domains/{industry}/data-sources.md`에 저장한다.

키를 입력하지 않은 API도 data-sources.md에 스펙은 기록하되, 시나리오에 "키 미설정 — 웹 검색 대체" 표시.

#### Step 2-E: 도메인 설정 확인

최종 결과를 요약 출력:

```
도메인 설정이 완료되었습니다:

  domains/{industry}/
  ├── README.md          ✅
  ├── frameworks.md      ✅ (기본 10개 + 산업 특화 N개)
  ├── data-sources.md    ✅ (API N개 + 시나리오 N개)
  └── agents/README.md   ✅

  API 상태:
  ✅ DART — 키 설정됨
  ✅ FRED — 키 설정됨
  ⏭️ Exa — 키 미설정 (웹 검색으로 대체)

수정하고 싶은 부분이 있으면 말씀하세요.
없으면 리서치 준비 완료입니다.
```

사용자가 수정 요청하면 해당 파일을 Edit 도구로 수정.
사용자가 확인하면 Phase 3으로 진행.

---

### Phase 3: 준비 완료

```
━━ Phase 3/3: 준비 완료 ━━
```

```
Deep-Briefing 설정이 완료되었습니다!
```

참고: 각 Division 아래에는 3~5개의 전문 분석가(Leaf)가 MECE로 범위를 분담합니다.
예: Market Division → market-sizing, customer-analysis, competitive-landscape, channel-landscape, market-dynamics
이 구조는 자동으로 작동하므로 별도 설정이 필요 없습니다.

사용자에게 질문한다:

```
설정이 완료되었습니다! 리서치를 바로 시작할 수 있습니다.
주제를 말씀해 주세요 (예: '한국 SaaS 시장 진출 전략')

프로젝트명도 함께 정해주세요 (예: my-first-research)
또는 'n'을 입력하면 수동 안내로 넘어갑니다.
```

#### 사용자가 주제를 입력한 경우 (바로 리서치 시작)

1. 사용자 입력에서 주제와 프로젝트명을 파악한다
   - 프로젝트명을 별도로 말하지 않았으면: "프로젝트명을 정해주세요 (예: my-first-research)"
2. `./scripts/init-project.sh {project-name}` 자동 실행
   - Phase 2에서 People & Org / Operations / Regulatory를 활성화했으면, 해당 Division이 포함되도록 init-project.sh 실행 결과를 확인하고 필요 시 디렉토리를 보완한다
3. 실행 결과를 보여준다:
   ```
   프로젝트 초기화 완료: {project-name}/
   ```
4. 자동으로 `/research interactive {project-name} {주제}` 실행으로 전환
   → 이 시점에서 /research 스킬이 인계받아 Phase 0 Discovery 시작

#### n (수동 안내)

기존 수동 안내를 출력한다:

```
첫 리서치 시작하기:

  1. 프로젝트 초기화:
     ./scripts/init-project.sh my-first-research

  2. 리서치 시작:
     /research interactive my-first-research {리서치 주제}

예시 주제:
  - '{industry} 시장 진출 전략'
  - '{대상 기업} 경쟁력 분석'
  - '{industry} 트렌드 분석 2026'

도메인 설정을 나중에 수정하려면: /setup 다시 실행
API 추가하려면: scripts/ADDING-API.md 참조
```

---

## 재실행 시 동작

/setup을 다시 실행하면:

1. **Phase 1**: 환경 재점검 (이미 설치된 것은 ✅ 빠르게 통과)
2. **Phase 2**: "기존 도메인이 있습니다: {domain_list}. 새 도메인을 추가할까요, 기존 도메인을 수정할까요?"
   - 새 도메인 추가 → `domains/example/` 기반 동일 플로우
   - 기존 수정 → 해당 도메인의 frameworks/data-sources/API 수정 플로우
3. **Phase 3**: 업데이트된 상태 요약

---

## 기술 제약사항

- 이 스킬은 Claude Code 내에서 실행되므로, 시스템 명령은 **Bash 도구**로 실행
- 사용자에게 질문할 때는 **자연어로 대화** (CLI 프롬프트가 아님)
- API 키 입력은 **.env 파일에 Edit 도구**로 직접 반영
- 도메인 파일 생성 시 **Write 도구** 사용
- 도메인 파일 수정 시 **Edit 도구** 사용
- 프레임워크/데이터 소스 작성 시 `domains/example/` 구조를 기반으로 확장
- 주석은 한국어, 변수/함수명은 영어

## 참조

- `domains/example/` — 도메인 템플릿
- `scripts/ADDING-API.md` — API 추가 프로세스
- `scripts/quickstart.sh` — 비인터랙티브 환경 점검 (CI/CD용)
- `.env.example` — API 키 환경변수 목록
- `.claude/skills/research/SKILL.md` — /research 스킬
