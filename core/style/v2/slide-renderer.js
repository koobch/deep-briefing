/* ═══════════════════════════════════════════════════════════
   Deep-Briefing Slide Renderer v2
   JSON AST → DOM 생성
   외부 의존성 0 · 전역 객체: SlideRenderer
   ═══════════════════════════════════════════════════════════ */

const SlideRenderer = (() => {
  'use strict';

  /* ─── 간이 Markdown → HTML 변환 ────────────────────────── */
  const mdToHtml = (text) => {
    const lines = text.split('\n');
    const out = [];
    let inList = false;

    const flushList = () => { if (inList) { out.push('</ul>'); inList = false; } };

    const inlineFormat = (s) =>
      s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    for (const line of lines) {
      // 제목 h3
      const h3 = line.match(/^###\s+(.+)$/);
      if (h3) { flushList(); out.push(`<h3>${inlineFormat(h3[1])}</h3>`); continue; }

      // 불릿 리스트
      const li = line.match(/^-\s+(.+)$/);
      if (li) {
        if (!inList) { out.push('<ul>'); inList = true; }
        out.push(`<li>${inlineFormat(li[1])}</li>`);
        continue;
      }
      flushList();

      // 테이블 행
      if (/^\|.+\|$/.test(line)) {
        // 구분선 건너뛰기
        if (/^\|[\s-|]+\|$/.test(line)) continue;
        const cells = line.split('|').slice(1, -1).map(c => c.trim());
        out.push('<tr>' + cells.map(c => `<td>${inlineFormat(c)}</td>`).join('') + '</tr>');
        continue;
      }

      // 빈 줄 무시
      if (!line.trim()) continue;

      // 일반 텍스트
      out.push(`<p>${inlineFormat(line)}</p>`);
    }
    flushList();
    return out.join('\n');
  };

  /* ─── 요소 생성 헬퍼 ───────────────────────────────────── */
  const el = (tag, cls, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  };

  /* ─── 블록 렌더러 ──────────────────────────────────────── */
  const renderBlock = (block) => {
    switch (block.type) {
      case 'bars': {
        const group = el('div', 'bar-group');
        // 최대 퍼센트 계산 (스케일링 기준)
        const maxPct = Math.max(...block.items.map(i => i.percent), 1);
        for (const item of block.items) {
          const row = el('div', 'bar-item');
          row.appendChild(el('span', 'bar-label', item.label));
          const track = el('div', 'bar-track');
          const fill = el('div', 'bar-fill');
          fill.style.width = `${(item.percent / maxPct) * 100}%`;
          track.appendChild(fill);
          row.appendChild(track);
          row.appendChild(el('span', 'bar-value', item.value));
          group.appendChild(row);
        }
        return group;
      }

      case 'panel': {
        const pane = el('div', 'side-pane');
        pane.innerHTML = mdToHtml(block.content);
        return pane;
      }

      case 'callout': {
        const box = el('div', 'callout');
        box.innerHTML = mdToHtml(block.content);
        return box;
      }

      case 'table': {
        const table = document.createElement('table');
        // 헤더
        const thead = document.createElement('thead');
        const headRow = document.createElement('tr');
        for (const h of block.headers) {
          headRow.appendChild(el('th', null, h));
        }
        thead.appendChild(headRow);
        table.appendChild(thead);
        // 본문
        const tbody = document.createElement('tbody');
        for (const row of block.rows) {
          const tr = document.createElement('tr');
          for (const cell of row) {
            tr.appendChild(el('td', null, cell));
          }
          tbody.appendChild(tr);
        }
        table.appendChild(tbody);
        return table;
      }

      case 'list': {
        const ul = document.createElement('ul');
        const inlineFormat = (s) => s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        for (const item of block.items) {
          ul.appendChild(el('li', null, inlineFormat(item)));
        }
        return ul;
      }

      case 'heading': {
        return el('h3', null, block.text);
      }

      case 'paragraph': {
        const inlineFormat = (s) => s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        return el('p', null, inlineFormat(block.text));
      }

      default:
        return el('p', null, block.text || '');
    }
  };

  /* ─── hero 레이아웃 ────────────────────────────────────── */
  const renderHero = (slide) => {
    const section = el('section', 'slide layout-hero');
    // hero는 헤더 없이 slot-body만
    const body = el('div', 'slot-body');
    if (slide.title) body.appendChild(el('div', 'hero-title', slide.title));
    if (slide.subtitle) body.appendChild(el('div', 'hero-subtitle', slide.subtitle));
    section.appendChild(body);
    // 푸터 (페이지 번호만)
    const footer = el('div', 'slot-footer');
    footer.appendChild(el('span', 'source', ''));
    footer.appendChild(el('span', 'page-num', ''));
    section.appendChild(footer);
    return section;
  };

  /* ─── two-panel 레이아웃 ───────────────────────────────── */
  const renderTwoPanel = (slide) => {
    const ratioClass = slide.ratio ? `ratio-${slide.ratio}` : 'ratio-65-35';
    const section = el('section', `slide layout-two-panel ${ratioClass}`);
    section.appendChild(buildHeader(slide));

    const body = el('div', 'slot-body');
    const mainPane = el('div', 'main-pane');
    const sidePane = el('div', 'side-pane');

    let panelFound = false;
    for (const block of slide.blocks) {
      if (block.type === 'panel') {
        sidePane.innerHTML = mdToHtml(block.content);
        panelFound = true;
      } else {
        mainPane.appendChild(renderBlock(block));
      }
    }
    body.appendChild(mainPane);
    if (panelFound) body.appendChild(sidePane);

    section.appendChild(body);
    section.appendChild(buildFooter(slide));
    return section;
  };

  /* ─── summary 레이아웃 ─────────────────────────────────── */
  const renderSummary = (slide) => {
    const section = el('section', 'slide layout-summary');
    section.appendChild(buildHeader(slide));

    const body = el('div', 'slot-body');
    // 테이블 블록을 summary-row로 변환
    for (const block of slide.blocks) {
      if (block.type === 'table') {
        for (const row of block.rows) {
          const sRow = el('div', 'summary-row');
          sRow.appendChild(el('div', 'summary-label', row[0] || ''));
          const sBody = el('div', 'summary-body');
          sBody.innerHTML = mdToHtml(row.slice(1).join('\n'));
          sRow.appendChild(sBody);
          body.appendChild(sRow);
        }
      } else {
        body.appendChild(renderBlock(block));
      }
    }

    section.appendChild(body);
    section.appendChild(buildFooter(slide));
    return section;
  };

  /* ─── three-stage 레이아웃 ─────────────────────────────── */
  const renderThreeStage = (slide) => {
    const section = el('section', 'slide layout-three-stage');
    section.appendChild(buildHeader(slide));

    const body = el('div', 'slot-body');
    // heading 블록 기준으로 stage-col 분할
    let currentCol = null;
    for (const block of slide.blocks) {
      if (block.type === 'heading') {
        currentCol = el('div', 'stage-col');
        currentCol.appendChild(el('div', 'stage-title', block.text));
        body.appendChild(currentCol);
      } else if (currentCol) {
        currentCol.appendChild(renderBlock(block));
      } else {
        // heading 이전 블록은 새 col 생성
        currentCol = el('div', 'stage-col');
        currentCol.appendChild(renderBlock(block));
        body.appendChild(currentCol);
      }
    }

    section.appendChild(body);
    section.appendChild(buildFooter(slide));
    return section;
  };

  /* ─── repeat-grid 레이아웃 ─────────────────────────────── */
  const renderRepeatGrid = (slide) => {
    // heading 수로 cols 결정
    const headingCount = slide.blocks.filter(b => b.type === 'heading').length;
    const cols = headingCount || 2;
    const section = el('section', `slide layout-repeat-grid cols-${Math.min(cols, 4)}`);
    section.appendChild(buildHeader(slide));

    const body = el('div', 'slot-body');
    let currentBlock = null;
    for (const block of slide.blocks) {
      if (block.type === 'heading') {
        currentBlock = el('div', 'grid-block');
        currentBlock.appendChild(el('h3', null, block.text));
        body.appendChild(currentBlock);
      } else if (currentBlock) {
        currentBlock.appendChild(renderBlock(block));
      } else {
        currentBlock = el('div', 'grid-block');
        currentBlock.appendChild(renderBlock(block));
        body.appendChild(currentBlock);
      }
    }

    section.appendChild(body);
    section.appendChild(buildFooter(slide));
    return section;
  };

  /* ─── rows 레이아웃 ────────────────────────────────────── */
  const renderRows = (slide) => {
    const section = el('section', 'slide layout-rows');
    section.appendChild(buildHeader(slide));

    const body = el('div', 'slot-body');
    for (const block of slide.blocks) {
      body.appendChild(renderBlock(block));
    }

    section.appendChild(body);
    section.appendChild(buildFooter(slide));
    return section;
  };

  /* ─── 공통 헤더/푸터 빌더 ──────────────────────────────── */
  const buildHeader = (slide) => {
    const header = el('div', 'slot-header');
    if (slide.kicker) header.appendChild(el('span', 'kicker', slide.kicker));
    if (slide.title) header.appendChild(el('div', 'title', slide.title));
    return header;
  };

  const buildFooter = (slide, pageNum) => {
    const footer = el('div', 'slot-footer');
    footer.appendChild(el('span', 'source', slide.source || ''));
    footer.appendChild(el('span', 'page-num', pageNum !== undefined ? String(pageNum) : ''));
    return footer;
  };

  /* ─── 레이아웃 디스패치 ────────────────────────────────── */
  const layoutMap = {
    'hero': renderHero,
    'summary': renderSummary,
    'two-panel': renderTwoPanel,
    'three-stage': renderThreeStage,
    'repeat-grid': renderRepeatGrid,
    'rows': renderRows,
  };

  /* ─── 메인 렌더 함수 ───────────────────────────────────── */
  const render = (ast, container) => {
    // 테마 적용
    if (ast.meta && ast.meta.theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    }

    // 타이틀 설정
    if (ast.meta && ast.meta.title) {
      document.title = ast.meta.title;
    }

    const slides = ast.slides;
    for (let i = 0; i < slides.length; i++) {
      const slide = slides[i];
      const renderFn = layoutMap[slide.layout] || renderRows;
      const section = renderFn(slide);

      // 페이지 번호 업데이트
      const pageEl = section.querySelector('.page-num');
      if (pageEl) pageEl.textContent = String(i + 1);

      container.appendChild(section);
    }
  };

  return { render };
})();

/* Node.js 환경 호환 */
if (typeof module !== 'undefined' && module.exports) module.exports = SlideRenderer;
