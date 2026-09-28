const $ = (sel) => document.querySelector(sel);

const KEY = "nex-primer-v1";

function loadProgress() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "{}");
  } catch {
    return {};
  }
}
function saveProgress(p) {
  localStorage.setItem(KEY, JSON.stringify(p));
}

let COURSE = null;
let progress = loadProgress();

async function boot() {
  COURSE = await fetch("/api/course").then((r) => r.json());
  const hash = (location.hash || "#ch-00").slice(1);
  drawToc();
  drawChapter(hash.startsWith("ch-") ? hash : "ch-00");
  window.addEventListener("hashchange", () => {
    const id = (location.hash || "#ch-00").slice(1);
    drawChapter(id);
  });
}

function drawToc() {
  const host = $("#toc");
  host.innerHTML = "<p class='kicker' style='margin:0 0 10px'>First Nex</p>";
  COURSE.toc.forEach((t) => {
    const a = document.createElement("a");
    a.href = "#" + t.id;
    const done = drillsDone(t.id);
    a.innerHTML =
      (t.n === 0 ? "Title" : t.n + ".") +
      " " +
      escapeHtml(t.title.replace(/^\d+\.\s*/, "")) +
      (t.drills ? `<small>${done}/${t.drills}</small>` : "");
    a.dataset.id = t.id;
    host.appendChild(a);
  });
  paintProgress();
}

function drillsDone(chId) {
  const ch = COURSE.chapters.find((c) => c.id === chId);
  if (!ch) return 0;
  return ch.exercises.filter((e) => progress[e.id]).length;
}

function paintProgress() {
  const total = COURSE.drill_count || 0;
  const n = Object.values(progress).filter(Boolean).length;
  $("#progress-lab").textContent = total ? `${n} / ${total} drills` : "";
  document.querySelectorAll(".toc a").forEach((a) => {
    a.classList.toggle("on", a.dataset.id === location.hash.slice(1));
  });
}

function drawChapter(id) {
  const ch = COURSE.chapters.find((c) => c.id === id) || COURSE.chapters[0];
  location.hash = ch.id;
  const host = $("#book");
  const kicker = ch.n === 0 ? "A primer from zero" : `Chapter ${ch.n}`;
  host.innerHTML = `
    <div class="chapter-kicker">${kicker}</div>
    <h1>${escapeHtml(ch.title)}</h1>
    <div class="prose-body">${ch.html}</div>
    <div id="drills"></div>
    <div class="nav-ch" id="nav-ch"></div>
  `;
  const drills = $("#drills");
  if (ch.exercises.length) {
    const h = document.createElement("h2");
    h.textContent = "Drills";
    drills.appendChild(h);
    ch.exercises.forEach((ex, i) => drills.appendChild(renderDrill(ex, i)));
  }
  const idx = COURSE.chapters.indexOf(ch);
  const nav = $("#nav-ch");
  if (idx > 0) {
    const prev = COURSE.chapters[idx - 1];
    const a = document.createElement("a");
    a.href = "#" + prev.id;
    a.textContent = "← " + prev.title;
    nav.appendChild(a);
  } else nav.appendChild(document.createElement("span"));
  if (idx < COURSE.chapters.length - 1) {
    const next = COURSE.chapters[idx + 1];
    const a = document.createElement("a");
    a.href = "#" + next.id;
    a.textContent = next.title + " →";
    nav.appendChild(a);
  }
  drawToc();
  window.scrollTo(0, 0);
}

function renderDrill(ex, i) {
  const d = document.createElement("div");
  d.className = "drill";
  d.id = "ex-" + ex.id;
  const done = progress[ex.id] ? '<span class="done-mark"> ✓</span>' : "";
  d.innerHTML = `<div class="tag">Drill ${i + 1}${done}</div><h4>${escapeHtml(ex.prompt)}</h4>`;
  if (ex.nex) {
    const pre = document.createElement("pre");
    pre.className = "code";
    pre.textContent = ex.nex;
    d.appendChild(pre);
  }
  if (ex.type === "choice") {
    const box = document.createElement("div");
    box.className = "choices";
    (ex.choices || []).forEach((c, n) => {
      const lab = document.createElement("label");
      lab.innerHTML = `<input type="radio" name="${ex.id}" value="${n}" /> <span>${escapeHtml(c)}</span>`;
      box.appendChild(lab);
    });
    d.appendChild(box);
  } else {
    const ta = document.createElement("textarea");
    ta.placeholder = ex.hint ? "hint: " + ex.hint : "write Nex here";
    ta.id = "in-" + ex.id;
    d.appendChild(ta);
  }
  const row = document.createElement("div");
  row.className = "row";
  const btn = document.createElement("button");
  btn.textContent = "Check";
  btn.onclick = () => submit(ex, d);
  row.appendChild(btn);
  d.appendChild(row);
  const fb = document.createElement("div");
  fb.className = "feedback";
  fb.hidden = true;
  d.appendChild(fb);
  return d;
}

async function submit(ex, root) {
  const fb = root.querySelector(".feedback");
  let payload = { id: ex.id };
  if (ex.type === "choice") {
    const picked = root.querySelector("input:checked");
    if (!picked) {
      fb.hidden = false;
      fb.className = "feedback no";
      fb.textContent = "Pick one.";
      return;
    }
    payload.choice = Number(picked.value);
  } else {
    payload.text = (root.querySelector("textarea") || {}).value || "";
  }
  const res = await fetch("/api/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then((r) => r.json());
  fb.hidden = false;
  if (res.correct) {
    fb.className = "feedback yes";
    fb.textContent = res.message || "Yes.";
    progress[ex.id] = true;
    saveProgress(progress);
    drawToc();
  } else {
    fb.className = "feedback no";
    fb.textContent = res.message || res.error || "Not yet.";
    if (res.yours) {
      fb.textContent += " Parser read: " + res.yours.replace(/\s+/g, " ");
    }
  }
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

boot().catch((err) => {
  $("#book").innerHTML = "<p>Could not load the primer: " + escapeHtml(err) + "</p>";
});
