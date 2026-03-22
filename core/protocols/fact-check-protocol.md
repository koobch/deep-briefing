# 4-Level 팩트체크 프로토콜

> 모든 데이터와 Claim의 정확성을 보장하는 계층적 검증 체계.
> 각 VL(Verification Level)은 독립적으로 동작하며, 상위 VL은 하위 VL의 검증을 전제한다.
>
> **용어 구분**: 출력 포맷의 Layer(0-3)는 데이터 구조, 이 문서의 VL(1-3)은 검증 프로세스.

## 설계 원칙

1. **자기 채점 금지** — 수집한 사람이 최종 검증자가 되지 않는다
2. **비용 효율** — 모든 것을 검증하지 않고, 리스크 기반으로 중요한 것에 집중
3. **구조적 교차** — 차원(Dimension) 기반 분해의 자연 교차점을 검증에 활용
4. **투명성** — 검증 과정과 결과가 추적 가능해야 한다

## 4-Level 구조 총괄

```
VL-3: fact-verifier (Cross-cutting)
  Division 간 교차 모순 + 방법론 감사 + 전략 핵심 전제 독립 재검증
         │
VL-2: Division Lead
  리프 간 수치 일관성 + 엔터티/시점 통일
         │
VL-1.5: Division Lead (리프 간)
  삼각 검증(Triangulation) + 핵심 Claim 스팟체크
         │
VL-1: Leaf Agent
  2소스+ 교차 확인 + 반증(Disconfirming) 검토
```

---

## VL-1: Leaf Agent 자가 검증

### 적용 시점
데이터 수집 즉시 — 자율 반복 루프 내에서 실행.

### 프로토콜

```
모든 Claim에 대해:

1. 독립 소스 교차 (Minimum 2-Source Rule)
   ┌─────────────────────────────────────────────────┐
   │ "독립"의 정의:                                    │
   │ - 서로 다른 원본 데이터에 기반                      │
   │ - 뉴스 A가 뉴스 B를 인용 → 1개로 카운트            │
   │ - DART 공시 + 산업 보고서 추정 → 2개 (원본 상이)    │
   │ - A 보고서 + A 인용 기사 → 1개 (원본 동일)         │
   └─────────────────────────────────────────────────┘

2. 소스 신뢰도 분류
   primary:   공시, 공식 발표, API 직접 조회 (DART, SEC, 앱스토어)
   secondary: 뉴스 보도, IR 자료, 애널리스트 리포트
   estimate:  시장 조사 기관 추정치, 모델 기반 산출

   규칙:
   - confidence: high → primary 소스 1개+ 필수
   - confidence: medium → secondary 이상 2개+
   - confidence: low → estimate만 있거나 소스 1개
   - unverified → 소스 없음, 추정/기억 기반

3. 반증 검토 (Disconfirming Evidence Search)
   ┌─────────────────────────────────────────────────┐
   │ 능동적으로 반대 증거를 검색:                        │
   │ "이 Claim이 틀렸다면 어떤 데이터가 존재할까?"       │
   │                                                   │
   │ 검색 방법:                                         │
   │ - 같은 주제의 다른 관점 기사/보고서 탐색             │
   │ - 경쟁 가설에 부합하는 데이터 검색                   │
   │ - 시계열 추이에서 반대 트렌드 확인                   │
   │                                                   │
   │ 출력:                                              │
   │ - 반증 발견 시: 내용 + 평가 + Claim 수정 여부       │
   │ - 미발견 시: "검색 방법 X, Y로 탐색 결과 반증 미발견"│
   │   (빈 값 불가 — 검색 방법이라도 명시)               │
   └─────────────────────────────────────────────────┘

   자동화 보조:
   - `python scripts/generate-disconfirming.py {project}` → 반증 쿼리 자동 생성 + 검색
   - strategic_impact: high Claim에 대해 실행 권장
   - 결과: qa/disconfirming-report.yaml
   - strong 반증 발견 시: confidence 하향 + Claim 수정 검토 필수
   - 실행 모드: --dry-run (쿼리 생성만) 또는 검색 모드 (Google API 직접 호출)

4. 수치 불일치 처리
   - 소스 간 불일치 ≤ 10%: 범위로 표기, 사유 추정
   - 소스 간 불일치 > 10%: 원인 분석 필수 (정의 차이? 시점 차이? 오류?)
   - 원인 불명 시: confidence를 한 단계 하향

5. 필수 라벨링
   - 엔터티: [그룹] / [별도] / [부문] (해당 시)
   - 시점: 데이터 기준 시점 (YYYY 또는 YYYY-QN)
   - 통화: 원화/달러 명시, 환율 기준 (해당 시)
```

### VL-1 통과 기준
- [ ] 모든 Claim에 confidence 태깅 완료
- [ ] confidence: high인 Claim에 primary 소스 1개+ 포함
- [ ] 모든 Claim에 disconfirming 필드 작성 (빈 값 없음)
- [ ] 소스 간 불일치 > 10%인 항목에 원인 분석 기재
- [ ] 엔터티/시점/통화 라벨 누락 없음

---

## VL-1.5: Division 내 교차 검증

### 적용 시점
Division Lead가 리프 출력을 수집한 직후, VL-2 정합성 검토 전에 실행.

### A. 삼각 검증 (Triangulation)

차원 기반 분해의 구조적 장점을 활용한 교차 검증.
**같은 수치를 다른 차원에서 독립적으로 산출할 수 있는 경우** 자동 교차한다.

```
[Division Lead 프로토콜]

1. 교차 가능 수치 식별
   리프 출력에서 "다른 리프의 데이터로도 산출 가능한 수치"를 추출

   예시 (Market Division):
   geography: "한국 시장 = $8.0B"
   platform:  "글로벌 $98B × 한국 비중 8.2% = $8.03B"
   category:  "카테고리A $4.2B + 세그먼트B $2.1B + ... = $8.0B"

2. 교차 실행
   불일치 판정 기준: 5% 이상 차이

   일치 (≤ 5%): triangulation verdict = "일치" → pass
   불일치 (> 5%):
     → 해당 리프들에 재확인 지시
     → 정의 차이인지 실제 오류인지 판별
     → 해소 안 되면 범위로 표기 + 사유 명시

3. 출력
   triangulation 결과를 Lead 출력의 synthesis.triangulation에 기록
```

**삼각 검증이 가능한 전형적 패턴:**

| 교차 유형 | 예시 |
|----------|------|
| 지역별 합산 = 전체 | 동아시아 + 서구 + 이머징 = 글로벌 |
| 카테고리별 합산 = 전체 | 카테고리A + 세그먼트B + ... = 전체 |
| 플랫폼별 합산 = 전체 | Mobile + PC + Console = 지역 전체 |
| 경쟁사 점유율 합산 | 개별 점유율 합 ≤ 100% |
| 매출 = 가격 × 볼륨 | ARPU × MAU = 매출 |

### B. 핵심 Claim 스팟체크

모든 Claim을 검증하는 것은 비현실적. **전략적 임팩트가 높은 상위 3~5개만 독립 검증.**

```
[Division Lead 프로토콜]

1. 스팟체크 대상 선정
   기준: strategic_impact: high인 Claim
   추가 기준:
   - 전체 전략 방향을 결정하는 Claim
   - confidence: medium인데 strategic_impact: high인 Claim (위험)
   - 직감적으로 "너무 깔끔한" 수치 (확증 편향 의심)

2. 독립 검증 방법 (택 1)
   a. 다른 리프에게 요청:
      "네가 수집한 데이터에서 이 수치를 역산할 수 있어?"
   b. Lead가 직접 출력 Layer 3 (Raw Source)까지 드릴다운:
      원본 URL 접속 → 수치 직접 확인
   c. 다른 방법론으로 재산출:
      "Top-down 추정 vs Bottom-up 추정이 일치하는가?"

3. 결과 기록
   spot_checks 결과를 Lead 출력의 synthesis.spot_checks에 기록
   - pass: 독립 검증으로 확인됨
   - fail: 수치 불일치 → 수정 지시
   - adjusted: 범위 조정 (예: $15B → $13-17B)
```

### VL-1.5 통과 기준
- [ ] 삼각 검증 가능한 수치에 대해 교차 실행 완료
- [ ] 불일치 항목 전부 해소 또는 범위 표기
- [ ] strategic_impact: high Claim 중 최소 3개 스팟체크 완료
- [ ] 스팟체크 결과 전부 기록

---

## VL-2: Division Lead 정합성 검토

### 적용 시점
VL-1.5 완료 후, Division 합성(synthesis) 전에 실행.

### 프로토콜

```
1. 수치 일관성 (Numerical Consistency)
   - 부분 합 = 전체 (세그먼트별 합산이 전체와 일치)
   - 비율 합 ≤ 100% (점유율 등)
   - 전년 대비 증감율과 절대값의 정합성
   - 같은 지표가 다른 리프에서 다른 값으로 인용되지 않는지

2. 엔터티 일관성 (Entity Consistency)
   - [그룹] / [별도] 라벨 일관 사용
   - 같은 기업이 다른 이름으로 인용되지 않는지
     (예: 같은 기업의 한글명 vs 영문명 vs 약칭)
   - 퍼블리셔 ≠ 개발사 혼동 (EP-015)
   - 자회사/부문 데이터가 전사 데이터와 혼용되지 않는지

3. 시점 일관성 (Temporal Consistency)
   - 리프들이 같은 기준 시점을 사용하는지
   - 2024 데이터와 2025 데이터가 비교 없이 혼용되지 않는지
   - 성장률 계산의 기준년과 비교년이 명확한지

4. 정의 일관성 (Definition Consistency)
   - 핵심 용어의 정의가 리프마다 동일한지
     (범위, 포함/제외 기준이 통일되었는지)
   - 카테고리 분류 기준이 일치하는지
   - 시장 규모의 기준 (매출? 소비자 지출? 개발사 수익?)
```

### VL-2 통과 기준
- [ ] 수치 일관성 이슈 0건 (또는 사유 명시)
- [ ] 엔터티 라벨 통일 완료
- [ ] 기준 시점 통일 또는 시점 차이 명시
- [ ] 핵심 용어 정의 통일

---

## VL-3: Cross-cutting Fact Verifier

### 적용 시점
Sync Round 때 — PM이 fact-verifier를 스폰.

### 프로토콜

```
1. Division 간 교차 모순 (Cross-Division Consistency)

   Market ↔ Finance:
   - 시장 규모/성장률과 매출 전망의 정합성
   - 시장 점유율 가정의 현실성 (경쟁 강도 대비)

   Product ↔ Market:
   - 제품 설계 가정과 시장 데이터의 부합
   - 제품 설계 가정과 시장 성공 사례의 일치

   Capability ↔ Product:
   - 제품 요구사항과 보유 역량의 갭 식별
   - 기술 요구사항의 현실성

   Capability ↔ Finance:
   - 역량 확보 비용(채용, M&A, 교육)과 재무 계획의 정합성
   - 개발 기간 가정과 인력 계획의 일치

   Finance ↔ Market:
   - BEP 시점과 시장 성장 지속 가정의 정합성
   - UA 비용 가정과 시장별 CPI 데이터의 일치

   === 확장 Division 교차 패턴 (해당 Division 활성 시) ===

   People & Org ↔ Capability:
   - 인재 전략과 현재 역량 갭의 정합성
   - 채용/리스킬링 타임라인과 기술 요구사항 시점의 일치

   People & Org ↔ Finance:
   - 인력 비용(채용, 교육, 복리후생)과 재무 계획의 정합성
   - 인력 생산성 가정과 매출 전망의 현실성

   Operations ↔ Product:
   - 운영 프로세스 역량과 제품 복잡도의 정합성
   - 서비스 운영 요구사항과 현재 운영 체계의 갭

   Operations ↔ Finance:
   - 운영 비용과 매출 구조의 정합성
   - 프로세스 효율화 투자의 ROI 현실성

   Regulatory ↔ Product:
   - 규제 요구사항(인허가, 개인정보, 산업 규제)과 제품 설계의 충돌
   - 지역별 규제 차이가 글로벌 출시 전략에 미치는 영향

   Regulatory ↔ Finance:
   - 컴플라이언스 비용과 재무 계획의 정합성
   - 규제 위반 리스크의 재무적 영향 (과징금, 매출 손실)

1-B. 엔터티 라벨 Cross-Division 일치 체크 (신규)

   같은 기업/IP/제품이 Division마다 다른 라벨로 사용되면 FAIL:
   - [그룹] vs [별도] 혼용 (예: Market에서 "A그룹" → Capability에서 "A자회사")
   - 조직 내 역할 혼동 (예: 유통사 vs 제조사, 퍼블리셔 vs 개발사)
   - IP 소유권 불일치 (그룹 IP를 자체 IP로 기술)

   체크 방법:
   a. 전체 Division의 division-synthesis.yaml에서 엔터티 목록 수집
   b. 같은 엔터티가 다른 라벨/귀속으로 사용된 건 탐지
   c. 불일치 발견 시 → 해당 Division Lead에 통일 요청

   이 체크는 VL-3의 수치 교차 모순 검증과 **동시에** 실행한다.

2. 방법론 감사 (Methodology Audit)
   - 단일 소스 의존: 어떤 리프가 핵심 Claim을 1개 소스로만 뒷받침
   - 순환 인용: 소스 A가 소스 B를 인용, 소스 B가 소스 A를 인용
   - confidence 부풀림: confidence: high인데 실제 근거가 estimate만
   - 선택 편향: 가설을 지지하는 데이터만 수집, 반증 검색 미흡
   - 시점 불일치: Division 간에 다른 기준 시점 사용

3. 전략 핵심 전제 독립 재검증 (Critical Premise Re-verification)
   - cross-domain-synthesis에서 전략의 핵심 전제로 사용되는 Claim 식별
   - 사고 루프(Phase 3)에서 새로 생성/수정된 전략 Claim도 검증 대상에 포함
   - 해당 Claim의 출력 Layer 3 (Raw Source)까지 직접 드릴다운
   - 원본 소스에서 해당 수치/사실을 직접 확인
   - 확인 불가 시: "전략 핵심 전제 미검증" 플래그 → PM 에스컬레이션
```

### VL-3 Context 관리

```
fact-verifier는 Layer 1~3까지 드릴다운하므로 Context 부담이 가장 크다.
이를 관리하기 위한 배치 처리 규칙:

1. 검증 우선순위:
   strategic_impact: high + confidence: low/unverified  → 1순위 (반드시 검증)
   strategic_impact: high + confidence: medium          → 2순위 (반드시 검증)
   strategic_impact: high + confidence: high            → 3순위 (샘플 검증)
   strategic_impact: medium 이하                        → 4순위 (시간 허용 시)

2. 배치 분할:
   - Division 단위로 배치 분할 (한 번에 1개 Division의 Claim만 검증)
   - 배치당 최대 5개 Claim (Layer 3까지 드릴다운 시)
   - 배치 완료 후 결과를 파일에 기록, 다음 배치 진행

3. 실행 방법:
   - PM이 fact-verifier를 Division별로 재스폰 (활성 Division 수만큼)
   - 또는 1회 스폰 후 Division별 배치를 순차 처리
   - 각 배치에서 검증 대상 Claim ID + 파일 경로만 전달 (전체 출력 임베딩 금지)
```

### VL-3 출력

```yaml
fact_verification_report:
  timestamp: YYYY-MM-DD

  cross_division_issues:
    - id: FV-01
      type: contradiction | inconsistency | gap
      divisions: [market, finance]
      description: "시장 점유율 4% 가정이 경쟁 강도 대비 비현실적"
      severity: critical | major | minor
      resolution: "investment-analyst에게 1%/2%/4% 시나리오 추가 요청"

  methodology_flags:
    - id: FM-01
      agent: {agent-id}
      issue: "세그먼트B CAGR 15%를 단일 소스에 의존"
      recommendation: "독립 소스 2개 이상으로 교차 확인 필요"

  critical_premises_verified:
    - premise: "세그먼트B CAGR 15%+"
      used_in: "전체 전략 방향 — 세그먼트B 진입 근거"
      verification: pass | fail | partial
      detail: "검증 과정 및 결과"

  overall_assessment:
    pass_rate: "{N}/{M} 항목 통과"
    blocking_issues: [{해결 필수 항목}]
    advisory_issues: [{권고 사항}]
```

### VL-3 통과 기준
- [ ] Division 간 critical severity 이슈 0건
- [ ] 전략 핵심 전제 전부 검증 (partial 이상)
- [ ] 방법론 플래그 중 critical 0건

---

## 보고서 레벨 검증 (+α)

리서치 팩트체크와 별도로, 보고서 작성 후 수행하는 최종 검증.

### mechanical-validator
- 보고서 내 수치와 findings 파일 수치의 일치
- % 계산 정확성
- 합계/평균 산술 검증
- **자동 실행**: `python scripts/verify-facts.py {project}` → qa/fact-verification.yaml 생성
- MISMATCH 1건이라도 → report-fixer에 수정 지시
- MISSING → golden-facts에 있지만 보고서 미인용 — 의도적 생략인지 확인
- UNTRACKED → 보고서 수치가 golden-facts에 미등록 — fact-verifier에 등록 요청

### source-traceability-checker
- 보고서의 모든 [S##] 태그가 실제 소스 파일에 존재하는지
- 소스 파일에 해당 수치가 실제로 있는지
- unverified 0건 달성

### report-auditor
- 논리 완결성 (Claim → Evidence → So What 연결)
- 피라미드 구조 준수
- Executive Summary가 본문과 일치

### source-url-verifier (신규)
- **L1 접근성 검증**: source_index의 모든 URL에 HTTP HEAD 요청 → 200/301/302 = PASS, 403/404/5xx = FAIL
  - url: null (유료 보고서 등)은 자동 SKIP + 사유 확인
  - 타임아웃: 10초. 타임아웃 = WARN (일시적 장애 가능)
- **L2 관련성 검증**: PASS된 URL의 페이지 제목/메타 or 본문 요약이 해당 Claim의 Layer 1 Evidence와 의미적으로 관련 있는지 판정
  - 관련성 판정: URL 페이지 내용에서 Claim의 핵심 키워드/수치가 존재하는지 확인
  - PASS = 관련 내용 확인됨, PARTIAL = 간접 관련, FAIL = 무관한 내용
- **배치 처리**: Division별로 실행 (Context 관리). 1배치 = 1개 Division의 source_index 전체
- **실행 시점**: Phase 5 QA에서 source-traceability-checker 직후

### confidence-prominence-checker (신규)
- confidence: low/medium 수치가 Executive Summary, 슬라이드 전면에 사용되면 FAIL
- "보수에서도 X" 같은 낙관적 프레이밍이 실제 데이터의 하단과 일치하는지 검증
- confidence 라벨이 슬라이드에서 누락되면 FAIL

### executability-checker (신규)
- 실행 카드의 담당 인원 × 기간 vs 가용 리소스 비교
- 선후 의존관계 태스크의 시점 정합성 (예: DE 채용 전에 DE 필요 태스크 불가)
- 동시 태스크 수가 조직 규모 대비 현실적인지

### audience-fit-checker (신규)
- 슬라이드 수 vs 발표 시간 적합성 (1슬라이드 = 1.5~2분)
- 전문용어 첫 등장 시 정의 동반 여부
- 내부 데이터 vs 외부 추정치 비율 명시 여부
- 경영진 필수 질문 3개에 대한 답 존재 여부

---

## Tier별 검증 게이트 — 실행 시점 및 반려 기준

VL-1~3 체계의 **구체적 실행 시점과 반려 기준**을 명시한다. 각 Tier에서 출력 즉시 검증하여 오류가 Phase 5까지 누적되는 것을 방지한다.

```
현재 (사후):
  Leaf 출력 → Sub-lead 합성 → Lead 합성 → PM Sync → 보고서 → QA 검증 → 재작업

개선 (사전):
  Leaf 출력 → [VL-1 자가검증] → Sub-lead 합성 → [VL-1.5 삼각검증]
  → Lead 합성 → [VL-2 정합성] → PM Sync → [VL-3 교차검증]
  → 보고서 → [golden-facts 대조 + 기계검증] → 최종 QA
```

### 게이트 상세

| 시점 | 검증자 | 검증 내용 | 반려 기준 | 반려 시 처리 |
|------|--------|----------|----------|------------|
| Leaf 출력 직후 | Leaf 자신 (VL-1) | disconfirming 비어있으면 반려, confidence 태깅 누락 반려, source 2개 미만 반려 | 3개 중 1개라도 실패 | Leaf가 자율 반복 Round 2에서 자체 수정 |
| Sub-lead 합성 직후 | Sub-lead (VL-1.5) | Leaf 간 수치 삼각검증, 핵심 Claim 스팟체크 3건 | 삼각검증 불일치 >5% 미해소 | 해당 Leaf 재호출 또는 범위 표기 |
| Lead 합성 직후 | Lead (VL-2) | 엔터티 라벨 통일, 데이터 시점 통일, 단위 통일, 정의 일관성 | 엔터티 혼동 1건이라도 | Lead가 수정 후 재합성 |
| Sync Round | fact-verifier (VL-3) | Division 간 모순, 핵심 전제 재검증, 방법론 감사 | Critical 모순 발견 | PM에 에스컬레이션 |
| 보고서 완성 후 | qa-orchestrator | golden-facts 대조 + mechanical-validator + source-traceability + source-url-verifier | error 1건이라도 | report-fixer 수정 → 재검증 |

### VL-1 반려 체크리스트 (Leaf 자가 검증)

Leaf가 자율 반복 루프의 **각 라운드 종료 시** 반드시 실행:

```
□ disconfirming 필드가 비어있지 않은가? (검색 방법이라도 명시)
□ 모든 Claim에 confidence 태깅이 되어 있는가?
□ confidence: high인 Claim에 primary 소스 1개+ 포함하는가?
□ 최소 2개 독립 소스가 있는가?

→ 1개라도 실패: 해당 Claim을 수정하거나 confidence 하향 후 다음 라운드 진행
→ 3라운드 후에도 미충족: 상위에 반환 (confidence: low로 태깅)
```

### VL-1.5 반려 체크리스트 (Sub-lead 삼각 검증)

Sub-lead가 **Leaf 출력 수집 직후, 합성 전에** 실행:

```
□ 삼각 검증 가능한 수치에 대해 교차 실행 완료
□ 불일치 >5% 항목 전부 해소 또는 범위 표기
□ strategic_impact: high Claim 중 최소 3개 스팟체크 완료

→ 삼각 검증 불일치 미해소: 해당 Leaf에 재확인 지시 (1회)
→ 재확인 후에도 미해소: 범위 표기 + 사유 명시 후 합성 진행
```

### VL-2 반려 체크리스트 (Lead 정합성)

Lead가 **VL-1.5 완료 후, Division 합성 전에** 실행:

```
□ 수치 일관성: 부분합=전체, 비율합≤100%, 증감율-절대값 정합
□ 엔터티 라벨: [그룹]/[별도] 통일, 기업명 통일
□ 시점 일관성: 기준 연도 통일 또는 시점 차이 명시
□ 정의 일관성: 핵심 용어 정의 통일

→ 엔터티 혼동 1건이라도: Lead가 해당 수치 수정 후 재합성
→ 시점 불일치: 시점 차이 명시 주석 추가
```

---

## 팩트체크 비용 관리

모든 것을 최고 수준으로 검증하면 리서치 시간이 2~3배 늘어난다.
비용 효율을 위한 규칙:

| strategic_impact | confidence | 검증 수준 |
|-----------------|------------|----------|
| high | any | VL-1 + VL-1.5 스팟체크 + VL-3 핵심 전제 재검증 |
| medium | low/unverified | VL-1 + VL-1.5 삼각 검증 |
| medium | medium/high | VL-1 기본 |
| low | any | VL-1 기본 (스팟체크 면제) |

**원칙: 전략을 바꿀 수 있는 숫자에 검증 리소스를 집중한다.**
