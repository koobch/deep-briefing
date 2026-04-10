/* ===================================================================
   Deep-Briefing 대시보드 — 인터랙션
   =================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  initTabs();
  initCountUp();
  initTimeline();
  initDivisionCards();
  initCopyButtons();
});

/* ─── 테마 토글 ──────────────────────────────────────────────── */
function initTheme() {
  const btn = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('db-theme') || 'dark';
  applyTheme(savedTheme);

  btn.addEventListener('click', function () {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('db-theme', next);
  });

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    btn.textContent = theme === 'dark' ? '☀' : '◑';
    btn.setAttribute('aria-label', theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환');
  }
}

/* ─── 탭 내비게이션 ──────────────────────────────────────────── */
function initTabs() {
  const tabBtns  = document.querySelectorAll('.tab-btn');
  const sections = document.querySelectorAll('.section[data-tab]');

  // URL 해시로 초기 탭 결정
  const hashTab = location.hash.replace('#', '') || tabBtns[0]?.dataset.tab;
  activateTab(hashTab);

  tabBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      activateTab(this.dataset.tab);
      history.replaceState(null, '', '#' + this.dataset.tab);
    });
  });

  function activateTab(tabId) {
    tabBtns.forEach(b => b.classList.toggle('active', b.dataset.tab === tabId));
    sections.forEach(s => s.classList.toggle('active', s.dataset.tab === tabId));

  }
}

/* ─── 카운트업 애니메이션 ────────────────────────────────────── */
function initCountUp() {
  const cards = document.querySelectorAll('.metric-card[data-target]');

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const card   = entry.target;
        const target = parseInt(card.dataset.target, 10);
        const el     = card.querySelector('.metric-value');
        animateCount(el, target);
        observer.unobserve(card);
      }
    });
  }, { threshold: 0.4 });

  cards.forEach(c => observer.observe(c));

  function animateCount(el, target) {
    const duration = 1200;
    const start    = performance.now();
    const ease = t => 1 - Math.pow(1 - t, 3); // cubic ease-out

    function frame(now) {
      const progress = Math.min((now - start) / duration, 1);
      el.textContent = Math.round(ease(progress) * target);
      if (progress < 1) requestAnimationFrame(frame);
      else el.textContent = target;
    }
    requestAnimationFrame(frame);
  }
}


/* ─── Phase 타임라인 ─────────────────────────────────────────── */
const PHASES = [
  {
    id:    'phase-0',
    num:   'P0',
    label: 'Discovery',
    title: 'Phase 0 — Discovery',
    desc:  '클라이언트 브리프 분석 및 프로젝트 초기화. 적응형 2-Pass 사용자 인터뷰 (Pass 1 기본 질문 → Pass 2 도메인 심층). 주제 파악, 범위 설정, 초기 컨텍스트 구축. `init-project.sh`로 디렉토리 스캐폴딩.',
    agents: ['research-pm', 'data-preprocessor'],
  },
  {
    id:    'phase-0-5',
    num:   'P0.5',
    label: '가설',
    title: 'Phase 0.5 — 가설 수립',
    desc:  '활성 Division 30분 Quick Scan → 가설 3~5개 도출 → 사용자 정렬 → Division Briefs에 반영. Phase 1이 가설 검증/반증 중심으로 구동.',
    agents: ['research-pm', 'market-lead', 'product-lead', 'capability-lead', 'finance-lead'],
  },
  {
    id:    'phase-1',
    num:   'P1',
    label: '병렬 리서치',
    title: 'Phase 1 — 병렬 리서치',
    desc:  'N-Division 병렬 실행. tmux 모드 A: `spawn-leads.sh`로 완전 병렬. 모드 B: Agent tool로 2개씩 순차-병렬. Leaf Sub-agent가 실질 데이터 수집.',
    agents: ['market-lead', 'product-lead', 'capability-lead', 'finance-lead', 'people-org-lead', 'operations-lead', 'regulatory-lead'],
  },
  {
    id:    'sync-1',
    num:   'S1',
    label: 'Sync 1',
    title: 'Sync 1 — 1차 동기화',
    desc:  'Division 간 findings 교차 확인. 초기 tension 식별. Golden Facts 업데이트. 맥락 체크인: 사용자 경험 기반 피드백 수집. `sync/sync-1.md` 생성.',
    agents: ['research-pm', 'fact-verifier', 'cross-domain-synthesizer'],
  },
  {
    id:    'phase-2',
    num:   'P2',
    label: '심화',
    title: 'Phase 2 — 심화 분석',
    desc:  'Phase 1 결과 기반 심화 리서치. 데이터 갭 보완, 특정 가설 집중 검증. `send-phase2.sh`로 활성 Lead CLI에 자동 전송.',
    agents: ['market-lead', 'product-lead', 'capability-lead', 'finance-lead'],
  },
  {
    id:    'sync-2',
    num:   'S2',
    label: 'Sync 2',
    title: 'Sync 2 — 교차 정합 + 통합',
    desc:  'Division 간 교차 정합 + 통합. 교차 검증 VL-3 실행. 맥락 체크인: 사용자 경험 기반 피드백 수집. insight-synthesizer가 통합 관점 초안 작성.',
    agents: ['fact-verifier', 'cross-domain-synthesizer', 'insight-synthesizer'],
  },
  {
    id:    'phase-3',
    num:   'P3',
    label: '사고 루프',
    title: 'Phase 3 — 사고 루프',
    desc:  'logic-prober: Why Chain 수직 검증. strategic-challenger: 5-레인 수평 도전. red-team: 적대적 반론 + 역 시나리오. insight-synthesizer: 도전·반론 통합 → 전략 보강.',
    agents: ['logic-prober', 'strategic-challenger', 'red-team', 'insight-synthesizer'],
  },
  {
    id:    'phase-3-7',
    num:   'P3.7',
    label: '외부 리뷰',
    title: 'Phase 3.7 — External Review',
    desc:  '약점 체크리스트(5항목) + 자기비판 + 외부모델 리뷰. external-reviewer 에이전트 스폰. 사고 루프 결과의 맹점을 독립적으로 검증.',
    agents: ['external-reviewer', 'insight-synthesizer'],
  },
  {
    id:    'phase-4a',
    num:   'P4-A',
    label: '세로 보고서',
    title: 'Phase 4-A — 세로형 보고서',
    desc:  'SCR 스토리라인 기반 세로형 보고서(report-docs.md) 작성. Action Title 섹션 구성. Golden Insights 5개 도출.',
    agents: ['report-writer'],
  },
  {
    id:    'phase-4b',
    num:   'P4-B',
    label: '슬라이드',
    title: 'Phase 4-B — 슬라이드 (선택적)',
    desc:  'report-docs.md를 core/style/ 22개 슬라이드 유형으로 변환. slide-deck.html + slide-outline.yaml + slide-meta.yaml 생성. Client Brief에서 슬라이드 요청 시에만 활성화.',
    agents: ['slide-writer'],
  },
  {
    id:    'phase-4c',
    num:   'P4-C',
    label: '원페이퍼',
    title: 'Phase 4-C — 경영진 원페이퍼 (선택적)',
    desc:  'report-docs.md를 1~2페이지 BLUF 구조로 압축. Key Findings 3개 + Recommended Actions + Risk Alert. 독립적 의사결정 문서.',
    agents: ['brief-writer'],
  },
  {
    id:    'phase-4-5',
    num:   'P4.5',
    label: '출처 레지스트리',
    title: 'Phase 4.5 — 출처 레지스트리',
    desc:  '통합 출처 추적. generate-source-registry.py로 source_index + golden-facts + [S##]/[GF-###] 태그를 통합하여 14컬럼 source-registry.csv 생성.',
    agents: ['research-pm'],
  },
  {
    id:    'phase-5',
    num:   'P5',
    label: 'QA',
    title: 'Phase 5 — QA 자동 루프',
    desc:  'audience-fit-checker(6개), executability-checker(5개), report-auditor 게이트. report-fixer 자동 스폰 → 재검증 → 최대 3회 반복. Critical/Major 0건 = PASS.',
    agents: ['qa-orchestrator', 'audience-fit-checker', 'executability-checker', 'report-auditor', 'report-fixer'],
  },
  {
    id:    'phase-5-5',
    num:   'P5.5',
    label: '피드백',
    title: 'Phase 5.5 — 피드백 루프',
    desc:  '사용자 피드백 L0~L3 분류(오타 → 구조 변경) + Cascade 영향 분석 → 영향 범위 판정(minimal / division / cross_division) → 부분 재실행. 세부 수정은 최소 범위만 재실행.',
    agents: ['research-pm', 'report-fixer'],
  },
];

function initTimeline() {
  const container = document.getElementById('timeline-container');
  const detail    = document.getElementById('phase-detail');
  if (!container) return;

  // 타임라인 렌더
  container.innerHTML = PHASES.map((p, i) => `
    <div class="timeline-item" data-phase="${p.id}" tabindex="0" role="button" aria-label="${p.title}">
      <div class="timeline-node">${p.num}</div>
      <div class="timeline-label">${p.label}</div>
      ${i < PHASES.length - 1 ? '<div class="timeline-connector"></div>' : ''}
    </div>
  `).join('');

  // 첫 Phase 기본 선택
  selectPhase(PHASES[0].id);

  container.addEventListener('click', e => {
    const item = e.target.closest('.timeline-item');
    if (item) selectPhase(item.dataset.phase);
  });

  container.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      const item = e.target.closest('.timeline-item');
      if (item) { e.preventDefault(); selectPhase(item.dataset.phase); }
    }
  });

  function selectPhase(phaseId) {
    const phase = PHASES.find(p => p.id === phaseId);
    if (!phase) return;

    container.querySelectorAll('.timeline-item').forEach(el => {
      el.classList.toggle('selected', el.dataset.phase === phaseId);
    });

    detail.innerHTML = `
      <div class="phase-detail-header">
        <span class="phase-detail-num">${phase.num}</span>
        <span class="phase-detail-title">${phase.title}</span>
      </div>
      <p class="phase-detail-desc">${phase.desc}</p>
      <div class="phase-agents">
        ${phase.agents.map(a => `<span class="phase-agent-tag">${a}</span>`).join('')}
      </div>
    `;
    detail.classList.add('visible');
  }
}

/* ─── Division 카드 슬라이드다운 ─────────────────────────────── */
function initDivisionCards() {
  document.querySelectorAll('.division-card').forEach(card => {
    card.addEventListener('click', function () {
      const isOpen = this.classList.contains('open');
      // 동일 그리드 내 다른 카드는 열어둠 (멀티 열기 허용)
      this.classList.toggle('open', !isOpen);
      const arrow = this.querySelector('.division-arrow');
      if (arrow) arrow.setAttribute('aria-expanded', String(!isOpen));
    });

    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        card.click();
      }
    });
  });
}

/* ─── 복사 버튼 ──────────────────────────────────────────────── */
function initCopyButtons() {
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const block = this.closest('.command-block');
      const code  = block?.querySelector('.command-code');
      if (!code) return;

      // HTML 태그 제거하고 순수 텍스트만 복사
      const text = code.innerText || code.textContent;
      navigator.clipboard.writeText(text.trim()).then(() => {
        this.textContent = '✓ 복사됨';
        this.classList.add('copied');
        setTimeout(() => {
          this.textContent = '복사';
          this.classList.remove('copied');
        }, 2000);
      }).catch(() => {
        // 폴백: execCommand
        const ta = document.createElement('textarea');
        ta.value = text.trim();
        ta.style.cssText = 'position:fixed;opacity:0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        this.textContent = '✓ 복사됨';
        this.classList.add('copied');
        setTimeout(() => {
          this.textContent = '복사';
          this.classList.remove('copied');
        }, 2000);
      });
    });
  });
}
