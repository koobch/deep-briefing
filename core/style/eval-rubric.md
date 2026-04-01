# 슬라이드 15축 평가 루브릭 (Evaluation Rubric)

> 이 파일은 슬라이드 프로토타입의 품질 평가 기준을 정의한다.
> Claude/Codex/기타 LLM이 이 파일을 읽고 동일한 기준으로 평가해야 한다.

## 평가 방법

1. `slide-system.css`와 `prototype-v6.html`을 읽는다
2. 각 슬라이드(SLIDE 1~22)에 대해 15축을 PASS/FAIL/EXEMPT 판정한다
3. EXEMPT는 해당 슬라이드에 적용 불가능한 축이다 (FAIL 카운트에서 제외)

## 면제 슬라이드 (Exempt Slides)

| 슬라이드 | 유형 | 면제 축 | 이유 |
|---------|------|---------|------|
| Slide 2 | Agenda | A1~A7, C3, C5 | grid-row:1/-1 전폭 레이아웃, 목차 용도 |
| Slide 10 | Cover EP | A1~A7, C3, C5 | grid-row:1/-1 전폭 레이아웃, 표지 |
| Slide 11 | Cover Global | A1~A7, C3, C5 | grid-row:1/-1 전폭 레이아웃, 표지 |
| Slide 22 | Back Cover | A1~A7, C3, C5 | grid-row:1/-1 전폭 레이아웃, 뒷표지 |

## 15축 정의

### A 그룹: 정렬 원칙 (P1~P7)

| 축 | 이름 | PASS 조건 | FAIL 조건 |
|---|------|----------|----------|
| A1 | 3행 그리드 | CSS `.slide`가 `grid-template-rows: var(--header-h) 1fr auto` 사용 | 비면제 슬라이드에 header/slot-body/footer 3행 구조 없음 |
| A2 | 컬럼 비율 | 허용 비율 사용: 전폭(1fr), 65:35, 30:70, 25:75, 50:50, 40:60(Split Layout 전용). CSS custom property 오버라이드(--col-primary 등)로 미세 조정 허용 | 허용 비율 외 고정 px 사용 |
| A3 | 수평 기준선 | 동일 역할 요소(예: 3개 exec-row의 라벨, 5개 rank-item)가 CSS class로 정렬됨 | 같은 역할 요소의 y 시작점이 CSS로 보장되지 않음 |
| A4 | 반복 간격 | 반복 요소 컨테이너에 단일 gap 토큰(var(--sp-*)) 사용 | 동일 반복 그룹 내 2개 이상 다른 gap 값 혼용 |
| A5 | 좌우 여백 | 슬라이드 외곽 좌/우에 var(--pad-x) 또는 var(--pad-x-right) 적용 | 외곽 여백이 pad-x와 불일치 |
| A6 | 엣지 정렬 | 배경색 행의 컨테이너 padding=0, 콘텐츠는 내부 padding으로 인덴트 | 배경색 행에 직접 padding이 있어 엣지가 안 맞음 |
| A7 | Grid 기준선 | 같은 슬라이드 내 인접 행이 동일 grid-template-columns 공유 | 인접 행의 grid 컬럼 수/비율이 다름 (의도적 변형 제외) |

### B 그룹: 코드 품질

| 축 | 이름 | PASS 조건 | FAIL 조건 |
|---|------|----------|----------|
| B1 | 토큰 일관성 | CSS 클래스 body 내 모든 간격/크기가 var() 토큰 사용. **면제**: :root 토큰 정의, .proto-tag, border-width(1~3px), border-radius, clip-path, border shorthand(`1px solid var(...)`) | CSS 클래스 body에 var()로 감싸지 않은 raw px 값 존재 |
| B2 | 콘텐츠 밀도 | 본문 2줄+, 패널 3문단+, 차트 4항목+(단, 강조형 레이아웃인 Split Layout/Big Number는 3항목 허용), Table 행에 bold+설명 | section-map 최소 요구량 미달 |
| B3 | 레이아웃 정확도 | section-map.md에 정의된 핵심 섹션 구조와 일치. **유연성**: callout이 annotation 역할을 대체할 수 있으며, 선택적(optional) 섹션의 생략은 허용 | 필수 섹션 누락 또는 구조 순서 오류 |

### C 그룹: 세부 품질

| 축 | 이름 | PASS 조건 | FAIL 조건 |
|---|------|----------|----------|
| C1 | 타이포 위계 | HTML 인라인 및 CSS 클래스의 모든 font-size가 var(--fs-*) 토큰 사용. **면제**: .proto-tag | raw px font-size (예: `font-size: 14px`) |
| C2 | 색상 토큰 | HTML 인라인의 모든 color/background가 var(--c-*) 토큰 사용. **면제**: 차트 데이터 바/버블의 background (데이터 시각화 구분색) — 단, 이들도 var(--c-chart-*) 토큰으로 관리되면 PASS | #hex 인라인 (예: `color:#333`) |
| C3 | Action Title | h1.action-title 텍스트가 주장형 문장 (동사 포함, 결론을 진술). **예외**: "사례 \|" 접두사 슬라이드(Case Study)는 성과 서술형 허용 (예: "...달성한 기업 사례") | 주제형 명사 종결 (예: "시장 분석", "비용 현황"). 단, Case Study의 성과 서술은 FAIL 아님 |
| C4 | 인라인 스타일 | HTML inline style에 **구조적 레이아웃 속성 없음**: `display`, `grid-template-columns`, `grid-template-rows`, `flex-direction`. **허용**: 데이터값(width%, left%, bottom%), 토큰 오버라이드(font-size:var(), color:var(), gap:var()), 프레젠테이셔널 속성(font-weight, text-align, margin, padding with var(), line-height, letter-spacing, text-transform, font-style), 배경/색상(background:var(), color:var()) | display:/grid-template-columns:/grid-template-rows:/flex-direction: 가 HTML inline style에 존재 |
| C5 | Source/Footer | "Source: [출처] ([날짜]); [분석주체]" 형식 + 페이지 번호 | 형식 미준수 또는 Source/Footer 누락 |

## 출력 형식

```
| Slide | A1 | A2 | A3 | A4 | A5 | A6 | A7 | B1 | B2 | B3 | C1 | C2 | C3 | C4 | C5 | Fails |
```

- P = PASS, F = FAIL, X = EXEMPT
- AxisFails 행: 각 축별 FAIL 수 (EXEMPT 제외)
- Total 행: 총 FAIL 수
