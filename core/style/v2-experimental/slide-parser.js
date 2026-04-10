/* ═══════════════════════════════════════════════════════════
   Deep-Briefing Slide Parser v2
   Markdown DSL → JSON AST 변환기
   외부 의존성 0 · 전역 객체: SlideParser
   ═══════════════════════════════════════════════════════════ */

const SlideParser = (() => {
  'use strict';

  /* ─── frontmatter 파싱 ─────────────────────────────────── */
  const parseFrontmatter = (raw) => {
    const meta = {};
    raw.split('\n').forEach(line => {
      const m = line.match(/^(\w+)\s*:\s*"?(.+?)"?\s*$/);
      if (m) meta[m[1]] = m[2];
    });
    return meta;
  };

  /* ─── HTML 코멘트 디렉티브 추출 ────────────────────────── */
  const parseDirectives = (lines) => {
    const dirs = {};
    const remaining = [];
    for (const line of lines) {
      const layoutMatch = line.match(/^<!--\s*layout\s*:\s*([^,>]+)(?:\s*,\s*ratio\s*:\s*([^>]+))?\s*-->/);
      if (layoutMatch) {
        dirs.layout = layoutMatch[1].trim();
        if (layoutMatch[2]) dirs.ratio = layoutMatch[2].trim();
        continue;
      }
      const kickerMatch = line.match(/^<!--\s*kicker\s*:\s*(.+?)\s*-->/);
      if (kickerMatch) { dirs.kicker = kickerMatch[1]; continue; }
      const sourceMatch = line.match(/^<!--\s*source\s*:\s*(.+?)\s*-->/);
      if (sourceMatch) { dirs.source = sourceMatch[1]; continue; }
      remaining.push(line);
    }
    return { dirs, remaining };
  };

  /* ─── <tag>...</tag> 커스텀 블록 추출 ──────────────────── */
  const extractTagBlocks = (lines) => {
    const blocks = [];
    const outside = [];
    let inside = null;
    let buf = [];

    for (const line of lines) {
      if (!inside) {
        const open = line.match(/^<(bars|panel|callout)>$/);
        if (open) { inside = open[1]; buf = []; continue; }
        outside.push(line);
      } else {
        const close = line.match(new RegExp(`^</${inside}>$`));
        if (close) {
          blocks.push({ tag: inside, body: buf.join('\n') });
          // 바깥 줄에 플레이스홀더 삽입 (위치 보존)
          outside.push(`__BLOCK_${blocks.length - 1}__`);
          inside = null;
          buf = [];
        } else {
          buf.push(line);
        }
      }
    }
    return { blocks, outside };
  };

  /* ─── bars 블록 내부 파싱 ───────────────────────────────── */
  const parseBars = (body) => {
    const items = [];
    body.split('\n').forEach(line => {
      const m = line.match(/^-\s*(.+?):\s*(.+?)\s*\|\s*(\d+)%?\s*$/);
      if (m) items.push({ label: m[1].trim(), value: m[2].trim(), percent: Number(m[3]) });
    });
    return { type: 'bars', items };
  };

  /* ─── 테이블 파싱 ──────────────────────────────────────── */
  const parseTable = (tableLines) => {
    const rows = [];
    for (const line of tableLines) {
      // 구분선 건너뛰기
      if (/^\|[\s-|]+\|$/.test(line)) continue;
      const cells = line.split('|').slice(1, -1).map(c => c.trim());
      if (cells.length) rows.push(cells);
    }
    if (!rows.length) return null;
    return { type: 'table', headers: rows[0], rows: rows.slice(1) };
  };

  /* ─── 본문 라인 → blocks 변환 ──────────────────────────── */
  const parseBodyLines = (lines, tagBlocks) => {
    const blocks = [];
    let listBuf = [];
    let tableBuf = [];

    const flushList = () => {
      if (!listBuf.length) return;
      blocks.push({ type: 'list', items: listBuf.map(l => l.replace(/^-\s*/, '')) });
      listBuf = [];
    };

    const flushTable = () => {
      if (!tableBuf.length) return;
      const tbl = parseTable(tableBuf);
      if (tbl) blocks.push(tbl);
      tableBuf = [];
    };

    for (const line of lines) {
      // 태그 블록 플레이스홀더
      const phMatch = line.match(/^__BLOCK_(\d+)__$/);
      if (phMatch) {
        flushList(); flushTable();
        const tb = tagBlocks[Number(phMatch[1])];
        if (tb.tag === 'bars') blocks.push(parseBars(tb.body));
        else blocks.push({ type: tb.tag, content: tb.body });
        continue;
      }

      // 테이블 행
      if (/^\|.+\|$/.test(line)) {
        flushList();
        tableBuf.push(line);
        continue;
      }
      if (tableBuf.length) flushTable();

      // 제목 (### 이하만 — #, ## 은 상위에서 처리됨)
      if (/^###\s/.test(line)) {
        flushList();
        blocks.push({ type: 'heading', level: 3, text: line.replace(/^###\s+/, '') });
        continue;
      }

      // 불릿 리스트
      if (/^-\s/.test(line)) { tableBuf.length && flushTable(); listBuf.push(line); continue; }
      flushList();

      // 빈 줄 무시
      if (!line.trim()) continue;

      // 일반 텍스트 → paragraph
      blocks.push({ type: 'paragraph', text: line });
    }
    flushList();
    flushTable();
    return blocks;
  };

  /* ─── 슬라이드 한 장 파싱 ──────────────────────────────── */
  const parseSlide = (raw) => {
    const allLines = raw.split('\n');
    const { dirs, remaining } = parseDirectives(allLines);
    const { blocks: tagBlocks, outside } = extractTagBlocks(remaining);

    const slide = { layout: dirs.layout || 'rows', blocks: [] };
    if (dirs.ratio) slide.ratio = dirs.ratio;
    if (dirs.kicker) slide.kicker = dirs.kicker;
    if (dirs.source) slide.source = dirs.source;

    // title / subtitle 추출
    const bodyLines = [];
    for (const line of outside) {
      const h1 = line.match(/^#\s+(.+)$/);
      if (h1 && !slide.title) { slide.title = h1[1]; continue; }
      const h2 = line.match(/^##\s+(.+)$/);
      if (h2 && !slide.subtitle) { slide.subtitle = h2[1]; continue; }
      bodyLines.push(line);
    }

    slide.blocks = parseBodyLines(bodyLines, tagBlocks);
    return slide;
  };

  /* ─── 메인 파서 ────────────────────────────────────────── */
  const parse = (source) => {
    const normalized = source.replace(/\r\n/g, '\n').trim();
    // --- 로 분할
    const parts = normalized.split(/^---\s*$/m);

    let meta = {};
    let slideRaws = [];

    if (parts.length >= 3) {
      // 첫 번째 --- ~ --- 구간이 frontmatter
      const first = parts[0].trim();
      if (!first) {
        // 표준 frontmatter: ---\n...\n---
        meta = parseFrontmatter(parts[1]);
        slideRaws = parts.slice(2);
      } else {
        // frontmatter 없음 — 전부 슬라이드
        slideRaws = parts.filter(p => p.trim());
      }
    } else {
      slideRaws = parts.filter(p => p.trim());
    }

    const slides = slideRaws
      .filter(r => r.trim())
      .map(r => parseSlide(r.trim()));

    return { meta, slides };
  };

  return { parse };
})();

/* Node.js 환경 호환 */
if (typeof module !== 'undefined' && module.exports) module.exports = SlideParser;
