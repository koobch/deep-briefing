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
  const htmlPath = path.resolve(__dirname, '../core/style/prototype-slide.html');
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

      // 겹침 감지
      const overlaps = [];
      for (let i = 0; i < elements.length; i++) {
        for (let j = i + 1; j < elements.length; j++) {
          const a = elements[i], b = elements[j];
          // 부모-자식 관계 제외 (같은 영역 공유는 정상)
          if (a.text === b.text) continue;
          if (a.w < 30 || a.h < 30 || b.w < 30 || b.h < 30) continue;

          const overlapX = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x));
          const overlapY = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
          const area = overlapX * overlapY;

          // 자식 요소가 부모 안에 있는 건 정상 — 비슷한 크기일 때만 겹침으로 판단
          const sizeRatio = Math.min(a.w * a.h, b.w * b.h) / Math.max(a.w * a.h, b.w * b.h);
          if (area > 200 && sizeRatio > 0.1 && sizeRatio < 0.9) {
            overlaps.push({
              element_a: a.id,
              element_b: b.id,
              text_a: a.text.substring(0, 30),
              text_b: b.text.substring(0, 30),
              overlap_area: area,
            });
          }
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
