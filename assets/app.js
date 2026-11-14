/* SWBLI Literature Atlas — offline interactions */
(function () {
  "use strict";

  const DATA = window.SWBLI_DATA || { papers: [], meta: {} };
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const byId = new Map((DATA.papers || []).map(p => [String(p.id), p]));

  /* ---------- theme ---------- */

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const btn = $("#themeBtn");
    if (btn) {
      btn.textContent = theme === "dark" ? "☀" : "◐";
      btn.setAttribute("aria-label", theme === "dark" ? "切换到浅色主题" : "切换到深色主题");
    }
  }

  let saved = "light";
  try { saved = localStorage.getItem("swbli-theme") || "light"; } catch (e) {}
  applyTheme(saved);

  document.addEventListener("click", function (e) {
    const btn = e.target.closest("#themeBtn");
    if (!btn) return;
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    try { localStorage.setItem("swbli-theme", next); } catch (err) {}
  });

  /* ---------- nav ---------- */

  (function markNav() {
    const path = location.pathname.replace(/\\/g, "/");
    $$(".nav a").forEach(a => {
      const href = (a.getAttribute("href") || "").split("?")[0];
      if (!href) return;
      if (href === "index.html" && (path.endsWith("/") || path.endsWith("/index.html"))) a.classList.add("active");
      else if (href !== "index.html" && path.endsWith("/" + href)) a.classList.add("active");
      else if (href === "library.html" && path.includes("/papers/")) a.classList.add("active");
    });
  })();

  /* ---------- helpers ---------- */

  const esc = (s) => String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");

  const accentOf = (p) => {
    const b = p.board || [];
    if (b.includes("流动分离") && b.includes("峰值传热")) return "both";
    if (b.includes("峰值传热")) return "heat";
    if (b.includes("流动分离")) return "sep";
    return "base";
  };

  const badgeClass = (p) => {
    const a = accentOf(p);
    return a === "heat" ? "red" : a === "sep" ? "teal" : "gold";
  };

  function boardBadges(p) {
    return (p.board || []).map(b => {
      const cls = b === "流动分离" ? "teal" : b === "峰值传热" ? "red" : "gold";
      return `<span class="badge ${cls}">${esc(b)}</span>`;
    }).join("");
  }

  function journalBadges(p) {
    return (p.journal_tags || []).map(j =>
      `<span class="badge journal${j === "非期刊" ? " non" : ""}" title="期刊目录：${esc(j)}">${esc(j)}</span>`
    ).join("");
  }

  function citationBadge(p) {
    if (p.cited_by == null || isNaN(Number(p.cited_by))) return "";
    const n = Number(p.cited_by).toLocaleString("en-US");
    const refs = (p.reference_count == null || isNaN(Number(p.reference_count))) ? "—" : Number(p.reference_count).toLocaleString("en-US");
    const refSrc = p.reference_source || p.citation_source || "学术平台";
    const tip = `${p.citation_source || "学术平台"} 被引 ${n} 次；${refSrc} 记录参考文献 ${refs} 篇${p.citation_as_of ? `，截至 ${p.citation_as_of}` : ""}`;
    return `<span class="badge cite${p.highly_cited ? " hot" : ""}" title="${esc(tip)}">${p.highly_cited ? "高被引" : "被引"} ${n}</span>`;
  }

  function referenceBadge(p) {
    if (p.reference_count == null || isNaN(Number(p.reference_count))) return "";
    const n = Number(p.reference_count).toLocaleString("en-US");
    const src = p.reference_source || p.citation_source || "学术平台";
    return `<span class="badge ref" title="${esc(`${src} 记录的参考文献 ${n} 篇`)}">参考 ${n}</span>`;
  }

  function tagsHtml(p, limit) {
    const all = p.tags || [];
    const tags = [...all.filter(t => t === "无全文pdf"), ...all.filter(t => t !== "无全文pdf")].slice(0, limit || 99);
    return tags.map(t => {
      const status = t === "无全文pdf";
      const title = status ? ' title="本库无全文文件，可通过 DOI 或来源页获取"' : "";
      return `<a class="tag${status ? " no-pdf" : ""}" href="library.html?tag=${encodeURIComponent(t)}"${title}>${esc(t)}</a>`;
    }).join("");
  }

  function citationHtml(p) {
    const cites = p.citations || {};
    const keys = Object.keys(cites);
    if (!keys.length) return "";
    const opts = keys.map((k, i) => `<option value="${esc(k)}">${esc(cites[k].label || k)}</option>`).join("");
    return `<details class="cite" data-cite data-pid="${p.id}">
      <summary>引用格式 <span aria-hidden="true">▾</span></summary>
      <div class="cite-pop">
        <div class="cite-top">
          <select data-cite-select aria-label="选择引用格式">${opts}</select>
          <button class="btn small" type="button" data-copy-cite>复制</button>
        </div>
        <pre data-cite-pre>${esc(cites[keys[0]].text)}</pre>
        <div class="cite-foot">
          <span class="hint">按各刊常见风格排版，文献出处保留原刊名</span>
          ${p.doi ? `<a href="https://doi.org/${esc(p.doi)}" target="_blank" rel="noopener">DOI ↗</a>` : ""}
        </div>
      </div>
    </details>`;
  }

  function accessAction(p) {
    if (p.doi) {
      return `<a class="btn small ghost" href="https://doi.org/${esc(p.doi)}" target="_blank" rel="noopener" title="通过 DOI 获取原文">DOI ↗</a>`;
    }
    if (p.url) {
      return `<a class="btn small ghost" href="${esc(p.url)}" target="_blank" rel="noopener" title="打开来源页面">来源 ↗</a>`;
    }
    return "";
  }

  function pdfAction(p) {
    if (p.pdf_href) {
      return `<a class="btn small ghost" href="${esc(p.pdf_href)}" target="_blank" rel="noopener" title="在本地打开 PDF">PDF ↗</a>`;
    }
    return accessAction(p) || `<span class="badge">无本地 PDF</span>`;
  }

  function cardHtml(p, opts) {
    const o = opts || {};
    const typeBadges = (p.article_types || []).filter(t => t !== "期刊")
      .map(t => `<span class="badge gold">${esc(t)}</span>`).join("");
    const kicker = o.kicker === false ? "" : `<div class="pc-kicker">${boardBadges(p)}${typeBadges}${journalBadges(p)}<span class="badge">${esc(p.regime_display || p.regime || "—")}</span>${p.methods && p.methods[0] ? `<span class="badge blue">${esc(p.methods[0])}</span>` : ""}${citationBadge(p)}${o.lib ? referenceBadge(p) : ""}</div>`;
    const abstract = o.abstract ? `<p class="lc-abs">${esc(p.abstract_zh || p.gist || "")}</p>` : "";
    const accent = accentOf(p);
    const accentVar = accent === "heat" ? "red" : accent === "sep" ? "teal" : "gold";
    const both = o.lib && accent === "both";
    return `<article class="paper-card ${o.lib ? "lib-card" : ""}${both ? " both" : ""}"${both ? "" : ` style="--accent:var(--${accentVar})"`}>
      <div class="${o.lib ? "lc-top" : ""}">
        <div class="${o.lib ? "lc-main" : ""}">
          ${kicker}
          <h3><a href="${esc(p.href)}">${esc(p.title)}</a></h3>
          <div class="${o.lib ? "lc-zh" : "zh-title"}">${esc(p.title_zh || "")}</div>
          <div class="${o.lib ? "lc-meta" : "pc-meta"}">
            <span>${esc(p.author_display || "—")}</span>
            <span>${esc(p.venue || p.journal || "")}${p.year ? ` · ${esc(p.year)}` : ""}</span>
            ${p.volume ? `<span>Vol. ${esc(p.volume)}${p.issue ? `(${esc(p.issue)})` : ""}</span>` : ""}
            ${p.pages ? `<span>${esc(p.pages)}</span>` : ""}
          </div>
          ${abstract}
          <div class="pc-tags">${tagsHtml(p, o.lib ? 6 : 4)}</div>
        </div>
        <div class="${o.lib ? "lc-actions" : ""}">
          ${o.lib ? "" : `<div class="pc-tags" style="margin:0">${pdfAction(p)}</div>`}
          ${citationHtml(p)}
          ${o.lib ? pdfAction(p) : ""}
        </div>
      </div>
    </article>`;
  }

  /* ---------- library ---------- */

  const library = $("#libraryList");
  if (library && DATA.papers) {
    const meta = DATA.meta || {};
    const state = {
      q: "", boards: new Set(), articleTypes: new Set(), journals: new Set(), eras: new Set(), regimes: new Set(),
      methods: new Set(), geometries: new Set(), gases: new Set(), focus: new Set(), tags: new Set(),
      sort: "year-desc",
    };

    const facets = [
      { key: "board", label: "板块", values: meta.boards || [], counts: meta.boardCounts || {} },
      { key: "articleType", label: "文章类型", values: meta.articleTypes || [], counts: meta.articleTypeCounts || {} },
      { key: "focus", label: "关注点", values: meta.focus || [], counts: meta.focusCounts || {} },
      { key: "tag", label: "标签", values: meta.tags || [], counts: meta.tagCounts || {} },
      { key: "era", label: "年代", values: meta.eras || [], counts: meta.eraCounts || {} },
      { key: "regime", label: "流态", values: meta.regimes || [], counts: meta.regimeCounts || {} },
      { key: "method", label: "方法", values: meta.methods || [], counts: meta.methodCounts || {} },
      { key: "geometry", label: "构型", values: meta.geometries || [], counts: meta.geometryCounts || {} },
      { key: "gas", label: "真实气体", values: meta.gases || [], counts: meta.gasCounts || {} },
      { key: "journal", label: "期刊目录", values: meta.journals || [], counts: meta.journalCounts || {} },
    ];

    const map = { board: "boards", articleType: "articleTypes", journal: "journals", era: "eras", regime: "regimes", method: "methods", geometry: "geometries", gas: "gases", focus: "focus", tag: "tags" };
    const paramName = { board: "board", articleType: "atype", journal: "journal", era: "era", regime: "regime", method: "method", geometry: "geom", gas: "gas", focus: "focus", tag: "tag" };

    function buildFacets() {
      $$("[data-facets]").forEach(row => {
        const key = row.getAttribute("data-facets");
        const f = facets.find(x => x.key === key) || { values: [], counts: {} };
        const chips = document.createElement("div");
        chips.className = "chips";
        chips.innerHTML = f.values.map(v => {
          const c = (f.counts || {})[v] || 0;
          const special = v === "课题组文章" ? " group" : v === "非期刊" ? " non" : "";
          return `<button type="button" class="chip${special}" data-facet="${key}" data-value="${esc(v)}">${esc(v)} <span class="cnt">${c}</span></button>`;
        }).join("");
        row.appendChild(chips);
      });
    }

    function syncChips() {
      let total = 0;
      $$("[data-facets]").forEach(row => {
        const key = row.getAttribute("data-facets");
        const set = state[map[key]];
        const n = set ? set.size : 0;
        total += n;
        const stateEl = row.querySelector(".facet-state");
        if (stateEl) stateEl.textContent = n ? `已选 ${n}` : "";
        row.classList.toggle("has-selection", n > 0);
        if (n > 0 && row.tagName === "DETAILS") row.open = true;
      });
      const shellState = $("#facetShellState");
      if (shellState) shellState.textContent = total ? `已选 ${total} 项` : "";
      $$(".chip[data-facet]").forEach(chip => {
        const set = state[map[chip.getAttribute("data-facet")]];
        chip.classList.toggle("on", set && set.has(chip.getAttribute("data-value")));
      });
    }

    function matches(p) {
      if (state.boards.size && !state.boards.has("__any")) {
        if (!(p.board || []).some(b => state.boards.has(b))) return false;
      }
      if (state.articleTypes.size && !(p.article_types || []).some(t => state.articleTypes.has(t))) return false;
      if (state.journals.size) {
        const jt = p.journal_tags || [];
        const ok = Array.from(state.journals).some(j =>
          j === "课题组文章" ? (p.tags || []).includes("课题组文章") : jt.includes(j)
        );
        if (!ok) return false;
      }
      if (state.eras.size && !state.eras.has(p.era)) return false;
      if (state.regimes.size) {
        const pr = p.regimes || (p.regime ? [p.regime] : []);
        const hit = Array.from(state.regimes).some(r => r === "多流态" ? pr.length > 1 : pr.includes(r));
        if (!hit) return false;
      }
      if (state.methods.size && !(p.methods || []).some(m => state.methods.has(m))) return false;
      if (state.geometries.size && !(p.geometry || []).some(g => state.geometries.has(g))) return false;
      if (state.gases.size) {
        const gas = p.real_gas || [];
        const ok = Array.from(state.gases).some(g => g === "真实气体效应" ? gas.length > 0 : gas.includes(g));
        if (!ok) return false;
      }
      if (state.focus.size && !(p.focus || []).some(f => state.focus.has(f))) return false;
      if (state.tags.size && !(p.tags || []).some(t => state.tags.has(t))) return false;
      if (state.q) {
        const hay = [
          p.title, p.title_zh, p.author_display, p.venue, p.journal, p.publisher,
          p.place, p.year, p.era, p.abstract_zh,
          p.gist, p.main_work, p.conclusions, p.background, p.method_detail,
          p.findings, p.limits, p.derivation_idea, (p.derivation_steps || []).join(" "),
          p.problem_solved, (p.key_findings || []).join(" "),
          p.regime_display, (p.tags || []).join(" "),
          (p.article_types || []).join(" "), (p.journal_tags || []).join(" "),
          (p.methods || []).join(" "), (p.geometry || []).join(" "), (p.focus || []).join(" "), p.doi,
        ].join(" ").toLowerCase();
        if (!hay.includes(state.q.toLowerCase())) return false;
      }
      return true;
    }

    function sortPapers(list) {
      const arr = list.slice();
      const count = (v) => (v == null || v === "" || isNaN(Number(v))) ? -1 : Number(v);
      const byYear = (a, b) => (parseInt(b.year) || 0) - (parseInt(a.year) || 0);
      const cmp = {
        "year-desc": (a, b) => byYear(a, b) || a.title.localeCompare(b.title),
        "year-asc": (a, b) => -byYear(a, b) || a.title.localeCompare(b.title),
        "citations": (a, b) => count(b.cited_by) - count(a.cited_by) || byYear(a, b) || a.title.localeCompare(b.title),
        "references": (a, b) => count(b.reference_count) - count(a.reference_count) || byYear(a, b) || a.title.localeCompare(b.title),
        "connections": (a, b) => (b.connections || 0) - (a.connections || 0) || byYear(a, b),
        "title": (a, b) => String(a.title).localeCompare(String(b.title)),
      };
      return arr.sort(cmp[state.sort] || cmp["year-desc"]);
    }

    function render() {
      const list = sortPapers((DATA.papers || []).filter(matches));
      $("#libCount").textContent = list.length;
      $("#libTotal").textContent = DATA.papers.length;
      if (!list.length) {
        library.innerHTML = `<div class="empty"><strong>没有匹配的文献</strong>尝试减少筛选条件，或换一个关键词。</div>`;
      } else {
        library.innerHTML = list.map(p => cardHtml(p, { lib: true, abstract: true })).join("");
      }
      renderActive();
      syncChips();
      updateUrl();
    }

    function renderActive() {
      const box = $("#activeFilters");
      if (!box) return;
      const parts = [];
      const labels = { boards: "板块", articleTypes: "文章类型", journals: "期刊目录", eras: "年代", regimes: "流态", methods: "方法", geometries: "构型", gases: "真实气体", focus: "关注点", tags: "标签" };
      Object.keys(labels).forEach(k => {
        state[k].forEach(v => {
          parts.push(`<button type="button" class="af" data-remove="${k}" data-value="${esc(v)}">${labels[k]}：<b>${esc(v)}</b> ×</button>`);
        });
      });
      if (state.q) parts.push(`<button type="button" class="af" data-remove="q" data-value="">搜索：<b>${esc(state.q)}</b> ×</button>`);
      box.innerHTML = parts.join("");
    }

    let urlTimer = null;
    function updateUrl() {
      clearTimeout(urlTimer);
      urlTimer = setTimeout(() => {
        const q = new URLSearchParams();
        if (state.q) q.set("q", state.q);
        if (state.boards.size) q.set("board", Array.from(state.boards).join(","));
        if (state.articleTypes.size) q.set("atype", Array.from(state.articleTypes).join(","));
        if (state.journals.size) q.set("journal", Array.from(state.journals).join(","));
        if (state.eras.size) q.set("era", Array.from(state.eras).join(","));
        if (state.regimes.size) q.set("regime", Array.from(state.regimes).join(","));
        if (state.methods.size) q.set("method", Array.from(state.methods).join(","));
        if (state.geometries.size) q.set("geom", Array.from(state.geometries).join(","));
        if (state.gases.size) q.set("gas", Array.from(state.gases).join(","));
        if (state.focus.size) q.set("focus", Array.from(state.focus).join(","));
        if (state.tags.size) q.set("tag", Array.from(state.tags).join(","));
        if (state.sort !== "year-desc") q.set("sort", state.sort);
        const s = q.toString();
        try {
          history.replaceState(null, "", s ? `?${s}` : location.pathname);
        } catch (err) {
          /* file:// in some browsers forbids history updates; filters still work */
        }
      }, 160);
    }

    function readUrl() {
      const q = new URLSearchParams(location.search);
      state.q = q.get("q") || "";
      const read = (key, set) => {
        const raw = q.get(key);
        if (raw) raw.split(",").filter(Boolean).forEach(v => set.add(v));
      };
      read("board", state.boards);
      read("atype", state.articleTypes);
      read("journal", state.journals);
      read("era", state.eras);
      read("regime", state.regimes);
      read("method", state.methods);
      read("geom", state.geometries);
      read("gas", state.gases);
      read("focus", state.focus);
      read("tag", state.tags);
      state.sort = q.get("sort") || "year-desc";
      const input = $("#libSearch");
      if (input) input.value = state.q;
      const sort = $("#libSort");
      if (sort) sort.value = state.sort;
      // 首次载入时若网址里已带筛选条件（例如从首页“理论建模”跳入），
      // 自动展开整个检索切面，避免筛选状态被折叠遮住。
      const active = ["boards", "articleTypes", "journals", "eras", "regimes", "methods", "geometries", "gases", "focus", "tags"]
        .some(k => state[k].size);
      const shell = $("#facetShell");
      if (shell && active) shell.open = true;
    }

    buildFacets();
    readUrl();
    syncChips();
    render();

    document.addEventListener("click", function (e) {
      const chip = e.target.closest(".chip[data-facet]");
      if (chip) {
        const key = map[chip.getAttribute("data-facet")];
        const val = chip.getAttribute("data-value");
        if (state[key].has(val)) state[key].delete(val);
        else state[key].add(val);
        render();
        return;
      }
      const rm = e.target.closest("[data-remove]");
      if (rm) {
        const key = rm.getAttribute("data-remove");
        const val = rm.getAttribute("data-value");
        if (key === "q") { state.q = ""; const input = $("#libSearch"); if (input) input.value = ""; }
        else if (state[key]) state[key].delete(val);
        render();
      }
    });

    const input = $("#libSearch");
    if (input) {
      let t = null;
      input.addEventListener("input", () => {
        clearTimeout(t);
        t = setTimeout(() => { state.q = input.value.trim(); render(); }, 110);
      });
    }

    const sort = $("#libSort");
    if (sort) sort.addEventListener("change", () => { state.sort = sort.value; render(); });

    const reset = $("#libReset");
    if (reset) reset.addEventListener("click", () => {
      state.q = "";
      ["boards", "articleTypes", "journals", "eras", "regimes", "methods", "geometries", "gases", "focus", "tags"].forEach(k => state[k].clear());
      state.sort = "year-desc";
      if (input) input.value = "";
      if (sort) sort.value = "year-desc";
      render();
    });
  }

  /* ---------- citations ---------- */

  document.addEventListener("change", function (e) {
    const sel = e.target.closest("[data-cite-select]");
    if (!sel) return;
    const details = sel.closest("[data-cite]");
    const p = byId.get(details.getAttribute("data-pid"));
    const pre = $("[data-cite-pre]", details);
    if (p && pre && p.citations && p.citations[sel.value]) pre.textContent = p.citations[sel.value].text;
  });

  document.addEventListener("click", function (e) {
    const copy = e.target.closest("[data-copy-cite]");
    if (copy) {
      const details = copy.closest("[data-cite]");
      const pre = $("[data-cite-pre]", details);
      const text = pre ? pre.textContent : "";
      copyText(text).then(ok => {
        const old = copy.textContent;
        copy.textContent = ok ? "已复制" : "复制失败";
        copy.classList.add("teal");
        setTimeout(() => { copy.textContent = old; copy.classList.remove("teal"); }, 1400);
      });
      return;
    }
    const copyPath = e.target.closest("[data-copy-path]");
    if (copyPath) {
      copyText(copyPath.getAttribute("data-copy-path")).then(ok => {
        const old = copyPath.textContent;
        copyPath.textContent = ok ? "已复制路径" : "复制失败";
        setTimeout(() => { copyPath.textContent = old; }, 1400);
      });
    }
  });

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(() => true).catch(() => fallbackCopy(text));
    }
    return Promise.resolve(fallbackCopy(text));
  }

  function fallbackCopy(text) {
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      ta.remove();
      return ok;
    } catch (e) { return false; }
  }

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".cite")) {
      $$("details.cite[open]").forEach(d => d.removeAttribute("open"));
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") $$("details.cite[open]").forEach(d => d.removeAttribute("open"));
  });

  /* ---------- reveal ---------- */

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.08 });
    $$(".reveal").forEach(el => io.observe(el));
  } else {
    $$(".reveal").forEach(el => el.classList.add("in"));
  }
})();
