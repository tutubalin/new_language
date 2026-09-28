"""Nex — a language designed for large language models."""

from .lexicon import LEXICON, closed_class, lookup, english_to_root
from .ast_nodes import Frame, Atom, Ref, Num, Spell, Program, Statement
from .parser import parse, ParseError
from .serialize import serialize, encode, decode, gloss
from .english import from_english
from .ids import token_id, id_layout
from .compare import compare_tokenization

__all__ = [
    "LEXICON",
    "closed_class",
    "lookup",
    "english_to_root",
    "Frame",
    "Atom",
    "Ref",
    "Num",
    "Spell",
    "Program",
    "Statement",
    "parse",
    "ParseError",
    "serialize",
    "encode",
    "decode",
    "gloss",
    "from_english",
    "token_id",
    "id_layout",
    "compare_tokenization",
]

__version__ = "0.1.0"
