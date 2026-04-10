/* ═══════════════════════════════════════════════════════════
   Deep-Briefing Slide Fit v2
   렌더 후 overflow 감지 + 자동 축소
   외부 의존성 0 · 전역 객체: SlideFit
   ═══════════════════════════════════════════════════════════ */

const SlideFit = (() => {
  'use strict';

  /* ─── overflow 판정 ────────────────────────────────────── */
  const isOverflowing = (el) => el.scrollHeight > el.clientHeight + 1;

  /* ─── 메인 체크 함수 ───────────────────────────────────── */
  const check = () => {
    const slides = document.querySelectorAll('.slide');
    const total = slides.length;
    let compact = 0;
    let overflow = 0;

    slides.forEach((slide, i) => {
      const body = slide.querySelector('.slot-body');
      if (!body) return;

      // 1차: overflow 확인
      if (!isOverflowing(body)) return;

      // 2차: compact 클래스 추가 (CSS에서 폰트 축소)
      slide.classList.add('compact');
      compact++;

      // 3차: compact 후에도 넘치면 경고
      // reflow 보장을 위해 offsetHeight 참조
      void body.offsetHeight;
      if (isOverflowing(body)) {
        overflow++;
        console.warn(`[slide-fit] Slide ${i + 1}: overflow after compact`);
      }
    });

    console.log(`[slide-fit] ${total} slides, ${compact} compacted, ${overflow} overflows`);

    return { total, compact, overflow };
  };

  return { check };
})();

/* Node.js 환경 호환 */
if (typeof module !== 'undefined' && module.exports) module.exports = SlideFit;
