/**
 * 슬라이드 빈 공간 자동 탐지 스크립트
 * 사용법: node visual-checker.js [html파일경로]
 *
 * 각 슬라이드의 slot-body 내부를 재귀 스캔하여
 * 60px 이상 연속 빈 공간을 탐지하고 보고한다.
 */
const puppeteer = require('puppeteer');
const path = require('path');

const MAX_GAP = 50; // 최대 허용 빈 공간 (px) — 콘텐츠 간 gap 기준
const MIN_RATIO = 82; // 최소 활용률 (%) — 차트/그리드 유형은 83~85%가 정상
const TOP_EXEMPT = 50; // 헤더→본문 간격(44px)은 면제
const EXEMPT = [1, 3, 9, 10, 21]; // 0-indexed: Agenda(1), Agenda2(3), CoverEP(9), CoverGlobal(10), BackCover(21)

const NAMES = [
  'Exec','Agenda','Insight+Chart','BigNum','Ranked',
  'Table','Process','Before/After','CaseStudy','CoverEP',
  'CoverGlobal','Intro','MultiCol','DualChart','Divergent',
  'Split','Heatmap','Scatter','Comparison','Matrix',
  'Framework','BackCover'
];

async function checkSlide(page, slideIdx) {
  return await page.evaluate((idx, maxGap) => {
    const slide = document.querySelectorAll('section.slide')[idx];
    if (!slide) return { pass: true, gaps: [], ratio: 0 };

    const body = slide.querySelector('.slot-body') ||
                 slide.querySelector('[class*="layout-"]');
    if (!body) return { pass: true, gaps: [], ratio: 0 };

    const bodyRect = body.getBoundingClientRect();

    // 모든 자손 요소의 bounding box 수집 (깊이 3까지)
    function collectBoxes(el, depth) {
      if (depth > 3) return [];
      const boxes = [];
      for (const child of el.children) {
        const r = child.getBoundingClientRect();
        if (r.height > 0 && r.width > 10) {
          boxes.push({ top: r.top, bottom: r.bottom, tag: child.tagName, cls: child.className.substring(0, 30) });
        }
        // 재귀 — 그리드/플렉스 컨테이너 내부도 검사
        if (child.children.length > 0 && child.children.length < 20) {
          boxes.push(...collectBoxes(child, depth + 1));
        }
      }
      return boxes;
    }

    const allBoxes = collectBoxes(body, 0);
    if (allBoxes.length === 0) return { pass: true, gaps: [], ratio: 0 };

    // y좌표로 정렬하고 연속 빈 공간 계산
    allBoxes.sort((a, b) => a.top - b.top);

    // 커버된 y범위를 병합
    const merged = [];
    for (const box of allBoxes) {
      if (merged.length === 0) {
        merged.push({ top: box.top, bottom: box.bottom });
      } else {
        const last = merged[merged.length - 1];
        if (box.top <= last.bottom + 2) {
          last.bottom = Math.max(last.bottom, box.bottom);
        } else {
          merged.push({ top: box.top, bottom: box.bottom });
        }
      }
    }

    // 병합된 영역 사이의 gap 계산
    const gaps = [];
    // body 상단 ~ 첫 요소 (헤더→본문 간격은 면제)
    const topGap = merged.length > 0 ? merged[0].top - bodyRect.top : 0;
    if (topGap > (typeof TOP_EXEMPT !== 'undefined' ? TOP_EXEMPT : maxGap)) {
      gaps.push({ from: Math.round(bodyRect.top), to: Math.round(merged[0].top), size: Math.round(topGap), where: 'top' });
    }
    // 요소 간 gap
    for (let i = 0; i < merged.length - 1; i++) {
      const gap = merged[i + 1].top - merged[i].bottom;
      if (gap > maxGap) {
        gaps.push({ from: Math.round(merged[i].bottom), to: Math.round(merged[i + 1].top), size: Math.round(gap), where: `between-${i}-${i+1}` });
      }
    }
    // 마지막 요소 ~ body 하단
    if (merged.length > 0 && bodyRect.bottom - merged[merged.length - 1].bottom > maxGap) {
      gaps.push({ from: Math.round(merged[merged.length - 1].bottom), to: Math.round(bodyRect.bottom), size: Math.round(bodyRect.bottom - merged[merged.length - 1].bottom), where: 'bottom' });
    }

    // 활용률 계산
    const contentH = merged.reduce((sum, m) => sum + (m.bottom - m.top), 0);
    const ratio = Math.round(contentH / bodyRect.height * 100);

    return {
      pass: gaps.length === 0,
      gaps: gaps,
      ratio: ratio,
      bodyH: Math.round(bodyRect.height),
      contentH: Math.round(contentH),
      mergedCount: merged.length
    };
  }, slideIdx, MAX_GAP);
}

(async () => {
  const htmlPath = process.argv[2] || path.resolve(__dirname, 'prototype-v6.html');

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.goto('file://' + path.resolve(htmlPath), { waitUntil: 'networkidle0', timeout: 15000 });

  const slides = await page.$$('section.slide');
  let totalFails = 0;
  const failList = [];

  console.log(`\n═══ 슬라이드 빈 공간 자동 검증 (MAX_GAP=${MAX_GAP}px) ═══\n`);

  for (let i = 0; i < slides.length; i++) {
    const isExempt = EXEMPT.includes(i);
    if (isExempt) {
      console.log(`[${String(i+1).padStart(2)}] ${NAMES[i].padEnd(14)} EXEMPT`);
      continue;
    }

    const result = await checkSlide(page, i);
    const ratioFail = result.ratio < MIN_RATIO;
    const status = (result.pass && !ratioFail) ? 'PASS' : 'FAIL';

    if (!result.pass || ratioFail) {
      totalFails++;
      failList.push({ idx: i, name: NAMES[i], ...result });
    }

    console.log(`[${String(i+1).padStart(2)}] ${NAMES[i].padEnd(14)} ${status} ratio=${result.ratio}% ${result.gaps.length > 0 ? `gaps=${result.gaps.map(g => `${g.where}:${g.size}px`).join(', ')}` : ''}`);
  }

  console.log(`\n═══ 결과: ${totalFails} FAIL / ${slides.length - EXEMPT.length} 검사 ═══\n`);

  if (failList.length > 0) {
    console.log('FAIL 상세:');
    for (const f of failList) {
      console.log(`  ${f.name}: ${f.gaps.map(g => `${g.where}에 ${g.size}px 빈 공간`).join(', ')}`);
    }
  }

  // JSON 결과 출력 (파이프라인용)
  console.log('\n__RESULT_JSON__');
  console.log(JSON.stringify({ totalFails, fails: failList.map(f => ({ name: f.name, idx: f.idx, gaps: f.gaps, ratio: f.ratio })) }));

  await browser.close();
  process.exit(totalFails > 0 ? 1 : 0);
})();
