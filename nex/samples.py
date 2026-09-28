"""Canonical Nex texts — a small parallel corpus."""

from __future__ import annotations

NORTH_WIND = """
asrt ( seq
  ( saki past
      agt ( wino mod ( northa ) def = $1 )
      rec ( suno def = $2 )
      cnt ( kabi exp $1 cnt ( stroa more thm $1 thm $2 ) ) )
  ( vini past
      thm ( pamo ind = $3 )
      mod ( dafi ong agt $3 thm ( muko tita ) ) )
  ( saki past agt $1 rec $2 cnt
      ( same
          ( pamo rel ( dusi agt slf thm ( muko ) first )
          )
          ( pamo stroa most ) ) )
) .
""".strip()

# cleaner North Wind
NORTH_WIND = """
asrt ( seq
  ( saki past agt ( wino def mod ( northa ) = $1 ) rec ( suno def = $2 ) cnt ( kabi exp $1 cnt ( stroa more thm $1 ) ) )
  ( vini past agt ( pamo ind = $3 ) gol here )
  ( dafi ong agt $3 thm ( muko def mod ( tita ) ) )
  ( saki past agt $1 rec $2 cnt ( kawi exp $1 thm ( dusi agt $3 thm ( muko def ) ) ) )
  ( dayi past agt $1 thm ( vaki agt $1 ) )
  ( dafi more agt $3 thm ( muko def ) )
  ( hofi past agt $1 )
  ( hosi past agt $2 thm ( luxo ) )
  ( dusi past agt $3 thm ( muko def ) )
  ( saki past agt $1 rec $2 cnt ( kuni exp $1 thm ( stroa more thm $2 ) ) )
) .
""".strip()

UDHR1 = """
asrt ( all ( pamo = $1 )
  ( and
    ( paxi thm $1 mod ( fria ) mod ( equa ) )
    ( havi agt $1 thm ( and ( keni ) ( koso mod ( guda ) ) ) )
  )
) .
""".strip()

HELLO = """
asrt ( saki agt spk rec hrd cnt ( hapa thm spk ) ) .
""".strip()

GIVE = """
asrt ( doni past done
  agt ( pamo name maria = $1 )
  thm ( mabo def mod ( ruga ) = $2 )
  rec ( pamo name john = $3 )
  tmp ( before nowt ( qnt ( dieno ) 1 ) )
  cau ( fali past exp $1 thm $3 )
) .
""".strip()

AMBIGUOUS = [
    {
        "id": "telescope-ins",
        "en": "I saw the man with the telescope.",
        "reading": "The telescope is the instrument of seeing.",
        "nex": "asrt ( vidi past exp spk thm ( pamo def = $1 ) ins ( teso def ) ) .",
    },
    {
        "id": "telescope-rel",
        "en": "I saw the man with the telescope.",
        "reading": "The man who had the telescope is who was seen.",
        "nex": "asrt ( vidi past exp spk thm ( pamo def = $1 rel ( havi agt $1 thm ( teso def ) ) ) ) .",
    },
    {
        "id": "chicken-eaten",
        "en": "The chicken is ready to eat.",
        "reading": "The chicken is prepared as food.",
        "nex": "asrt ( redi thm ( puko def = $1 ) prp ( pusi agt unk thm $1 ) ) .",
    },
    {
        "id": "chicken-eater",
        "en": "The chicken is ready to eat.",
        "reading": "The chicken is ready to eat something.",
        "nex": "asrt ( redi thm ( puko def = $1 ) prp ( pusi agt $1 thm unk ) ) .",
    },
    {
        "id": "nobody-every",
        "en": "Nobody saw every dog.",
        "reading": "There is no person such that they saw every dog.",
        "nex": "asrt ( none ( pamo = $1 ) ( all ( pugo = $2 ) ( vidi past exp $1 thm $2 ) ) ) .",
    },
    {
        "id": "every-nobody",
        "en": "Nobody saw every dog.",
        "reading": "For every dog, nobody saw it. (different scope)",
        "nex": "asrt ( all ( pugo = $2 ) ( none ( pamo = $1 ) ( vidi past exp $1 thm $2 ) ) ) .",
    },
]

EXAMPLES = [
    {
        "id": "give",
        "title": "A transfer with cause and time",
        "en": "Maria gave John the red book yesterday because she liked him.",
        "nex": GIVE,
    },
    {
        "id": "hello",
        "title": "A greeting is just a speech frame",
        "en": "I tell you that I am happy.",
        "nex": HELLO,
    },
    {
        "id": "udhr",
        "title": "Universal Declaration, article 1 (abridged)",
        "en": "All people are born free and equal, and they have thought and a good-state.",
        "nex": UDHR1,
    },
    {
        "id": "wind",
        "title": "The North Wind and the Sun (abridged)",
        "en": "The north wind and the sun argued; a traveller came; the sun warmed him; he took off the cloak; the wind knew the sun was stronger.",
        "nex": NORTH_WIND,
    },
]


def all_nex_snippets() -> list[str]:
    out = [GIVE, HELLO, UDHR1, NORTH_WIND]
    out.extend(a["nex"] for a in AMBIGUOUS)
    return out
