# Unpushed kernel (this session could not push)

GitHub on the old Arena session is closed. A new session clones GitHub, not this sandbox.

**Do this in the new session:** apply the roots below to `nex/lexicon.py`, list them in `spec/NEX_LLM.md`, allow stem family `flu` (with `red` and `piv`) in `validate_lexicon` and `tests/test_nex.py`, add the wiki parse tests.

Rules: events `-i`, kinds `-o`, qualities `-a`; unique primitive stems; `flui`/`fluo` is derivation (flow/river). Proper names stay `name` atoms.

## Events to add

```
_e("flui", "evt", "motion", "flow", "flow/flowed/flowing", "agt gol src"),
_e("presi", "evt", "transfer", "press", "press/pressed/pressing", "agt thm"),
_e("stoki", "evt", "change", "store", "store/stored/keep/kept", "agt thm loc"),
_e("viki", "evt", "change", "win", "win/won/winning/defeat/defeated", "agt thm"),
_e("bati", "evt", "transfer", "fight", "fight/fought/fighting/wrestle", "agt thm"),
_e("koki", "evt", "life", "cook", "cook/cooked/cooking", "agt thm"),
_e("akti", "evt", "speech", "act", "act/acted/acting/perform/star-in", "agt thm"),
_e("lidi", "evt", "cognition", "lead", "lead/led/direct/directed", "agt thm"),
_e("pubi", "evt", "speech", "publish", "publish/published/release/released", "agt thm tmp"),
```

Insert `flui` after `voci`. Insert the rest after `redi`.

## Kinds to add

Life (after `puko`): `vego` plant, `bito` insect, `buto` butterfly, `speko` species, `sito` cell

Place (after `laso`): `fluo` river (notes: kind; event flui), `maro` sea/ocean, `monto` mountain/hill, `silvo` forest/woods, `lito` coast/shore, `bordo` border/frontier, `kapo` capital, `atmo` atmosphere

Matter/info/people (after `namo` / near `roso`): `muzo` music, `piano` piano, `keyo` key, `cordo` string/cord, `ergo` energy, `oxo` oxygen, `filmo` film/movie, `pago` paper/page, `armo` army, `firmo` company/firm, `rufo` roof, `metalo` metal

## Qualities to add (end of QUALS)

```
_e("grava", "qual", "value", "important", "important/historic"),
_e("skara", "qual", "feeling", "scary", "scary/horror/horrifying"),
```

## Stem families

`allowed_families` / test allowlist: `red`, `piv`, `flu`.

## Full files in this folder

If the new session can read attached files, copy:

- `handoff/nex_lexicon.py` → `nex/lexicon.py`
- `handoff/NEX_LLM.md` → `spec/NEX_LLM.md`
- `handoff/test_nex.py` → `tests/test_nex.py`

Then `PYTHONPATH=. python -m unittest tests.test_nex tests.test_course tests.test_llm_spec -q`