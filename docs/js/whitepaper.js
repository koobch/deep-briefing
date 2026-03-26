// Deep-Briefing Whitepaper — 인터랙티브 기능
// 담당: 테마 토글, 목차 스크롤 추적, 부드러운 스크롤, 복사 버튼, 모바일 목차

document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  initScrollTracking();
  initSmoothScroll();
  initCopyButtons();
  initMobileToc();
});

/* ─── 테마 토글 ──────────────────────────────────────────────────── */
function initTheme() {
  const btn = document.getElementById('wpThemeToggle');
  const html = document.documentElement;
  const label = btn ? btn.querySelector('.wp-theme-label') : null;

  // 저장된 테마 또는 시스템 기본값 적용 (백서 기본: dark)
  const savedTheme = localStorage.getItem('wp-theme') || 'dark';
  applyTheme(savedTheme);

  if (btn) {
    btn.addEventListener('click', function () {
      const current = html.getAttribute('data-theme') || 'dark';
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('wp-theme', theme);
    if (label) {
      label.textContent = theme === 'dark' ? '라이트 모드' : '다크 모드';
    }
  }
}

/* ─── 목차 스크롤 추적 ───────────────────────────────────────────── */
function initScrollTracking() {
  const sections = document.querySelectorAll('.wp-section[id]');
  const tocLinks  = document.querySelectorAll('.wp-toc-link');
  const mobileTocLinks = document.querySelectorAll('.wp-mobile-toc-menu a');

  if (!sections.length) return;

  // IntersectionObserver: 뷰포트 상단 20% 지점 통과 시 활성화
  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          setActive(id);
        }
      });
    },
    {
      rootMargin: '-10% 0px -75% 0px',
      threshold: 0,
    }
  );

  sections.forEach(function (section) {
    observer.observe(section);
  });

  function setActive(id) {
    tocLinks.forEach(function (link) {
      const isActive = link.getAttribute('data-section') === id;
      link.classList.toggle('active', isActive);
    });
    mobileTocLinks.forEach(function (link) {
      const href = link.getAttribute('href');
      link.classList.toggle('active', href === '#' + id);
    });
  }
}

/* ─── 부드러운 스크롤 ────────────────────────────────────────────── */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      // 모바일 목차 메뉴 닫기
      closeMobileToc();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

/* ─── 복사 버튼 ──────────────────────────────────────────────────── */
function initCopyButtons() {
  document.querySelectorAll('.wp-copy-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = btn.getAttribute('data-copy-target');
      let text = '';

      if (targetId) {
        const el = document.getElementById(targetId);
        if (el) text = el.innerText || el.textContent;
      }

      if (!text) return;

      navigator.clipboard.writeText(text.trim()).then(function () {
        const original = btn.innerHTML;
        btn.classList.add('copied');
        btn.innerHTML = '<svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M2 7L5 10L11 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg> 복사됨';
        setTimeout(function () {
          btn.classList.remove('copied');
          btn.innerHTML = original;
        }, 2000);
      }).catch(function () {
        // fallback: execCommand
        const ta = document.createElement('textarea');
        ta.value = text.trim();
        ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none;';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      });
    });
  });
}

/* ─── 모바일 목차 토글 ───────────────────────────────────────────── */
function initMobileToc() {
  const btn  = document.getElementById('mobileTocBtn');
  const menu = document.getElementById('mobileTocMenu');
  if (!btn || !menu) return;

  btn.addEventListener('click', function () {
    const isOpen = btn.getAttribute('aria-expanded') === 'true';
    toggleMobileToc(!isOpen);
  });

  // 외부 클릭 시 닫기
  document.addEventListener('click', function (e) {
    if (!btn.contains(e.target) && !menu.contains(e.target)) {
      closeMobileToc();
    }
  });
}

function toggleMobileToc(open) {
  const btn  = document.getElementById('mobileTocBtn');
  const menu = document.getElementById('mobileTocMenu');
  if (!btn || !menu) return;
  btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  if (open) {
    menu.removeAttribute('hidden');
  } else {
    menu.setAttribute('hidden', '');
  }
}

function closeMobileToc() {
  toggleMobileToc(false);
}
