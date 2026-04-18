# Report Templates — v4.10 HTML Export System

> MD 정본(`report-docs.md`, `one-pager.md`) → HTML/PDF 변환 레이어.
> Phase 4-A/4-C 산출물은 그대로 MD 유지. Phase 4.7에서 변환 실행.

## 디렉토리 구조

```
core/style/report-templates/
├── shared/
│   ├── tokens.css        # 디자인 토큰 (색상/타이포/간격, McKinsey/BCG 팔레트)
│   ├── base.css          # 리셋 + 본문 타이포그래피 + 테이블/리스트/코드
│   └── print.css         # @media print 공통 규칙
├── report-docs/
│   ├── report-docs.css   # 세로형 상세 보고서 (15~30페이지)
│   └── report-docs.html.j2  # Jinja2 템플릿
├── one-pager/
│   ├── one-pager.css     # A4 1페이지 원페이퍼
│   └── one-pager.html.j2 # Jinja2 템플릿
└── README.md             # 이 문서
```

## 설계 원칙

| 원칙 | 구현 |
|------|------|
| **MD 정본** | QA 검증 대상은 MD. HTML/PDF는 뷰어용 파생물 |
| **인쇄/PDF 호환** | `@page` + `print` 미디어쿼리로 A4 규격 강제 |
| **태그 보존** | `[GF-###]`, `[S##]`은 `<mark class="rt-tag-gf">`로 변환하여 추적성 유지 |
| **외부 의존성 최소** | 시스템 폰트 fallback, 온라인 Google Fonts 의존 제거 |
| **네임스페이스** | 모든 클래스는 `.rt-` 접두사 (기존 사이트/슬라이드 CSS와 충돌 방지) |

## 디자인 토큰 요약

```css
/* 색상 */
--rt-accent: #003a70        /* 딥 네이비 (컨설팅 주색) */
--rt-accent-2: #0066cc      /* 강조 블루 */
--rt-success: #0b7d5a       /* 긍정 */
--rt-danger: #b93a30        /* 리스크 */

/* 타이포 */
--rt-font-sans: Pretendard + Inter + Noto Sans KR
--rt-fs-h1: 28px / h2: 22px / body: 13px

/* 페이지 */
--rt-page-max: 780px        /* 본문 최대 폭 */
--rt-a4-margin: 18mm        /* A4 여백 */
```

## 변환 파이프라인 (Phase 4.7)

```
Phase 4-A → reports/report-docs.md   ─┐
Phase 4-C → reports/one-pager.md     ─┤
                                      ├→ Phase 5 QA (MD 검증)
                                      │
                                      ▼ (QA PASS 시)
                             scripts/render-report-html.py
                                      │
                                      ▼
             reports/report-docs.html  (뷰어)
             reports/one-pager.html    (뷰어 + 인쇄)
                                      │
                                      ▼ (one-pager만)
                         scripts/render-onepager-pdf.py
                                      │
                                      ▼
             reports/one-pager.pdf     (이메일/인쇄 배포)
```

## 사용법

```bash
# MD → HTML (Phase 4.7)
python3 scripts/render-report-html.py {project-name}

# 원페이퍼 HTML → PDF
python3 scripts/render-onepager-pdf.py {project-name}
```

## QA와의 관계

- **MD가 SSOT**: `report-auditor`, `audience-fit-checker`, `executability-checker`, `report-fixer`는 MD만 본다
- **HTML은 파생물**: QA PASS 후에만 생성. 수정이 필요하면 MD를 수정 후 재생성
- **태그 추적**: `verify-source-traceability.py`는 MD 기반. HTML은 `<mark>` 태그로 보존만 담당

## 변경 이력

- **v4.10 (2026-04-18)** — 초기 버전. Phase 4.7 도입
