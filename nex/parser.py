"""Deterministic recursive-descent parser for Nex.

The grammar is PEG-shaped: at every position exactly one alternative
matches. Open-class words are never consulted — only closed-class lists —
so unknown roots still parse as long as they sit in head position.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .ast_nodes import Atom, Frame, Node, Num, Program, Ref, Spell, Statement
from .lexicon import is_feature, is_illoc, is_operator, is_role


TOKEN_RE = re.compile(
    r"""
    \s+
    | \(
    | \)
    | \.
    | =
    | \$[0-9]+
    | [0-9]+
    | [a-z][a-z0-9]*
    | '
    """,
    re.VERBOSE,
)


class ParseError(Exception):
    def __init__(self, message: str, index: int = 0, token: str | None = None):
        super().__init__(message)
        self.index = index
        self.token = token


@dataclass
class _Tok:
    text: str
    index: int


class _Lexer:
    def __init__(self, source: str):
        self.source = source.strip()
        self.tokens: list[_Tok] = []
        pos = 0
        for m in TOKEN_RE.finditer(self.source):
            if m.start() != pos:
                bad = self.source[pos : m.start()]
                raise ParseError(f"illegal input {bad!r} at {pos}", pos, bad)
            piece = m.group(0)
            if not piece.isspace():
                self.tokens.append(_Tok(piece, m.start()))
            pos = m.end()
        if pos != len(self.source):
            bad = self.source[pos:]
            raise ParseError(f"illegal input {bad!r} at {pos}", pos, bad)
        self.i = 0

    def peek(self) -> _Tok | None:
        if self.i < len(self.tokens):
            return self.tokens[self.i]
        return None

    def get(self) -> _Tok:
        t = self.peek()
        if t is None:
            raise ParseError("unexpected end of input", len(self.source))
        self.i += 1
        return t

    def eat(self, wanted: str) -> _Tok:
        t = self.get()
        if t.text != wanted:
            raise ParseError(f"expected {wanted!r}, got {t.text!r}", t.index, t.text)
        return t

    def at_end(self) -> bool:
        return self.i >= len(self.tokens)


def parse(source: str) -> Program:
    """Parse Nex text into a program. Raises ParseError."""
    lx = _Lexer(source)
    stmts: list[Statement] = []
    if lx.at_end():
        raise ParseError("empty input")
    while not lx.at_end():
        stmts.append(_statement(lx))
    return Program(stmts)


def _statement(lx: _Lexer) -> Statement:
    t = lx.peek()
    if t is None:
        raise ParseError("expected statement")
    if is_illoc(t.text):
        illoc = lx.get().text
    else:
        illoc = "asrt"
    frame = _frame(lx)
    nxt = lx.peek()
    if nxt and nxt.text == ".":
        lx.get()
    return Statement(illoc, frame)


def _frame(lx: _Lexer) -> Frame:
    lx.eat("(")
    head_tok = lx.get()
    if not re.fullmatch(r"[a-z][a-z0-9]*", head_tok.text):
        raise ParseError(
            f"frame head must be an atom, got {head_tok.text!r}",
            head_tok.index,
            head_tok.text,
        )
    head = head_tok.text
    features: list[str] = []
    binding: int | None = None
    slots: list[tuple[str | None, Node]] = []
    op = is_operator(head)

    while True:
        t = lx.peek()
        if t is None:
            raise ParseError(f"unclosed frame {head}")
        if t.text == ")":
            lx.get()
            break
        if t.text == "=":
            lx.get()
            binding = _ref(lx).n
            continue
        if op:
            # operators take bare arguments, optionally role-tagged
            if is_role(t.text) and t.text not in {"name"}:
                # still allow role tags inside operators for `qnt unit ...`
                role = lx.get().text
                slots.append((role, _arg(lx)))
            else:
                slots.append((None, _arg(lx)))
            continue
        if is_feature(t.text):
            features.append(lx.get().text)
            continue
        if is_role(t.text):
            role = lx.get().text
            slots.append((role, _arg(lx)))
            continue
        # sugar: a nested frame with a quality/kind head becomes mod
        if t.text == "(":
            inner = _frame(lx)
            slots.append(("mod", inner))
            continue
        raise ParseError(
            f"unexpected {t.text!r} in frame {head}; "
            f"need a role, feature, binding, or nested frame",
            t.index,
            t.text,
        )
    return Frame(head, features, binding, slots)


def _arg(lx: _Lexer) -> Node:
    t = lx.peek()
    if t is None:
        raise ParseError("expected argument")
    if t.text == "(":
        return _frame(lx)
    if t.text.startswith("$"):
        return _ref(lx)
    if t.text.isdigit():
        lx.get()
        return Num(int(t.text))
    if re.fullmatch(r"[a-z][a-z0-9]*", t.text):
        lx.get()
        return Atom(t.text)
    raise ParseError(f"expected argument, got {t.text!r}", t.index, t.text)


def _ref(lx: _Lexer) -> Ref:
    t = lx.get()
    if not re.fullmatch(r"\$[0-9]+", t.text):
        raise ParseError(f"expected $N, got {t.text!r}", t.index, t.text)
    return Ref(int(t.text[1:]))


def try_parse(source: str) -> tuple[Program | None, str | None]:
    try:
        return parse(source), None
    except ParseError as e:
        return None, str(e)
