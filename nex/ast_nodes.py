"""Nex abstract syntax — the true language.

Text is a serialization. Token ids are another. Both round-trip to this graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Iterator, Union


Node = Union["Frame", "Atom", "Ref", "Num", "Spell"]


@dataclass(frozen=True)
class Atom:
    form: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "atom", "form": self.form}


@dataclass(frozen=True)
class Ref:
    n: int

    def to_dict(self) -> dict[str, Any]:
        return {"type": "ref", "n": self.n}

    @property
    def form(self) -> str:
        return f"${self.n}"


@dataclass(frozen=True)
class Num:
    """Integer whose model encoding is a sequence of digits."""

    value: int

    def digits(self) -> list[str]:
        if self.value < 0:
            return ["neg", *list(str(abs(self.value)))]
        return list(str(self.value))

    def to_dict(self) -> dict[str, Any]:
        return {"type": "num", "value": self.value}


@dataclass(frozen=True)
class Spell:
    """Open-class surface form spelled from letters."""

    text: str

    def letters(self) -> list[str]:
        return [ch.lower() for ch in self.text if ch.isalnum()]

    def to_dict(self) -> dict[str, Any]:
        return {"type": "spell", "text": self.text}


@dataclass
class Frame:
    head: str
    features: list[str] = field(default_factory=list)
    binding: int | None = None
    slots: list[tuple[str | None, Node]] = field(default_factory=list)
    # slots: (role, arg). role is None for operator children.

    def args(self, role: str) -> list[Node]:
        return [n for r, n in self.slots if r == role]

    def arg(self, role: str) -> Node | None:
        found = self.args(role)
        return found[0] if found else None

    def walk(self) -> Iterator[Node]:
        yield self
        for _, n in self.slots:
            if isinstance(n, Frame):
                yield from n.walk()
            else:
                yield n

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "frame",
            "head": self.head,
            "features": list(self.features),
            "binding": self.binding,
            "slots": [
                {
                    "role": role,
                    "arg": arg.to_dict() if hasattr(arg, "to_dict") else arg,
                }
                for role, arg in self.slots
            ],
        }

    def canonical(self) -> Frame:
        from .lexicon import FEAT_ORDER, ROLE_ORDER, is_operator

        feat_rank = {f: i for i, f in enumerate(FEAT_ORDER)}
        role_rank = {r: i for i, r in enumerate(ROLE_ORDER)}
        features = sorted(self.features, key=lambda f: feat_rank.get(f, 1000))
        if is_operator(self.head):
            slots = [(r, _canon_node(n)) for r, n in self.slots]
        else:
            numbered = []
            mods = []
            rest = []
            for i, (r, n) in enumerate(self.slots):
                n2 = _canon_node(n)
                if r == "mod":
                    mods.append((r, n2))
                elif r in role_rank:
                    numbered.append((role_rank[r], i, r, n2))
                else:
                    rest.append((r, n2))
            numbered.sort()
            slots = [(r, n) for _, _, r, n in numbered] + rest + mods
        return Frame(self.head, features, self.binding, slots)


def _canon_node(n: Node) -> Node:
    if isinstance(n, Frame):
        return n.canonical()
    return n


@dataclass
class Statement:
    illoc: str
    frame: Frame

    def to_dict(self) -> dict[str, Any]:
        return {"type": "stmt", "illoc": self.illoc, "frame": self.frame.to_dict()}

    def canonical(self) -> Statement:
        return Statement(self.illoc, self.frame.canonical())


@dataclass
class Program:
    statements: list[Statement] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"type": "program", "statements": [s.to_dict() for s in self.statements]}

    def canonical(self) -> Program:
        return Program([s.canonical() for s in self.statements])
