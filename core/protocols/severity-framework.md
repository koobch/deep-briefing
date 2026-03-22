# Unified Severity Framework (통합 심각도 프레임워크)

> 모든 Cross-cutting 에이전트와 QA 모듈이 공유하는 이슈 심각도 분류 체계.

## 3-Tier 심각도 정의

| 통합 등급 | 명칭 | 정의 | 처리 규칙 |
|----------|------|------|----------|
| **P1** | Critical | 전략 방향 변경 필요. 미해결 시 보고서 신뢰성 근본 훼손 | 즉시 해결 필수. 수렴 판정 시 0건이어야 PASS |
| **P2** | Major | 보강/수정 필요. 미해결 시 특정 섹션 신뢰성 저하 | Phase 내 해결 권고. QA PASS 조건에 포함 |
| **P3** | Minor | 참고/모니터링. 정밀도 개선 수준 | 가능하면 해결. QA PASS에 불포함 (Minor는 허용) |

## 에이전트별 매핑 테이블

각 에이전트는 고유 라벨을 유지하되, 출력에 `unified_severity: P1|P2|P3` 필드를 반드시 병기한다.

| 에이전트 | 고유 라벨 | → P1 (Critical) | → P2 (Major) | → P3 (Minor) |
|---------|----------|-----------------|--------------|--------------|
| **logic-prober** | severity | critical | major | minor |
| **strategic-challenger** | Severity | Critical | Major | Minor |
| **red-team** | 반론 강도 | Strong | Moderate | Weak |
| **fact-verifier** | severity | critical | major | minor |
| **escalation-protocol** | 심각도 | 치명, 중대 | 중간 | 경미 |

> **참고**: escalation-protocol은 4단계(경미/중간/중대/치명)를 사용하지만, 통합 프레임워크에서는 3-tier로 매핑한다. `치명`과 `중대`는 모두 즉각 행동이 필요하므로 P1로 통합. 로그 스키마의 영어 라벨(`moderate`=중간→P2, `major`=중대→P1, `critical`=치명→P1)도 동일 매핑을 따른다.
| **QA 모듈** | Severity | Critical | Major | Minor |

## 적용 규칙

### 1. 출력 시 필수 필드
모든 Cross-cutting 에이전트와 QA 모듈은 이슈/발견사항 출력 시 다음 필드를 포함해야 한다:
```yaml
severity: {에이전트 고유 라벨}    # 예: Strong, critical 등
unified_severity: P1              # 통합 등급
```

### 2. 수렴 판정 (insight-synthesizer)
- P1 잔존 0건 = 필수 조건
- P2 잔존 0건 = 필수 조건
- P3 잔존 = 허용 (모니터링 권고)

### 3. QA PASS 기준 (qa-orchestrator)
- P1 (Critical) 0건 + P2 (Major) 0건 = PASS
- P3 (Minor) = PASS에 불포함

### 4. 에스컬레이션 트리거
- P1 2건+ 동시 발견 → PM 즉시 보고 (전략 재검토 신호)
- P1 1건 = 해당 에이전트가 counter-proposal 제시 후 insight-synthesizer에 전달
- P2 5건+ 누적 → PM에 "품질 경고" 알림

## 참조
- 이 프레임워크는 `core/protocols/` 하위의 다른 프로토콜에서 참조된다.
- 에이전트별 상세 적용은 각 에이전트 정의(.claude/agents/*.md)에서 확인.
