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
├── knowledge/             ← 학습 엔진 축적 지식 (리서치 완료 후 자동 머지)
│   ├── _meta.yaml         ← 도메인 메타데이터 (프로젝트 이력, 성숙도)
│   ├── learned-sources.yaml    ← 데이터 소스 신뢰도/접근성
│   ├── learned-patterns.yaml   ← 산업별 분석 패턴
│   ├── learned-terms.yaml      ← 용어 정의/혼동 방지
│   ├── learned-frameworks.yaml ← 프레임워크 효과성
│   └── learned-pitfalls.yaml   ← 분석 함정/실수 방지
└── agents/
    └── README.md          ← 에이전트 커스텀 가이드
```

> **학습 엔진**: 리서치 완료 후 `python scripts/merge-learnings.py {project} --domain example`을 실행하면 프로젝트에서 배운 것이 `knowledge/`에 축적됩니다. 프로젝트를 거듭할수록 시스템이 해당 도메인에서 더 똑똑해집니다.

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
