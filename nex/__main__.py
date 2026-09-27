"""CLI: python -m nex parse|gloss|en|encode|compare ..."""

from __future__ import annotations

import json
import sys

from .compare import compare_tokenization, morphology_table
from .english import TranslateError, from_english
from .lexicon import lexicon_public, validate_lexicon
from .parser import ParseError, parse
from .serialize import encode, gloss, serialize


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print(__doc__)
        print("commands: parse, gloss, en, encode, compare, morph, lexicon, check")
        return 0
    cmd, *rest = argv
    text = " ".join(rest) if rest else sys.stdin.read()
    try:
        if cmd == "parse":
            prog = parse(text)
            print(serialize(prog.canonical()))
            return 0
        if cmd == "gloss":
            print(gloss(text))
            return 0
        if cmd == "en":
            print(from_english(text)["nex"])
            return 0
        if cmd == "encode":
            print(" ".join(encode(text)))
            return 0
        if cmd == "compare":
            # rest: english | nex
            if "|" in text:
                en, nex = [s.strip() for s in text.split("|", 1)]
            else:
                en, nex = text, None
            print(json.dumps(compare_tokenization(en, nex), indent=2))
            return 0
        if cmd == "morph":
            print(json.dumps(morphology_table(), indent=2))
            return 0
        if cmd == "lexicon":
            print(json.dumps(lexicon_public(), indent=2))
            return 0
        if cmd == "check":
            probs = validate_lexicon()
            if probs:
                print("\n".join(probs))
                return 1
            print("lexicon ok", len(lexicon_public()), "entries")
            return 0
        print(f"unknown command {cmd}", file=sys.stderr)
        return 2
    except (ParseError, TranslateError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
