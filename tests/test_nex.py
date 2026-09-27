import unittest

from nex.ast_nodes import Frame
from nex.compare import compare_tokenization, morphology_table
from nex.english import TranslateError, from_english
from nex.lexicon import LEXICON, validate_lexicon
from nex.parser import ParseError, parse
from nex.samples import AMBIGUOUS, EXAMPLES, all_nex_snippets
from nex.serialize import decode, encode, gloss, serialize


class LexiconTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_lexicon(), [])

    def test_no_fake_stem_families(self):
        from collections import defaultdict
        from nex.lexicon import DERIVED_AGENTS

        derived = {d.form for d in DERIVED_AGENTS}
        stems = defaultdict(list)
        for e in LEXICON.values():
            if e.kind not in {"evt", "kind", "qual"} or e.form in derived:
                continue
            stems[e.form[:-1]].append(e)
        allowed = {"red", "piv"}
        for stem, items in stems.items():
            if stem in allowed:
                continue
            self.assertLessEqual(len(items), 1, [(x.form, x.gloss) for x in items])

    def test_type_endings(self):
        for e in LEXICON.values():
            if e.kind == "evt":
                self.assertTrue(e.form.endswith("i"), e.form)
            if e.kind == "kind":
                self.assertTrue(
                    e.form.endswith("o") or e.form.endswith("u"),
                    e.form,
                )
            if e.kind == "qual":
                self.assertTrue(e.form.endswith("a"), e.form)

    def test_closed_disjoint(self):
        from nex.lexicon import FEATURES, ILLOCUTIONS, OPERATORS, ROLES

        bags = {
            "illoc": {e.form for e in ILLOCUTIONS},
            "role": {e.form for e in ROLES},
            "feat": {e.form for e in FEATURES},
            "op": {e.form for e in OPERATORS},
        }
        seen = {}
        for name, forms in bags.items():
            for f in forms:
                self.assertNotIn(f, seen, f"collision {f} in {name} and {seen.get(f)}")
                seen[f] = name


class ParserTests(unittest.TestCase):
    def test_double_bind_rejected(self):
        with self.assertRaises(ParseError):
            parse("asrt ( pamo = $1 name earth = $2 ) .")

    def test_earth_sentence(self):
        src = (
            "asrt ( and "
            "( same ( plano def = $1 name earth ) "
            "( plano def src ( suno def ) mod ( ord 3 ) ) ) "
            "( one ( celo = $2 ) "
            "( kuni exp unk thm ( havi agt $2 thm ( pivo ) ) ) ) "
            "( same $1 $2 ) ) ."
        )
        p = parse(src)
        self.assertEqual(p.statements[0].frame.head, "and")

    def test_give(self):
        src = (
            "asrt ( doni past done "
            "agt ( pamo name maria = $1 ) "
            "thm ( mabo def mod ( ruga ) ) "
            "rec ( pamo name john = $2 ) ) ."
        )
        p = parse(src)
        self.assertEqual(len(p.statements), 1)
        f = p.statements[0].frame
        self.assertEqual(f.head, "doni")
        self.assertIn("past", f.features)
        self.assertEqual(f.arg("agt").head, "pamo")  # type: ignore
        self.assertEqual(f.arg("agt").binding, 1)  # type: ignore

    def test_roundtrip(self):
        src = "ask ( vidi past exp spk thm ( pamo def = $1 ) ) ."
        p = parse(src)
        text = serialize(p, pretty=False)
        p2 = parse(text)
        self.assertEqual(p2.to_dict(), p.to_dict())

    def test_encode_roundtrip(self):
        src = "asrt ( doni past agt spk thm ( mabo ind ) rec hrd ) ."
        toks = encode(src)
        p = decode(toks)
        self.assertEqual(p.statements[0].frame.head, "doni")
        self.assertIn("(", toks)
        self.assertIn("doni", toks)
        self.assertIn("spk", toks)

    def test_digits_explode(self):
        toks = encode("asrt ( qnt ( dieno ) 12345 ) .")
        for d in "12345":
            self.assertIn(d, toks)
        self.assertNotIn("12345", toks)

    def test_unique_parse_rejects_junk(self):
        with self.assertRaises(ParseError):
            parse("( doni maria john )")  # missing roles

    def test_samples_parse(self):
        for snip in all_nex_snippets():
            try:
                parse(snip)
            except ParseError as e:
                self.fail(f"{e} in {snip}")

    def test_ambiguous_pairs_differ(self):
        by_en: dict[str, list] = {}
        for row in AMBIGUOUS:
            by_en.setdefault(row["en"], []).append(row["nex"])
        for en, nexa in by_en.items():
            trees = [parse(n).to_dict() for n in nexa]
            # every reading is a different tree
            dumped = [str(t) for t in trees]
            self.assertEqual(len(dumped), len(set(dumped)), en)

    def test_gloss_not_empty(self):
        g = gloss("asrt ( fali exp spk thm hrd ) .")
        self.assertIn("like", g)


class EnglishTests(unittest.TestCase):
    def test_simple_give(self):
        r = from_english("Maria gave John the red book.")
        p = parse(r["nex"])
        f = p.statements[0].frame
        self.assertEqual(f.head, "doni")
        self.assertIn("past", f.features)
        agt = f.arg("agt")
        self.assertIsInstance(agt, Frame)
        self.assertEqual(agt.head, "pamo")  # type: ignore

    def test_see(self):
        r = from_english("I saw the dog.")
        f = parse(r["nex"]).statements[0].frame
        self.assertEqual(f.head, "vidi")

    def test_unknown_verb(self):
        with self.assertRaises(TranslateError):
            from_english("Maria yeeted the book.")

    def test_what_time_is_it_now(self):
        r = from_english("What time is it now?")
        p = parse(r["nex"])
        self.assertEqual(p.statements[0].illoc, "ask")
        f = p.statements[0].frame
        self.assertEqual(f.head, "toko")
        self.assertIsNotNone(f.arg("tmp"))

    def test_what_is_the_time(self):
        r = from_english("What is the time?")
        self.assertEqual(parse(r["nex"]).statements[0].frame.head, "toko")


class CompareTests(unittest.TestCase):
    def test_unhappiness_splits_in_english(self):
        cmp = compare_tokenization("unhappiness", "( koso mod ( hapa not ) )")
        self.assertGreaterEqual(cmp["english_count"], 2)
        self.assertIsNotNone(cmp["nex"])
        toks = [t["tok"] for t in cmp["nex"]["tokens"]]
        self.assertIn("hapa", toks)
        self.assertIn("not", toks)

    def test_morph_table(self):
        rows = morphology_table()
        self.assertGreaterEqual(len(rows), 8)


class DerivationTests(unittest.TestCase):
    def test_reader_packed(self):
        from nex.lexicon import AGENT_PACK, lookup

        self.assertEqual(AGENT_PACK.get("seni"), "senu")
        self.assertEqual(lookup("senu").gloss, "reader")

    def test_every_event_has_an_agent_noun(self):
        from nex.lexicon import AGENT_PACK, EVENTS, lookup

        for e in EVENTS:
            packed = AGENT_PACK.get(e.form)
            self.assertIsNotNone(packed, e.form)
            self.assertTrue(packed.endswith("u"), packed)
            self.assertEqual(lookup(packed).kind, "kind")

    def test_remember_does_not_collide_with_color(self):
        from nex.lexicon import AGENT_PACK, lookup

        self.assertEqual(AGENT_PACK.get("koli"), "kolu")
        self.assertEqual(lookup("tino").gloss, "color")
        self.assertNotEqual(AGENT_PACK.get("koli"), "tino")

    def test_agto_parses_and_packs(self):
        from nex.serialize import pack_derived

        p = parse("( agto seni )")
        packed = pack_derived(p)
        self.assertEqual(packed.statements[0].frame.head, "senu")

    def test_reader_of_books(self):
        p = parse("( agto seni thm ( mabo ) )")
        self.assertEqual(p.statements[0].frame.head, "agto")


class CanonicalTests(unittest.TestCase):
    def test_role_order_stable(self):
        a = parse("( doni rec hrd agt spk thm ( mabo ) )")
        b = parse("( doni agt spk thm ( mabo ) rec hrd )")
        sa = serialize(a.canonical(), pretty=False)
        sb = serialize(b.canonical(), pretty=False)
        self.assertEqual(sa, sb)


if __name__ == "__main__":
    unittest.main()
