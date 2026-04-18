# HTML Export Protocol (Phase 4.7)

> MD 정본 → HTML/PDF 뷰어 변환 프로토콜.
> Phase 5 QA PASS + Phase 5.5 사용자 확정 이후 실행.
> MD는 Single Source of Truth, HTML/PDF는 파생물.

## 1. 목적

- 경영진/실무진이 브라우저·이메일·인쇄로 바로 소비할 수 있는 산출물 제공
- 출처 추적성(`[GF-###]`, `[S##]`) 유지하되 원페이퍼에서는 시각적 제거
- 기존 MD 기반 QA 파이프라인을 변경하지 않고 부가 레이어로 확장

## 2. 설계 원칙

| 원칙 | 구현 방식 |
|------|----------|
| **MD 정본** | `report-docs.md`, `one-pager.md`가 SSOT. HTML은 매 실행마다 재생성 |
| **QA는 MD만 본다** | audience-fit-checker, report-auditor, executability-checker, report-fixer는 MD만 읽고 수정 |
| **HTML은 QA 후 생성** | Phase 5 PASS 이후에만 render-report-html.py 실행 |
| **출처 분리** | 태그는 `sources.html`의 딥링크로 이동 가능한 별도 페이지 |
| **인쇄/이메일 호환** | A4 1페이지 강제 (one-pager), 시스템 폰트 fallback, 외부 네트워크 의존 0 |

## 3. 실행 순서

```
Phase 4-A → reports/report-docs.md   ┐
Phase 4-C → reports/one-pager.md     ┤
Phase 4.5 → reports/source-registry.csv
                                     │
Phase 5   → qa/qa-report.md (PASS/FAIL)
Phase 5.5 → 사용자 피드백 반영 (MD 수정)
                                     │
                                     ▼
Phase 4.7 (본 프로토콜)
  1. render-report-html.py 실행
     → report-docs.html  (본문 태그는 sources.html 딥링크)
     → one-pager.html    (태그 자동 제거, A4 1p)
     → sources.html      (Golden Facts + Source Index 통합 인덱스)

  2. render-onepager-pdf.py 실행 (Chrome headless)
     → one-pager.pdf     (경영진 배포용, A4 1p)

  3. PM이 산출물 경로를 사용자에게 제시
```

**중요**: QA가 MD를 수정할 때마다 HTML은 폐기 후 재생성. HTML을 직접 수정 금지.

## 4. 산출물 상세

### 4.1 `reports/report-docs.html`

- 좌측 고정 TOC 사이드바 + 본문
- 표지 (제목, 프로젝트, 기밀등급, 배포 범위)
- Trust Badge (QA PASS, Golden Facts N건, Sources N건, Red Team 통과)
- 본문은 MD → HTML 변환 (테이블, 인용, 코드블록, blockquote 전체 보존)
- `[GF-###]`, `[S##]` 태그는 `sources.html`의 앵커로 이동하는 클릭 가능 링크

### 4.2 `reports/one-pager.html` + `reports/one-pager.pdf`

- A4 1페이지 고정 (CSS `@page` + 고정 min-height)
- **태그 자동 제거**: `[GF-###]`, `[S##]`이 렌더링에서 사라지고 본문 흐름이 자연스러워짐
- 출처 확인은 `sources.html` 참조 (별도 경로)
- PDF는 Chrome headless 기반, 없으면 weasyprint fallback
- 섹션 구조: Header → BLUF → Key Findings → Financial Snapshot → Recommended Actions → Risk Alert → Footer

### 4.3 `reports/sources.html`

- 2개 탭: Golden Facts (from `findings/golden-facts.yaml`) / Source Index (from `findings/**/*.yaml`의 `source_index` 집계)
- 각 항목 고유 앵커 (`#gf-001`, `#s-01`) → report-docs.html의 링크가 여기로 이동
- 검색 + 필터 (클라이언트 사이드 JS, 외부 의존성 0)
- URL 클릭 시 원 소스 새 창 오픈

## 5. 변환 옵션

```bash
# 기본 (권장)
python3 scripts/render-report-html.py {project}

# 상세 옵션
--only {docs|one-pager|sources}        # 특정 보고서만
--docs-tags {link|mark|strip}          # report-docs의 태그 처리 (기본: link)
--one-pager-tags {link|mark|strip}     # one-pager의 태그 처리 (기본: strip)

# PDF 변환
python3 scripts/render-onepager-pdf.py {project}
--target {one-pager|docs|both}         # 변환 대상 (기본: one-pager만)
```

### 태그 처리 모드

| 모드 | 효과 | 용도 |
|------|------|------|
| `link` | `<a href="sources.html#gf-001">[GF-001]</a>` | 기본 — 출처 추적 가능 |
| `mark` | `<mark class="rt-tag-gf">[GF-001]</mark>` | 하이라이트만, 클릭 불가 |
| `strip` | 태그 제거 + 인접 공백 정리 | 경영진 원페이퍼, 인쇄용 |

## 6. 출처 열 자동 제거 (원페이퍼 한정)

원페이퍼는 공간이 제한되므로 Financial Snapshot 표에서 출처 열을 자동 감지·제거한다:
- 헤더에 `출처`, `Source`, `소스`, `src`, `ref`, `출전` 중 하나가 포함된 열 → 제거
- MD 정본에는 영향 없음 (렌더 시점 후처리)

## 7. QA 에이전트와의 관계

| 에이전트 | 입력 | 출력 | HTML 관련 |
|---------|------|------|----------|
| `audience-fit-checker` | MD | QA Report | 영향 없음 (MD만 검증) |
| `report-auditor` | MD | QA Report | 영향 없음 |
| `executability-checker` | MD | QA Report | 영향 없음 |
| `report-fixer` | MD | 수정된 MD | HTML은 폐기 후 재생성 |
| `fact-verifier` | MD + YAML | golden-facts.yaml 수정 | sources.html 입력 데이터 갱신 |

**핵심**: QA 루프는 기존 그대로. Phase 4.7은 루프 밖에서 한 번만 실행.

## 8. 실패 처리

| 실패 | 대응 |
|------|------|
| markdown/jinja2 미설치 | `pip install -r requirements.txt` 안내 후 중단 |
| MD 파일 없음 | 해당 보고서만 SKIP (다른 보고서는 진행) |
| Chrome/Chromium 미설치 | weasyprint fallback 시도, 둘 다 없으면 PDF만 생략하고 HTML은 유지 |
| golden-facts.yaml 없음 | sources.html 생성 생략 (Golden Facts + Source Index 모두 비어 있을 때만) |

## 9. 재실행 조건

아래 중 하나라도 변경되면 HTML 재생성:
- `reports/report-docs.md`
- `reports/one-pager.md`
- `findings/golden-facts.yaml`
- `findings/**/*.yaml` (source_index 포함)
- `qa/qa-report.md` (Trust Badge 갱신용)

PM은 Phase 5.5 피드백 루프 종료 시점에 **마지막 1회** 실행. 중간 실행은 선택 사항.

## 10. 변경 이력

- **v4.10 (2026-04-18)**: Phase 4.7 프로토콜 도입. 슬라이드 시스템(v4.9 제거) 대체 레이어.
