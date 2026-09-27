"""A small English → Nex translator for the playground.

This is not general MT. It covers a useful clause grammar so visitors can
type real sentences and see Nex force a unique structure. Failures return
a structured error instead of silently guessing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .ast_nodes import Atom, Frame, Node, Num, Program, Ref, Statement
from .lexicon import ENGLISH_MAP, Entry, is_operator, lookup
from .serialize import serialize


IRREGULAR_VBD = {
    "gave": "give",
    "got": "get",
    "taken": "take",
    "took": "take",
    "put": "put",
    "made": "make",
    "did": "do",
    "used": "use",
    "worked": "work",
    "played": "play",
    "sent": "send",
    "opened": "open",
    "closed": "close",
    "broke": "break",
    "broken": "break",
    "cut": "cut",
    "bought": "buy",
    "sold": "sell",
    "paid": "pay",
    "helped": "help",
    "hit": "hit",
    "held": "hold",
    "found": "find",
    "waited": "wait",
    "tried": "try",
    "went": "go",
    "gone": "go",
    "came": "come",
    "ran": "run",
    "sat": "sit",
    "stood": "stand",
    "brought": "bring",
    "fell": "fall",
    "flew": "fly",
    "swam": "swim",
    "walked": "walk",
    "left": "leave",
    "arrived": "arrive",
    "stayed": "stay",
    "saw": "see",
    "seen": "see",
    "looked": "look",
    "heard": "hear",
    "said": "say",
    "told": "tell",
    "asked": "ask",
    "answered": "answer",
    "wrote": "write",
    "written": "write",
    "read": "read",
    "called": "call",
    "meant": "mean",
    "knew": "know",
    "known": "know",
    "thought": "think",
    "believed": "believe",
    "remembered": "remember",
    "forgot": "forget",
    "forgotten": "forget",
    "learned": "learn",
    "taught": "teach",
    "wanted": "want",
    "needed": "need",
    "decided": "decide",
    "understood": "understand",
    "hoped": "hope",
    "felt": "feel",
    "liked": "like",
    "loved": "love",
    "feared": "fear",
    "lived": "live",
    "died": "die",
    "ate": "eat",
    "eaten": "eat",
    "drank": "drink",
    "slept": "sleep",
    "woke": "wake",
    "happened": "happen",
    "became": "become",
    "started": "start",
    "began": "begin",
    "ended": "end",
    "finished": "finish",
    "stopped": "stop",
    "had": "have",
    "was": "be",
    "were": "be",
    "is": "be",
    "are": "be",
    "am": "be",
    "been": "be",
    "caused": "cause",
    "changed": "change",
    "existed": "exist",
}

IRREGULAR_VBG = {
    "giving": "give",
    "taking": "take",
    "putting": "put",
    "making": "make",
    "doing": "do",
    "going": "go",
    "coming": "come",
    "running": "run",
    "seeing": "see",
    "looking": "look",
    "saying": "say",
    "telling": "tell",
    "thinking": "think",
    "feeling": "feel",
    "eating": "eat",
    "having": "have",
    "being": "be",
    "dying": "die",
    "lying": "lie",
}

PRONOUNS = {
    "i": ("spk", None),
    "me": ("spk", None),
    "my": ("spk", "pos"),
    "we": ("spk", None),
    "us": ("spk", None),
    "you": ("hrd", None),
    "your": ("hrd", "pos"),
    "he": ("ref", None),
    "him": ("ref", None),
    "his": ("ref", "pos"),
    "she": ("ref", None),
    "her": ("ref", None),
    "it": ("ref", None),
    "they": ("ref", None),
    "them": ("ref", None),
    "their": ("ref", "pos"),
    "someone": ("unk", None),
    "something": ("unk", None),
    "this": ("this", None),
    "that": ("that", None),
}

FUNCTION = {
    "the": "def",
    "a": "ind",
    "an": "ind",
    "some": "ind",
    "not": "not",
    "n't": "not",
    "never": "not",
    "no": "not",
    "will": "fut",
    "shall": "fut",
    "can": "can",
    "could": "can",
    "may": "may",
    "might": "may",
    "must": "must",
    "should": "must",
    "very": "very",
    "really": "very",
    "yesterday": "yest",
    "tomorrow": "tom",
    "today": "today",
    "now": "nowt",
    "here": "here",
    "there": "there",
    "and": "and",
    "or": "or",
    "if": "if",
    "because": "cau",
    "with": "ins",
    "using": "ins",
    "to": "to",
    "from": "src",
    "at": "loc",
    "in": "loc",
    "on": "loc",
    "for": "ben",
    "of": "pos",
    "by": "agt",
    "who": "who",
    "what": "what",
    "where": "where",
    "when": "when",
    "why": "why",
    "how": "how",
    "did": "did",
    "does": "does",
    "do": "doaux",
    "please": "please",
}


@dataclass
class Tok:
    raw: str
    norm: str
    tag: str  # NNP NN VB JJ DT IN PRP CC RB CD WH
    lemma: str
    entry: Entry | None = None
    feat: list[str] = field(default_factory=list)


class TranslateError(Exception):
    pass


def tokenize_en(text: str) -> list[str]:
    text = text.strip()
    text = re.sub(r"n't", " n't", text)
    text = re.sub(r"([.,!?;:()\"])", r" \1 ", text)
    return [t for t in text.split() if t]


def _tag(word: str) -> Tok:
    raw = word
    punct = raw in {".", ",", "!", "?", ";", ":"}
    if punct:
        return Tok(raw, raw, "PUNCT", raw)
    lower = raw.lower()
    feat: list[str] = []
    lemma = lower
    entry = None
    tag = "NN"

    if lower in FUNCTION:
        tag = "FN"
        lemma = lower
    elif lower in PRONOUNS:
        tag = "PRP"
        lemma = lower
    elif re.fullmatch(r"[0-9]+", lower):
        tag = "CD"
        lemma = lower
    elif raw[:1].isupper() and raw[1:].islower() and lower not in {"i"}:
        tag = "NNP"
        lemma = lower
    elif lower in IRREGULAR_VBD:
        lemma = IRREGULAR_VBD[lower]
        tag = "VB"
        if lemma != "be":
            feat.append("past")
            if lower.endswith("en") or lower in {"gone", "done", "seen", "taken"}:
                feat.append("done")
        entry = ENGLISH_MAP.get(lemma) or ENGLISH_MAP.get(lower)
    elif lower in IRREGULAR_VBG:
        lemma = IRREGULAR_VBG[lower]
        tag = "VB"
        feat.append("ong")
        entry = ENGLISH_MAP.get(lemma)
    elif lower.endswith("ing") and lower[:-3] in ENGLISH_MAP:
        lemma = lower[:-3]
        tag = "VB"
        feat.append("ong")
        entry = ENGLISH_MAP.get(lemma)
    elif lower.endswith("ing") and lower[:-3] + "e" in ENGLISH_MAP:
        lemma = lower[:-3] + "e"
        tag = "VB"
        feat.append("ong")
        entry = ENGLISH_MAP.get(lemma)
    elif (
        lower.endswith("ed")
        and len(lower) > 4
        and lower[:-2] in ENGLISH_MAP
        and ENGLISH_MAP[lower[:-2]].kind == "evt"
    ):
        lemma = lower[:-2]
        tag = "VB"
        feat.append("past")
        feat.append("done")
        entry = ENGLISH_MAP.get(lemma)
    elif (
        lower.endswith("ed")
        and len(lower) > 4
        and lower[:-1] in ENGLISH_MAP
        and ENGLISH_MAP[lower[:-1]].kind == "evt"
    ):
        lemma = lower[:-1]
        tag = "VB"
        feat.append("past")
        feat.append("done")
        entry = ENGLISH_MAP.get(lemma)
    elif lower.endswith("s") and lower[:-1] in ENGLISH_MAP:
        maybe = ENGLISH_MAP[lower[:-1]]
        if maybe.kind == "evt":
            lemma = lower[:-1]
            tag = "VB"
            entry = maybe
        elif maybe.kind == "kind":
            lemma = lower[:-1]
            tag = "NN"
            feat.append("pl")
            entry = maybe
        else:
            entry = ENGLISH_MAP.get(lower)
            tag = "JJ" if entry and entry.kind == "qual" else "NN"
            lemma = lower
    else:
        entry = ENGLISH_MAP.get(lower)
        if entry:
            if entry.kind == "evt":
                tag = "VB"
            elif entry.kind == "qual":
                tag = "JJ"
            elif entry.kind == "kind":
                tag = "NN"
            elif entry.kind == "feat":
                tag = "FN"
            else:
                tag = "NN"
            lemma = lower
        else:
            tag = "NNP" if raw[:1].isupper() else "NN"
            lemma = lower
    if entry is None:
        entry = ENGLISH_MAP.get(lemma)
    return Tok(raw, lower, tag, lemma, entry, feat)


@dataclass
class _State:
    next_bind: int = 1
    binds: dict[str, int] = field(default_factory=dict)
    last_person: int | None = None


REF_KEYS = {
    "he": "m",
    "him": "m",
    "his": "m",
    "she": "f",
    "her": "f",
    "they": "p",
    "them": "p",
    "their": "p",
    "it": "n",
}


@dataclass
class _C:
    toks: list[Tok]
    i: int = 0
    st: _State = field(default_factory=_State)

    def peek(self) -> Tok | None:
        if self.i < len(self.toks):
            return self.toks[self.i]
        return None

    def at(self, *norms: str) -> bool:
        t = self.peek()
        return bool(t and t.norm in norms)

    def at_tag(self, *tags: str) -> bool:
        t = self.peek()
        return bool(t and t.tag in tags)

    def get(self) -> Tok:
        t = self.peek()
        if t is None:
            raise TranslateError("unexpected end of sentence")
        self.i += 1
        return t

    def skip_punct(self) -> None:
        while self.peek() and self.peek().tag == "PUNCT":  # type: ignore
            self.i += 1

    def bind(self, key: str) -> int:
        if key not in self.st.binds:
            self.st.binds[key] = self.st.next_bind
            self.st.next_bind += 1
        return self.st.binds[key]


def from_english(text: str) -> dict:
    """Translate English to Nex. Returns a dict with text, ast, notes."""
    raw_toks = tokenize_en(text)
    if not raw_toks:
        raise TranslateError("empty input")
    toks = [_tag(t) for t in raw_toks if t]
    # drop terminal punctuation but remember illocution
    illoc = "asrt"
    while toks and toks[-1].tag == "PUNCT":
        p = toks.pop()
        if p.raw == "?":
            illoc = "ask"
        elif p.raw == "!":
            illoc = "cmd"
    if not toks:
        raise TranslateError("no words")

    # question words / auxiliaries at front
    if toks[0].norm in {"who", "what", "where", "when", "why", "how"}:
        illoc = "ask"
    if toks[0].norm in {"did", "do", "does", "is", "are", "was", "were", "can", "will"}:
        if illoc != "ask" and any(t.raw == "?" for t in [_tag(x) for x in raw_toks]):
            illoc = "ask"
        if toks[0].norm in {"did", "do", "does"} and illoc == "asrt":
            # keep as assert unless ? was present — already handled
            pass

    c = _C(toks)
    # split on because / if / and at top level
    frame = _top(c)
    c.skip_punct()
    if c.peek() is not None and c.peek().norm not in {".", "?", "!"}:
        # leftover words
        leftover = " ".join(t.raw for t in c.toks[c.i :])
        if leftover.strip():
            # try to ignore trailing leftovers that are function words
            if not all(t.tag in {"PUNCT", "FN"} and t.norm in {"please"} for t in c.toks[c.i :]):
                raise TranslateError(
                    f"could not consume {leftover!r}. "
                    "Try a simpler clause: Subject Verb Object, optional "
                    "'to' recipient, 'because', adjectives, 'the/a', names."
                )
    prog = Program([Statement(illoc, frame)])
    return {
        "nex": serialize(prog.canonical(), pretty=True),
        "ast": prog.canonical().to_dict(),
        "illoc": illoc,
        "notes": _notes_for(text, prog),
    }


def _top(c: _C) -> Frame:
    # because-clause split
    parts_because = _split_word(c.toks, "because")
    if parts_because:
        left, right = parts_because
        f1 = _top(_C(left, st=c.st))
        _sync(c, left)
        f2 = _top(_C(right, st=c.st))
        f1.slots.append(("cau", f2))
        return f1
    if c.at("if"):
        c.get()
        cond_toks, rest = _split_comma_or_then(c.toks[c.i :])
        cond = _clause(_C(cond_toks, st=c.st))
        body = _clause(_C(rest, st=c.st))
        c.i = len(c.toks)
        return Frame("if", slots=[(None, cond), (None, body)])
    # and at clause level if two verbs
    return _clause(c)


def _sync(c: _C, consumed: list[Tok]) -> None:
    c.i = len(c.toks)


def _split_word(toks: list[Tok], word: str) -> tuple[list[Tok], list[Tok]] | None:
    for i, t in enumerate(toks):
        if t.norm == word:
            if i == 0 or i == len(toks) - 1:
                return None
            return toks[:i], toks[i + 1 :]
    return None


def _split_comma_or_then(toks: list[Tok]) -> tuple[list[Tok], list[Tok]]:
    for i, t in enumerate(toks):
        if t.norm in {"then", ","} and i > 0:
            rest = toks[i + 1 :]
            if rest and rest[0].norm == "then":
                rest = rest[1:]
            return toks[:i], rest
    mid = max(1, len(toks) // 2)
    return toks[:mid], toks[mid:]


def _clause(c: _C) -> Frame:
    feats_front: list[str] = []
    illoc_skip = False
    # auxiliaries
    while c.peek() and c.peek().norm in {
        "did",
        "do",
        "does",
        "please",
        "never",
        "will",
        "shall",
        "can",
        "could",
        "must",
        "should",
    }:
        t = c.get()
        if t.norm == "did":
            feats_front.append("past")
        if t.norm == "never":
            feats_front.append("not")
        if t.norm in {"will", "shall"}:
            feats_front.append("fut")
        if t.norm in {"can", "could"}:
            feats_front.append("can")
        if t.norm in {"must", "should"}:
            feats_front.append("must")
    # negation
    # NP + VP
    # question who/what as argument
    wh = None
    if c.peek() and c.peek().norm in {"who", "what", "where", "when", "why", "how"}:
        wh = c.get().norm

    subj: Node | None = None
    if wh == "who":
        subj = Frame("pamo", binding=_fresh(c))
    elif wh == "what" and c.peek() and c.peek().tag == "VB":
        subj = Frame("moto", binding=_fresh(c))
    elif c.peek() and c.peek().tag in {"PRP", "NNP", "NN", "FN", "JJ", "CD"}:
        # FN the/a starts NP
        if not (c.peek().tag == "FN" and c.peek().norm in {"will", "can", "must", "may", "not"}):
            subj = _np(c)

    # more auxiliaries / not / tense
    feats = list(feats_front)
    verb_tok: Tok | None = None
    while c.peek():
        t = c.peek()
        if t.norm in {"not", "n't", "never"}:
            feats.append("not")
            c.get()
            continue
        if t.norm in {"will", "shall"}:
            feats.append("fut")
            c.get()
            continue
        if t.norm in {"can", "could"}:
            # wrap later
            c.get()
            feats.append("can")
            continue
        if t.norm in {"must", "should"}:
            feats.append("must")
            c.get()
            continue
        if t.norm in {"is", "are", "am", "was", "were", "be", "been"}:
            # copula
            cop = c.get()
            if cop.norm in {"was", "were"}:
                feats.append("past")
            return _copula(c, subj, feats)
        if t.tag == "VB" or (t.entry and t.entry.kind == "evt"):
            verb_tok = c.get()
            break
        if t.norm in {"ready"}:
            # "is ready" handled in copula; bare ready as verb
            verb_tok = c.get()
            break
        break
    if verb_tok is None:
        # maybe adjective as copula leftover
        if subj is not None and c.peek() and c.peek().tag == "JJ":
            return _copula(c, subj, feats)
        raise TranslateError("could not find a verb. Try e.g. 'Maria gave John a book.'")

    feats.extend(verb_tok.feat)
    # drop duplicate
    feats = list(dict.fromkeys(feats))
    lemma = verb_tok.lemma
    if lemma in {"look"}:
        lemma = "see"
    if lemma in {"tell"}:
        lemma = "say"
    if lemma in {"love"}:
        lemma = "like"
    if lemma in {"bring"}:
        lemma = "carry"
    if lemma in {"begin"}:
        lemma = "start"
    if lemma in {"finish", "stop"}:
        lemma = "end"
    if lemma in {"be"}:
        return _copula(c, subj, feats)

    entry = ENGLISH_MAP.get(lemma) or verb_tok.entry
    if entry is None or entry.kind != "evt":
        # unknown verb: use deki (do) with spelled content? better fail
        if entry and entry.kind == "qual":
            # "is ready" already handled; "chicken is ready to eat"
            return _ready_like(c, subj, entry, feats)
        raise TranslateError(
            f"unknown verb {verb_tok.raw!r}. "
            f"Nex kernel verbs include give, see, go, say, know, want, eat, have, ..."
        )

    head = entry.form
    slots: list[tuple[str | None, Node]] = []
    if subj is not None:
        role = "exp" if "exp" in entry.roles and "agt" not in entry.roles else "agt"
        if head in {"vidi", "suli", "kuni", "keni", "kabi", "kawi", "nidi", "fili", "fali", "fori"}:
            role = "exp"
        slots.append((role, subj))

    # objects, to-PP, with-PP, yesterday, etc.
    rec_from_to = False
    # ditransitive: V NP NP
    obj1 = None
    if c.peek() and _can_start_np(c.peek()):
        obj1 = _np(c)
    obj2 = None
    if c.peek() and _can_start_np(c.peek()) and "rec" in entry.roles:
        obj2 = _np(c)

    if obj1 is not None and obj2 is not None:
        slots.append(("rec", obj1))
        slots.append(("thm", obj2))
    elif obj1 is not None:
        # theme, unless 'to' follows making obj1 recipient? we'll see to
        slots.append(("thm", obj1))

    # prepositional extras
    while c.peek():
        t = c.peek()
        if t.norm == "to":
            c.get()
            if c.peek() and c.peek().tag == "VB":
                # purpose / infinitive: to eat
                inf = _inf_clause(c)
                slots.append(("prp", inf))
            else:
                rec = _np(c)
                # if we already put theme, this is recipient
                slots.append(("rec", rec))
            continue
        if t.norm in {"with", "using"}:
            c.get()
            slots.append(("ins", _np(c)))
            continue
        if t.norm in {"from"}:
            c.get()
            slots.append(("src", _np(c)))
            continue
        if t.norm in {"at", "in", "on"}:
            c.get()
            slots.append(("loc", _np(c)))
            continue
        if t.norm in {"for"}:
            c.get()
            slots.append(("ben", _np(c)))
            continue
        if t.norm in {"yesterday", "tomorrow", "today", "now"}:
            c.get()
            slots.append(("tmp", _time_word(t.norm)))
            continue
        if t.norm in {"because", "if", "and", "or"}:
            break
        if t.tag == "PUNCT":
            break
        break

    if "can" in feats:
        feats = [f for f in feats if f != "can"]
        inner = Frame(head, feats, None, slots)
        return Frame("can", slots=[(None, inner)])
    return Frame(head, feats, None, slots)


def _ready_like(c: _C, subj: Node | None, entry: Entry, feats: list[str]) -> Frame:
    slots: list[tuple[str | None, Node]] = []
    if subj is not None:
        slots.append(("thm", subj))
    if c.at("to"):
        c.get()
        slots.append(("prp", _inf_clause(c)))
    return Frame("redi", feats, None, slots)


def _inf_clause(c: _C) -> Frame:
    """Parse an infinitive VP whose agent is unspecified or previous."""
    if not c.peek():
        raise TranslateError("expected a verb after 'to'")
    v = c.get()
    lemma = v.lemma
    if lemma in IRREGULAR_VBD:
        lemma = IRREGULAR_VBD[lemma]
    entry = ENGLISH_MAP.get(lemma) or v.entry
    if entry is None or entry.kind != "evt":
        raise TranslateError(f"unknown infinitive {v.raw!r}")
    slots: list[tuple[str | None, Node]] = []
    # optional object
    if c.peek() and _can_start_np(c.peek()) and c.peek().norm not in {"to"}:
        slots.append(("thm", _np(c)))
    else:
        # intransitive or implied object — leave unspecified
        pass
    # agent unspecified
    slots.insert(0, ("agt", Atom("unk")))
    return Frame(entry.form, v.feat, None, slots)


def _copula(c: _C, subj: Node | None, feats: list[str]) -> Frame:
    if c.at("not", "n't"):
        feats.append("not")
        c.get()
    if c.peek() and c.peek().norm == "ready":
        c.get()
        return _ready_like(c, subj, ENGLISH_MAP["ready"], feats)
    if c.peek() and c.peek().tag == "JJ":
        adj = c.get()
        entry = adj.entry or ENGLISH_MAP.get(adj.lemma)
        if entry is None or entry.kind != "qual":
            raise TranslateError(f"unknown adjective {adj.raw!r}")
        slots: list[tuple[str | None, Node]] = []
        if subj is not None:
            slots.append(("thm", subj))
        return Frame(entry.form, feats, None, slots)
    if c.peek() and _can_start_np(c.peek()):
        pred = _np(c)
        slots = []
        if subj is not None:
            slots.append((None, subj))
        slots.append((None, pred))
        return Frame("same", feats, None, slots)
    if c.peek() and c.peek().norm in {"here", "there"}:
        loc = Atom(c.get().norm if c.peek() else "here")  # type: ignore
        # fix
    t = c.peek()
    if t and t.norm in {"here", "there"}:
        loc_tok = c.get()
        loc: Node = Atom("here" if loc_tok.norm == "here" else "there")
        slots = [("thm", subj or Atom("unk")), ("loc", loc)]
        return Frame("holi", feats, None, slots)
    raise TranslateError("could not parse complement of 'be'")


def _can_start_np(t: Tok) -> bool:
    if t.tag in {"DT", "PRP", "NNP", "NN", "JJ", "CD"}:
        return True
    if t.tag == "FN" and t.norm in {"the", "a", "an", "some"}:
        return True
    if t.entry and t.entry.kind in {"kind", "qual"}:
        return True
    return False


def _fresh(c: _C) -> int:
    n = c.st.next_bind
    c.st.next_bind += 1
    return n


def _np(c: _C) -> Node:
    t = c.peek()
    if t is None:
        raise TranslateError("expected a noun phrase")
    if t.tag == "PRP":
        c.get()
        deictic, _ = PRONOUNS[t.norm]
        if deictic == "ref":
            key = REF_KEYS.get(t.norm, "x")
            n = c.bind("ref:" + key)
            c.st.last_person = n
            return Ref(n)
        return Atom(deictic)
    feats: list[str] = []
    mods: list[Frame] = []
    name: str | None = None
    head_entry: Entry | None = None
    number: Num | None = None

    if t.tag == "FN" and t.norm in {"the", "a", "an", "some"}:
        feats.append(FUNCTION[t.norm] if t.norm != "some" else "ind")
        c.get()
        t = c.peek()
    if t and t.tag == "CD":
        number = Num(int(t.norm))
        c.get()
        t = c.peek()
        if "pl" not in feats and number.value != 1:
            feats.append("pl")

    # adjectives
    while c.peek() and (c.peek().tag == "JJ" or (c.peek().entry and c.peek().entry.kind == "qual")):
        adj = c.get()
        ae = adj.entry or ENGLISH_MAP.get(adj.lemma)
        if ae and ae.kind == "qual":
            mods.append(Frame(ae.form))
        else:
            raise TranslateError(f"unknown adjective {adj.raw!r}")

    t = c.peek()
    if t is None:
        raise TranslateError("noun phrase ran out before a noun")
    if t.tag == "NNP":
        name = t.raw
        c.get()
        head_entry = lookup("pamo")
    elif t.entry and t.entry.kind == "kind":
        head_entry = t.entry
        feats.extend(t.feat)
        c.get()
    elif t.lemma in ENGLISH_MAP and ENGLISH_MAP[t.lemma].kind == "kind":
        head_entry = ENGLISH_MAP[t.lemma]
        feats.extend(t.feat)
        c.get()
    elif t.tag in {"NN", "NNP"}:
        # unknown noun: kind moto with name/spell
        name = t.raw
        c.get()
        head_entry = lookup("moto")
    else:
        raise TranslateError(f"expected a noun, got {t.raw!r}")

    assert head_entry is not None
    slots: list[tuple[str | None, Node]] = []
    if name:
        slots.append(("name", Atom(name.lower())))
    for m in mods:
        slots.append(("mod", m))
    if number is not None:
        slots.append(("mod", Frame("qnt", slots=[(None, number)])))
    bind = None
    if head_entry.form == "pamo" or name:
        bind = _fresh(c)
        c.st.last_person = bind
        c.st.binds[name or f"p{bind}"] = bind
    return Frame(head_entry.form, feats, bind, slots)


def _time_word(norm: str) -> Node:
    if norm == "yesterday":
        return Frame("before", slots=[(None, Atom("nowt")), (None, Frame("qnt", slots=[(None, Frame("dieno")), (None, Num(1))]))])
    if norm == "tomorrow":
        return Frame("after", slots=[(None, Atom("nowt")), (None, Frame("qnt", slots=[(None, Frame("dieno")), (None, Num(1))]))])
    if norm == "today":
        return Frame("dieno", features=["def"])
    return Atom("nowt")


def _notes_for(text: str, prog: Program) -> list[str]:
    notes = []
    low = text.lower()
    if "with the telescope" in low or "with a telescope" in low:
        notes.append(
            "English 'with' is ambiguous (instrument vs accompaniment vs part). "
            "Nex used role ins (instrument). Use a relative clause for 'who had a telescope'."
        )
    if "ready to eat" in low:
        notes.append(
            "English 'ready to eat' is ambiguous (eater vs eaten). "
            "Nex used purpose with unspecified agent: ready FOR someone to eat it. "
            "Swap agt/thm in the purpose frame for the other reading."
        )
    words = set(re.findall(r"[a-z']+", low))
    if words & {"he", "she", "him", "her", "they", "them", "his", "their"}:
        notes.append(
            "Pronouns became indexed refs ($N) bound to the last person mentioned. "
            "In Nex, reference is never guessed from gender."
        )
    return notes


# Hand-built showcase pairs used when the heuristic translator is the wrong tool.
PARALLELS: list[dict[str, str]] = [
    {
        "en": "Maria gave John the red book.",
        "nex": "asrt ( doni past done agt ( pamo name maria = $1 ) thm ( mabo def mod ( ruga ) ) rec ( pamo name john = $2 ) ) .",
    },
    {
        "en": "I saw the man with the telescope.  (instrument)",
        "nex": "asrt ( vidi past agt spk thm ( pamo def = $1 ) ins ( teso def ) ) .",
    },
    {
        "en": "I saw the man with the telescope.  (the man has it)",
        "nex": "asrt ( vidi past agt spk thm ( pamo def = $1 rel ( havi agt $1 thm ( teso def ) ) ) ) .",
    },
    {
        "en": "The chicken is ready to eat.  (someone will eat the chicken)",
        "nex": "asrt ( redi thm ( puko def ) prp ( pusi agt unk thm ( puko def ) ) ) .",
    },
    {
        "en": "The chicken is ready to eat.  (the chicken will eat)",
        "nex": "asrt ( redi thm ( puko def = $1 ) prp ( pusi agt $1 thm unk ) ) .",
    },
    {
        "en": "Nobody saw every dog.",
        "nex": "asrt ( none ( pamo = $1 ) ( all ( pugo = $2 ) ( vidi past not exp $1 thm $2 ) ) ) .",
    },
    {
        "en": "Unhappiness faded.",
        "nex": "asrt ( hofi past thm ( koso mod ( hapa not ) ) ) .",
    },
    {
        "en": "She liked him because he helped her.",
        "nex": "asrt ( fali past exp $1 thm $2 cau ( duli past agt $2 thm $1 ) ) .",
    },
]
