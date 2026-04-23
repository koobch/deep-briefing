# Slide Export Protocol (Phase 4.8, v4.12)

> MD 정본 → 슬라이드 이미지(PNG) 변환. Phase 5 QA PASS + Phase 5.5 피드백 확정 이후 선택적 실행.
> Codex CLI의 gpt-image-2 활용 (주력) 또는 Canva MCP (대안).

## 1. 목적

- 경영진 발표/외부 공유용 슬라이드 이미지를 MD/HTML 정본과 별도 산출
- v4.9에서 제거한 자체 슬라이드 렌더러 대신 **외부 도구 위임** (gpt-image-2 / Canva)
- Phase 4.7 HTML/PDF와 **병렬** 산출물 (경쟁 아닌 보완)

## 2. 설계 원칙

| 원칙 | 구현 |
|------|------|
| **MD 정본** | `report-docs.md` + `one-pager.md`가 여전히 SSOT |
| **QA 후 실행** | Phase 5 PASS + Phase 5.5 확정 이후에만 슬라이드 생성 |
| **외부 도구 위임** | 내부 슬라이드 렌더러 미구축 (v4.9 결정 유지) |
| **선택적 실행** | Phase 4.8은 명시적 요청 시에만 동작 (기본 스킵) |
| **역호환** | 기존 4.7 파이프라인 100% 유지 |

## 3. analysis_type별 슬라이드 수 권장

| Type | 슬라이드 수 | 구조 |
|------|-----------|------|
| **decision** | 8~12장 | 표지 → BLUF → Key Findings (3~5) → Financial Snapshot → Actions → Risk → Next Steps |
| **profile** | 12~20장 | 표지 → 엔터티 개요 → Market Context → Entity Profile (4~6) → Financial → Strategy → Observations |
| **exploration** | 6~10장 | 표지 → 탐색 공간 → 후보 가설 매트릭스 → 확정/기각 판정 → 추가 리서치 권고 |
| **monitoring** | 4~6장 | 표지 → 지표 대시보드 → 변화 방향 → 이상치 → 관찰 포인트 |

## 4. 4단계 파이프라인

### Step 1: Design (내부 디자인 시스템 추출)

`core/style/report-templates/`의 CSS 토큰을 **DESIGN.md**로 변환.

- 색상 팔레트 (딥 네이비 `#003a70`, 블루 `#0066cc`, 그레이 계열)
- 타이포 스케일 (Pretendard + Inter + Noto Sans KR)
- 레이아웃 컴포넌트 (표지, 본문, 차트, KPI 박스, Pull Quote)
- Action Title + 4-Layer 피라미드 시각 규칙

**산출**: `{project}/slides/DESIGN.md`

### Step 2: Plan (슬라이드 개요 생성)

`report-docs.md` + Golden Insights + SCR 스토리라인 → **slide-outline.yaml**

```yaml
slide_outline:
  analysis_type: {type}
  total_pages: {N}
  pages:
    - page: 1
      type: cover
      title: "..."
      subtitle: "..."
    - page: 2
      type: bluf
      headline: "..."
      supporting: [...]
    # ...
```

**산출**: `{project}/slides/slide-outline.yaml`

### Step 3: Prompt (페이지별 프롬프트 생성)

outline + DESIGN.md → 페이지별 JSON 프롬프트.

```yaml
# {project}/slides/prompts/page_{N}.json
{
  "page_number": 1,
  "layout": "cover",
  "design_constraints": {
    "primary_color": "#003a70",
    "typography": "Pretendard",
    "dimensions": "1920x1080"
  },
  "content": {
    "title": "...",
    "subtitle": "...",
    "meta": {...}
  },
  "image_generation_hint": "..."
}
```

**산출**: `{project}/slides/prompts/page_*.json`

### Step 4: Generate (이미지 렌더링)

**Path A (Codex gpt-image-2 — 주력)**:
```bash
python3 scripts/render-slides-codex.py {project}
```
- 각 페이지 프롬프트를 `codex exec`로 전달
- 생성된 이미지를 `{project}/slides/page_*.png`로 저장
- 실패 시 Path B로 폴백

**Path B (Canva MCP — 대안)**:
- `mcp__claude_ai_Canva__generate-design-structured` 호출
- Brand Kit 적용 + PNG 내보내기
- Claude.ai Canva 계정 필요

**Path C (수동 실행 — 최후 수단)**:
- 프롬프트 JSON만 생성하고 사용자가 직접 OpenAI/Canva에서 실행

## 5. 실행 방법

### 기본 실행 (Codex 자동 감지)
```bash
# QA PASS + 피드백 확정 후
python3 scripts/render-slides-codex.py {project}
```

### 옵션 (render-slides-codex.py 실제 지원)
```
--pages {N}                                  # 슬라이드 수 override
--only {design|plan|prompt|generate}          # 특정 단계만 실행
--language {ko|en}                            # 슬라이드 언어
--skip-generate                               # Step 4 생략 (프롬프트만)
--project-root {path}                         # 프로젝트 루트
```
향후 확장 예정 (v4.12.3+):
- `--path {A|B|C}`: Codex/Canva/수동 선택
- `--dimensions`: 해상도 override

## 6. 산출 구조

```
{project}/slides/
├── DESIGN.md                      # Step 1
├── slide-outline.yaml             # Step 2
├── prompts/
│   ├── page_1.json                # Step 3
│   └── page_*.json
├── page_1.png                     # Step 4 (최종)
├── page_*.png
└── slides-manifest.yaml           # 생성 이력 + 인증 정보
```

## 7. 실패 처리

| 실패 | 대응 |
|------|------|
| Codex 미설치 | Path B 또는 Path C로 폴백 + 경고 |
| Codex 인증 실패 | `codex login` 안내 + Path C |
| 이미지 생성 타임아웃 | 페이지별 재시도 최대 3회 |
| QA 미PASS 상태 | Phase 4.8 중단, QA 먼저 완료 필요 |
| 분류 불명 (analysis_type=ambiguous) | 사용자 확인 요청 |

## 8. QA 연계

- **report-auditor**: 슬라이드는 MD의 파생물이므로 슬라이드 자체는 QA 대상 아님
- **그러나**: slide-outline.yaml이 생성된 경우, 본문과의 일관성은 검증 가능
  - 슬라이드의 핵심 메시지가 보고서 Executive Summary와 일치?
  - 슬라이드의 수치가 golden-facts와 일치?

이 QA는 v4.13에서 `scripts/verify-slide-consistency.py`로 자동화 예정.

## 9. v4.7 HTML과의 관계

| 산출물 | 용도 | 포맷 |
|--------|------|------|
| `reports/report-docs.html` | 브라우저 뷰어 (상세, 15~30p) | HTML + 좌측 TOC |
| `reports/one-pager.html/pdf` | 이메일 배포 (A4 1p) | HTML/PDF |
| `reports/sources.html` | 출처 인덱스 | HTML + 딥링크 |
| `slides/page_*.png` (Phase 4.8) | 발표·외부 공유 | PNG 시퀀스 |

**사용자 선택**: 보고서 단독 / 원페이퍼 단독 / 슬라이드 단독 / 전체. Phase 4.7과 4.8은 독립 실행.

## 10. 참조

- `core/style/report-templates/` — DESIGN.md 원천
- `.claude/agents/report-writer.md` — Step 0-pre analysis_type 분기
- `scripts/render-slides-codex.py` — Path A 구현
- `core/protocols/html-export-protocol.md` — Phase 4.7 (별도 산출물)

## 11. 변경 이력

- **v4.12 (2026-04-23)**: Phase 4.8 신규. v4.9에서 제거한 슬라이드 시스템을 외부 도구 위임 형태로 재도입.
