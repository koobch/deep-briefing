#!/usr/bin/env node
// 슬라이드 프로토타입 → 1920x1080 스크린샷 자동 저장
// scale 변환을 일시 제거하고 원본 크기로 캡처
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
  const htmlPath = path.resolve(__dirname, 'prototype-v6.html');
  const outDir = path.resolve(__dirname, '../../.claude/plans/ppt-ref-images/proto');
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  // 1920 폭으로 설정하여 scale 변환이 1.0이 되도록
  await page.setViewport({ width: 1920, height: 10000, deviceScaleFactor: 1 });
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle0' });
  await page.evaluateHandle('document.fonts.ready');
  await new Promise(r => setTimeout(r, 1000));

  // scale을 1로 강제 + margin 제거
  await page.evaluate(() => {
    document.querySelectorAll('.slide').forEach(s => {
      s.style.transform = 'none';
      s.style.marginBottom = '24px';
    });
  });
  await new Promise(r => setTimeout(r, 300));

  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    const box = await slides[i].boundingBox();
    if (!box) continue;
    await page.screenshot({
      path: path.join(outDir, `slide-${i + 1}.png`),
      clip: { x: Math.round(box.x), y: Math.round(box.y), width: 1920, height: 1080 }
    });
    console.log(`Saved slide-${i + 1}.png (${Math.round(box.x)},${Math.round(box.y)})`);
  }

  await browser.close();
  console.log(`Done. ${slides.length} slides saved to ${outDir}`);
})();
