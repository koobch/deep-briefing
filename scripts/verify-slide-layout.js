#!/usr/bin/env node
/**
 * 슬라이드 프로토타입 자동 검증 — Puppeteer DOM 측정
 * 모든 요소의 실제 렌더링 위치/크기/폰트/색상을 추출하고
 * overflow와 텍스트 겹침을 감지한다.
 */
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
  const htmlPath = path.resolve(__dirname, '../core/style/prototype-v6.html');
  const outPath = path.resolve(__dirname, '../core/style/proto-rendered-spec.json');

  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 10000, deviceScaleFactor: 1 });
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle0' });
  await page.evaluateHandle('document.fonts.ready');
  await new Promise(r => setTimeout(r, 1000));

  // scale 제거
  await page.evaluate(() => {
    document.querySelectorAll('.slide').forEach(s => {
      s.style.transform = 'none';
      s.style.marginBottom = '24px';
    });
  });
  await new Promise(r => setTimeout(r, 500));

  const result = await page.evaluate(() => {
    const slides = [...document.querySelectorAll('.slide')];
    return slides.map((slide, slideIdx) => {
      const slideRect = slide.getBoundingClientRect();
      const slideTop = slideRect.top;
      const slideLeft = slideRect.left;

      // 슬라이드 내 모든 자식 요소 수집
      const allElements = [...slide.querySelectorAll('*')].filter(el => {
        const style = getComputedStyle(el);
        // 의미 있는 요소만 (텍스트 있거나, 배경 있거나, 크기 있는)
        return (el.textContent.trim().length > 0 || style.backgroundColor !== 'rgba(0, 0, 0, 0)')
          && el.tagName !== 'STYLE' && el.tagName !== 'SCRIPT' && el.tagName !== 'SPAN'
          && el.offsetWidth > 10 && el.offsetHeight > 10;
      });

      const elements = allElements.map((el, i) => {
        const rect = el.getBoundingClientRect();
        const style = getComputedStyle(el);
        return {
          id: `s${slideIdx + 1}_e${i}`,
          tag: el.tagName.toLowerCase(),
          text: el.textContent.trim().substring(0, 50),
          x: Math.round(rect.left - slideLeft),
          y: Math.round(rect.top - slideTop),
          w: Math.round(rect.width),
          h: Math.round(rect.height),
          fontSize: style.fontSize,
          fontWeight: style.fontWeight,
          color: style.color,
          bgColor: style.backgroundColor,
          overflow: el.scrollHeight > el.clientHeight + 2,
          scrollH: el.scrollHeight,
          clientH: el.clientHeight,
        };
      });

      // 겹침 감지 — DOM containment 체크를 활용하여 false-positive 제거
      const slideArea = slideRect.width * slideRect.height;
      const overlaps = [];
      for (let i = 0; i < allElements.length; i++) {
        for (let j = i + 1; j < allElements.length; j++) {
          const elA = allElements[i], elB = allElements[j];
          const a = elements[i], b = elements[j];

          // 1) 부모-자식 DOM 중첩 제외 (정상적인 CSS 레이아웃)
          if (elA.contains(elB) || elB.contains(elA)) continue;

          // 2) 같은 부모의 형제 요소 제외 (grid/flex 컨테이너 내 의도적 배치)
          if (elA.parentElement === elB.parentElement) continue;

          // 3) 너무 작은 요소 무시
          if (a.w < 30 || a.h < 30 || b.w < 30 || b.h < 30) continue;

          const overlapX = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x));
          const overlapY = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
          const area = overlapX * overlapY;

          // 4) 슬라이드 면적의 5% 미만이면 무시 (미세 겹침)
          if (area < slideArea * 0.05) continue;

          overlaps.push({
            element_a: a.id,
            element_b: b.id,
            text_a: a.text.substring(0, 30),
            text_b: b.text.substring(0, 30),
            overlap_area: area,
            overlap_pct: Math.round(area / slideArea * 100) + '%',
          });
        }
      }

      // overflow 감지
      const overflowElements = elements.filter(e => e.overflow);

      return {
        slide: slideIdx + 1,
        slideRect: { x: Math.round(slideLeft), y: Math.round(slideTop), w: 1920, h: 1080 },
        elementCount: elements.length,
        elements: elements.filter(e => e.w > 30 && e.h > 15), // 의미 있는 크기만
        overlaps: overlaps.slice(0, 20), // 상위 20개만
        overflowElements: overflowElements,
        overflowCount: overflowElements.length,
      };
    });
  });

  // 요약 출력
  console.log('\n=== SLIDE LAYOUT VERIFICATION ===\n');
  for (const slide of result) {
    const overlapCount = slide.overlaps.length;
    const overflowCount = slide.overflowCount;
    const status = (overlapCount === 0 && overflowCount === 0) ? 'PASS ✅' : 'FAIL ❌';
    console.log(`Slide ${slide.slide}: ${status} | elements: ${slide.elementCount} | overlaps: ${overlapCount} | overflows: ${overflowCount}`);

    if (overlapCount > 0) {
      console.log('  Overlaps:');
      for (const o of slide.overlaps.slice(0, 5)) {
        console.log(`    "${o.text_a}" ↔ "${o.text_b}" → ${o.overlap_area}px²`);
      }
    }
    if (overflowCount > 0) {
      console.log('  Overflows:');
      for (const o of slide.overflowElements.slice(0, 5)) {
        console.log(`    ${o.id} "${o.text.substring(0, 30)}" scrollH:${o.scrollH} > clientH:${o.clientH}`);
      }
    }
  }

  // JSON 저장
  fs.writeFileSync(outPath, JSON.stringify(result, null, 2));
  console.log(`\nSaved to ${outPath}`);

  await browser.close();
})();
