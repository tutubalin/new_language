/* Nex playground */

const $ = (id) => document.getElementById(id);

async function api(path, body) {
  const opt = body
    ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }
    : {};
  const r = await fetch(path, opt);
  return r.json();
}

function chip(t) {
  const s = document.createElement("span");
  s.className = "chip " + (t.kind || "");
  s.title = t.gloss || "";
  s.textContent = t.tok;
  return s;
}

function renderStream(tokens, into) {
  into.replaceChildren();
  (tokens || []).forEach((t) => into.appendChild(chip(t)));
}

function renderTree(ast, host) {
  host.replaceChildren(nodeEl(ast));
}

function nodeEl(n) {
  if (!n) return document.createTextNode("—");
  if (n.type === "program") {
    const d = document.createElement("div");
    n.statements.forEach((s) => d.appendChild(nodeEl(s)));
    return d;
  }
  if (n.type === "stmt") {
    const d = document.createElement("div");
    const ill = document.createElement("div");
    ill.innerHTML = `<span class="role-lab">illoc</span> <span class="head">${esc(n.illoc)}</span>`;
    d.appendChild(ill);
    d.appendChild(nodeEl(n.frame));
    return d;
  }
  if (n.type === "frame") {
    const d = document.createElement("div");
    d.className = "frame-box";
    const h = document.createElement("div");
    const feats = (n.features || []).map((f) => `<span class="feat">${esc(f)}</span>`).join("");
    const bind = n.binding != null ? ` <span class="role-lab">= $${n.binding}</span>` : "";
    h.innerHTML = `<span class="head">${esc(n.head)}</span> ${feats}${bind}`;
    d.appendChild(h);
    (n.slots || []).forEach((sl) => {
      const row = document.createElement("div");
      row.style.marginLeft = "8px";
      if (sl.role) {
        const lab = document.createElement("span");
        lab.className = "role-lab";
        lab.textContent = sl.role + " ";
        row.appendChild(lab);
      }
      row.appendChild(nodeEl(sl.arg));
      d.appendChild(row);
    });
    return d;
  }
  const s = document.createElement("span");
  s.style.fontFamily = "var(--mono)";
  if (n.type === "ref") s.textContent = "$" + n.n;
  else if (n.type === "num") s.textContent = String(n.value);
  else if (n.type === "atom") s.textContent = n.form;
  else if (n.type === "spell") s.textContent = n.text;
  else s.textContent = JSON.stringify(n);
  return s;
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function showResult(res, fromEn) {
  $("en-err").textContent = "";
  $("nx-err").textContent = "";
  $("en-notes").replaceChildren();
  if (!res.ok) {
    const el = fromEn ? $("en-err") : $("nx-err");
    el.textContent = res.error || "error";
    return;
  }
  $("nx-in").value = res.nex;
  $("gloss").textContent = res.gloss;
  renderStream(res.tokens, $("stream"));
  $("stream-meta").textContent = res.token_count + " tokens · ids are kind+field+root, not BPE accidents";
  renderTree(res.ast, $("tree"));
  (res.notes || []).forEach((n) => {
    const d = document.createElement("div");
    d.className = "note";
    d.textContent = n;
    $("en-notes").appendChild(d);
  });
}

async function translateEn() {
  const text = $("en-in").value;
  showResult(await api("/api/en", { text }), true);
}

async function parseNx() {
  const text = $("nx-in").value;
  showResult(await api("/api/parse", { text }), false);
}

let EXAMPLES = [];
let AMBIG = [];

async function boot() {
  $("btn-en").onclick = translateEn;
  $("btn-parse").onclick = parseNx;
  $("btn-canon").onclick = parseNx;
  $("btn-cmp").onclick = runCompare;
  $("lex-q").oninput = drawLex;
  $("lex-k").onchange = drawLex;

  const pack = await api("/api/examples");
  EXAMPLES = pack.examples || [];
  AMBIG = pack.ambiguous || [];
  const list = $("ex-list");
  EXAMPLES.forEach((ex) => {
    const b = document.createElement("button");
    b.className = "ex";
    b.innerHTML = `<b>${esc(ex.title)}</b>${esc(ex.en)}`;
    b.onclick = async () => {
      $("en-in").value = ex.en;
      $("nx-in").value = ex.nex;
      showResult(await api("/api/parse", { text: ex.nex }), false);
    };
    list.appendChild(b);
  });
  $("btn-ex").onclick = () => {
    const ex = EXAMPLES[Math.floor(Math.random() * EXAMPLES.length)];
    if (ex) {
      $("en-in").value = ex.en;
      translateEn();
    }
  };

  drawAmbig();
  await runCompare();
  drawMorph();
  LEX = await api("/api/lexicon");
  drawLex();
  drawGlyphs();
  const ids = await api("/api/ids");
  $("id-note").textContent = ids.note || "";
  // initial parse of default english
  translateEn();
}

function drawAmbig() {
  const host = $("ambig");
  const groups = {};
  AMBIG.forEach((a) => {
    (groups[a.en] ||= []).push(a);
  });
  Object.entries(groups).forEach(([en, rows]) => {
    const h = document.createElement("h4");
    h.style.fontFamily = "var(--serif)";
    h.style.fontStyle = "italic";
    h.style.marginBottom = "4px";
    h.textContent = en;
    host.appendChild(h);
    const pair = document.createElement("div");
    pair.className = "pair";
    rows.forEach((r) => {
      const col = document.createElement("div");
      col.innerHTML = `<p class="reading">${esc(r.reading)}</p><div class="nx">${esc(r.nex)}</div>`;
      col.querySelector(".nx").style.cursor = "pointer";
      col.querySelector(".nx").onclick = async () => {
        $("nx-in").value = r.nex;
        $("en-in").value = r.en;
        showResult(await api("/api/parse", { text: r.nex }), false);
        document.getElementById("studio").scrollIntoView();
      };
      pair.appendChild(col);
    });
    host.appendChild(pair);
  });
}

async function runCompare() {
  const r = await api("/api/compare", { english: $("cmp-en").value, nex: $("cmp-nx").value });
  const enH = $("cmp-en-toks");
  enH.replaceChildren();
  (r.english_tokens || []).forEach((t) => {
    const s = document.createElement("span");
    s.textContent = t;
    enH.appendChild(s);
  });
  $("cmp-en-n").textContent = r.english_count + " pieces";
  if (r.nex) {
    renderStream(r.nex.tokens, $("cmp-nx-toks"));
    $("cmp-nx-n").textContent = r.nex.count + " atoms" + (r.nex.error ? " · " + r.nex.error : "");
  }
}

async function drawMorph() {
  const rows = await api("/api/morph");
  const tbl = document.createElement("table");
  tbl.innerHTML =
    "<thead><tr><th>English</th><th>BPE</th><th>Nex</th><th>shared stem</th></tr></thead>";
  const tb = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const bpe = (row.english_tokens || []).map((t) => t.replace(/ /g, "·")).join(" │ ");
    const nx = row.nex ? row.nex.tokens.map((t) => t.tok).filter((t) => !("().".includes(t))).join(" ") : "";
    tr.innerHTML = `<td>${esc(row.english)}</td><td class="mono">${esc(bpe)}</td><td class="mono">${esc(nx)}</td><td>${esc(row.note)}</td>`;
    tb.appendChild(tr);
  });
  tbl.appendChild(tb);
  $("morph-table").replaceChildren(tbl);
}

let LEX = [];

function drawLex() {
  const q = ($("lex-q").value || "").toLowerCase();
  const k = $("lex-k").value;
  const host = $("lex-grid");
  host.replaceChildren();
  LEX.filter((e) => {
    if (k && e.kind !== k) return false;
    if (!q) return true;
    return (
      e.form.includes(q) ||
      e.gloss.toLowerCase().includes(q) ||
      e.english.join(" ").toLowerCase().includes(q) ||
      e.field.includes(q)
    );
  }).forEach((e) => {
    const d = document.createElement("div");
    d.className = "lex-card";
    d.innerHTML = `<div class="form">${esc(e.form)}</div>
      <div class="meta">${esc(e.kind)} · ${esc(e.field)}</div>
      <div>${esc(e.gloss)}</div>
      <div class="meta">${esc(e.english.slice(0, 4).join(" / "))}</div>`;
    host.appendChild(d);
  });
}

function glyphSvg(kind, hue) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("width", "72");
  svg.setAttribute("height", "72");
  svg.setAttribute("viewBox", "0 0 72 72");
  const mk = (tag, attrs) => {
    const el = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
    return el;
  };
  svg.appendChild(mk("rect", { x: 0, y: 0, width: 72, height: 72, fill: "#16130f" }));
  const stroke = hue || "#e4c36a";
  if (kind === "evt") {
    svg.appendChild(mk("polygon", { points: "16,16 56,36 16,56", fill: "none", stroke, "stroke-width": 3 }));
  } else if (kind === "kind") {
    svg.appendChild(mk("circle", { cx: 36, cy: 36, r: 20, fill: "none", stroke, "stroke-width": 3 }));
  } else if (kind === "qual") {
    svg.appendChild(mk("rect", { x: 16, y: 16, width: 40, height: 40, rx: 6, fill: "none", stroke, "stroke-width": 3 }));
  } else if (kind === "role") {
    svg.appendChild(mk("rect", { x: 10, y: 26, width: 52, height: 20, rx: 10, fill: "none", stroke, "stroke-width": 3 }));
  } else if (kind === "op" || kind === "feat") {
    svg.appendChild(mk("polygon", { points: "36,12 60,36 36,60 12,36", fill: "none", stroke, "stroke-width": 3 }));
  } else {
    svg.appendChild(mk("line", { x1: 18, y1: 36, x2: 54, y2: 36, stroke, "stroke-width": 3 }));
  }
  svg.appendChild(mk("circle", { cx: 36, cy: 36, r: 3, fill: stroke }));
  return svg;
}

function drawGlyphs() {
  const samples = [
    { form: "doni", kind: "evt", hue: "#f0a36a" },
    { form: "pamo", kind: "kind", hue: "#a8d4b6" },
    { form: "ruga", kind: "qual", hue: "#e4c36a" },
    { form: "agt", kind: "role", hue: "#b7bef5" },
    { form: "past", kind: "feat", hue: "#e0b8f5" },
    { form: "and", kind: "op", hue: "#e0b8f5" },
  ];
  const host = $("glyphs");
  samples.forEach((s) => {
    const fig = document.createElement("figure");
    fig.className = "glyph-item";
    fig.appendChild(glyphSvg(s.kind, s.hue));
    const c = document.createElement("figcaption");
    c.textContent = s.form + " · " + s.kind;
    fig.appendChild(c);
    host.appendChild(fig);
  });
}

boot().catch((err) => {
  console.error(err);
  $("en-err").textContent = String(err);
});
