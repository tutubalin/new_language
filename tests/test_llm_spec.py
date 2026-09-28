import re
import unittest
from pathlib import Path

from nex.lexicon import (
    DEICTICS,
    EVENTS,
    FEATURES,
    ILLOCUTIONS,
    KINDS,
    OPERATORS,
    QUALS,
    ROLES,
)


SPEC = Path(__file__).resolve().parent.parent / "spec" / "NEX_LLM.md"


class LlmSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SPEC.read_text(encoding="utf-8")
        cls.atoms = set(re.findall(r"\b[a-z][a-z0-9]*\b", cls.text))

    def _present(self, entries, label):
        missing = [e.form for e in entries if e.form not in self.atoms]
        self.assertEqual(missing, [], f"missing {label} in spec/NEX_LLM.md")

    def test_closed_listed(self):
        self._present(ILLOCUTIONS, "illoc")
        self._present(ROLES, "roles")
        self._present(FEATURES, "features")
        self._present(OPERATORS, "ops")
        self._present(DEICTICS, "deix")

    def test_open_listed(self):
        self._present(EVENTS, "events")
        self._present(KINDS, "kinds")
        self._present(QUALS, "quals")

    def test_no_drama_length(self):
        # brief: grammar+lexicon should fit a context window comfortably
        self.assertLess(len(self.text), 20_000)
