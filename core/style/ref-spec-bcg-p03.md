# BCG Cost & Growth p3 — Exec Summary 좌표 스펙

## 슬라이드 전체 (1920 x 1080px)

```
┌─────────────────────────────────────────────────────────────────┬────┐
│ HEADER BAR (green #00875A, full width)                          │DECO│
│ y:0 → y:65                                                      │RATI│
│ ┌─────────────────────────────────────────────────────────────┐ │VE  │
│ │ "Executive summary |" 12pt 400w rgba(255,255,255,0.7)      │ │STRI│
│ │ "In a complex..." 20pt 700w #FFF                           │ │P   │
│ │ text-x: 45px, vertical-center                              │ │    │
│ └─────────────────────────────────────────────────────────────┘ │x:  │
├─────────────────────────────────────────────────────────────────┤1790│
│ GREEN SEPARATOR LINE (3px, #00875A) y:65                        │ to │
├──────┬──────────────────────────────────────────────────────────┤1920│
│ ROW1 │                                                          │    │
│LABEL │  BODY TEXT                                                │    │
│green │  y:80 → y:340 (~260px)                                   │    │
│bg    │  "The global market outlook..." 10.5pt 400w              │    │
│45→200│  • "40% of executives..." 10.5pt, bold: "40%"           │    │
│(155px│  • "North American..." bold: "margins and profitability" │    │
│wide) │  • "Asia-Pacific¹..." bold: "slow economic growth"      │    │
│      │  [light green box] "85% of executives are already..."    │    │
│"Navi-│  text-x: 210px → 1760px                                  │    │
│gating│                                                          │    │
│the   │                                                          │    │
│econo-│                                                          │    │
│mic   │                                                          │    │
│land- │                                                          │    │
│scape"│                                                          │    │
│14pt  │                                                          │    │
│700w  │                                                          │    │
│#FFF  │                                                          │    │
├──────┼──────────────────────────────────────────────────────────┤    │
│ ROW2 │                                                          │    │
│LABEL │  BODY TEXT                                                │    │
│green │  y:340 → y:580 (~240px)                                  │    │
│bg    │  "Amid a complex..." 10.5pt                              │    │
│      │  • "Insulating less, executives are..."                  │    │
│"Mana-│  • "Executives in the sample..." bold: "only 40%"       │    │
│ging  │  • "The greatest barrier..."                             │    │
│cost  │                                                          │    │
│struc-│  text-x: 210px → 1760px                                  │    │
│tures"│                                                          │    │
│14pt  │                                                          │    │
├──────┼──────────────────────────────────────────────────────────┤    │
│ ROW3 │                                                          │    │
│LABEL │  BODY TEXT                                                │    │
│green │  y:580 → y:810 (~230px)                                  │    │
│bg    │  "Laying the foundations..." 10.5pt                      │    │
│      │  • "Executives see GenAI..." bold: "86%"                │    │
│"Unlo-│  • "Executives see GenAI..."                             │    │
│cking │  [full-width paragraph] "BCG's holistic approach..."     │    │
│sust- │                                                          │    │
│ainab-│  text-x: 210px → 1760px                                  │    │
│le    │                                                          │    │
│grow- │                                                          │    │
│th"   │                                                          │    │
├──────┴──────────────────────────────────────────────────────────┤    │
│ SOURCE AREA y:1040 → 1080 (40px)                                │    │
│ "Source: BCG global executive survey..." 7pt #7A8594             │    │
│ "1. Asia-Pacific includes..." 7pt #7A8594                       │    │
│ text-x: 45px                                                    │    │
│ page number "3" at x:1870, y:1060                               │    │
└─────────────────────────────────────────────────────────────────┴────┘
```

## 정밀 좌표 (px 기준, 1920x1080)

### 전체 구조
| 영역 | x-start | x-end | y-start | y-end | 높이 | 비고 |
|------|---------|-------|---------|-------|------|------|
| 헤더바 | 0 | 1920 | 0 | 65 | 65px | 전폭 초록 |
| 구분선 | 0 | 1920 | 65 | 68 | 3px | 초록 |
| Row 1 | 45 | 1790 | 80 | 340 | 260px | |
| Row 2 | 45 | 1790 | 340 | 580 | 240px | |
| Row 3 | 45 | 1790 | 580 | 810 | 230px | |
| 빈 공간 | 45 | 1790 | 810 | 1040 | 230px | 실제로는 Row3가 더 길 수 있음 |
| Source | 45 | 1790 | 1040 | 1080 | 40px | |
| 장식 스트립 | 1790 | 1920 | 0 | 1080 | 1080px | 우측 블러 사진 |

### 헤더바 내부
| 요소 | x | y | 크기 | weight | 색상 |
|------|---|---|------|--------|------|
| 섹션 라벨 | 45 | 15 | 12pt (16px) | 400 | rgba(255,255,255,0.7) — 주황/금색 톤 |
| Action Title | 45 | 28 | 20pt (27px) | 700 | #FFFFFF |
| 라벨 최대 폭 | — | — | 1700px | — | 2줄 허용 |

### Row 구조
| 요소 | x-start | x-end | 폭 | 크기 | weight | 색상 | 배경 |
|------|---------|-------|-----|------|--------|------|------|
| 좌측 라벨 | 45 | 200 | 155px | 12pt (16px) | 700 | #FFF | #00875A gradient |
| 라벨 padding | — | — | 좌우 18px, 상하 20px | — | — | — | — |
| 우측 본문 | 210 | 1760 | 1550px | 10.5pt (14px) | 400 | #1A1A1A | #FFF |
| 본문 padding | — | — | 좌 22px, 우 20px, 상 16px | — | — | — | — |
| 불릿 마커 | 232 | — | • (6px) | — | — | #1A1A1A | — |
| 불릿 텍스트 | 244 | 1740 | — | 10.5pt | 400 | #1A1A1A | — |
| Bold 구절 | — | — | — | 10.5pt | 700 | #1A1A1A (동색) | — |
| 행 간 구분 | 45 | 1790 | — | 1px | — | #E2E8F0 | — |

### Source 영역
| 요소 | x | y | 크기 | 색상 |
|------|---|---|------|------|
| Source 텍스트 | 45 | 1045 | 7pt (9px) | #7A8594 |
| 각주 | 45 | 1058 | 7pt (9px) | #7A8594 |
| 페이지 번호 | 1870 | 1060 | 7pt (9px) | #7A8594 |

### 장식 스트립
| 속성 | 값 |
|------|-----|
| x | 1790 → 1920 (130px) |
| 처리 | 블러(4px) + saturate + gradient overlay |
| opacity | 65% |

## 핵심 관찰

1. **행이 본문 영역을 모두 채움**: Row1(260px) + Row2(240px) + Row3(230px) = 730px. 본문 영역은 y:80~y:1040 = 960px. 실제로는 행 높이가 더 크고 빈 공간이 거의 없음.
2. **좌측 라벨 폭 155px**: 전체 너비 1745px 중 ~9%
3. **라벨-본문 gap**: 10px (200→210)
4. **불릿은 본문 영역 안에서 indent**: 본문 x:210에서 불릿 마커 x:232 (+22px)
5. **한 Row 안에서 여러 문단**: 첫 문단 (서두) + 불릿 2~4개 + 마감 문단
6. **섹션 라벨 색상**: "Executive summary |" 부분이 약간 주황/금색 톤으로 보임 (단순 흰색이 아님)
