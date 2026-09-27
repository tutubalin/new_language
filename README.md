# Nex

**A language invented for models that think in tokens.**

Natural languages are good for humans. They are quietly bad for LLMs.
Tokenizers cut words where morphology would not. One English string hides
two syntax trees. `go` and `went` are strangers in embedding space.
`she` is a search problem.

Nex is a constructed language whose unit of writing **is** the unit of
computation.

```
asrt ( doni past done
  agt ( pamo name maria = $1 )
  thm ( mabo def mod ( ruga ) )
  rec ( pamo name john = $2 )
) .
```

That is not a gloss of “Maria gave John the red book.” It *is* the sentence:
one predicate, named roles, a bound speaker-independent index, a modifier
that is itself a frame. There is no other parse.

## Why a new language

| English in a transformer | Nex |
| --- | --- |
| BPE shards `unhappiness` | `not` + `hapa` + `koso` |
| `Apple` / `apple` / `APPLE` | no case |
| `123` vs `12345` as different chunks | digits, always |
| `go / went / gone` | `veli` + `past` + `done` |
| “I saw the man with the telescope” | writer must pick `ins` or `rel` |
| `she` | `$1` |
| 50k–100k accidental ids | ~300 kernel tokens, structured bits |

The design is in [`spec/DESIGN.md`](spec/DESIGN.md). Short version:

1. **Token = meaning.** Never split a root.
2. **One string, one tree.** Deterministic grammar.
3. **Roles are tokens.** `agt` is an attention hook.
4. **Morphology is syntax.** No irregular affixes.
5. **Reference is an index.**
6. **Closed vocabulary.** Names and numbers explode to letters and digits.
7. **Form encodes type.** Events `-i`, kinds `-o`, qualities `-a`.

This is not Lojban with a fresh coat of paint. Lojban is a spoken logical
language. Nex is a *token language*: predicate-first for autoregression,
named roles for attention, `$n` for RASP-style index hints, digit explosion
for arithmetic, and 16-bit ids that pack kind and field so embeddings can
be initialized with a real inductive bias.

## Run the playground

```bash
python server.py
```

Then open the URL it prints. The studio translates a kernel subset of
English, parses Nex, shows the unique tree, and compares BPE against Nex
atoms.

```bash
PYTHONPATH=. python -m nex parse 'asrt ( vidi past exp spk thm ( pugo def ) ) .'
PYTHONPATH=. python -m nex en 'Maria gave John the red book.'
PYTHONPATH=. python -m nex encode 'asrt ( qnt ( dieno ) 12345 ) .'
PYTHONPATH=. python -m unittest tests.test_nex
```

## Layout

```
nex/           language: lexicon, parser, encoder, English bridge
web/           playground
spec/DESIGN.md why these choices
examples/      sample texts
tests/         round-trip, disambiguation, tokenization
```

## A note on ambition

Nex does not pretend a full English translator. The English bridge is a
clause grammar for the kernel, so you can feel the language. The language
itself is specified, parsed, canonicalized, and encoded. That is the claim:
**we know what “suitable for LLMs” means well enough to write one down.**
