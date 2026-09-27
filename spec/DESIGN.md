# Nex — design notes

Nex is a language whose unit of writing is the unit of computation.
This file records *why* the language looks the way it does.

## The job

A language for humans is shaped by the vocal tract, working memory,
and social transmission. A language for large language models is shaped by:

1. **Discrete tokens** and a finite vocabulary.
2. **Self-attention** (pairwise relations, quadratic in sequence length).
3. **Next-token prediction** (left-to-right commitment).
4. **Embedding geometry** (similar ids should start similar).
5. **Systematic generalization** (old parts, new combinations).
6. **A context window** (dependency length is a cost).

English, and natural language generally, is not optimized for any of these.
BPE on top of English is a compression codec pretending to be a morphology.

## Failure modes of natural language inside transformers

### Tokenization ≠ meaning

Subword tokenizers maximize corpus likelihood of merges. They will:

- cut a stem (`tokenization` → `token` + `ization`)
- treat case as new words (`Apple` / `apple` / `APPLE`)
- chunk numbers differently at every magnitude (`123` vs `1234` vs `12345`)
- split or fuse morphemes depending on frequency, not structure

A model cannot reliably learn that `un-` is negation if `unhappiness` and
`unfolding` do not share a token. Nex makes negation the token `not`.

### Ambiguity spends capacity

Attachment, pronoun reference, and quantifier scope are underspecified in
English strings. The model must infer a graph. That inference is useful for
*reading humans*. It is wasteful if the only readers are models — they would
rather be handed the graph.

Nex's grammar is PEG-shaped: one parse. If a meaning is not chosen, the
sentence cannot be written.

### Irregular morphology is a lookup table

`go / went / gone` is three embeddings that must be pulled together from
co-occurrence. Nex writes `( veli )`, `( veli past )`, `( veli past done )`.
The identity of the event is literal in the stream.

### Pronouns are untyped pointers

`she` is a search problem over the previous discourse. Nex binds
`( pamo name maria = $1 )` and then uses `$1`. Equality, not gender.

## Design laws

1. **Token = meaning.** Custom vocabulary. Roots never split.
2. **One string, one tree.** Recursive descent over closed-class lists.
3. **Roles are tokens.** `agt thm rec loc tmp cau …` — attention hooks.
4. **Morphology is syntax.** Features are atoms. There is no affix layer.
5. **Reference is an index.** `$n` from 1.
6. **Closed vocab, open world.** Names and numbers explode to letters/digits.
7. **Form encodes type; stems do not collide.** Events `-i`, primitive
   kinds `-o`, qualities `-a`, derived doers `-u`. The ending is a badge
   for humans and OOV fallback — the model already has type in syntax and
   in the structured id. Two primitives must not share a stem: that would
   look like a paradigm and lie.

## Why this shape and not Lojban / Ithkuil / ACE

- **Lojban** is the closest ancestor: unambiguous syntax, predicate logic.
  It is still a *spoken* language. Place structures (`x1 x2 x3`) are hard
  for humans *and* hide roles from attention. Apostrophes and cmavo clusters
  still fight BPE. Nex uses named roles and a tokenizer that *is* the language.
- **Ithkuil** maximizes morphological density. That is the wrong direction
  for token purity: one word, twelve categories, unreadable ids.
- **Attempto Controlled English** is still English at the tokenizer.
- **AMR / logical forms** are graphs. A decoder samples strings. Nex is a
  *canonical linearization* of a graph, so it is both a language and an IR.
- **Lisp** has the parens and none of the semantics.

## Transformer-specific bets

**Predicate-first.** Autoregressive generation commits left-to-right.
Announcing `doni` (give) constrains every later slot. Selectional
restrictions become next-token evidence immediately.

**Named roles as repeated keys.** Every agent is introduced by the same
token `agt`. An attention head can learn “copy the argument of `agt`”
once, globally — the thing SCAN-style work calls abstract grammatical roles.

**Index hints.** `$1` is the RASP-friendly version of a pronoun: a literal
pointer. Transformers length-generalize better when positions and indices
are in the tokens, not only in the positional encoding.

**Matching delimiters.** `(` and `)` are cheap, well-studied induction-head
targets. Depth is visible.

**Digit explosion.** Arithmetic in language models fails in part because
`12345` is not `1 2 3 4 5`. Nex's encoder always emits digits.

**Structured ids.** 16 bits: kind, field, root. Embedding init

```
E[t] = W_kind[k] + W_field[f] + W_root[r]
```

puts all transfer-events in one region before any gradient step.
BPE cannot offer an equivalent bias.

**Tiny kernel lexicon.** A few hundred atoms, composition for the rest.
Embedding matrix is small; parameters go to the residual stream.

**Derivation, then packing.** A relative clause is a definition, not a
word. English *-er* is `( agto seni )` (four tokens) or the packed kind
`senu` (one token). Packing flips the type vowel into a *reserved*
namespace: events `-i`, primitive kinds `-o`, qualities `-a`, derived
doers `-u`. `koli` (remember) becomes `kolu`, and never has to fight
`tino` (color). If two roots would collide, the lexicon is wrong — you
do not add an exception. The long form
`( pamo rel ( seni hab agt slf thm ( mabo ) ) )` stays available when you
actually need a clause.

## What Nex is not

It is not a claim that humans should speak this. It is not a trained LLM.
It is not a replacement for the world's languages at the human interface.

It *is* a proposal for the language models talk to themselves in:
an interlingua, a scratchpad, a tool-call format that is also a language.

## Training sketch (not executed here)

1. Semantic-parse or translate corpora into Nex kernel form.
2. Encode with the Nex vocabulary (~300 atoms + letters + digits).
3. Train a small decoder-only transformer on the stream.
4. Optionally initialize embeddings from structured ids.
5. Constrain decoding with the PEG (every sample is grammatical).

The hypothesis: lower perplexity per *meaning*, better compositional
generalization, no tokenizer mismatch — at the cost of a translation step
at the human boundary.
