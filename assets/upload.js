/* SWBLI Literature Atlas — local PDF upload and extraction.
   Runs entirely in the browser. No file leaves the machine. */
(function () {
  "use strict";

  const section = document.getElementById("pdfUpload");
  if (!section) return;

  const pid = section.getAttribute("data-pid") ||
    (document.querySelector(".detail-wrap") || {}).getAttribute?.("data-pid") || "";
  const drop = document.getElementById("pdfDrop");
  const fileInput = document.getElementById("pdfFile");
  const status = document.getElementById("pdfUploadStatus");
  const panel = document.getElementById("pdfParsed");

  const SCRIPT_BASE = (document.currentScript && document.currentScript.src)
    ? document.currentScript.src.replace(/[^/]*$/, "")
    : "../assets/";
  const PDFJS_BASE = SCRIPT_BASE + "pdfjs/";
  const MAX_BYTES = 80 * 1024 * 1024;
  const DB_NAME = "swbli-uploaded-pdfs";
  const STORE = "pdfs";

  let pdfjsPromise = null;
  let currentUrl = null;
  let memoryStore = new Map();

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const esc = (s) => String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");

  function setStatus(msg, kind) {
    if (!status) return;
    status.className = "upload-status" + (kind ? " " + kind : "");
    status.innerHTML = msg || "";
  }

  /* ---------- persistent storage ---------- */

  function openDB() {
    return new Promise((resolve, reject) => {
      if (!window.indexedDB) return reject(new Error("IndexedDB unavailable"));
      const req = indexedDB.open(DB_NAME, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(STORE)) db.createObjectStore(STORE, { keyPath: "pid" });
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error || new Error("IndexedDB open failed"));
    });
  }

  async function dbGet(key) {
    try {
      const db = await openDB();
      return await new Promise((resolve, reject) => {
        const tx = db.transaction(STORE, "readonly");
        const req = tx.objectStore(STORE).get(key);
        req.onsuccess = () => resolve(req.result || null);
        req.onerror = () => reject(req.error);
      });
    } catch (err) {
      return memoryStore.get(key) || null;
    }
  }

  async function dbPut(rec) {
    memoryStore.set(rec.pid, rec);
    try {
      const db = await openDB();
      await new Promise((resolve, reject) => {
        const tx = db.transaction(STORE, "readwrite");
        tx.objectStore(STORE).put(rec);
        tx.oncomplete = resolve;
        tx.onerror = () => reject(tx.error);
      });
      return true;
    } catch (err) {
      return false;
    }
  }

  async function dbDelete(key) {
    memoryStore.delete(key);
    try {
      const db = await openDB();
      await new Promise((resolve, reject) => {
        const tx = db.transaction(STORE, "readwrite");
        tx.objectStore(STORE).delete(key);
        tx.oncomplete = resolve;
        tx.onerror = () => reject(tx.error);
      });
    } catch (err) { /* ignore */ }
  }

  /* ---------- pdf.js ---------- */

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const old = document.querySelector('script[data-swbli-pdfjs="' + src + '"]');
      if (old) { old.addEventListener("load", () => resolve()); old.addEventListener("error", reject); return; }
      const s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.setAttribute("data-swbli-pdfjs", src);
      s.onload = () => resolve();
      s.onerror = () => reject(new Error("无法加载本地 PDF.js：" + src));
      document.head.appendChild(s);
    });
  }

  function loadPdfJs() {
    if (window.pdfjsLib) return Promise.resolve(window.pdfjsLib);
    if (pdfjsPromise) return pdfjsPromise;
    pdfjsPromise = loadScript(PDFJS_BASE + "pdf.min.js").then(() => {
      if (!window.pdfjsLib) throw new Error("PDF.js 已加载但未初始化");
      try {
        window.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS_BASE + "pdf.worker.min.js";
      } catch (err) { /* fake worker fallback is fine */ }
      return window.pdfjsLib;
    });
    return pdfjsPromise;
  }

  /* ---------- text extraction ---------- */

  function itemsToLines(items) {
    const rows = [];
    items.forEach(it => {
      const str = String(it.str || "");
      if (!str.trim()) return;
      const tr = it.transform || [1, 0, 0, 1, 0, 0];
      const x = Number(tr[4]) || 0;
      const y = Number(tr[5]) || 0;
      let row = rows.find(r => Math.abs(r.y - y) < 2.2);
      if (!row) { row = { y: y, parts: [] }; rows.push(row); }
      row.parts.push({ x: x, str: str });
    });
    rows.sort((a, b) => b.y - a.y);
    return rows.map(r => {
      r.parts.sort((a, b) => a.x - b.x);
      let out = "";
      r.parts.forEach((p, i) => {
        if (!out) { out = p.str; return; }
        const prev = r.parts[i - 1];
        const gap = p.x - (prev.x + String(prev.str).length * 4.2);
        out += (gap > 6 ? "  " : "") + p.str;
      });
      return out.replace(/\s+/g, " ").trim();
    }).filter(Boolean);
  }

  function detectHeading(line) {
    const s = line.trim();
    if (!s || s.length > 90) return "";
    const en = s.match(/^(?:\d+(?:\.\d+)*\.?\s*)?(abstract|summary|introduction|background|methods?|methodology|experimental(?:\s+(?:setup|apparatus|methods?))?|numerical(?:\s+(?:method|methods|approach|simulation|setup))?|results?|discussion|conclusions?|concluding remarks|references|acknowledg(?:e)?ments)\b/i);
    if (en) return en[1].toLowerCase();
    const zh = s.match(/^(?:[一二三四五六七八九十]+[、.．]\s*)?(摘要|引言|前言|研究方法|方法|实验(?:方法|装置)?|数值(?:方法|模拟)?|结果(?:与分析)?|讨论|结论|参考文献|致谢)\s*$/);
    if (zh) return zh[1];
    return "";
  }

  function sectionKind(head) {
    if (!head) return "";
    if (/abstract|summary|摘要/.test(head)) return "abstract";
    if (/introduction|background|引言|前言/.test(head)) return "intro";
    if (/method|experimental|numerical|方法|实验|数值/.test(head)) return "methods";
    if (/result|结果/.test(head)) return "results";
    if (/discussion|讨论/.test(head)) return "discussion";
    if (/conclusion|concluding|结论/.test(head)) return "conclusions";
    return "";
  }

  function buildSections(pageTexts) {
    const buckets = { abstract: [], intro: [], methods: [], results: [], discussion: [], conclusions: [] };
    let current = "";
    pageTexts.forEach(p => {
      p.lines.forEach(line => {
        const head = detectHeading(line);
        const kind = sectionKind(head);
        if (kind) { current = kind; return; }
        if (current && buckets[current].length < 240) buckets[current].push(line);
      });
    });
    Object.keys(buckets).forEach(k => {
      buckets[k] = buckets[k].join("\n").replace(/\n{3,}/g, "\n\n").trim();
    });
    return buckets;
  }

  function splitSentences(text) {
    return String(text || "")
      .replace(/\s+/g, " ")
      .split(/(?<=[。！？!?])\s+|(?<=[.!?])\s+(?=[A-Z0-9])/u)
      .map(s => s.trim())
      .filter(s => s.length >= 45 && s.length <= 520);
  }

  function pickSentences(text, n, preferNumbers) {
    const sents = splitSentences(text);
    const seen = new Set();
    const scored = sents.map((s, i) => {
      let score = 0;
      if (/\d/.test(s)) score += 3;
      if (/(increase|decrease|higher|lower|depend|effect|sensitive|trend|随着|增加|降低|增大|减小|影响|趋势|无关|独立)/i.test(s)) score += 3;
      if (/(Fig\.?|Figure|表|图|Table)\s*\d+/i.test(s)) score += 2;
      if (/(%|×|10\^|kpa|mpa|k\b|m\/s|pa\b)/i.test(s)) score += 2;
      if (preferNumbers && /\d/.test(s)) score += 1;
      score -= Math.min(3, Math.abs(i - sents.length * 0.35) * 0.15);
      return { s, score, i };
    }).sort((a, b) => b.score - a.score || a.i - b.i);
    const out = [];
    scored.forEach(x => {
      const key = x.s.slice(0, 80).toLowerCase();
      if (out.length < n && !seen.has(key)) { seen.add(key); out.push(x.s); }
    });
    return out;
  }

  function extractAbstract(buckets, pageTexts) {
    if (buckets.abstract && buckets.abstract.length > 80) return buckets.abstract;
    const first = pageTexts.slice(0, 2).map(p => p.text).join("\n");
    const m = first.match(/(?:abstract|摘要)\s*[:：.]?\s*([\s\S]{120,2200}?)(?=\n\s*(?:keywords?|关键词|1\.?\s*introduction|introduction|引言)\b)/i);
    if (m) return m[1].replace(/\s+/g, " ").trim();
    return "";
  }

  function extractCaptions(pageTexts) {
    const out = [];
    pageTexts.forEach(p => {
      p.lines.forEach(line => {
        if (/^(fig(?:ure)?\.?|table|图|表)\s*\d+/i.test(line.trim()) && line.length < 320) {
          out.push({ page: p.n, text: line.trim() });
        }
      });
    });
    return out.slice(0, 12);
  }

  function extractDoi(text) {
    const m = String(text || "").match(/\b10\.\d{4,9}\/[-._;()/:A-Za-z0-9]+/);
    return m ? m[0].replace(/[.,;]+$/, "") : "";
  }

  async function extractPdf(file) {
    const pdfjs = await loadPdfJs();
    const buf = await file.arrayBuffer();
    setStatus("正在读取 PDF 结构…", "busy");
    const pdf = await pdfjs.getDocument({
      data: new Uint8Array(buf),
      disableFontFace: true,
      isEvalSupported: false,
      useSystemFonts: true,
    }).promise;

    const pageTexts = [];
    const total = pdf.numPages;
    for (let n = 1; n <= total; n++) {
      const page = await pdf.getPage(n);
      const tc = await page.getTextContent();
      const lines = itemsToLines(tc.items || []);
      pageTexts.push({ n: n, lines: lines, text: lines.join("\n") });
      if (n % 5 === 0 || n === total) {
        setStatus("正在抽取文本：" + n + " / " + total + " 页…", "busy");
      }
    }

    let meta = {};
    try {
      const md = await pdf.getMetadata();
      meta = md && md.info ? md.info : {};
    } catch (err) { /* optional */ }

    const allText = pageTexts.map(p => p.text).join("\n");
    const buckets = buildSections(pageTexts);
    const abstract = extractAbstract(buckets, pageTexts);
    const firstPage = pageTexts[0] ? pageTexts[0].text : "";
    const title = String(meta.Title || "").trim() ||
      (pageTexts[0] && pageTexts[0].lines.find(l => l.length >= 18 && l.length <= 220) || "").trim();
    const metaYear = (String(meta.CreationDate || "").match(/(19|20)\d{2}/) ||
      firstPage.match(/\b(19|20)\d{2}\b/) || [""])[0];
    // 详情页的题录年份优先。PDF 的 CreationDate 往往是扫描/数字化时间，
    // 对老报告会把 1968 年误显示成 2002 年。
    const siteYear = String(section && section.dataset.year || "").trim();
    const year = siteYear || metaYear;
    const yearSource = siteYear ? "record" : (metaYear ? "pdfmeta" : "");

    const imrad = {};
    ["intro", "methods", "results", "discussion", "conclusions"].forEach(k => {
      imrad[k] = pickSentences(buckets[k], 3, k === "results");
    });
    const keySentences = pickSentences(
      [buckets.results, buckets.discussion, buckets.conclusions].join("\n"), 7, true
    );

    // Render pages that contain a figure/table caption (plus the first page).
    const figPages = new Set();
    extractCaptions(pageTexts).forEach(c => figPages.add(c.page));
    figPages.add(1);
    const wanted = Array.from(figPages).sort((a, b) => a - b).slice(0, 6);
    const thumbnails = [];
    for (let i = 0; i < wanted.length; i++) {
      const n = wanted[i];
      setStatus("正在生成含图页面：" + (i + 1) + " / " + wanted.length + "…", "busy");
      try {
        const page = await pdf.getPage(n);
        const vp = page.getViewport({ scale: 1 });
        const scale = Math.min(1.55, 1100 / Math.max(1, vp.width));
        const viewport = page.getViewport({ scale: scale });
        const canvas = document.createElement("canvas");
        canvas.width = Math.ceil(viewport.width);
        canvas.height = Math.ceil(viewport.height);
        const ctx = canvas.getContext("2d");
        await page.render({ canvasContext: ctx, viewport: viewport }).promise;
        thumbnails.push({
          page: n,
          dataUrl: canvas.toDataURL("image/jpeg", 0.82),
          width: canvas.width,
          height: canvas.height,
        });
      } catch (err) {
        console.warn("page render failed", n, err);
      }
    }

    return {
      pid: String(pid),
      fileName: file.name,
      size: file.size,
      importedAt: new Date().toISOString(),
      pageCount: total,
      title: title,
      year: year,
      yearSource: yearSource,
      doi: extractDoi(firstPage),
      abstract: abstract,
      sections: buckets,
      imrad: imrad,
      keySentences: keySentences,
      captions: extractCaptions(pageTexts),
      thumbnails: thumbnails,
      pdfBlob: file,
    };
  }

  /* ---------- page update ---------- */

  function installPdfLinks(url, name) {
    if (currentUrl && currentUrl !== url) {
      try { URL.revokeObjectURL(currentUrl); } catch (err) { /* ignore */ }
    }
    currentUrl = url;
    $$("[data-pdf-slot]").forEach(slot => {
      const a = document.createElement("a");
      a.className = "btn small ghost";
      a.href = url;
      a.target = "_blank";
      a.rel = "noopener";
      a.setAttribute("data-pdf-link", "");
      a.textContent = "PDF ↗";
      slot.replaceWith(a);
    });
    $$("a[data-pdf-link]").forEach(a => {
      a.href = url;
      a.target = "_blank";
      a.rel = "noopener";
      a.classList.remove("pdf-missing");
    });
    $$("[data-pdf-name]").forEach(el => { el.textContent = name; });
  }

  function download(name, content, type) {
    const blob = content instanceof Blob ? content : new Blob([content], { type: type || "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }

  function safeBase(rec) {
    const base = String(rec.title || rec.fileName || ("paper-" + rec.pid))
      .replace(/[\\/:*?"<>|]+/g, "_").replace(/\s+/g, " ").trim();
    return (base.slice(0, 70) || ("paper-" + rec.pid));
  }

  function renderParsed(rec, opts) {
    if (!panel) return;
    const flags = opts || {};
    const sections = rec.sections || {};
    const imrad = rec.imrad || {};
    const labels = {
      intro: "Introduction / 引言",
      methods: "Methods / 方法",
      results: "Results / 结果",
      discussion: "Discussion / 讨论",
      conclusions: "Conclusions / 结论",
    };
    const imradHtml = Object.keys(labels).map(k => {
      const picked = imrad[k] || [];
      return `<div class="parsed-block"><h4>${labels[k]}</h4>${
        picked.length
          ? `<ul>${picked.map(s => `<li>${esc(s)}</li>`).join("")}</ul>`
          : `<p class="muted small">未检测到清晰的该章节。原文可能使用其他标题，或 PDF 文本层不可读。</p>`
      }</div>`;
    }).join("");

    const keys = (rec.keySentences || []).length
      ? `<ul class="parsed-keys">${rec.keySentences.map(s => `<li>${esc(s)}</li>`).join("")}</ul>`
      : `<p class="muted small">未抽取到带定量信息的关键句。</p>`;

    const caps = (rec.captions || []).slice(0, 8);
    const capHtml = caps.length
      ? `<ul class="parsed-captions">${caps.map(c => `<li><b>p.${c.page}</b> ${esc(c.text)}</li>`).join("")}</ul>`
      : `<p class="muted small">未检测到 Fig./Table 图注。</p>`;

    const thumbs = (rec.thumbnails || []).length
      ? `<div class="parsed-thumbs">${rec.thumbnails.map(t =>
          `<figure><a href="${esc(t.dataUrl)}" target="_blank" rel="noopener"><img loading="lazy" src="${esc(t.dataUrl)}" alt="第 ${t.page} 页"></a><figcaption>第 ${t.page} 页</figcaption></figure>`
        ).join("")}</div>`
      : "";

    const stored = flags.persisted ? "已保存在本机浏览器（IndexedDB）" : "浏览器禁止本地持久化，本次会话有效";
    const size = rec.size ? (rec.size / 1024 / 1024).toFixed(2) + " MB" : "—";
    const abstract = rec.abstract
      ? `<div class="parsed-abstract"><div class="parsed-label">原摘要（机器抽取）</div><p>${esc(rec.abstract.slice(0, 2600))}${rec.abstract.length > 2600 ? "…" : ""}</p></div>`
      : `<div class="parsed-abstract"><div class="parsed-label">原摘要</div><p class="muted">未检测到 Abstract 段。可在上方“原始摘要”或 PDF 中核对。</p></div>`;

    panel.innerHTML = `
      <div class="parsed-head">
        <div>
          <div class="parsed-title">${esc(rec.title || rec.fileName || "未命名 PDF")}</div>
          <div class="parsed-meta">${rec.pageCount || "?"} 页 · ${size} · ${esc(rec.fileName || "")}${rec.year ? " · " + esc(rec.year) + (rec.yearSource === "pdfmeta" ? "（PDF 元数据）" : "") : ""}${rec.doi ? " · DOI " + esc(rec.doi) : ""}</div>
          <div class="parsed-note">${stored} · 解析于 ${esc((rec.importedAt || "").slice(0, 16).replace("T", " "))}</div>
        </div>
        <div class="parsed-actions">
          ${rec.pdfBlob ? `<a class="btn small" data-pdf-link href="#" target="_blank" rel="noopener">打开 PDF ↗</a>` : ""}
          <button class="btn small ghost" type="button" data-upload-json>下载解析 JSON</button>
          <button class="btn small ghost" type="button" data-upload-bundle>下载 AI 精读输入包</button>
          <button class="btn small ghost danger" type="button" data-upload-remove>移除上传</button>
        </div>
      </div>
      ${abstract}
      <div class="parsed-grid">${imradHtml}</div>
      <div class="parsed-block"><h4>关键句（原文，未经改写）</h4>${keys}</div>
      <div class="parsed-block"><h4>图注线索</h4>${capHtml}</div>
      <div class="parsed-block"><h4>含图页面（页面截图，非裁切图件）</h4>${thumbs || '<p class="muted small">未能生成页面图。</p>'}</div>
      <p class="parsed-foot">说明：以上为浏览器端确定性抽取，保留原文语言，不做翻译或臆测；公式、图件细节与因果解释请以 PDF 原文和页面既有精读记录为准。若需与库内条目同等级的中文 IMRaD 精读，请把“AI 精读输入包”交给 paper-reader 流程。</p>
    `;

    $$("[data-upload-json]", panel).forEach(b => b.addEventListener("click", () => {
      const clean = Object.assign({}, rec);
      delete clean.pdfBlob;
      download(safeBase(rec) + ".parsed.json", JSON.stringify(clean, null, 2), "application/json;charset=utf-8");
    }));
    $$("[data-upload-bundle]", panel).forEach(b => b.addEventListener("click", () => {
      const text = buildBundle(rec);
      download(safeBase(rec) + ".deep-input.md", text, "text/markdown;charset=utf-8");
    }));
    $$("[data-upload-remove]", panel).forEach(b => b.addEventListener("click", async () => {
      if (!confirm("移除本页已上传的 PDF 与解析结果？不会删除项目内原有文件。")) return;
      await dbDelete(pid);
      if (currentUrl) { try { URL.revokeObjectURL(currentUrl); } catch (err) {} }
      location.reload();
    }));
    if (currentUrl) {
      $$("a[data-pdf-link]", panel).forEach(a => {
        a.href = currentUrl;
        a.target = "_blank";
        a.rel = "noopener";
      });
    }
  }

  function buildBundle(rec) {
    const head = [
      "# 单篇精读输入包（浏览器抽取）",
      "",
      "- 条目 ID：" + rec.pid,
      "- 文件名：" + (rec.fileName || ""),
      "- 页数：" + (rec.pageCount || ""),
      "- 题名（机器识别）：" + (rec.title || ""),
      "- DOI（机器识别）：" + (rec.doi || "未识别"),
      "- 年份：" + (rec.year || "未识别"),
      "",
      "> 本文件由文献图谱详情页在浏览器本地生成。文本来自 PDF 文本层；公式与图表未做语义还原。请按 paper-reader 的 IMRaD、LaTeX、图页引用与不编造约束继续精读。",
      "",
      "## 全文（按页）",
      "",
    ].join("\n");
    const body = Object.keys(rec.sections || {}).map(k => {
      return "### " + k + "\n\n" + (rec.sections[k] || "（未检测到）") + "\n";
    }).join("\n");
    const caps = (rec.captions || []).map(c => "- p." + c.page + "：" + c.text).join("\n");
    return head + body + "\n## 检测到的图注\n\n" + (caps || "（无）") + "\n";
  }

  /* ---------- upload flow ---------- */

  async function handleFile(file) {
    if (!file) return;
    if (!/\.pdf$/i.test(file.name) && file.type !== "application/pdf") {
      setStatus("请选择 PDF 文件。", "error");
      return;
    }
    if (file.size > MAX_BYTES) {
      setStatus("文件超过 80 MB，浏览器端解析可能失败；请先压缩或拆分。", "error");
      return;
    }
    if (!panel) return;
    panel.innerHTML = "";
    try {
      const rec = await extractPdf(file);
      setStatus("正在保存解析结果…", "busy");
      const persisted = await dbPut(rec);
      const url = URL.createObjectURL(file);
      installPdfLinks(url, file.name);
      renderParsed(rec, { persisted: persisted });
      setStatus(persisted
        ? "解析完成，本页已更新；刷新页面后仍会保留（存储于本机浏览器）。"
        : "解析完成，本页已更新；浏览器禁止本地持久化，刷新后需重新上传。", "ok");
      if (section) section.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      console.error(err);
      setStatus("解析失败：" + esc(err && err.message ? err.message : String(err)) +
        "。可尝试用 Chrome/Edge 打开，或把 PDF 放到本地后用项目脚本处理。", "error");
    }
  }

  if (fileInput) fileInput.addEventListener("change", () => {
    const f = fileInput.files && fileInput.files[0];
    handleFile(f);
    fileInput.value = "";
  });
  $$("[data-upload-trigger]").forEach(btn => {
    btn.addEventListener("click", () => {
      if (fileInput) {
        fileInput.click();
      } else if (section) {
        section.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
  if (drop) {
    ["dragenter", "dragover"].forEach(ev => drop.addEventListener(ev, e => {
      e.preventDefault(); e.stopPropagation(); drop.classList.add("over");
    }));
    ["dragleave", "drop"].forEach(ev => drop.addEventListener(ev, e => {
      e.preventDefault(); e.stopPropagation(); drop.classList.remove("over");
    }));
    drop.addEventListener("drop", e => {
      const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      handleFile(f);
    });
  }

  (async function init() {
    if (!pid) return;
    try {
      const rec = await dbGet(pid);
      if (!rec) return;
      if (rec.pdfBlob) {
        const url = URL.createObjectURL(rec.pdfBlob);
        installPdfLinks(url, rec.fileName || "uploaded.pdf");
        renderParsed(rec, { persisted: true });
        setStatus("已载入本机保存的上传解析结果。", "ok");
      } else {
        renderParsed(rec, { persisted: false });
      }
    } catch (err) {
      console.warn("upload restore failed", err);
    }
  })();
})();
