import unittest

from nex.course import all_accept_parses, check_exercise, load_primer, public_course
from nex.parser import parse


class PrimerTests(unittest.TestCase):
    def test_loads(self):
        data = load_primer()
        self.assertGreaterEqual(len(data["chapters"]), 12)
        self.assertGreaterEqual(data["drill_count"], 20)

    def test_hides_answers(self):
        pub = public_course()
        blob = str(pub)
        self.assertNotIn('"accept"', blob.replace(" ", ""))
        for ch in pub["chapters"]:
            for ex in ch["exercises"]:
                self.assertNotIn("answer", ex)

    def test_model_answers_parse(self):
        problems = all_accept_parses()
        self.assertEqual(problems, [])

    def test_see_dog(self):
        r = check_exercise("02-see-dog", "asrt ( vidi exp spk thm ( pugo ind ) ) .")
        self.assertTrue(r["correct"], r)

    def test_role_order_does_not_matter(self):
        r = check_exercise(
            "04-give",
            "asrt ( doni rec ( pamo name john ) thm ( mabo def ) agt ( pamo name maria ) ) .",
        )
        self.assertTrue(r["correct"], r)

    def test_wrong_role_fails(self):
        r = check_exercise("02-see-dog", "asrt ( vidi agt spk thm ( pugo ind ) ) .")
        self.assertFalse(r["correct"])

    def test_unparseable(self):
        r = check_exercise("02-see-dog", "I see a dog")
        self.assertFalse(r["correct"])
        self.assertIn("parser", r["message"].lower())

    def test_choice(self):
        r = check_exercise("00-ready", choice=1)
        self.assertTrue(r["correct"])
        r2 = check_exercise("00-ready", choice=0)
        self.assertFalse(r2["correct"])

    def test_feature_order(self):
        r = check_exercise("03-books", "asrt ( vidi exp spk thm ( mabo def pl ) ) .")
        self.assertTrue(r["correct"], r)

    def test_unhappy_frame(self):
        r = check_exercise("06-unhappy", "( koso mod ( hapa not ) )")
        self.assertTrue(r["correct"], r)
        r2 = check_exercise("06-unhappy", "( koso ( hapa not ) )")
        self.assertTrue(r2["correct"], r2)

    def test_reader_short(self):
        for form in ("( seno )", "( agto seni )", "( seno ind )"):
            r = check_exercise("12-reader", form)
            self.assertTrue(r.get("correct"), (form, r))


if __name__ == "__main__":
    unittest.main()
