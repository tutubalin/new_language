"""Load First Nex (the primer) and check drills against the parser."""

from __future__ import annotations

import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

from .ast_nodes import Atom, Frame, Node, Num, Program, Ref, Spell
from .parser import ParseError, parse
from .serialize import serialize

PRIMER = Path(__file__).resolve().parent.parent / "book" / "primer.md"


def _extract_exercises(body: str) -> tuple[str, list[dict]]:
    """Pull <!--ex ... --> JSON blocks without a DOTALL regex."""
    exercises: list[dict] = []
    out: list[str] = []
    i = 0
    start_tag = "<!--ex"
    end_tag = "-->"
    while i < len(body):
        j = body.find(start_tag, i)
        if j < 0:
            out.append(body[i:])
            break
        out.append(body[i:j])
        k = body.find(end_tag, j + len(start_tag))
        if k < 0:
            out.append(body[j:])
            break
        blob = body[j + len(start_tag) : k].strip()
        exercises.append(json.loads(blob))
        i = k + len(end_tag)
    return "".join(out).strip(), exercises


def _split_chapters(md: str) -> list[dict]:
    parts = re.split(r"^# ", md, flags=re.MULTILINE)
    chapters = []
    n = 0
    for part in parts:
        if not part.strip():
            continue
        title, _, body = part.partition("\n")
        body_clean, exercises = _extract_exercises(body)
        chapters.append(
            {
                "id": f"ch-{n:02d}",
                "n": n,
                "title": title.strip(),
                "markdown": body_clean,
                "html": md_to_html(body_clean),
                "exercises": exercises,
            }
        )
        n += 1
    return chapters


@lru_cache(maxsize=1)
def load_primer() -> dict:
    text = PRIMER.read_text(encoding="utf-8")
    chapters = _split_chapters(text)
    toc = [
        {"id": c["id"], "n": c["n"], "title": c["title"], "drills": len(c["exercises"])}
        for c in chapters
    ]
    return {
        "title": chapters[0]["title"] if chapters else "First Nex",
        "chapters": chapters,
        "toc": toc,
        "drill_count": sum(len(c["exercises"]) for c in chapters),
    }


def public_course() -> dict:
    data = load_primer()
    chapters = []
    for c in data["chapters"]:
        drills = []
        for ex in c["exercises"]:
            item = {k: v for k, v in ex.items() if k not in {"answer", "accept"}}
            drills.append(item)
        chapters.append(
            {
                "id": c["id"],
                "n": c["n"],
                "title": c["title"],
                "html": c["html"],
                "exercises": drills,
            }
        )
    return {
        "title": "First Nex",
        "subtitle": "A primer from zero",
        "toc": data["toc"],
        "chapters": chapters,
        "drill_count": data["drill_count"],
    }


def find_exercise(ex_id: str) -> dict | None:
    for c in load_primer()["chapters"]:
        for ex in c["exercises"]:
            if ex.get("id") == ex_id:
                return ex
    return None


def check_exercise(ex_id: str, text: str = "", choice: int | None = None) -> dict:
    ex = find_exercise(ex_id)
    if ex is None:
        return {"ok": False, "error": f"unknown drill {ex_id}"}
    kind = ex.get("type")
    if kind == "choice":
        if choice is None:
            return {"ok": False, "correct": False, "error": "pick an answer"}
        right = int(ex["answer"])
        return {
            "ok": True,
            "correct": choice == right,
            "expected": right,
            "message": "Yes." if choice == right else "Not that one. Read the chapter once more.",
        }
    if kind == "match":
        return _check_match(ex, text or "")
    return {"ok": False, "error": f"unhandled drill type {kind}"}


def _check_match(ex: dict, text: str) -> dict:
    text = text.strip()
    if not text:
        return {"ok": False, "correct": False, "error": "write some Nex first"}
    try:
        got = parse(text)
    except ParseError as e:
        return {
            "ok": True,
            "correct": False,
            "parsed": False,
            "error": str(e),
            "message": f"The parser refused it: {e}",
        }
    last_err = "did not match"
    for acc in ex.get("accept") or []:
        try:
            want = parse(acc)
        except ParseError:
            continue
        ok, why = programs_match(got, want, acc)
        if ok:
            return {
                "ok": True,
                "correct": True,
                "parsed": True,
                "message": "Yes. The parser agrees.",
                "yours": serialize(got.canonical(), pretty=True),
            }
        last_err = why
    return {
        "ok": True,
        "correct": False,
        "parsed": True,
        "message": f"It parses, but it is not this meaning. {last_err}",
        "yours": serialize(got.canonical(), pretty=True),
        "hint": ex.get("hint"),
    }


def programs_match(got: Program, want: Program, accepted_src: str) -> tuple[bool, str]:
    src = accepted_src.strip()
    ignore_illoc = not re.match(r"^(asrt|ask|cmd|opt|exch)\b", src)
    if not ignore_illoc and len(got.statements) != len(want.statements):
        return False, f"Expected {len(want.statements)} sentence(s)."
    if ignore_illoc:
        if not got.statements:
            return False, "Empty."
        return frames_match(got.statements[0].frame, want.statements[0].frame)
    for g, w in zip(got.statements, want.statements):
        if g.illoc != w.illoc:
            return False, f"Illocution should be {w.illoc}, not {g.illoc}."
        ok, why = frames_match(g.frame, w.frame)
        if not ok:
            return False, why
    return True, "ok"


def frames_match(g: Frame, w: Frame, path: str = "frame") -> tuple[bool, str]:
    if g.head != w.head:
        return False, f"{path}: head `{g.head}` vs `{w.head}`."
    if set(g.features) != set(w.features):
        return False, (
            f"{path}: features {sorted(set(g.features))} vs {sorted(set(w.features))}."
        )
    if w.binding is not None and g.binding != w.binding:
        return False, f"{path}: bind ${w.binding}."
    g_named = [(r, n) for r, n in g.slots if r]
    w_named = [(r, n) for r, n in w.slots if r]
    g_bare = [n for r, n in g.slots if not r]
    w_bare = [n for r, n in w.slots if not r]
    if Counter(r for r, _ in g_named) != Counter(r for r, _ in w_named):
        return False, f"{path}: roles {[r for r, _ in g_named]} vs {[r for r, _ in w_named]}."
    used = [False] * len(g_named)
    for wr, wn in w_named:
        found = False
        for i, (gr, gn) in enumerate(g_named):
            if used[i] or gr != wr:
                continue
            ok, why = nodes_match(gn, wn, f"{path}.{wr}")
            if ok:
                used[i] = True
                found = True
                break
        if not found:
            return False, f"{path}: missing or wrong `{wr}`."
    if len(g_bare) != len(w_bare):
        return False, f"{path}: expected {len(w_bare)} bare arguments."
    for i, (gn, wn) in enumerate(zip(g_bare, w_bare)):
        ok, why = nodes_match(gn, wn, f"{path}[{i}]")
        if not ok:
            return False, why
    return True, "ok"


def nodes_match(g: Node, w: Node, path: str) -> tuple[bool, str]:
    if isinstance(w, Atom):
        if not isinstance(g, Atom) or g.form != w.form:
            got = getattr(g, "form", type(g).__name__)
            return False, f"{path}: `{got}` vs `{w.form}`."
        return True, "ok"
    if isinstance(w, Ref):
        if not isinstance(g, Ref) or g.n != w.n:
            return False, f"{path}: expected ${w.n}."
        return True, "ok"
    if isinstance(w, Num):
        if not isinstance(g, Num) or g.value != w.value:
            return False, f"{path}: expected number {w.value}."
        return True, "ok"
    if isinstance(w, Spell):
        if not isinstance(g, Spell) or g.text.lower() != w.text.lower():
            return False, f"{path}: spelling."
        return True, "ok"
    if isinstance(w, Frame) and isinstance(g, Frame):
        return frames_match(g, w, path)
    if isinstance(g, Frame) and isinstance(w, Atom):
        return False, f"{path}: expected atom `{w.form}`."
    if isinstance(g, Atom) and isinstance(w, Frame):
        return False, f"{path}: expected a frame headed `{w.head}`."
    return False, f"{path}: type mismatch."


def all_accept_parses() -> list[str]:
    problems = []
    for c in load_primer()["chapters"]:
        for ex in c["exercises"]:
            for acc in ex.get("accept") or []:
                try:
                    parse(acc)
                except ParseError as e:
                    problems.append(f"{ex['id']}: {acc!r} → {e}")
    return problems


def md_to_html(md: str) -> str:
    """Line-based markdown → HTML. No DOTALL regexes."""
    md = md.replace("\r\n", "\n").replace("\r", "\n")
    lines = md.split("\n")
    parts: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.startswith("```"):
            i += 1
            buf: list[str] = []
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            if i < n:
                i += 1
            parts.append(
                '<pre class="code"><code>' + _esc("\n".join(buf)) + "</code></pre>"
            )
            continue
        if line.strip() == "<details>":
            i += 1
            summary = "Notes"
            if i < n and lines[i].strip().startswith("<summary>"):
                raw = lines[i].strip()
                summary = raw.replace("<summary>", "").replace("</summary>", "")
                i += 1
            inner: list[str] = []
            while i < n and lines[i].strip() != "</details>":
                inner.append(lines[i])
                i += 1
            if i < n:
                i += 1
            parts.append(
                "<details><summary>"
                + _esc(summary)
                + "</summary>"
                + md_to_html("\n".join(inner))
                + "</details>"
            )
            continue
        if line.startswith("### "):
            parts.append("<h3>" + _inline(line[4:]) + "</h3>")
            i += 1
            continue
        if line.startswith("## "):
            parts.append("<h2>" + _inline(line[3:]) + "</h2>")
            i += 1
            continue
        if line.startswith("|"):
            rows: list[str] = []
            while i < n and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            parts.append(_table(rows))
            continue
        if re.match(r"^[-*] ", line) or re.match(r"^\d+\. ", line):
            items: list[str] = []
            ordered = bool(re.match(r"^\d+\. ", line))
            tag = "ol" if ordered else "ul"
            while i < n and (re.match(r"^[-*] ", lines[i]) or re.match(r"^\d+\. ", lines[i])):
                items.append(
                    "<li>"
                    + _inline(re.sub(r"^([-*] |\d+\. )", "", lines[i]))
                    + "</li>"
                )
                i += 1
            parts.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        if line.strip() == "":
            i += 1
            continue
        para = [line]
        i += 1
        while i < n:
            nxt = lines[i]
            if nxt.strip() == "":
                break
            if nxt.startswith(("#", "|", "```", "<details", "</details")):
                break
            if re.match(r"^[-*] ", nxt) or re.match(r"^\d+\. ", nxt):
                break
            para.append(nxt)
            i += 1
        parts.append("<p>" + _inline(" ".join(para)) + "</p>")
    return "\n".join(parts)


def _table(rows: list[str]) -> str:
    body = []
    header = True
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        stripped = [c.replace(":", "").replace(" ", "") for c in cells]
        if stripped and all(s and set(s) <= {"-"} for s in stripped):
            header = False
            continue
        tag = "th" if header else "td"
        body.append(
            "<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>"
        )
        header = False
    return "<table>" + "".join(body) + "</table>"


def _inline(text: str) -> str:
    text = _esc(text)
    out: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j < 0:
                out.append(text[i])
                i += 1
                continue
            out.append("<code>" + text[i + 1 : j] + "</code>")
            i = j + 1
            continue
        if text.startswith("**", i):
            j = text.find("**", i + 2)
            if j < 0:
                out.append(text[i])
                i += 1
                continue
            out.append("<strong>" + text[i + 2 : j] + "</strong>")
            i = j + 2
            continue
        if text[i] == "*" and i + 1 < len(text) and text[i + 1] != " ":
            j = text.find("*", i + 1)
            if j < 0:
                out.append(text[i])
                i += 1
                continue
            out.append("<em>" + text[i + 1 : j] + "</em>")
            i = j + 1
            continue
        if text[i] == "[":
            close = text.find("]", i + 1)
            if close > i and close + 1 < len(text) and text[close + 1] == "(":
                endp = text.find(")", close + 2)
                if endp > close:
                    label = text[i + 1 : close]
                    href = text[close + 2 : endp]
                    out.append(f'<a href="{href}">{label}</a>')
                    i = endp + 1
                    continue
        out.append(text[i])
        i += 1
    return "".join(out)


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
