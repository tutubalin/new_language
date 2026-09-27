"""Serialize Nex ASTs to text, model token streams, and English glosses."""

from __future__ import annotations

import re

from .ast_nodes import Atom, Frame, Node, Num, Program, Ref, Spell, Statement
from .lexicon import LEXICON, is_operator, lookup
from .parser import parse


def serialize(node: Program | Statement | Node, pretty: bool = True) -> str:
    if isinstance(node, Program):
        parts = [serialize(s, pretty=pretty) for s in node.statements]
        return ("\n" if pretty else " ").join(parts)
    if isinstance(node, Statement):
        body = _frame(node.frame, pretty=pretty, indent=0)
        return f"{node.illoc} {body} ."
    if isinstance(node, Frame):
        return _frame(node, pretty=pretty, indent=0)
    return _leaf(node)


def _leaf(node: Node) -> str:
    if isinstance(node, Atom):
        return node.form
    if isinstance(node, Ref):
        return f"${node.n}"
    if isinstance(node, Num):
        return str(node.value)
    if isinstance(node, Spell):
        letters = " ".join(node.letters())
        return f"( spell {letters} )"
    raise TypeError(type(node))


def _frame(frame: Frame, pretty: bool, indent: int) -> str:
    bits: list[str] = [frame.head, *frame.features]
    if frame.binding is not None:
        bits.append(f"= ${frame.binding}")
    compact = _is_compact(frame)
    for role, arg in frame.slots:
        arg_s = (
            _frame(arg, pretty=pretty and not compact, indent=indent + 1)
            if isinstance(arg, Frame)
            else _leaf(arg)
        )
        if role:
            bits.append(f"{role} {arg_s}")
        else:
            bits.append(arg_s)
    inner = " ".join(bits)
    if not pretty or compact or len(inner) < 48:
        return f"( {inner} )"
    pad = "  " * (indent + 1)
    close = "  " * indent
    lines = [frame.head, *frame.features]
    if frame.binding is not None:
        lines.append(f"= ${frame.binding}")
    pretty_bits = " ".join(lines)
    chunks = [f"( {pretty_bits}"]
    for role, arg in frame.slots:
        arg_s = (
            _frame(arg, pretty=True, indent=indent + 1)
            if isinstance(arg, Frame)
            else _leaf(arg)
        )
        if role:
            chunks.append(f"{pad}{role} {arg_s}")
        else:
            chunks.append(f"{pad}{arg_s}")
    chunks.append(f"{close})")
    return "\n".join(chunks)


def _is_compact(frame: Frame) -> bool:
    if len(frame.slots) > 3:
        return False
    for _, arg in frame.slots:
        if isinstance(arg, Frame) and (arg.slots or arg.binding is not None):
            return False
    return True


# ---------------------------------------------------------------------------
# Model encoding: a closed vocabulary of atoms. Numbers explode to digits.
# Unknown open-class atoms explode to spell + letters.
# ---------------------------------------------------------------------------

STRUCT_TOKENS = ("(", ")", ".", "=", "neg")
REF_TOKENS = tuple(f"${i}" for i in range(1, 33))


def vocab() -> list[str]:
    """Deterministic vocabulary. Index in this list is the stable id offset."""
    from .lexicon import LEXICON as L

    skip = set("abcdefghijklmnopqrstuvwxyz") | set("0123456789") | {"(", ")", ".", "="}
    roots = sorted(k for k in L if k not in skip)
    letters = list("abcdefghijklmnopqrstuvwxyz")
    digits = list("0123456789")
    return ["<pad>", "<bos>", "<eos>"] + list(STRUCT_TOKENS) + list(REF_TOKENS) + roots + digits + letters


_VOCAB: list[str] | None = None
_VOCAB_INDEX: dict[str, int] | None = None


def _vindex() -> dict[str, int]:
    global _VOCAB, _VOCAB_INDEX
    if _VOCAB is None:
        _VOCAB = vocab()
        _VOCAB_INDEX = {t: i for i, t in enumerate(_VOCAB)}
    return _VOCAB_INDEX


def encode(node: Program | Statement | Node | str) -> list[str]:
    """Canonical model token stream (string tokens, not ids)."""
    if isinstance(node, str):
        node = parse(node)
    out: list[str] = []
    _encode(node, out)
    return out


def encode_ids(node: Program | Statement | Node | str) -> list[int]:
    idx = _vindex()
    return [idx[t] for t in encode(node)]


def _encode(node: object, out: list[str]) -> None:
    if isinstance(node, Program):
        for s in node.statements:
            _encode(s, out)
        return
    if isinstance(node, Statement):
        out.append(node.illoc)
        _encode(node.frame, out)
        out.append(".")
        return
    if isinstance(node, Frame):
        out.append("(")
        _emit_atom(node.head, out)
        for f in node.features:
            out.append(f)
        if node.binding is not None:
            out.append("=")
            _emit_ref(node.binding, out)
        for role, arg in node.slots:
            if role:
                out.append(role)
            _encode(arg, out)
        out.append(")")
        return
    if isinstance(node, Atom):
        _emit_atom(node.form, out)
        return
    if isinstance(node, Ref):
        _emit_ref(node.n, out)
        return
    if isinstance(node, Num):
        out.append("(")
        out.append("num")
        for d in node.digits():
            out.append(d)
        out.append(")")
        return
    if isinstance(node, Spell):
        out.append("(")
        out.append("spell")
        for ch in node.letters():
            out.append(ch)
        out.append(")")
        return
    raise TypeError(type(node))


def _emit_atom(form: str, out: list[str]) -> None:
    idx = _vindex()
    if form in idx:
        out.append(form)
        return
    # unknown: spell it
    out.append("(")
    out.append("spell")
    for ch in form:
        if ch.lower() in idx:
            out.append(ch.lower())
    out.append(")")


def _emit_ref(n: int, out: list[str]) -> None:
    if 1 <= n <= 32:
        out.append(f"${n}")
    else:
        out.append("$")
        out.append("(")
        out.append("num")
        for d in str(n):
            out.append(d)
        out.append(")")


def decode(tokens: list[str]) -> Program:
    """Parse a model token stream back to a program (join with spaces)."""
    # $ tokens and punctuation already atomic
    text = " ".join(tokens)
    return parse(text)


# ---------------------------------------------------------------------------
# Gloss — readable English paraphrase, not a full translation
# ---------------------------------------------------------------------------

def gloss(node: Program | Statement | Node | str) -> str:
    if isinstance(node, str):
        node = parse(node)
    if isinstance(node, Program):
        return " ".join(gloss(s) for s in node.statements)
    if isinstance(node, Statement):
        ill = {
            "asrt": "",
            "ask": "QUESTION:",
            "cmd": "COMMAND:",
            "opt": "WISH:",
            "exch": "EXCLAIM:",
        }.get(node.illoc, node.illoc)
        inner = _gloss_frame(node.frame)
        return (ill + " " + inner).strip() + "."
    if isinstance(node, Frame):
        return _gloss_frame(node)
    return _gloss_leaf(node)


def _gloss_leaf(node: Node) -> str:
    if isinstance(node, Atom):
        e = lookup(node.form)
        return e.gloss if e else node.form
    if isinstance(node, Ref):
        return f"[#{node.n}]"
    if isinstance(node, Num):
        return str(node.value)
    if isinstance(node, Spell):
        return node.text
    return "?"


def _word(form: str) -> str:
    e = lookup(form)
    return e.gloss if e else form


def _gloss_frame(frame: Frame) -> str:
    feats = [_word(f) for f in frame.features]
    feat_s = " ".join(feats)

    if frame.head in {"and", "or"}:
        parts = [_gloss_node(n) for _, n in frame.slots]
        joiner = f" {frame.head} "
        body = joiner.join(parts)
        return f"({body})"
    if frame.head == "if":
        args = [_gloss_node(n) for _, n in frame.slots]
        if len(args) == 2:
            return f"if {args[0]} then {args[1]}"
        if len(args) >= 3:
            return f"if {args[0]} then {args[1]} else {args[2]}"
        return "if " + " ".join(args)
    if frame.head == "seq":
        return " then ".join(_gloss_node(n) for _, n in frame.slots)
    if frame.head in {"all", "some", "exist", "none", "one", "mostq"}:
        args = [_gloss_node(n) for _, n in frame.slots]
        return f"{_word(frame.head)} " + " : ".join(args)
    if frame.head == "num":
        if frame.slots and all(isinstance(n, (Num, Atom)) for _, n in frame.slots):
            digits = []
            for _, n in frame.slots:
                digits.append(_gloss_leaf(n) if not isinstance(n, Num) else str(n.value))
            return "".join(digits)
        if frame.slots:
            return _gloss_node(frame.slots[0][1])
        return "0"
    if frame.head == "spell":
        return "".join(_gloss_node(n) for _, n in frame.slots)
    if frame.head in {"qnt", "dur", "before", "after", "can", "cause", "same", "sim"}:
        args = [_gloss_node(n) for _, n in frame.slots]
        return f"{_word(frame.head)} " + " ".join(args)

    head = _word(frame.head)
    bind = f" as #{frame.binding}" if frame.binding is not None else ""
    pieces = []
    mods = []
    name = None
    for role, arg in frame.slots:
        if role == "mod":
            mods.append(_gloss_node(arg))
        elif role == "name":
            name = _gloss_node(arg)
        elif role:
            pieces.append(f"{_word(role)}={_gloss_node(arg)}")
        else:
            pieces.append(_gloss_node(arg))
    mod_s = (" " + " ".join(mods)) if mods else ""
    name_s = f" '{name}'" if name else ""
    feat_bit = (feat_s + " ") if feat_s else ""
    if pieces:
        return f"{feat_bit}{head}{name_s}{mod_s}{bind} (" + ", ".join(pieces) + ")"
    return f"{feat_bit}{head}{name_s}{mod_s}{bind}".strip()


def _gloss_node(n: Node) -> str:
    if isinstance(n, Frame):
        return _gloss_frame(n)
    return _gloss_leaf(n)


def pretty_tokens(tokens: list[str]) -> list[dict]:
    """Annotate a model stream for the UI."""
    out = []
    for t in tokens:
        e = lookup(t) if not t.startswith("$") else None
        kind = "ref" if t.startswith("$") else (e.kind if e else "open")
        gloss_s = e.gloss if e else (t if t in "().=" or t.startswith("$") else t)
        out.append({"tok": t, "kind": kind, "gloss": gloss_s, "field": e.field if e else ""})
    return out
