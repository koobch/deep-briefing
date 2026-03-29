# BCG Cost & Growth p8 — Insight+Chart 좌표 스펙

## 슬라이드 전체 (1920 x 1080px)

```
┌─────────────────────────────────────────────────────────────────┬────┐
│ HEADER BAR (green #00875A, full width)                          │DECO│
│ y:0 → y:65 (65px)                                               │    │
│ "Asia-Pacific executives are concerned about impacts on exports │    │
│  that could slow economic growth" 20pt 700w #FFF                │    │
│ text-x: 45px, 2줄, vertical-center                              │    │
├─────────────────────────────────────────────────────────────────┤    │
│ GREEN SEPARATOR (3px) y:65                                       │    │
├─────────────────────────────────────────────────────────────────┤    │
│ SUB-QUESTION y:80                                                │    │
│ "What top macroeconomic factors..." 12pt 700w #00875A           │    │
│ text-x: 45px, 2줄                                                │    │
│ y:80 → y:115 (35px)                                              │    │
├──────────────────────────────────────┬──────────────────────────┤    │
│ CHART AREA                           │ TEXT PANEL               │    │
│ x:45 → x:1140 (1095px, ~60%)        │ x:1160 → x:1760 (600px) │    │
│ y:125 → y:800                        │ y:125 → y:800           │    │
│                                      │                          │    │
│ ┌──────┬──────┬──────────┐           │ "Asia-Pacific executives│    │
│ │ N.Am │Europe│Asia-Pac¹ │           │  are navigating a       │    │
│ │      │      │          │           │  complex..."            │    │
│ │legend│legend│legend    │           │  11pt 400w #1A1A1A      │    │
│ │      │      │          │           │                          │    │
│ │[bar] │[bar] │[bar]     │           │ "They are increasingly │    │
│ │2023  │2023  │2023      │           │  **concerned about     │    │
│ │2024  │2024  │2024      │           │  economic uncertainty** │    │
│ │2025  │2025  │2025      │           │  stemming from..."      │    │
│ │      │      │          │           │  11pt, bold구절 700w    │    │
│ │[bar] │[bar] │[bar]     │           │                          │    │
│ │      │      │          │           │ "Potential geopolitical │    │
│ │[bar] │[bar] │[bar]     │           │  tensions could further│    │
│ │      │      │          │           │  **erode investor      │    │
│ ├──────┴──────┴──────────┤           │  confidence**..."       │    │
│ │• bullet text           │           │                          │    │
│ │  3컬럼 각 하단          │           │                          │    │
│ │  10pt 400w             │           │                          │    │
│ └────────────────────────┘           │                          │    │
├──────────────────────────────────────┴──────────────────────────┤    │
│ CALLOUT BOX y:810 → y:840 (30px)                                │    │
│ green bg, "Over 60% of Asia-Pacific..." 9pt 700w #FFF           │    │
│ x:45 → x:1760                                                   │    │
├─────────────────────────────────────────────────────────────────┤    │
│ FOOTNOTES y:860 → y:910                                         │    │
│ "Note: Asia-Pacific countries excluding China" 7pt #7A8594       │    │
│ "Source: BCG global executive survey..." 7pt #7A8594             │    │
│ "1. Asia-Pacific includes..." 7pt #7A8594                        │    │
├─────────────────────────────────────────────────────────────────┤    │
│ (여백) y:910 → y:1080                                             │    │
│ page number "8" at x:1870                                        │    │
└─────────────────────────────────────────────────────────────────┴────┘
```

## 정밀 좌표

### 전체 영역 분할
| 영역 | x-start | x-end | y-start | y-end | 크기 |
|------|---------|-------|---------|-------|------|
| 헤더바 | 0 | 1920 | 0 | 65 | 1920×65 |
| Sub-question | 45 | 1760 | 80 | 115 | 1715×35 |
| 차트 영역 | 45 | 1140 | 125 | 800 | 1095×675 |
| 텍스트 패널 | 1160 | 1760 | 125 | 800 | 600×675 |
| Callout 박스 | 45 | 1760 | 810 | 840 | 1715×30 |
| Footnotes | 45 | 1760 | 860 | 920 | 1715×60 |
| 장식 스트립 | 1790 | 1920 | 0 | 1080 | 130×1080 |

### 비율 분석 (핵심)
```
좌측(차트): 1095 / 1715 = 64%
우측(텍스트): 600 / 1715 = 35%
gap: 20px (~1%)

→ BCG p8의 실제 비율은 64:35 (차트가 훨씬 넓음!)
→ 우리 시스템의 Insight+Chart (55:45)와 다름
→ BCG는 슬라이드마다 비율이 다름 — 유동적
```

### 차트 영역 내부 (3컬럼 스택바)
| 요소 | 값 |
|------|-----|
| 컬럼 수 | 3 (North America, Europe, Asia-Pacific) |
| 컬럼 폭 | 각 ~340px |
| 컬럼 gap | ~17px |
| 컬럼 헤더 | 12pt 700w, 중앙 정렬 (Asia-Pacific¹은 빨강 강조) |
| 범례 | 각 컬럼 상단, 8pt, 2가지 색상 마커 |
| 바 높이 | ~35px |
| 바 gap | ~4px |
| 바 라벨 (좌) | "Inflation and rising interest rates" 9pt 400w, 좌측 |
| 바 값 라벨 | 바 내부 or 외부, 8pt Bold |
| 바 색상 | 초록 계열 2~3색 (Pre/Post election) |
| 하단 불릿 | 각 컬럼 아래, 10pt 400w, • 마커 |

### 텍스트 패널 내부
| 요소 | x | 크기 | weight | 색상 |
|------|---|------|--------|------|
| 문단 1 | 1160 | 11pt (15px) | 400 | #1A1A1A |
| Bold 구절 | — | 11pt | 700 | #1A1A1A (동색) |
| 문단 간 gap | — | ~16px | — | — |
| 문단 수 | 3개 | — | — | — |
| 문단 최대 줄 수 | 6~8줄 | — | — | — |

### Callout 박스
| 속성 | 값 |
|------|-----|
| 배경 | 연한 초록 (#E6F4ED) — p8은 연한 초록 (진한 초록 아님!) |
| 텍스트 색 | #1A1A1A (검정) |
| Bold 구절 | 700w |
| 높이 | ~30px |
| padding | 상하 8px, 좌우 16px |
| 모서리 | 0 |

## BCG p3 vs p8 비교

| 항목 | p3 (Exec Summary) | p8 (Insight+Chart) |
|------|-------------------|-------------------|
| 헤더바 | 2줄 (라벨+제목) | 2줄 (제목만, 길어서) |
| 본문 구조 | 3행 (라벨+텍스트) | 좌차트+우텍스트 |
| 차트:텍스트 비율 | N/A (테이블형) | 64:35 |
| 불릿 크기 | 10.5pt | 10pt |
| 텍스트 패널 크기 | — | 11pt |
| Callout | 없음 | 있음 (연초록 bg) |
| Footnote | 1줄 | 3줄 |
| 콘텐츠 높이 | Row가 본문 85%+ 채움 | 차트+텍스트가 675px 채움 |
