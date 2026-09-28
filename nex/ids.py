"""Feature-aligned token IDs.

Bits of the id encode type and semantic field so a model can be initialized
with embeddings that already know 'doni' and 'daki' are both transfer events.
This is an inductive bias BPE vocabularies cannot offer: their ids are
accidents of merge order.
"""

from __future__ import annotations

from .lexicon import LEXICON, Entry

KIND_CODE = {
    "struct": 0x0,
    "illoc": 0x1,
    "role": 0x2,
    "feat": 0x3,
    "op": 0x4,
    "deictic": 0x5,
    "evt": 0x6,
    "kind": 0x7,
    "qual": 0x8,
    "ref": 0x9,
}

FIELD_CODE = {
    "struct": 0x0,
    "speech": 0x1,
    "role": 0x2,
    "polarity": 0x3,
    "tense": 0x3,
    "aspect": 0x3,
    "mood": 0x3,
    "evid": 0x3,
    "det": 0x3,
    "number": 0x3,
    "degree": 0x3,
    "logic": 0x4,
    "quant": 0x5,
    "modal": 0x4,
    "rel": 0x4,
    "deixis": 0x6,
    "time": 0x7,
    "transfer": 0x8,
    "motion": 0x9,
    "sense": 0xA,
    "cognition": 0xB,
    "feeling": 0xC,
    "life": 0xD,
    "change": 0xE,
    "people": 0xD,
    "matter": 0xF,
    "info": 0xB,
    "place": 0x9,
    "abstract": 0x4,
    "value": 0xC,
    "phys": 0xF,
    "space": 0x9,
    "spell": 0x0,
}


def token_id(form: str) -> int:
    """16-bit id: KKKK FFFF RRRRRRRR  (kind, field, root)."""
    if form.startswith("$") and form[1:].isdigit():
        n = int(form[1:])
        return (KIND_CODE["ref"] << 12) | (n & 0xFF)
    e = LEXICON.get(form)
    if e is None:
        # hash open form into root byte
        h = sum(ord(c) for c in form) & 0xFF
        return h
    k = KIND_CODE.get(e.kind, 0)
    f = FIELD_CODE.get(e.field, 0)
    root = sum(ord(c) * (i + 1) for i, c in enumerate(e.form)) & 0xFF
    return (k << 12) | (f << 8) | root


def decode_id_fields(i: int) -> dict:
    kind_n = (i >> 12) & 0xF
    field_n = (i >> 8) & 0xF
    root = i & 0xFF
    kind = next((k for k, v in KIND_CODE.items() if v == kind_n), str(kind_n))
    return {"id": i, "kind": kind, "field_code": field_n, "root": root, "hex": f"0x{i:04X}"}


def id_layout() -> dict:
    return {
        "bits": "KKKK FFFF RRRRRRRR",
        "kind": KIND_CODE,
        "field": FIELD_CODE,
        "note": (
            "Embeddings can be initialized as E = Wk[kind] + Wf[field] + Wr[root]. "
            "All transfer-events then start in the same region of space."
        ),
    }
