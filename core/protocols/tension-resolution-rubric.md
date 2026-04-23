# Tension Resolution Rubric (v4.12 Issue #3)

> Division 간 모순(tension)을 **우선순위화하여 일관되게 해소**하는 판정 체계.
> insight-synthesizer가 수렴 판정 단계에서 이 rubric을 적용한다.

## 1. 배경

v4.11까지는 Sync Round 2의 `tension-resolution.yaml`이 tension을 **감지·기록**하기만 했다. 실제 해소 판정은 insight-synthesizer의 자율 판단에 맡겨져 일관성이 부족했다.
예: "Market Division은 성장 긍정 / Finance Division은 수익성 부정" 같은 tension이 어떤 기준으로 해소되는지 불명확.

v4.12는 **4단계 우선순위 rubric**으로 tension을 판정한다.

## 2. Tension 유형 분류

| 유형 | 정의 | 예시 |
|------|------|------|
| **수치 모순** | 같은 지표에 대해 다른 값 | Market $10B, Finance $8B |
| **전망 모순** | 같은 미래에 대한 다른 예측 | Market "+20%", Finance "-5%" |
| **해석 모순** | 같은 사실에 다른 의미 부여 | Product "기술 우위", Capability "기술 부채" |
| **전제 모순** | 전략의 핵심 가정 충돌 | Market "시장 성장 지속" vs Red Team "포화 임박" |
| **범위 모순** | Division 간 분석 경계 충돌 | Market "TAM 1조", customer-analysis "세그먼트 합 1.2조" |

## 3. 4단계 우선순위 Rubric

### (a) 엔터티 라벨 일치 우선 (최우선)

다른 엔터티/시점/단위를 비교하고 있는 경우 → **모순이 아님**, 라벨 정정으로 해소.

```
예: Market Division — "매출 1조 (그룹 기준, 2025)"
    Finance Division — "매출 8천억 (별도 기준, 2024)"
    
판정: 엔터티 라벨 불일치 → 두 값 모두 유효. 보고서에 라벨 명시.
해소 경로: fact-verifier가 entity_label 정정 후 tension 종료.
```

### (b) 소스 강도 우선 (수치/사실 모순)

수치·사실이 다르면 **소스 조합이 더 강한 쪽을 채택**.

소스 강도 순위 (output-format.md §신뢰도 정량화):
1. primary 2개+ 일치
2. primary 1 + secondary 1+
3. secondary 2개+ 독립
4. secondary 1개
5. estimate

```
예: Market — TAM $10B (DART 2025년 사업보고서 primary)
    Product — TAM $8B (업계 블로그 estimate)
    
판정: Market 채택. Product는 보고서에서 "초기 추정"으로 각주.
해소 경로: golden-facts.yaml에 Market 값 등록, Product는 참조로 대체.
```

### (c) 최신성 우선 (전망·해석 모순)

전망이나 해석이 다르면 **더 최신 데이터 기반을 채택**. 단, 시점이 같으면 (d)로.

```
예: Market — "연 20% 성장 지속" (2024년 1분기 데이터)
    Finance — "2025년 하반기 둔화 감지" (2025년 3분기 데이터)
    
판정: Finance 채택 (더 최신). Market 전망은 "과거 추세" 참고로.
해소 경로: insight-synthesizer가 최신 데이터 우선 반영, tension 해소.
```

### (d) 사용자 의도 + 시나리오 명시 (전제·범위 모순)

위 3단계로 해소 안 되는 경우 (동일 엔터티·시점·소스 강도) → **사용자 Client Brief의 decision_frame·kill_criteria와 대조**하여 어느 쪽이 decision에 더 적합한지 판정.

```
예: Market — "AI NPC 상용화 2년 내" (Capability "기술 성숙도 충분" 근거)
    Red Team — "상용화 4년+" (규제·윤리 이슈 근거)
    
판정: 사용자 Client Brief가 "빠른 진출" 방향이면 Market 채택 + Red Team 리스크 섹션 명시
      사용자 Client Brief가 "리스크 회피" 방향이면 Red Team 채택 + 진입 시점 조정
해소 경로: insight-synthesizer가 user-profile.yaml의 risk_tolerance 참조.
```

### (e) 해소 불가 — 양측 병기 (마지막 수단)

(a)~(d)로 판정 불가능한 경우 → **양측을 보고서에 병기** + 미해결 불확실성으로 표시.

```
보고서 형식:
  "[Market 관점] 성장 지속 (근거 A, confidence: medium)
   [Finance 관점] 하락 임박 (근거 B, confidence: medium)
   현재 데이터로는 판정 불가 — 추가 리서치 필요: [구체 질문]"
```

## 4. insight-synthesizer 실행 프로토콜

```
Phase 3 사고 루프 말미, 수렴 판정 전에 실행:

Step T-1: tension-resolution.yaml 로드 (Sync Round 2에서 기록됨)

Step T-2: 각 tension에 대해 rubric 순차 적용
  (a) → (b) → (c) → (d) → (e)
  첫 번째로 매치되는 단계에서 판정 확정

Step T-3: 판정 결과를 exploration-confirmation.yaml과 병합하여
         loop-convergence.md에 기록

Step T-4: 수렴 판정의 4조건에 "미해소 tension 2건+ 없음" 추가
```

## 5. 출력 포맷 (tension-resolution.yaml 확장)

```yaml
tensions:
  - id: T-01
    type: 수치 모순 | 전망 모순 | 해석 모순 | 전제 모순 | 범위 모순
    divisions: [market, finance]
    claim_ids: [MGE-03, FRV-07]
    description: "간단 설명"

    # v4.12 신규 rubric 판정
    resolution:
      verdict: a | b | c | d | e | unresolved
      winner: market | finance | both | neither
      rationale: "어떤 단계 기준으로 어떻게 판정했는지"
      applied_rule: "엔터티 라벨 일치 | 소스 강도 | 최신성 | 사용자 의도 | 양측 병기"
      report_treatment: "본문 처리 방식 (단일 채택 / 각주 / 리스크 섹션 / 미해결 불확실성)"
```

## 6. 역호환

- v4.11 이전 `tension-resolution.yaml` 파일은 `resolution` 필드 없이 존재 → insight-synthesizer가 자동 추가 (또는 미판정으로 유지)
- 기존 "4조건 수렴" 로직은 유지 + "tension rubric 적용"이 5번째 조건으로 추가

## 7. 참조

- `core/protocols/output-format.md` §소스 추적 규칙 (소스 강도)
- `core/protocols/fact-check-protocol.md` VL-1.5 삼각 검증 (모순 감지)
- `core/protocols/analysis-type-protocol.md` §사용자 의도 (decision_frame)
- `.claude/agents/insight-synthesizer.md` Step T-1~4 (rubric 실행)
