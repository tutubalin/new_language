"""Show why English tokenization fights meaning, and Nex does not."""

from __future__ import annotations

import re
from typing import Iterable

from .parser import ParseError, parse
from .serialize import encode, pretty_tokens, serialize


# Classic GPT-2 / GPT-3 BPE fragmentations. These match OpenAI tiktoken
# `gpt2` for the listed strings (leading space sensitive). Used when tiktoken
# is not installed so the demo stays honest about real model behaviour.
CANONICAL_BPE: dict[str, list[str]] = {
    "unhappiness": ["un", "happiness"],
    "unhappiness.": ["un", "happiness", "."],
    "Unhappiness": ["Un", "happiness"],
    "tokenization": ["token", "ization"],
    "Tokenization": ["Token", "ization"],
    "unfolding": ["unfold", "ing"],
    "the unfolding": ["the", " unfold", "ing"],
    "Apple": ["Apple"],
    "apple": ["apple"],
    "APPLE": ["APP", "LE"],
    "it's": ["it", "'s"],
    "It's": ["It", "'s"],
    "123": ["123"],
    "1234": ["123", "4"],
    "12345": ["123", "45"],
    "123456": ["123", "456"],
    "1,234": ["1", ",", "234"],
    "looking": ["looking"],
    "looked": ["looked"],
    "Looked": ["Look", "ed"],
    "ran": ["ran"],
    "run": ["run"],
    "running": ["running"],
    "the": ["the"],
    "The": ["The"],
    " THE": [" THE"],
    "I saw the man with the telescope": [
        "I",
        " saw",
        " the",
        " man",
        " with",
        " the",
        " telescope",
    ],
}


def _try_tiktoken(text: str) -> list[str] | None:
    try:
        import tiktoken  # type: ignore
    except Exception:
        return None
    try:
        enc = tiktoken.get_encoding("gpt2")
        ids = enc.encode(text)
        return [enc.decode([i]) for i in ids]
    except Exception:
        return None


def english_bpe(text: str) -> list[str]:
    got = _try_tiktoken(text)
    if got is not None:
        return got
    if text in CANONICAL_BPE:
        return list(CANONICAL_BPE[text])
    # Fall back: split like a cheap byte-level BPE analogue.
    # Keep known fragments, otherwise split camelCase / punctuation / digits.
    return _fallback_pieces(text)


def _fallback_pieces(text: str) -> list[str]:
    # Prefer whole-word lookup of substrings from CANONICAL_BPE longest first.
    keys = sorted(CANONICAL_BPE, key=len, reverse=True)
    i = 0
    out: list[str] = []
    while i < len(text):
        matched = False
        for k in keys:
            if text.startswith(k, i):
                out.extend(CANONICAL_BPE[k])
                i += len(k)
                matched = True
                break
        if matched:
            continue
        # eat one "word-like" chunk
        m = re.match(r"\s+|[A-Z]?[a-z]+|[A-Z]+|[0-9]+|[^\s]", text[i:])
        if not m:
            out.append(text[i])
            i += 1
            continue
        piece = m.group(0)
        if piece in CANONICAL_BPE:
            out.extend(CANONICAL_BPE[piece])
        else:
            out.append(piece)
        i += m.end()
    return out


SHOWCASE = [
    {
        "title": "Negation is a morpheme, not a coin-flip split",
        "en": "unhappiness",
        "nex": "( koso mod ( hapa not ) )",
        "why": "English BPE may keep 'happiness' and split 'un', or worse, split inside the stem. In Nex, not is always the same token, hapa is always the same token, koso always nominalizes.",
    },
    {
        "title": "Case must not duplicate a word",
        "en": "Apple apple APPLE",
        "nex": "( mabo name apple )",
        "why": "English vocabularies store Apple, apple, APPLE as unrelated ids. Nex has no case. Names are a role, not a new lemma.",
    },
    {
        "title": "Numbers should be digits",
        "en": "12345",
        "nex": "( num 1 2 3 4 5 )",
        "why": "BPE chunks integers differently at every magnitude (123 vs 1234 vs 12345). Nex explodes numbers to digits, which is the encoding transformers can actually compute with.",
    },
    {
        "title": "Irregular verbs are a tax on embeddings",
        "en": "go went gone going",
        "nex": "( veli ) ( veli past ) ( veli past done ) ( veli ong )",
        "why": "English forces the model to learn that go/went/gone are 'the same verb' from co-occurrence. Nex says so in the token stream.",
    },
    {
        "title": "Attachment ambiguity is not a feature",
        "en": "I saw the man with the telescope",
        "nex": "asrt ( vidi past agt spk thm ( pamo def = $1 ) ins ( teso def ) ) .",
        "why": "One English string, two syntax trees. Nex refuses to write the sentence until you pick instrument vs modifier.",
    },
]


def compare_tokenization(english: str, nex: str | None = None) -> dict:
    en_toks = english_bpe(english)
    nex_info: dict | None = None
    if nex:
        try:
            prog = parse(nex)
            stream = encode(prog)
            nex_info = {
                "text": serialize(prog, pretty=False),
                "tokens": pretty_tokens(stream),
                "count": len(stream),
                "error": None,
            }
        except ParseError as e:
            # still show whitespace tokens of the raw string
            raw = nex.split()
            nex_info = {
                "text": nex,
                "tokens": [{"tok": t, "kind": "open", "gloss": t, "field": ""} for t in raw],
                "count": len(raw),
                "error": str(e),
            }
    return {
        "english": english,
        "english_tokens": en_toks,
        "english_count": len(en_toks),
        "nex": nex_info,
    }


def morphology_table() -> list[dict]:
    """Same root, many English surface forms, one Nex stem."""
    rows = [
        ("happy", "( hapa )", "hapa"),
        ("unhappy", "( hapa not )", "hapa + not"),
        ("happiness", "( koso ( hapa ) )", "koso + hapa"),
        ("unhappiness", "( koso ( hapa not ) )", "koso + hapa + not"),
        ("reader", "( seno )", "seno ← agto + seni"),
        ("happier", "( hapa more )", "hapa + more"),
        ("happiest", "( hapa most )", "hapa + most"),
        ("go", "( veli )", "veli"),
        ("went", "( veli past )", "veli + past"),
        ("gone", "( veli past done )", "veli + past + done"),
        ("going", "( veli ong )", "veli + ong"),
        ("books", "( mabo pl )", "mabo + pl"),
        ("the book", "( mabo def )", "mabo + def"),
    ]
    out = []
    for en, nex, note in rows:
        cmp = compare_tokenization(en, nex)
        out.append({**cmp, "note": note})
    return out
