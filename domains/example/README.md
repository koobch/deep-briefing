# General Strategy 도메인 (기본 제공)

> 특정 산업에 종속되지 않는 범용 전략 분석 도메인.
> 이 도메인을 그대로 사용하거나, 복사하여 산업별 도메인을 만들 수 있습니다.

## 구조

```
domains/example/
├── README.md              ← 이 파일
├── frameworks.md          ← 범용 전략 프레임워크 (12개)
├── data-sources.md        ← 범용 데이터 소스 정의
├── benchmarks.md          ← 피어 비교/산업 벤치마크 (선택적 활성화)
└── agents/
    └── README.md          ← 에이전트 커스텀 가이드
```

## 포함된 프레임워크

- Market: Porter's Five Forces, TAM/SAM/SOM
- Product: Value Proposition Canvas, Jobs-to-be-Done
- Capability: VRIO, McKinsey 7S, **Peer Comparison Matrix**
- Finance: DCF Framework, Unit Economics, **Scenario P&L**
- Cross-cutting: 3C, SWOT

## 커스텀 도메인 생성

```bash
cp -r domains/example/ domains/{your-domain}/
```

1. `frameworks.md` — 산업에 맞는 프레임워크로 교체/추가
2. `data-sources.md` — 산업별 API, 데이터 소스 정의
3. `benchmarks.md` — 산업별 KPI, 피어 선정 기준 커스텀
4. `agents/` — (선택) 산업 특화 에이전트 정의
