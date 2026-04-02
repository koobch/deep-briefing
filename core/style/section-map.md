# 장표 유형별 섹션 맵 (Section Map)

> BCG Executive Perspectives 17개 PDF(322p) 전수 분석 기반
> 각 유형의 섹션 구조 + 내용 패턴 + 논리 흐름 + 디자인 속성 정의

---

## 공통 섹션 (모든 유형에 적용)

### S-HEADER (헤더 영역)
| 속성 | 값 |
|------|-----|
| 높이 | 188px |
| 배경 | 다크 그라데이션 (#004d33→#002e1f→#1a1a2e) + 사진 오버레이 |
| Action Title | `--fs-title` (:lang(ko) 42px), bold, `var(--c-white)`, 좌정렬 |
| 섹션 라벨 (선택) | `--fs-title-label` (20px), semibold, `var(--c-accent-label)` (#74e0ac), Action Title 위 |
| 하단 구분선 | 2px, `var(--c-accent)` (#29b974) |
| **콘텐츠 규칙** | 제목은 **주장형 문장** — 주제형 금지 |

### S-SOURCE (푸터 영역)
| 속성 | 값 |
|------|-----|
| Source 텍스트 | `--fs-source` (:lang(ko) 18px), `var(--c-text-muted)` (#7f7f7f), 좌정렬 |
| 페이지 번호 | `--fs-page` (:lang(ko) 22px), `var(--c-text-page)` (#898989), 우정렬 |
| 패딩 | `--sp-md` (12px) 77px `--sp-2xl` (28px) |
| **콘텐츠 규칙** | "Source: [출처] ([날짜]); [분석 주체]" 형식 |

---

## 유형 0-A: Cover (Executive Perspectives 시리즈)
> 레퍼런스: bcg-cost-p01, ai-first-win-p01, ai-engineering-p01 등

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-COVER (전폭 사진 배경)                          │
│                                                  │
│  S-LOGO (좌상단): BCG 로고                        │
│  S-SERIES (좌상단): "Executive Perspectives"      │
│                                                  │
│  S-COVER-BOX (중앙 반투명 박스):                   │
│    S-COVER-TITLE: 보고서 제목                     │
│    S-COVER-SUBTITLE: 부제                        │
│    S-COVER-DATE: 날짜                            │
│                                                  │
└─────────────────────────────────────────────────┘
```

| 섹션 | 폰트 | 색상 | 콘텐츠 규칙 |
|------|------|------|-----------|
| S-LOGO | — | — | BCG 로고 이미지 |
| S-SERIES | `--fs-source` (20px), italic | `var(--c-accent-dark)` (#187955) | "Executive Perspectives" |
| S-COVER-TITLE | 36px, bold | `var(--c-text)` (#000000) | 보고서 핵심 테마 1~2줄 |
| S-COVER-SUBTITLE | `--fs-body` (:lang(ko) 22px) | `var(--c-text)` (#000000) | 부제 설명 1~2줄 |
| S-COVER-DATE | `--fs-source` (20px) | `var(--c-accent)` (#29b974) | "January 2025" 형식 |

---

## 유형 0-B: Cover (Global Report 시리즈)
> 레퍼런스: consumer-spending-p01 등

### 섹션 구조
```
┌─────────────────────┬───────────────────────────┐
│ S-COVER-TEXT (좌50%) │ S-COVER-IMAGE (우50%)      │
│                     │ (사진)                      │
│  S-LOGO             │                            │
│  S-COVER-TITLE      │                            │
│  S-COVER-SUBTITLE   │                            │
│  S-COVER-DATE       │                            │
└─────────────────────┴───────────────────────────┘
```

| 섹션 | 폰트 | 색상 | 콘텐츠 규칙 |
|------|------|------|-----------|
| S-COVER-TITLE | 40px, light weight | `var(--c-text)` (#000000) | 2~3줄 |
| S-COVER-SUBTITLE | `--fs-body` (:lang(ko) 22px) | `var(--c-text)` (#000000) | 시리즈명 |
| S-COVER-DATE | `--fs-source` (20px) | `var(--c-accent)` (#29b974) | "DECEMBER 2025" 형식 |

---

## 유형 0-C: Exec Summary
> 레퍼런스: bcg-cost-p03, ai-engineering-p03 등

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: (Executive summary |) Action Title      │
├─────────┬───────────────────────────────────────┤
│ S-EXEC  │ S-EXEC-CONTENT                         │
│ -LABEL  │  리드 문장 1줄                           │
│ 초록배경  │  • 불릿 ×3~5 (bold 핵심구 포함)         │
│ Kicker  │  마무리 문장 1줄 (선택)                   │
│ + Topic │                                        │
├─────────┤                                        │
│ S-EXEC  │ S-EXEC-CONTENT                         │
│ -LABEL  │  리드 문장 + 불릿 ×3~5                   │
├─────────┤                                        │
│ S-EXEC  │ S-EXEC-CONTENT                         │
│ -LABEL  │  리드 문장 + 불릿 ×3~5                   │
├─────────┴───────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-EXEC-KICKER | 14px, uppercase | 중앙 | `var(--c-accent-dark)` (#187955) | 영문 키워드 (Cost, Growth 등) |
| S-EXEC-TOPIC | `--fs-body` (:lang(ko) 22px), bold | 중앙 | `var(--c-text)` (#000000) | 한글 주제 (2줄 이내) |
| S-EXEC-LEAD | `--fs-source` (20px) | 좌 | `var(--c-text-body)` (#3e3e3e) | 해당 행의 리드 문장 |
| S-EXEC-BULLET | `--fs-source` (20px) | 좌 | `var(--c-text-body)` (#3e3e3e) | 불릿 3~5개, bold 핵심구 1~2개 |
| S-EXEC-CLOSE | `--fs-source` (20px) | 좌 | `var(--c-text-body)` (#3e3e3e) | 마무리 종합 (선택) |

### 내용 패턴 (bcg-cost-p03 기준)
- **Action Title**: "Executive summary | 복잡하고 불확실한 경제 환경에서 비용 관리가 전 산업의 최우선 과제다"
- **3행 구조**: Navigating(거시환경) → Managing(비용구조) → Unlocking(지속성장)
- **밀도**: 행당 리드 1줄 + 불릿 4~5개 + 마무리 1줄 = **최소 6줄**
- **핵심 규칙**: 3행이 전체 본문 영역을 **flex:1로 균등 분할**

### 논리 흐름
1. **독자의 질문**: "이 보고서의 핵심 결론은 무엇인가?"
2. **데이터 제시**: 3행 구조 — 각 행에 리드 문장 + 불릿 3~5개
3. **해석**: 3행이 SCR 스토리라인(Situation→Complication→Resolution)에 대응
4. **Action Title 회귀**: 3행의 종합이 "Executive summary | [핵심 메시지]"와 일치

**체인 연결**: 이 유형은 보고서 전체의 축약이며, 이후 슬라이드의 로드맵 역할을 한다

### 정렬·간격 규칙
- **P4**: exec-content가 행 본문 전폭 활용
- S-EXEC-BULLET은 S-EXEC-LEAD와 동일 x좌표에서 시작. 불릿 기호(•)만 좌측으로 hanging indent
- **간격**: exec-content gap `--sp-sm`(8px), padding `--sp-md`(12px) `--sp-xl`(20px)

---

## 유형 1-A: Data-Visualization — Multi-Column (다중 컬럼 비교)
> 레퍼런스: bcg-cost-p05, p07 등
> Codex 검증: 기존 정의 FAIL → 서브타입 분리

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├─────────────────────────────────────────────────┤
│ S-SUBQ (질문)                                    │
│                                                  │
│ S-REGION-TITLE ×3 (지역/카테고리명)                │
│ S-STACKED-BAR-GROUP ×3 (각 지역 막대 세트)         │
│  - 연도별/Pre-Post 막대                           │
│  - 데이터 라벨 (바 내부)                          │
│                                                  │
│ S-REGION-INSIGHT-BOX ×3 (각 지역 해석)             │
│  • 불릿 ×3~4 (bold 핵심구)                        │
├─────────────────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-SUBQ | `--fs-subq` (:lang(ko) 28px), bold | 좌 | `var(--c-text-sub)` (#03522d) | 질문형 |
| S-REGION-TITLE | `--fs-body` (:lang(ko) 22px), bold | 중앙 | `var(--c-text)` (#000000) | 지역/카테고리명 |
| S-STACKED-BAR | — | — | `var(--c-accent)`/`var(--c-danger)` 계열 | 연도별 or Pre/Post 그룹 |
| S-BAR-VALUE | `--fs-source` (20px), bold | 바 내부 | `var(--c-white)` | % 수치 |
| S-REGION-INSIGHT-BOX | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 불릿 3~4개, bold 핵심구 |

### 내용 패턴
- **특징**: 우측 패널 **없음**. 대신 각 컬럼 하단에 인사이트 박스
- **용도**: 지역별/세그먼트별 동일 지표 비교

### 논리 흐름
1. **독자의 질문** (Sub-question): "지역/세그먼트별로 어떤 차이가 있는가?"
2. **데이터 제시**: N개 지역/카테고리 막대 차트 병렬 배치
3. **해석**: 각 컬럼 하단 인사이트 박스에서 지역별 So-What 도출
4. **Action Title 회귀**: 지역별 패턴 차이를 종합한 결론이 Action Title과 일치

**체인 연결**: 이 유형의 지역별 차이는 다음 유형의 원인 분석/질문이 된다

### 정렬·간격 규칙
- **P2**: N개 지역 컬럼 균등 배분 — grid repeat(N, 1fr)

---

## 유형 1-B: Data-Visualization — Chart + Side Panel (차트 + 우측 패널)
> 레퍼런스: bcg-cost-p08, dt-tech-hw-p06, p14 등
> 가장 빈번한 콘텐츠 유형

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├──────────────────────┬──────────────────────────┤
│ S-SUBQ               │ S-PANEL (우측 35%)         │
│                      │  ┌ S-PANEL-BODY          │
│ S-CHART (flex:1)     │  │ 문단 ×3~5              │
│  막대/라인/도넛 등    │  │ (bold 핵심구 + 설명)    │
│  + 데이터 라벨       │  │                        │
│                      │  │                        │
│ S-CALLOUT            │  └                        │
├──────────────────────┴──────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-SUBQ | `--fs-subq` (:lang(ko) 28px), bold | 좌 | `var(--c-text-sub)` (#03522d) | 질문형 |
| S-CHART | — | flex:1 | — | 차트 항목 최소 5~6개, 데이터 라벨 필수 |
| S-CHART-LABEL | `--fs-source` (20px) | 우정렬 | `var(--c-text)` (#000000) | 항목명 (2줄 이내) |
| S-CHART-VALUE | `--fs-chart-val` (28px), bold | 좌 | `var(--c-text)` (#000000) | 수치 + 단위 |
| S-CALLOUT | `--fs-callout` (:lang(ko) 22px) | 좌 | `var(--c-text)`, `var(--c-callout-bg)` 배경 | So-What 한 문장 |
| S-PANEL-BODY | `--fs-body` (:lang(ko) 22px) | 좌 | `var(--c-text)` (#000000) | 4~5문단, bold 핵심구 |
| S-LEGEND | `--fs-source` (18px) | 좌 | 검정 | 범례: 차트 막대 시작 x좌표에 좌정렬. Sub-question과 차트 사이 배치, 간격 `--sp-md`(12px) |

### 내용 패턴
- **특징**: 좌 65% + 우 35% 분할
- **용도**: 단일 데이터 세트 + 해석

### 논리 흐름
1. **독자의 질문** (Sub-question): "이 데이터가 의미하는 바는 무엇인가?"
2. **데이터 제시**: 차트(막대/라인/도넛) + 데이터 라벨
3. **해석**: Callout에서 So-What 한 문장 도출 → 패널에서 배경/원인/시사점 서술
4. **Action Title 회귀**: 차트 데이터 → Callout So-What → 패널 맥락을 종합한 결론이 Action Title과 일치

**체인 연결**: 이 유형의 So-What은 다음 유형의 배경/질문이 된다

---

## 유형 1-C: Data-Visualization — Dual Chart (이중 차트)
> 레퍼런스: bcg-cost-p10 등
> 빈도: ~3%

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├────────────────────┬────────────────────────────┤
│ S-SUBQ (공통 질문)  │                            │
│                    │                            │
│ S-CHART-A (좌 50%) │ S-CHART-B (우 50%)          │
│  차트 제목 (bold)   │  차트 제목 (bold)           │
│  차트 (바/파이/라인)│  차트 (바/파이/라인)        │
│  데이터 라벨       │  데이터 라벨               │
│                    │                            │
│ S-LEGEND (공통 범례)│                            │
│                    │                            │
│ S-CALLOUT (공통 시사점)                           │
├────────────────────┴────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-SUBQ | `--fs-subq` (한글 28px) | 좌 | `var(--c-text-sub)` | 두 차트가 공통으로 답하는 질문 |
| S-CHART-TITLE | `--fs-body-lg` (한글 22px), bold | 좌 | 검정 | 각 차트의 측정 지표 |
| S-CHART | — | flex:1 | — | 차트 항목 최소 5~6개 |
| S-CHART-VALUE | `--fs-chart-val` (28px), bold | — | 검정 | 수치 + 단위 |
| S-LEGEND | `--fs-source` (18px) | 중앙 | 검정 | 공통 범례 (2색 이내) |
| S-CALLOUT | `--fs-callout` (한글 22px) | 좌 | 검정, `var(--c-callout-bg)` | 두 차트의 교차 인사이트 |

### 내용 패턴
- **Action Title**: "두 차트의 교차 인사이트" (예: "채택률이 높은 기능에서 생산성 효과도 크다")
- **핵심 규칙**: 두 차트는 같은 데이터의 다른 절단면이어야 함. 독립적 차트 2개 병렬 **금지**
- **우측 패널 없음**: 두 차트가 서로를 보완하므로 별도 해석 패널 불필요

### 논리 흐름
1. **독자의 질문** (Sub-question): "이 두 측면은 어떤 관계인가?"
2. **데이터 제시**: 차트A(측면1) + 차트B(측면2) — 같은 데이터의 다른 절단면
3. **해석**: 공통 범례로 연결 → Callout에서 교차 인사이트 도출
4. **Action Title 회귀**: 두 절단면의 교차점이 Action Title의 주장과 일치

**체인 연결**: 이 유형의 교차 인사이트는 다음 유형의 배경/가설이 된다

---

## 유형 2-A: Ranked — Row-Based Leaderboard (행 반복 순위)
> 레퍼런스: bcg-cost-p11 등
> Codex 검증: 기존 정의 FAIL → 수평 row 반복 + 우측 callout 기반으로 재정의

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├──────────────────────────────┬──────────────────┤
│ S-SUBQ                       │ S-SIDEBAR-CALLOUT│
│                              │ (우측 단일 문단)  │
│ S-RANK-ROW #1                │                  │
│  순위번호 + 아이콘 + 제목     │ 종합 해석 텍스트  │
│  + 설명 1~2줄                │ (bold 핵심구)     │
│ ─────────────────────────    │                  │
│ S-RANK-ROW #2                │                  │
│  순위번호 + 아이콘 + 제목     │                  │
│  + 설명 1~2줄                │                  │
│ ─────────────────────────    │                  │
│ S-RANK-ROW #3                │                  │
│  순위번호 + 아이콘 + 제목     │                  │
│  + 설명 1~2줄                │                  │
├──────────────────────────────┴──────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-SUBQ | `--fs-subq` (:lang(ko) 28px), bold | 좌 | `var(--c-text-sub)` (#03522d) | 질문형 |
| S-RANK-NUM | `--fs-title` (48px), bold | 좌 | `var(--c-text)` (#000000) | #1, #2, #3 |
| S-RANK-ICON | 40×40px | 좌 | `var(--c-accent)` (#29b974) | 아이콘 (행 내 좌측) |
| S-RANK-TITLE | `--fs-body` (:lang(ko) 22px), bold | 좌 | `var(--c-text)` (#000000) | 항목명 |
| S-RANK-DESC | `--fs-source` (20px) | 좌 | `var(--c-text-body)` (#3e3e3e) | 설명 1~2줄 (bold 수치 포함) |
| S-RANK-SEPARATOR | 1px | — | `var(--c-border)` (#b1b2b1) | 행 구분선 |
| S-SIDEBAR-CALLOUT | `--fs-body` (:lang(ko) 22px) | 좌 | `var(--c-text)` (#000000) | 종합 해석 단일 문단, bold 핵심구 |

### 내용 패턴 (bcg-cost-p11 기준)
- **Action Title**: "비용 관리가 지역과 산업을 불문하고 임원들의 최우선 전략 과제로 유지되고 있다"
- **핵심 규칙**: 각 행은 독립적으로 읽을 수 있어야 함. 행간 구분선 필수

### 논리 흐름
1. **독자의 질문** (Sub-question): "가장 중요한 항목은 무엇인가?"
2. **데이터 제시**: #1/#2/#3 행 반복 (각 행에 아이콘+제목+설명 1~2줄)
3. **해석**: 우측 Sidebar-Callout에서 순위 종합 해석
4. **Action Title 회귀**: 순위 패턴을 종합한 결론이 Action Title과 일치

**체인 연결**: 이 유형의 우선순위 결론은 다음 유형의 실행 과제/질문이 된다

---

## 유형 2-B: Ranked — Icon Grid (아이콘 그리드 순위)
> 레퍼런스: bcg-cost-p12 등
> 수평 아이콘 나열 + 하단 산업별 그리드

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├──────────────────────┬──────────────────────────┤
│ S-SUBQ               │ S-PANEL (우측 32%)         │
│                      │  S-PANEL-BODY (3~4문단)   │
│ S-RANK-BAR (배경바)   │                           │
│                      │                           │
│ S-RANK-ICONS (5열)   │                           │
│  #1~#5 아이콘+라벨    │                           │
│  + 각 아이콘 아래 설명│                           │
│                      │                           │
│ S-RANK-DETAIL (하단)  │  S-CALLOUT (선택)         │
│  산업별 그리드        │                           │
├──────────────────────┴──────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-RANK-BAR | `--fs-body` (:lang(ko) 22px), bold | 좌 | `var(--c-text)`, `var(--c-callout-bg)` 배경 | 카테고리 제목 |
| S-RANK-NUM | `--fs-title` (48px), bold | 중앙 | `var(--c-text)` (#000000) | #1~#5 |
| S-RANK-ICON | 72×72px | 중앙 | `var(--c-accent)`→`var(--c-text-muted)` | 아이콘 |
| S-RANK-LABEL | `--fs-source` (20px) | 중앙 | `var(--c-text)` (#000000) | 항목명 (2~3줄) |
| S-RANK-DESC | `--fs-source` (20px) | 중앙 | `var(--c-text-muted)` (#7f7f7f) | 1줄 설명 |
| S-RANK-DETAIL | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 산업별 그리드 (5컬럼) |
| S-PANEL-BODY | `--fs-body` (:lang(ko) 22px) | 좌 | `var(--c-text)` (#000000) | 3~4문단 |

### 내용 패턴
- **특징**: 수평 아이콘 나열 + 하단 산업별 그리드 + 우측 패널
- **용도**: 5개 항목의 시각적 순위 + 산업별 세부 분류

### 논리 흐름
1. **독자의 질문** (Sub-question): "주요 항목의 순위와 산업별 차이는?"
2. **데이터 제시**: #1~#5 아이콘 그리드 + 산업별 세부 그리드
3. **해석**: 패널에서 순위의 배경/맥락/시사점 서술
4. **Action Title 회귀**: 아이콘 순위 + 산업별 패턴을 종합한 결론이 Action Title과 일치

**체인 연결**: 이 유형의 순위 인사이트는 다음 유형의 심화 분석 배경이 된다

### 정렬·간격 규칙
- **P2**: #1~#5 아이콘 균등 배분 — ranked-icons grid repeat(5, 1fr)
- **P6**: ranked-bar(연두 배경)는 ranked-content 전폭으로 확장. negative margin 또는 container padding 0 방식
- **P3**: S-RANK-ICONS의 5열과 S-RANK-DETAIL의 5열은 동일 `grid-template-columns: repeat(5, 1fr)` + 동일 gap 토큰
- **간격**: rank-item gap `--sp-sm`(8px)

---

## 유형 3: Big Number + 차트 복합
> 레퍼런스: bcg-cost-p15, p06, p09 등
> 빈도: ~6%

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├─────────┬───────────────────────────────────────┤
│ S-BIG   │ S-SUBQ (우측)                          │
│  48%    │  질문형 소제목                          │
│  라벨   │                                        │
│         │ S-CHART (3D 실린더/도넛 등)              │
│ S-BIG   │  4개 항목 + 데이터 라벨                 │
│  50%    │                                        │
│  라벨   │ S-CALLOUT                               │
│         │  시사점 요약 (bold + 일반)               │
│ S-BODY  │                                        │
│  해석   │                                        │
├─────────┴───────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-BIG-NUM | `--fs-rank` (56px), bold | 좌/중앙 | `var(--c-accent-dark)` (#187955) 또는 `var(--c-danger)` (#c0392b) | 핵심 수치 1개 (%, $, pp) |
| S-BIG-LABEL | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 수치 설명 1~2줄 |
| S-BIG-DESC | `--fs-source` (20px) | 좌 | `var(--c-text-body)` (#3e3e3e) | 추가 해석 1~2문장 |
| S-SUBQ | `--fs-subq` (:lang(ko) 28px), bold | 좌 | `var(--c-text-sub)` (#03522d) | 질문형 |
| S-CHART | — | flex:1 | — | 3D 실린더, 도넛, 또는 막대 |
| S-CALLOUT | `--fs-callout` (:lang(ko) 22px) | 좌 | `var(--c-text)`, `var(--c-callout-bg)` 배경 | 시사점 한 문장 |

### 내용 패턴 (bcg-cost-p15 기준)
- **Action Title**: "기업들은 비용 절감 목표 달성에 어려움을 겪고 있다"
- **좌측 Big Numbers**: 48%(비용 절감 목표 달성률) + 50%(구조적 비용 절감 실패 비율)
- **우측**: 질문 → 4개 장벽 차트(조직 문화 69%, 경영 구조 58% 등) → Callout
### 논리 흐름
1. **독자의 질문** (Sub-question): "핵심 지표가 어떤 수준인가?"
2. **데이터 제시**: 좌측 Big Number(핵심 수치) + 우측 차트(세부 근거)
3. **해석**: Callout에서 수치의 So-What 도출
4. **Action Title 회귀**: 핵심 수치 → 세부 데이터 → 시사점을 종합한 결론이 Action Title과 일치

**체인 연결**: 이 유형의 핵심 수치는 다음 유형의 문제 정의/배경이 된다

### CSS 클래스 매핑
| 섹션 | HTML 클래스 | 비고 |
|------|-----------|------|
| 좌측 KPI 패널 | `.kpi-panel` | flex column, 중앙 정렬, 배경 #f1f2f1 |
| 핵심 수치 | `.kpi-number` | font-size: --fs-big, weight 800 |
| 우측 상세 | `.bignumber-detail` | padding, flex column |
| KPI 목록 | `.bignumber-kpi-list` | flex column, gap --sp-xs |
| 하단 2분할 | `.spread-2` | grid 1fr 1fr |

**주의**: `.metric-value`, `.metric-label`은 `.case-metrics` 하위에서만 작동 — Big Number에서는 `.kpi-number` 사용

### 차트 바 작성 규칙
- `chart-bar-row` 내 바 `<div>`에 `chart-bar` 클래스 불요 — CSS가 자동으로 `height: var(--bar-h)` 적용
- `chart-dual-bar` 내 바 `<div>`도 동일 — 자동 높이 적용
- **바에 필요한 인라인**: `background:var(--c-*);width:N%` 만 지정

---

## 유형 4: Before/After (Current → 전환 → Impact)
> 레퍼런스: ai-first-pu-p08, ai-first-win-p14 등
> 빈도: ~4%

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├─────────┬──────────────────┬────────────────────┤
│ S-COL-T │ S-COL-TITLE      │ S-COL-TITLE        │
│ Current │ AI-first 전환     │ Impact             │
│         │                  │                    │
│ S-COL-S │ S-SOLUTION ×4~5  │ S-BIG-NUM ×3       │
│ 부제    │  제목+설명(2줄)    │  수치+라벨+설명     │
│         │                  │                    │
│ S-ITEM  │                  │                    │
│ ×6~8개  │                  │ S-FOOTER-TEXT      │
│ 아이콘  │                  │  종합 설명          │
│ +텍스트 │                  │                    │
├─────────┴──────────────────┴────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-COL-TITLE | `--fs-subq` (:lang(ko) 28px), bold | 좌 | `var(--c-text)`/`var(--c-accent)` | 컬럼 헤더 — 3컬럼 동일 y좌표 |
| S-COL-SUBTITLE | `--fs-source` (20px), semibold | 좌 | `var(--c-danger)`(현황)/`var(--c-accent)`(전환) | 한줄 요약 |
| S-ITEM | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 아이콘(28px) + bold 핵심어 + 설명 |
| S-SOLUTION-TITLE | `--fs-source` (20px), bold | 좌 | `var(--c-accent-dark)` (#187955) | 해결책 제목 |
| S-SOLUTION-DESC | `--fs-source` (20px) | 좌 | `var(--c-text-body)` (#3e3e3e) | 해결책 설명 1~2줄 |
| S-BIG-NUM | `--fs-rank` (56px), bold | 좌 | `var(--c-accent-dark)` (#187955) | 8~15%, 15~25%, +40% |
| S-BIG-LABEL | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 수치 라벨 |
| S-BIG-DESC | `--fs-source` (20px) | 좌 | `var(--c-text-body)` (#3e3e3e) | 수치 설명 1줄 |

### 내용 패턴 (ai-first-pu-p08 기준)
- **Action Title**: "AI-first P&U 기업은 자본 우수성을 경쟁 우위로 재구상한다"
- **Current**: 문제점 5~6개 (구체적 수치 포함: "3건 중 2건 지연", "6배 비용")
- **AI-first**: 해결책 4~5개 (bold 제목 + 설명 2줄)
- **Impact**: Big Number 3개 + 하단 종합 설명
- **핵심 규칙**: 3컬럼 헤더는 반드시 **같은 수직 위치**에 정렬

### 논리 흐름
1. **독자의 질문** (Sub-question): "현재 문제를 어떻게 해결하고 어떤 효과가 있는가?"
2. **데이터 제시**: Current(문제점 5~6개) → AI-first(해결책 4~5개) → Impact(Big Number 3개)
3. **해석**: 좌→중→우 흐름 자체가 논리 전개 (As-Is → To-Be → 효과)
4. **Action Title 회귀**: 전환의 정량 효과가 Action Title의 주장과 일치

**체인 연결**: 이 유형의 Impact 수치는 다음 유형의 근거/배경이 된다

### 정렬·간격 규칙
- **P1**: 3컬럼 제목(Current/전환/Impact) 동일 y좌표 — subgrid 필수
- **P1 subgrid**: 3컬럼의 ba-title이 동일 grid-row에 배치. 중앙 컬럼의 accent bar는 `position: absolute`로 처리하여 row를 밀지 않음
- **P5**: 중앙 컬럼 배경색(`--c-panel-bg`)으로 경계 구분
- **Impact 배분**: Impact 컬럼 ba-body에 `justify-content: space-evenly` (space-between 아닌)
- **간격**: ba-column gap `--sp-sm`(8px), ba-body gap `--sp-md`(12px)

---

## 유형 5: Table/List (행 나열)
> 레퍼런스: ai-engineering-p05, bcg-cost-p13 등
> 빈도: ~9%

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: (라벨 |) Action Title                   │
├─────────┬───────────────────────────────────────┤
│ S-ROW-1 │                                        │
│ [a] 제목 │ bold 핵심문장 + 상세 설명 1~2줄          │
├─────────┼───────────────────────────────────────┤
│ [b] 제목 │ bold 핵심문장 + 상세 설명 1~2줄          │
├─────────┼───────────────────────────────────────┤
│ [c] 제목 │ bold 핵심문장 + 상세 설명 1~2줄          │
├─────────┼───────────────────────────────────────┤
│ ...     │ (4~6행)                                 │
├─────────┴───────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-ROW-MARKER | `--fs-subq` (:lang(ko) 28px), bold | 중앙 | `var(--c-white)` | a, b, c, d, e, f |
| S-ROW-TITLE | `--fs-body` (:lang(ko) 22px), bold | 좌 | `var(--c-white)` | 행 제목 (1~2줄) |
| S-ROW-BODY-LEAD | `--fs-source` (20px), bold | 좌 | `var(--c-text)` (#000000) | 핵심 문장 (첫 문장) |
| S-ROW-BODY-DETAIL | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 상세 설명 (1~2문장 추가) |
| 라벨 배경 | — | — | `var(--c-accent)` (#29b974) | 좌측 200px |

### 내용 패턴 (ai-engineering-p05 기준)
- **Action Title**: "과제 | AI 가치 실현을 가로막는 6가지 핵심 과제를 극복해야 한다"
- **각 행 구성**: [마커 a] + [제목: "삽질의 역설"] | [본문: **bold 핵심** + 상세 1~2줄]
- **콘텐츠 밀도 규칙**: 각 행에 **반드시 2줄 이상** (bold 핵심문 + 상세 설명)

### 논리 흐름
1. **독자의 질문** (Sub-question): "해결해야 할 핵심 과제는 무엇인가?"
2. **데이터 제시**: a→f 행 나열 (각 행: bold 핵심문장 + 상세 설명)
3. **해석**: 각 행 자체가 [현상 + 원인 + 필요 행동] 구조로 해석 내포
4. **Action Title 회귀**: 과제 전체를 관통하는 핵심 메시지가 Action Title과 일치

**체인 연결**: 이 유형의 과제 목록은 다음 유형의 해결책/프로세스 배경이 된다

### 정렬·간격 규칙
- **P4**: table-row-content가 행 본문 전폭 활용
- **간격**: table-row-content padding `--sp-md`(12px) `--sp-xl`(20px)

---

## 유형 6: Case Study (사례)
> 레퍼런스: genai-marketing-p12, ai-first-pu-p11 등
> 빈도: ~10%

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: (사례 |) Action Title                   │
│ S-CASE-TAG: "예시: BCG 컨설팅 프로젝트 사례"       │
├──────┬──────────────────────────────────────────┤
│ ICON │ S-CASE-SECTION: Impact                    │
│ 🎯   │  Big Number ×2~3 + 설명 + 종합 텍스트      │
├──────┼──────────────────────────────────────────┤
│ ICON │ S-CASE-SECTION: Platform/Method           │
│ ⚙️   │  플로우 박스 ×3 (→ 연결) + 각 설명          │
├──────┼──────────────────────────────────────────┤
│ ICON │ S-CASE-SECTION: Operating Model           │
│ 🏢   │  불릿 텍스트 ×3~4 (bold 핵심 + 상세)       │
├──────┴──────────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-CASE-TAG | `--fs-source` (:lang(ko) 18px), italic | 좌 | `var(--c-text-muted)` (#7f7f7f) | "예시: ..." 또는 "Illustrative ..." |
| S-CASE-ICON | `--fs-subq` (:lang(ko) 28px) | 중앙 | — | 이모지 또는 아이콘 |
| S-CASE-LABEL | `--fs-body` (:lang(ko) 22px), bold | 좌 | `var(--c-text)` (#000000) | 섹션명 (Impact/플랫폼/운영모델) |
| S-CASE-BIG | `--fs-rank` (56px), bold | 좌 | `var(--c-accent-dark)` (#187955) | 핵심 수치 |
| S-CASE-BIG-DESC | `--fs-source` (20px) | 좌 | `var(--c-text-body)` (#3e3e3e) | 수치 설명 |
| S-CASE-FLOW | `--fs-source` (20px), bold | 중앙 | `var(--c-white)`, `var(--c-accent)` 배경 | 플로우 박스 |
| S-CASE-FLOW-DESC | `--fs-source` (20px) | 좌 | `var(--c-text-muted)` (#7f7f7f) | 각 플로우 단계 설명 |
| S-CASE-BODY | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | bold 핵심 + 상세, 최소 3줄 |

### 내용 패턴 (genai-marketing-p12 기준)
- **Action Title**: "사례 | AI와 역량 구축을 결합하여 대규모 미디어 실행 효율화를 달성한 뷰티 기업"
- **3행 구조**: Impact(수치 성과) → Platform(기술 구성) → Operating Model(운영 방식)
### 논리 흐름
1. **독자의 질문** (Sub-question): "실제 사례에서 어떤 성과를 달성했는가?"
2. **데이터 제시**: Impact(Big Number 2~3개) → Platform/Method(플로우 박스) → Operating Model(불릿)
3. **해석**: 결과(What) → 방법(How) → 실행 체계(Who/Where) 순서로 설득력 확보
4. **Action Title 회귀**: 사례의 성과와 방법이 Action Title의 주장과 일치

**체인 연결**: 이 유형의 사례 성과는 다음 유형의 벤치마크/근거가 된다

### 정렬·간격 규칙
- **P2**: Impact Big Number 3개 균등 배분 — `.case-metrics` grid repeat(3, 1fr)
- **P3**: 플로우 박스와 아래 설명 수직 정렬 — 같은 grid column
- **P6**: 인접 행 콘텐츠 좌우 엣지 정렬 — case-row-body padding 0 + 내부 요소 `--sp-xl` padding
- **P6 확장**: 인접 행의 grid 열 수가 다를 때(예: Impact 3열 vs Platform 4열), 전체 좌우 끝(첫 열 좌측, 마지막 열 우측)은 반드시 동일 x좌표. 내부 열 경계 일치는 요구하지 않음
- **구현**: 모든 case-row-body 내부 콘텐츠 블록(case-metrics, case-flow-grid, `<p>`)에 동일한 좌우 padding `--sp-xl`(20px) 적용
- **간격**: case-row-body gap `--sp-sm`(8px), case-metrics gap `--sp-lg`(16px)

---

## 유형 7: Framework / Diagram
> 레퍼런스: ai-cost-advantage-p06, genai-hr-p05, bcg-cost-p18 등
> 빈도: ~19% (2번째로 빈번)

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├─────────────────────────────────────────────────┤
│ S-DIAGRAM (전폭 또는 좌 65%)                      │
│  벤 다이어그램 / 원형 / 매트릭스 / 레이어 등       │
│  - 번호 라벨 (①②③④)                             │
│  - 내부 텍스트 (항목명)                           │
│                                                  │
│ S-LEGEND (하단)                                   │
│  번호별 1줄 설명 그리드                            │
├─────────────────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-DIAGRAM | — | flex:1 | — | 도식이 본문 영역의 60%+ 차지 |
| S-DIAGRAM-LABEL | `--fs-body` (:lang(ko) 22px), bold | 중앙 | `var(--c-white)`/`var(--c-accent)` | 영역명 |
| S-DIAGRAM-ITEM | `--fs-source` (:lang(ko) 18px) | 중앙 | `var(--c-text)`/`var(--c-text-muted)` | 세부 항목명 |
| S-LEGEND-NUM | `--fs-subq` (:lang(ko) 28px), bold | 좌 | `var(--c-accent)` (#29b974) | ①②③④ |
| S-LEGEND-DESC | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 번호별 설명 1줄 |

### 내용 패턴
- **특징**: 도식이 본문 영역의 60%+ 차지
- **용도**: 개념 구조, 분류 체계, 생태계 설명

### 논리 흐름
1. **독자의 질문** (Sub-question): "이 구조/체계는 어떻게 구성되는가?"
2. **데이터 제시**: 도식(벤 다이어그램/매트릭스/트리 등) + 번호 라벨
3. **해석**: 하단 범례에서 번호별 1줄 설명으로 구조의 의미 전달
4. **Action Title 회귀**: 프레임워크의 핵심 구조가 Action Title의 주장과 일치

**체인 연결**: 이 유형의 프레임워크는 다음 유형의 분석 틀/기준이 된다

---

## 유형 8: Process / Flow
> 레퍼런스: bcg-cost-p14, ai-first-telco-p12 등
> 빈도: ~5%

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├──────────┬──────────────────────────────────────┤
│ S-LEFT   │ S-PROCESS-PANEL (우측 70%)             │
│ (30%)    │  S-PROCESS-TITLE (방법론 제목)          │
│          │  S-PROCESS-DESC (설명)                  │
│ 제목     │                                        │
│ 설명     │  S-LEVER #1 + 설명                     │
│ 불릿×5   │  S-LEVER #2 + 설명                     │
│          │                                        │
│ KPI박스  │  S-CHEVRON (3~5단계)                    │
│          │   각 단계 + 하위 불릿 ×3                │
├──────────┴──────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-LEFT-TITLE | `--fs-subq` (:lang(ko) 28px), bold | 좌 | `var(--c-text)` (#000000) | 문제/맥락 제목 |
| S-LEFT-DESC | `--fs-source` (20px) | 좌 | `var(--c-text-body)` (#3e3e3e) | 문제 설명 1~2문장 |
| S-LEFT-BULLET | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 불릿 5개 |
| S-LEFT-KPI | `--fs-kpi-inline` (36px), bold | 좌 | `var(--c-accent-dark)` (#187955) | 인라인 KPI 수치 |
| S-PROCESS-TITLE | `--fs-body` (:lang(ko) 22px), bold | 좌 | `var(--c-text)` (#000000) | 방법론 제목 |
| S-LEVER-NUM | `--fs-subq` (:lang(ko) 28px), bold | 좌 | `var(--c-text)` (#000000) | #1, #2 |
| S-LEVER-DESC | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 레버 설명 1~2줄 |
| S-CHEVRON | `--fs-source` (20px), bold | 중앙 | `var(--c-white)`, `var(--c-accent-dark)` 배경 | 단계명 |
| S-CHEVRON-DETAIL | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 하위 불릿 ×3 |

### 내용 패턴
- **특징**: 좌 30% 문제 정의 + 우 70% 해결 프로세스
- **용도**: 문제 → 해결 방법론 → 실행 단계

### 논리 흐름
1. **독자의 질문** (Sub-question): "이 문제를 어떤 프로세스로 해결하는가?"
2. **데이터 제시**: 좌측(문제 정의 + 불릿 + KPI) → 우측(방법론 + 레버 + 쉐브론 스텝)
3. **해석**: 쉐브론 각 단계의 하위 불릿이 실행 방법을 구체화
4. **Action Title 회귀**: 프로세스를 통한 목표 달성이 Action Title의 주장과 일치

**체인 연결**: 이 유형의 프로세스 결과는 다음 유형의 성과 측정/배경이 된다

### 정렬·간격 규칙
- **P6**: 쉐브론 3~5단계는 process-panel 내부의 좌우 padding 경계와 일치하도록 전폭 확장
- **P3**: 쉐브론 하단 detail 불릿의 좌측 시작점은 쉐브론 내부 텍스트 시작 x좌표와 동일
- **간격**: process-steps gap `--sp-xs`(4px), process-detail padding `--sp-md`(12px) `--sp-sm`(8px)
- **KPI 박스**: 좌측 하단 KPI 배경 박스는 좌측 영역 전폭 확장 (P6 적용)

---

## 콘텐츠 밀도 기준 (전 유형 공통)

| 영역 | 최소 요구량 |
|------|-----------|
| 본문 텍스트 | 모든 문장은 `--fs-source` (20px) 이상. 각 섹션에 최소 2줄 |
| 우측 패널 | 최소 4~5문단 (문단당 bold 1~2개) |
| 차트 | 항목 최소 5~6개, 데이터 라벨 필수 |
| Table 행 | bold 핵심문 + 상세 설명 (최소 2줄) |
| Big Number | 수치 + 라벨 + 설명 1줄 |

> 콘텐츠가 부족하면 **리서치를 보강**한다. 폰트 축소/여백 확대 금지.

### 유형별 상세 밀도 (1920×1080 기준)

| 유형 | 차트/데이터 항목 | 텍스트 영역 | 보조 요소 |
|------|-------------|---------|---------|
| Exec Summary | 행당 리드 1줄 + 불릿 4~5개 | 3행 균등 분할 | 마무리 문장 |
| Insight+Chart | 차트 5~6행 | 패널 4~5문단 | callout 1개 |
| Ranked | 아이콘 5개 | 패널 4문단 | 하단 산업별 그리드 |
| Big Number | KPI 2~3개 | 차트 4~5행 | spread-2 하단 |
| Process | 좌 불릿 5개 | 우 레버 2~3개 | 쉐브론 3단계 |
| Before/After | 3컬럼 × 4행 | Impact Big Number 3개 | 각 행 2줄+ |
| Table/List | 행 5개 | 각 행 bold + 상세 | 아이콘 |
| Case Study | Impact 3개 | 플랫폼 3개 | 운영모델 3개 |
| Multi-Column | 컬럼당 바 4~5개 | 불릿 3~4개 | 지역 헤더 |
| Dual Chart | 차트당 바 5~6개 | 범례 + callout | 차트 제목 |
| Divergent | 행 7~8개 | callout 1개 | 헤더 라벨 |
| Split Layout | 좌 불릿 5개+ | 우 바 4~5개 | 좌 callout |
| Heatmap | 행 6개 × 열 6개 | 범례 4개 | 축 라벨 |
| Scatter | 점 8~9개 | 축 라벨 | 기준선 + 범례 |
| Comparison | 좌우 각 5~6불릿 | 섹션 제목 | 헤더 대비 |
| Matrix | 4셀 내용 각 3줄 | 축 라벨 | 헤더 |
| Framework | 링 4라벨 | 범례 4항목 | 중심 텍스트 |
| Introduction | 좌 문단 4개 + 불릿 3~4개 | 우 사이드바 5항목 | — |

> **공간 채우기 원칙**: 콘텐츠가 slot-body 수직 공간의 80% 이상을 차지해야 한다. 연속 빈 공간 80px 이상 금지 — 빈 공간 발견 시 annotation, callout, 보조 통계 추가.

---

---

## 유형 9: Divergent Bar (좌우 대칭 막대)
> 레퍼런스: consumer-spending-p03 등
> 특징: 긍정/부정, 찬성/반대 등 양방향 비교에 사용

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├─────────────────────────────────────────────────┤
│ S-SUBQ (질문)                                    │
│                                                  │
│ S-CHART-HEADER (컬럼 라벨: 긍정 | 부정)           │
│                                                  │
│ S-DIVERGENT-ROW ×8~10                            │
│  국가명 | ◄ 긍정 바 | 부정 바 ► | 변화량          │
│                                                  │
│ S-ANNOTATION (선택: 우측 해석 텍스트. Callout 대체 가능) │
├─────────────────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-DIVERGENT-LABEL | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 국가/항목명 |
| S-DIVERGENT-BAR | — | — | `var(--c-accent)`(긍정)/`var(--c-danger)`(부정) | 비율에 비례 |
| S-DIVERGENT-VALUE | `--fs-source` (20px), bold | 중앙(바 내부) | `var(--c-white)` | % 수치 |
| S-DIVERGENT-DELTA | `--fs-source` (20px) | 우 | `var(--c-danger)`/`var(--c-accent)` | 변화량 (+/−) |
| S-ANNOTATION | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | (선택) 우측 해석 텍스트 2블록. S-CALLOUT이 있으면 생략 가능 |

### 내용 패턴
- **용도**: 설문 결과 양극화, 시장별 온도차, Before/After 수치 비교

### 논리 흐름
1. **독자의 질문** (Sub-question): "항목별 긍정/부정 분포와 양극화 패턴은?"
2. **데이터 제시**: N개 행 × 좌우 대칭 막대(긍정=초록, 부정=빨강) + 변화량 컬럼
3. **해석**: 우측 Annotation 2블록에서 그룹별 해석(선진국 vs 개도국 등)
4. **Action Title 회귀**: 양극화/대조 패턴을 종합한 결론이 Action Title과 일치

**체인 연결**: 이 유형의 양극화 인사이트는 다음 유형의 원인 분석/배경이 된다

---

## 유형 10: Split Layout (2톤 배경)
> 레퍼런스: decarb-oil-gas-p06 등
> 특징: 좌측 다크 배경(텍스트) + 우측 라이트 배경(차트/데이터)

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├──────────────┬──────────────────────────────────┤
│ S-DARK-PANEL │ S-LIGHT-PANEL                     │
│ (다크 배경)   │ (라이트 배경)                      │
│              │                                   │
│ 핵심 메시지   │ 차트/데이터                        │
│ (큰 폰트)    │ + 데이터 라벨                      │
│              │                                   │
│ Source       │                                   │
├──────────────┴──────────────────────────────────┤
└─────────────────────────────────────────────────┘
```

### 섹션별 상세
| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-DARK-TEXT | `--fs-subq` (:lang(ko) 28px), bold | 좌 | `var(--c-white)` | 핵심 메시지 (2~3줄) |
| S-LIGHT-CHART-TITLE | `--fs-source` (20px), bold | 좌 | `var(--c-text)` (#000000) | 차트 제목 |
| S-LIGHT-CHART | — | flex:1 | — | 바 차트, 라인 등 |
| S-LIGHT-LABEL | `--fs-source` (20px) | 중앙 | `var(--c-text)` (#000000) | 축 라벨 |

### 내용 패턴
- **용도**: 핵심 메시지를 시각적으로 강조할 때, 데이터와 해석을 명확히 분리할 때

### 논리 흐름
1. **독자의 질문** (Sub-question): "핵심 메시지는 무엇이고 근거는?"
2. **데이터 제시**: 우측 라이트 패널에 차트/데이터
3. **해석**: 좌측 다크 패널에 큰 폰트로 So-What 직접 표시
4. **Action Title 회귀**: 좌측 주장(So-What) = Action Title, 우측 데이터가 Why-So

**체인 연결**: 이 유형의 핵심 메시지는 다음 유형의 출발점/전제가 된다

---

---

## 유형 11: Heatmap/Grid (히트맵 격자)
> 레퍼런스: consumer-spending-p05 등
> 특징: N개 카테고리 × M개 지역/세그먼트 격자, 색상 코딩

### 사용 조건
- **언제 쓰는가**: 2차원 범주형 데이터 (카테고리 × 세그먼트)의 전체 패턴을 한눈에 보여줄 때
- **언제 쓰지 않는가**: 정확한 수치 비교가 필요할 때 (→ 막대 차트), 항목이 3개 이하일 때 (→ Big Number)
- **Action Title 공식**: "[대상]은 [카테고리별] [지역별] [양극화/패턴]을 보인다"
- **최소 입력**: 행 6개+ × 열 6개+, 각 셀에 방향성(증가/감소) 또는 수치

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├─────────────────────────────────────────────────┤
│ S-SUBTITLE (단위/범례 설명)                       │
│                                                  │
│ S-GRID-HEADER (국가/세그먼트명 ×M)                │
│ S-GRID-ROW ×N                                    │
│  카테고리명 | 셀 색상(초록=증가, 회색=감소)         │
│                                                  │
│ S-LEGEND (범례: 색상 설명)                         │
│ S-GROUP-LABEL (선택: 그룹 구분. 범례로 대체 가능)    │
├─────────────────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-GRID-HEADER | `--fs-source` (20px), bold | 중앙 | `var(--c-text)` (#000000) | 국가/세그먼트명 |
| S-GRID-ROW-LABEL | `--fs-source` (20px) | 좌 | `var(--c-text)` (#000000) | 카테고리명 |
| S-GRID-CELL | — | 중앙 | `var(--c-accent)`/`var(--c-text-muted)` 배경 | 수치 또는 색상만 |
| S-LEGEND | `--fs-source` (:lang(ko) 18px) | 우 | `var(--c-text)` (#000000) | 색상 의미 설명 |
| S-GROUP-LABEL | `--fs-source` (20px), bold | 중앙 | `var(--c-text)` (#000000) | 그룹 구분 (선진국/개도국) |

### 논리 흐름
1. **독자의 질문** (Sub-question): "카테고리별/지역별 전체 패턴은?"
2. **데이터 제시**: N×M 격자 + 색상 코딩(초록=증가, 회색=감소)
3. **해석**: 범례 + 그룹 라벨로 패턴 그룹핑
4. **Action Title 회귀**: 격자 전체 패턴을 종합한 결론이 Action Title과 일치

**체인 연결**: 이 유형의 패턴 발견은 다음 유형의 심화 분석 대상이 된다

---

## 유형 12: Scatter Plot (산점도)
> 레퍼런스: insurance-vcr-p03 등
> 특징: 2차원 연속형 축에 버블/점 배치

### 사용 조건
- **언제 쓰는가**: 2차원 연속형 데이터로 상관관계/포지셔닝을 보여줄 때
- **언제 쓰지 않는가**: 범주형 비교 (→ 막대 차트), 시계열 (→ 라인 차트), 항목 5개 미만 (→ Big Number)
- **Action Title 공식**: "[대상]은 [X축] 대비 [Y축]에서 [패턴/아웃라이어]를 보인다"
- **최소 입력**: 점 8~9개+, X축/Y축 연속형 수치, 각 점에 라벨, 기준선+범례 포함

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├─────────────────────────────────────────────────┤
│ S-SUBTITLE (축 단위 설명)                         │
│                                                  │
│ S-SCATTER (전폭)                                  │
│  X축 라벨 + Y축 라벨                              │
│  점/버블 × N개 (라벨 포함)                        │
│  기준선/평균선 (선택)                              │
├─────────────────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

| 섹션 | 폰트 | 정렬 | 색상 | 콘텐츠 규칙 |
|------|------|------|------|-----------|
| S-AXIS-LABEL | `--fs-source` (20px) | 중앙 | `var(--c-text)` (#000000) | 축 이름 + 단위 |
| S-POINT-LABEL | `--fs-source` (:lang(ko) 18px) | 좌/우 | `var(--c-text)` (#000000) | 항목명 (산업/기업명) |
| S-POINT | — | — | `var(--c-accent)`(강조)/`var(--c-danger)`(약점) | 점 크기로 비중 표현 가능 |

### 논리 흐름
1. **독자의 질문** (Sub-question): "항목들의 상관관계/포지셔닝은?"
2. **데이터 제시**: 2차원 연속형 축에 N개 점/버블 배치 + 기준선
3. **해석**: 아웃라이어와 클러스터를 시각적으로 식별
4. **Action Title 회귀**: 포지셔닝 패턴을 종합한 결론이 Action Title과 일치

**체인 연결**: 이 유형의 포지셔닝 인사이트는 다음 유형의 전략 방향/배경이 된다

---

---

## 유형 13: Agenda (목차/진행 표시)
> 레퍼런스: bcg-cost-p04/p10/p17, dt-telecom-p03 등

### 사용 조건
- **언제 쓰는가**: 보고서 섹션 구분, 현재 위치 표시
- **언제 쓰지 않는가**: 콘텐츠 전달이 목적일 때 (→ 다른 유형)
- **Action Title 공식**: 없음 (Agenda는 제목 없이 사용)
- **최소 입력**: 섹션 3~5개, 현재 활성 섹션 1개 지정

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-AGENDA (grid-row:1/-1, 전폭)                    │
├──────────────┬──────────────────────────────────┤
│ S-AGENDA-IMG │ S-AGENDA-LIST                     │
│ (좌 40%)     │  체크 아이콘 + 섹션명 ×3~5         │
│ 사진 패널    │  활성: 초록 체크 + bold 초록        │
│              │  비활성: 회색 체크 + 일반            │
├──────────────┴──────────────────────────────────┤
└─────────────────────────────────────────────────┘
```

| 섹션 | 폰트 | 색상 | 콘텐츠 규칙 |
|------|------|------|-----------|
| S-AGENDA-TITLE | `--fs-agenda-title` (52px), bold | `var(--c-accent-dark)` (#187955) | 타이틀 (보고서명) |
| S-AGENDA-ITEM-ACTIVE | `--fs-subq` (:lang(ko) 28px), bold | `var(--c-accent)` (#29b974) | 현재 섹션 |
| S-AGENDA-ITEM | `--fs-subq` (:lang(ko) 28px) | `var(--c-text)` (#000000) | 비활성 섹션 |

### 논리 흐름
1. **독자의 질문**: "지금 어디까지 왔고 다음은 무엇인가?"
2. **데이터 제시**: 섹션 목록 (활성=초록, 비활성=회색)
3. **해석**: 현재 위치 표시로 보고서 전체 구조를 환기
4. **Action Title 회귀**: Agenda는 Action Title 없음 — 네비게이션 목적

**체인 연결**: 이 유형은 다음 섹션의 도입부 역할을 한다

---

## 유형 14: Text-heavy / Introduction (텍스트 중심)
> 레퍼런스: bcg-cost-p02, ai-engineering-p02, decarb-oil-gas-p02~04 등

### 사용 조건
- **언제 쓰는가**: 보고서 도입부, 배경 설명, 방법론 기술
- **언제 쓰지 않는가**: 데이터/수치가 핵심일 때 (→ Data-Viz/Big Number)
- **Action Title 공식**: "Introduction" 라벨 + 핵심 메시지 또는 라벨 없이 주장형
- **최소 입력**: 좌 본문 4문단 + 불릿 3~4개, 우 사이드바 5항목

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title (또는 "Introduction")      │
├──────────────────────┬──────────────────────────┤
│ S-TEXT-BODY (좌 65%) │ S-TEXT-RIGHT (우 35%)      │
│ 본문 2~4문단         │ 이미지 또는 핵심 메시지 박스 │
│ + 불릿 리스트        │                           │
├──────────────────────┴──────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

| 섹션 | 폰트 | 색상 | 콘텐츠 규칙 |
|------|------|------|-----------|
| S-TEXT-BODY | `--fs-body` (:lang(ko) 22px) | `var(--c-text)` (#000000) | 2~4문단, bold 핵심구 |
| S-TEXT-BULLET | `--fs-body` (:lang(ko) 22px) | `var(--c-text)` (#000000) | 불릿 3~5개 |

### 논리 흐름
1. **독자의 질문**: "이 보고서의 배경과 범위는 무엇인가?"
2. **데이터 제시**: 본문 2~4문단 + 불릿 3~5개
3. **해석**: 문제 정의, 분석 범위, 접근법을 서술형으로 전달
4. **Action Title 회귀**: 도입부의 핵심 메시지가 Action Title과 일치

**체인 연결**: 이 유형의 문제 정의는 다음 유형의 분석 출발점이 된다

---

## 유형 15: Comparison / Dual (좌우 비교)
> 레퍼런스: ai-first-win-p11/p14, genai-hr-p07/p19/p30, virtual-mentoring-p06 등

### 사용 조건
- **언제 쓰는가**: As-Is vs To-Be, 옵션 A vs B, Traditional vs Digital 등 대칭 비교
- **언제 쓰지 않는가**: 3개 이상 컬럼 비교 (→ Before/After 또는 Multi-Column), 순위가 있을 때 (→ Ranked)
- **Action Title 공식**: "[A]에서 [B]로의 전환이 [효과]를 가져온다"
- **최소 입력**: 좌/우 각 제목 + 본문 3~4문단 + 불릿 5~6개

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├──────────────────────┬──────────────────────────┤
│ S-COMPARE-LEFT       │ S-COMPARE-RIGHT           │
│ (50%)                │ (50%)                     │
│ 제목 + 본문 + 불릿   │ 제목 + 본문 + 불릿        │
│                      │                           │
├──────────────────────┴──────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

| 섹션 | 폰트 | 색상 | 콘텐츠 규칙 |
|------|------|------|-----------|
| S-COMPARE-TITLE | `--fs-subq` (:lang(ko) 28px), bold | `var(--c-text)`/`var(--c-accent)` | 컬럼 헤더 |
| S-COMPARE-BODY | `--fs-body` (:lang(ko) 22px) | `var(--c-text)` (#000000) | 2~3문단 |
| S-COMPARE-BULLET | `--fs-body` (:lang(ko) 22px) | `var(--c-text)` (#000000) | 불릿 3~5개 |

### 논리 흐름
1. **독자의 질문**: "A와 B의 차이는 무엇인가?"
2. **데이터 제시**: 좌측(As-Is/Before) vs 우측(To-Be/After) 대칭 배치
3. **해석**: 각 컬럼의 본문+불릿에서 차이점 구체화
4. **Action Title 회귀**: A→B 전환의 효과/의미가 Action Title과 일치

**체인 연결**: 이 유형의 비교 결론은 다음 유형의 실행 방안/배경이 된다

---

## 유형 16: Matrix / 2x2 (매트릭스)
> 레퍼런스: ai-first-pu-p24, ai-engineering-p07/p21, ai-first-telco-p09 등

### 사용 조건
- **언제 쓰는가**: 2차원 범주형 축으로 항목을 분류/포지셔닝할 때
- **언제 쓰지 않는가**: 연속형 수치 축 (→ Scatter Plot), 단순 순위 (→ Ranked)
- **Action Title 공식**: "[대상]을 [축1] × [축2] 기준으로 분류하면 [패턴]이 드러난다"
- **최소 입력**: 2개 축 정의 + 셀 4개(2×2) 이상, 각 셀에 항목명+설명 3줄

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-HEADER: Action Title                           │
├─────────────────────────────────────────────────┤
│ S-MATRIX (전폭)                                   │
│  X축 라벨 / Y축 라벨                              │
│  2×2 또는 N×M 셀                                 │
│  각 셀: 아이콘 + 항목명 + 설명                    │
├─────────────────────────────────────────────────┤
│ S-SOURCE                                         │
└─────────────────────────────────────────────────┘
```

| 섹션 | 폰트 | 색상 | 콘텐츠 규칙 |
|------|------|------|-----------|
| S-MATRIX-AXIS | `--fs-body` (:lang(ko) 22px), bold | `var(--c-text)` (#000000) | 축 이름 |
| S-MATRIX-CELL-TITLE | `--fs-body` (:lang(ko) 22px), bold | `var(--c-text)` (#000000) | 셀 제목 |
| S-MATRIX-CELL-DESC | `--fs-source` (20px) | `var(--c-text-body)` (#3e3e3e) | 셀 설명 |

### 논리 흐름
1. **독자의 질문**: "항목들을 어떤 기준으로 분류/포지셔닝할 수 있는가?"
2. **데이터 제시**: 2차원 격자(2×2 또는 N×M) + 각 셀에 아이콘+항목명+설명
3. **해석**: 축 정의와 셀 배치가 분류 논리를 시각적으로 전달
4. **Action Title 회귀**: 분류 패턴을 종합한 결론이 Action Title과 일치

**체인 연결**: 이 유형의 포지셔닝 결과는 다음 유형의 전략 선택/배경이 된다

---

## 유형 17: Back Cover (뒷표지)
> 레퍼런스: 모든 PDF 마지막 페이지

### 사용 조건
- **언제 쓰는가**: 보고서 마지막 페이지
- **언제 쓰지 않는가**: 콘텐츠 전달 목적 (→ 다른 유형)
- **최소 입력**: 로고 + 연락처 또는 저자 프로필

### 섹션 구조
```
┌─────────────────────────────────────────────────┐
│ S-BACKCOVER (전폭)                                │
│  로고 + 연락처 또는 저자 프로필 그리드             │
│  또는 단순 로고 + 배경 사진                       │
└─────────────────────────────────────────────────┘
```

---

## Codex 2회차 검증 반영 — 폰트 크기 보정

> Codex 피드백: 일부 폰트 크기가 실제 BCG보다 작음. JSON 실측값 기반 보정.

| 섹션 | 기존 | 보정 (CSS 변수) | 근거 |
|------|------|---------------|------|
| S-SUBQ | 26px | **`--fs-subq` (32px)** | 실측 31.9px |
| S-RANK-NUM | 48px | **`--fs-rank` (56px)** | 실측 55.9~64.1px |
| S-BIG-NUM | 56px | **`--fs-big` (72px)** | 실측 80px 케이스 존재 |
| S-COL-TITLE | 26px | **`--fs-col-title` (28px)** | 실측 27~29px |

> 참고: 사용자 피드백에 따라 "고정값" 원칙 유지. 범위가 아닌 단일 값으로 확정.

---

*Phase 1 완료 — 17개 PDF, 337p 전수 분석. 21개 유형(서브타입 포함) 정의. Codex 2회 교차검증 완료.*
