# First Nex

A primer from zero. Sixteen short chapters, a handful of roots at a time,
drills the parser will actually mark. You do not need linguistics, and you
do not need to care about models — but every rule you learn is a rule a
transformer can keep.

How to use this: read a chapter, say the examples out loud (it helps), then
do the drills. In the [interactive primer](/book.html) the drills are checked
by the real Nex parser. On GitHub, answers sit in the folded blocks.

Nex is written in lowercase. Spaces separate atoms. Parentheses group
meaning. That is the whole orthography.

<!--ex
{"id": "00-ready", "type": "choice", "prompt": "Nex is written with…", "choices": ["capital letters and commas", "lowercase atoms, spaces, and parentheses", "a private alphabet you must install"], "answer": 1}
-->

# 1. The skeleton

Every Nex sentence has three pieces:

1. an **illocution** — what you are doing with the sentence
2. a **frame** — the meaning, in parentheses
3. a **dot** — the sentence is finished

```
asrt ( … ) .
```

`asrt` means *I assert this*. It is the default speech act, the cousin of a
period in English. The other four, which you will meet later:

| atom | you are… |
| --- | --- |
| `asrt` | stating |
| `ask` | asking |
| `cmd` | telling someone to do it |
| `opt` | wishing |
| `exch` | exclaiming |

Inside the parentheses the **first atom is the head**. Everything after it
hangs off that head. A head that is an event ends in **-i**. A thing ends in
**-o**. A quality ends in **-a**. You can see the type without a dictionary.

```
( vidi … )     ← an event: seeing
( pugo … )     ← a kind: dog
( ruga … )     ← a quality: red
```

If you remember only one thing from this chapter: **Nex does not use word
order to mean “who did what.”** It uses role atoms. We start those next.

<details>
<summary>Check yourself</summary>

- A sentence without a dot is unfinished.
- `vidi` is an event because it ends in `i`.
- `asrt` is not a verb. It is the kind of move you are making.

</details>

<!--ex
{"id": "01-ending", "type": "choice", "prompt": "The atom `mabo` (book) is a…", "choices": ["event (-i)", "kind (-o)", "quality (-a)"], "answer": 1}
-->

<!--ex
{"id": "01-illoc", "type": "choice", "prompt": "Which atom means you are asking, not stating?", "choices": ["asrt", "ask", "agt"], "answer": 1}
-->

# 2. I see a dog

Seeing is `vidi`. The one who sees is not an agent in Nex — seeing happens
to you — so the role is `exp` (experiencer). The thing seen is `thm`
(theme): the thing the event is about.

I is `spk` (speaker). You is `hrd` (hearer). A dog is `pugo`. “A” is the
feature `ind` (indefinite). “The” is `def`.

```
asrt ( vidi exp spk thm ( pugo ind ) ) .
```

Read it slowly: *assert / see / experiencer=speaker / theme=a dog.*

Swap `ind` for `def` and you have a particular dog:

```
asrt ( vidi exp spk thm ( pugo def ) ) .
```

The nested parentheses are not decoration. `( pugo ind )` is a whole
argument, a little frame sitting in the `thm` slot. Nested frames are how
Nex grows without new grammar.

**A pattern you will use forever:**

```
asrt ( EVENT  ROLE ARG  ROLE ARG ) .
```

Arguments are either a short atom (`spk`, `hrd`) or a frame `( … )`.

<details>
<summary>Answers for the drills below</summary>

I see the dog:

```
asrt ( vidi exp spk thm ( pugo def ) ) .
```

You see a dog:

```
asrt ( vidi exp hrd thm ( pugo ind ) ) .
```

</details>

<!--ex
{"id": "02-see-dog", "type": "match", "prompt": "Write Nex: I see a dog.", "hint": "vidi, exp spk, thm ( pugo ind )", "accept": ["asrt ( vidi exp spk thm ( pugo ind ) ) ."]}
-->

<!--ex
{"id": "02-see-the", "type": "match", "prompt": "Write Nex: I see the dog.", "hint": "Only ind changes.", "accept": ["asrt ( vidi exp spk thm ( pugo def ) ) ."]}
-->

<!--ex
{"id": "02-you-see", "type": "match", "prompt": "Write Nex: You see a dog.", "hint": "Hearer is hrd.", "accept": ["asrt ( vidi exp hrd thm ( pugo ind ) ) ."]}
-->

<!--ex
{"id": "02-read", "type": "choice", "prompt": "asrt ( vidi exp hrd thm ( pugo def ) ) .", "choices": ["You see the dog.", "The dog sees you.", "I see a dog."], "answer": 0}
-->

# 3. People, cats, books, names

Kinds you need this week:

| Nex | English |
| --- | --- |
| `pamo` | person |
| `pugo` | dog |
| `piko` | cat |
| `mabo` | book |
| `pabo` | child |
| `meso` | house |

A name is not a new kind of word. It is a **role** on a person frame:

```
( pamo name maria )
( pamo name john )
```

Names are lowercase. Nex has no capital letters, so “Maria” cannot smuggle
a second identity into the vocabulary.

```
asrt ( vidi exp ( pamo name maria ) thm ( piko def ) ) .
```

*Maria sees the cat.*

Hear that `exp` is now a whole frame, not `spk`. Anywhere an argument can
be an atom, it can be a frame.

Two features you already know, on kinds:

| feature | English |
| --- | --- |
| `def` | the |
| `ind` | a / some |
| `pl` | more than one |

```
asrt ( vidi exp spk thm ( mabo pl def ) ) .
```

*I see the books.* Features sit on the head, before the roles:

```
( mabo pl def )
```

Order of features does not matter. The canonicalizer will sort them. You
can write `def pl` or `pl def`.

<details>
<summary>Answers</summary>

Maria sees a book:

```
asrt ( vidi exp ( pamo name maria ) thm ( mabo ind ) ) .
```

I see the cats:

```
asrt ( vidi exp spk thm ( piko pl def ) ) .
```

</details>

<!--ex
{"id": "03-maria-cat", "type": "match", "prompt": "Write Nex: Maria sees the cat.", "hint": "( pamo name maria ) in exp. Cat is piko.", "accept": ["asrt ( vidi exp ( pamo name maria ) thm ( piko def ) ) ."]}
-->

<!--ex
{"id": "03-books", "type": "match", "prompt": "Write Nex: I see the books.", "hint": "mabo pl def", "accept": ["asrt ( vidi exp spk thm ( mabo pl def ) ) .", "asrt ( vidi exp spk thm ( mabo def pl ) ) ."]}
-->

<!--ex
{"id": "03-kind", "type": "choice", "prompt": "Which frame is “a child”?", "choices": ["( pabo ind )", "( pamo child )", "( pabo name child )"], "answer": 0}
-->

# 4. Who does what to whom

Events with a doer use `agt` (agent), not `exp`. Giving is `doni`. It has
three core roles:

| role | meaning |
| --- | --- |
| `agt` | who gives |
| `thm` | what is given |
| `rec` | who receives |

```
asrt ( doni agt ( pamo name maria ) thm ( mabo def ) rec ( pamo name john ) ) .
```

*Maria gives John the book.*

You may write the roles in any order. Nex will canonicalize them. This is
on purpose: a model should not have to learn that `agt` before `thm` is a
different language from `thm` before `agt`. The role atom *is* the meaning.

A short map of the roles you will live in:

| role | ask | typical |
| --- | --- | --- |
| `agt` | who did it? | do, give, go |
| `exp` | who felt/saw it? | see, know, want, like |
| `thm` | what is it about? | almost everything |
| `rec` | to whom? | give, say, send |
| `cnt` | what was said/thought? | say, think |
| `loc` | where? | be-at, sit |
| `gol` | to where? | go, come |
| `src` | from where? | leave, take |
| `tmp` | when? | any event |
| `cau` | why? | any event |
| `ins` | with what tool? | see, cut, hit |
| `prp` | in order to? | ready, go |
| `mod` | what is it like? | any kind |
| `rel` | which one, that…? | any kind |
| `name` | what is it called? | people, places |

Other useful events:

| Nex | English | usual roles |
| --- | --- | --- |
| `deki` | do | agt thm |
| `saki` | say | agt cnt rec |
| `veli` | go | agt gol |
| `pusi` | eat | agt thm |
| `havi` | have | agt thm |
| `duli` | help | agt thm |

```
asrt ( pusi agt ( piko def ) thm ( pifo ind ) ) .
```

*The cat eats a fish.* (`pifo` = fish)

```
asrt ( saki agt spk rec hrd cnt ( hapa thm spk ) ) .
```

*I tell you that I am happy.* Saying takes `cnt` (content), a whole frame.

<details>
<summary>Answers</summary>

Maria gives you a book:

```
asrt ( doni agt ( pamo name maria ) thm ( mabo ind ) rec hrd ) .
```

The dog eats the fish:

```
asrt ( pusi agt ( pugo def ) thm ( pifo def ) ) .
```

</details>

<!--ex
{"id": "04-give", "type": "match", "prompt": "Write Nex: Maria gives John the book.", "hint": "doni agt rec thm. Book is mabo def.", "accept": ["asrt ( doni agt ( pamo name maria ) thm ( mabo def ) rec ( pamo name john ) ) ."]}
-->

<!--ex
{"id": "04-eat", "type": "match", "prompt": "Write Nex: The cat eats a fish.", "hint": "pusi agt ( piko def ) thm ( pifo ind )", "accept": ["asrt ( pusi agt ( piko def ) thm ( pifo ind ) ) ."]}
-->

<!--ex
{"id": "04-role", "type": "choice", "prompt": "In doni, the gift itself sits in which role?", "choices": ["agt", "thm", "rec"], "answer": 1}
-->

# 5. Time, not, and still happening

English hides time inside the verb: *give, gave, given, giving*. Nex never
changes the root. It adds **features**, atoms that sit on the head.

| feature | meaning |
| --- | --- |
| `past` | before now |
| `now` | at now (optional) |
| `fut` | after now |
| `done` | complete |
| `ong` | ongoing, -ing |
| `hab` | habitual |
| `not` | negation |
| `may` | possible |
| `must` | necessary |

```
asrt ( doni past agt ( pamo name maria ) thm ( mabo def ) rec ( pamo name john ) ) .
```

*Maria gave John the book.*

```
asrt ( doni past done agt spk thm ( mabo def ) rec hrd ) .
```

*I have given you the book.* (`past` + `done` ≈ perfect)

```
asrt ( pusi ong agt ( piko def ) thm ( pifo def ) ) .
```

*The cat is eating the fish.*

```
asrt ( vidi not exp spk thm ( pugo def ) ) .
```

*I do not see the dog.* `not` is a feature of the event, not a verb.

```
asrt ( veli fut agt spk gol ( meso def ) ) .
```

*I will go to the house.* Going takes `gol` (goal), the place aimed at.

There are no irregular verbs. There will never be irregular verbs. If you
can say it now, you can say it in the past by writing `past`.

<details>
<summary>Answers</summary>

I did not see the cat:

```
asrt ( vidi past not exp spk thm ( piko def ) ) .
```

You will go to the house:

```
asrt ( veli fut agt hrd gol ( meso def ) ) .
```

</details>

<!--ex
{"id": "05-gave", "type": "match", "prompt": "Write Nex: Maria gave John the book.", "hint": "Same as chapter 4, plus past.", "accept": ["asrt ( doni past agt ( pamo name maria ) thm ( mabo def ) rec ( pamo name john ) ) ."]}
-->

<!--ex
{"id": "05-not-see", "type": "match", "prompt": "Write Nex: I do not see the dog.", "hint": "not is a feature of vidi.", "accept": ["asrt ( vidi not exp spk thm ( pugo def ) ) ."]}
-->

<!--ex
{"id": "05-going", "type": "match", "prompt": "Write Nex: The child is going to the house.", "hint": "veli ong. Child is pabo. Goal is gol.", "accept": ["asrt ( veli ong agt ( pabo def ) gol ( meso def ) ) ."]}
-->

<!--ex
{"id": "05-feat", "type": "choice", "prompt": "How do you say the English perfect (have given)?", "choices": ["a different verb root", "past + done on the same root", "the feature have"], "answer": 1}
-->

# 6. What something is like

A quality ends in **-a**. It does not glue onto a noun. It sits in a `mod`
slot — a modifier frame.

| Nex | English |
| --- | --- |
| `ruga` | red |
| `blua` | blue |
| `biga` | big |
| `soma` | small |
| `guda` | good |
| `bada` | bad |
| `hapa` | happy |
| `fasta` | fast |
| `nova` | new |
| `olda` | old |

```
asrt ( vidi exp spk thm ( mabo def mod ( ruga ) ) ) .
```

*I see the red book.*

More than one modifier: more than one `mod`.

```
( pugo def mod ( biga ) mod ( ruga ) )
```

*the big red dog*

Degree is a feature of the quality, not a new word:

```
( biga very )
( hapa more )
( fasta most )
```

*very big, happier, fastest.*

When the sentence *is about* the quality — “the book is red” — the quality
is the head, and the thing is `thm`:

```
asrt ( ruga thm ( mabo def ) ) .
```

*The book is red.* There is no verb *to be* for this. English *is* is doing
nothing Nex needs.

```
asrt ( hapa thm spk ) .
```

*I am happy.*

Nominalizing a quality — talking about *happiness* as a thing — wraps it in
`koso` (a state). Nested frames are modifiers, so you can drop the word `mod`:

```
( koso ( hapa ) )              happiness
( koso ( hapa not ) )          unhappiness
```

That is why Nex does not have a word *unhappiness*. It would be a crime
against the tokenizer.

<details>
<summary>Answers</summary>

I see a small cat:

```
asrt ( vidi exp spk thm ( piko ind mod ( soma ) ) ) .
```

The book is good:

```
asrt ( guda thm ( mabo def ) ) .
```

</details>

<!--ex
{"id": "06-red-book", "type": "match", "prompt": "Write Nex: I see the red book.", "hint": "mod ( ruga ) inside the book frame.", "accept": ["asrt ( vidi exp spk thm ( mabo def mod ( ruga ) ) ) ."]}
-->

<!--ex
{"id": "06-is-red", "type": "match", "prompt": "Write Nex: The book is red.", "hint": "Quality as head, thing as thm. No copula.", "accept": ["asrt ( ruga thm ( mabo def ) ) ."]}
-->

<!--ex
{"id": "06-unhappy", "type": "match", "prompt": "Write the Nex kind for “unhappiness” (not a whole sentence).", "hint": "koso wraps ( hapa not ). Include the outer parentheses.", "accept": ["( koso ( hapa not ) )", "( koso mod ( hapa not ) )"]}
-->

<!--ex
{"id": "06-mod", "type": "choice", "prompt": "“the big red dog” is which frame?", "choices": ["( pugo def biga ruga )", "( pugo def mod ( biga ) mod ( ruga ) )", "( ruga ( biga ( pugo def ) ) )"], "answer": 1}
-->

# 7. Never say she

English pronouns are scavenger hunts: *she* might be Maria, or the child,
or someone in the next room. Nex **binds** a frame to an index the first
time you mention it, and then uses the index.

```
( pamo name maria = $1 )
```

The `= $1` is a binding. Later, `$1` *is* Maria. Not “probably Maria.”

```
asrt ( doni past
  agt ( pamo name maria = $1 )
  thm ( mabo def )
  rec ( pamo name john = $2 )
) .
asrt ( fali exp $1 thm $2 ) .
```

*Maria gave John the book. She likes him.*

`$1` and `$2` are not gendered. They do not care who was last mentioned.
They are equal to the frame that bound them.

`slf` is the special atom for *oneself*, when the same participant is in
two roles of one frame:

```
asrt ( vidi exp $1 thm slf ) .
```

*She sees herself.* (whoever `$1` is)

Use a new number for each new referent. `$1` through `$32` are single
tokens. Do not reuse a number for a different person.

A full mini-story:

```
asrt ( vini past agt ( pamo name maria = $1 ) gol ( meso def ) ) .
asrt ( vidi past exp $1 thm ( piko def = $2 ) ) .
asrt ( fali exp $1 thm $2 ) .
```

*Maria came to the house. She saw the cat. She likes it.*

<details>
<summary>Answers</summary>

John sees Maria. He likes her.

```
asrt ( vidi exp ( pamo name john = $1 ) thm ( pamo name maria = $2 ) ) .
asrt ( fali exp $1 thm $2 ) .
```

</details>

<!--ex
{"id": "07-bind-read", "type": "choice", "prompt": "asrt ( fali exp $1 thm $2 ) .  — if $1 was bound to Maria and $2 to the cat, this means:", "choices": ["Maria likes the cat.", "The cat likes Maria.", "Someone likes someone."], "answer": 0}
-->

<!--ex
{"id": "07-bind-write", "type": "match", "prompt": "Write one sentence: Maria sees John. Bind Maria as $1 and John as $2.", "hint": "vidi exp ( pamo name maria = $1 ) thm ( pamo name john = $2 )", "accept": ["asrt ( vidi exp ( pamo name maria = $1 ) thm ( pamo name john = $2 ) ) ."]}
-->

<!--ex
{"id": "07-like", "type": "match", "prompt": "Now write: She likes him.  (Use the same $1 and $2, no names.)", "hint": "fali exp $1 thm $2", "accept": ["asrt ( fali exp $1 thm $2 ) ."]}
-->

# 8. Asking and telling

Change the illocution. The frame stays.

**Yes/no question** — same frame, `ask` instead of `asrt`:

```
ask ( vidi exp hrd thm ( pugo def ) ) .
```

*Do you see the dog?*

**Who / what** — bind the unknown as a kind, and ask:

```
ask ( vidi exp ( pamo = $1 ) thm ( pugo def ) ) .
```

*Who sees the dog?*  (`pamo` with a binding and no name)

```
ask ( vidi exp hrd thm ( moto = $1 ) ) .
```

*What do you see?*  (`moto` = thing)

**Command** — `cmd`. The hearer is usually the agent, and you may omit
`agt hrd` only if you like being explicit; this primer keeps the agent in.

```
cmd ( veli agt hrd gol ( meso def ) ) .
```

*Go to the house.*

```
cmd ( doni agt hrd thm ( mabo def ) rec spk ) .
```

*Give me the book.*

**Wish:**

```
opt ( hapa thm hrd ) .
```

*May you be happy.*

<details>
<summary>Answers</summary>

Do you see the cat?

```
ask ( vidi exp hrd thm ( piko def ) ) .
```

Give John the book. (command to the hearer)

```
cmd ( doni agt hrd thm ( mabo def ) rec ( pamo name john ) ) .
```

</details>

<!--ex
{"id": "08-ask", "type": "match", "prompt": "Write Nex: Do you see the dog?", "hint": "ask, not asrt.", "accept": ["ask ( vidi exp hrd thm ( pugo def ) ) ."]}
-->

<!--ex
{"id": "08-cmd", "type": "match", "prompt": "Write Nex as a command: Go to the house.", "hint": "cmd ( veli agt hrd gol ( meso def ) )", "accept": ["cmd ( veli agt hrd gol ( meso def ) ) ."]}
-->

<!--ex
{"id": "08-who", "type": "choice", "prompt": "ask ( pusi agt ( pamo = $1 ) thm ( pifo def ) ) .", "choices": ["Does someone eat the fish?", "Who eats the fish?", "Eat the fish."], "answer": 1}
-->

# 9. Where, when, why

These are ordinary roles on the same event. You do not start a new sentence
for “yesterday” or “because.”

**Place.** `holi` is *be-at*. `loc` is the place. `here` and `there` are
ready-made deictics.

```
asrt ( holi thm ( piko def ) loc here ) .
```

*The cat is here.*

```
asrt ( veli past agt $1 gol ( meso def ) src here ) .
```

*She went to the house from here.*

**Time.** `tmp` takes a time frame. “Yesterday” is *one day before now*:

```
( before nowt ( qnt ( dieno ) 1 ) )
```

`nowt` is the deictic *now*. `dieno` is *day*. `qnt` is the quantity
operator. So:

```
asrt ( vidi past
  exp spk
  thm ( pugo def )
  tmp ( before nowt ( qnt ( dieno ) 1 ) )
) .
```

*I saw the dog yesterday.*

Tomorrow is `after` instead of `before`.

**Cause.** `cau` takes a whole event:

```
asrt ( fali exp $1 thm $2 cau ( duli past agt $2 thm $1 ) ) .
```

*She likes him because he helped her.*

**Purpose.** `prp` is *in order to*:

```
asrt ( veli agt spk gol ( meso def ) prp ( seni agt spk thm ( mabo def ) ) ) .
```

*I go to the house in order to read the book.* (`seni` = read)

**Instrument.** `ins` — and this is how you refuse the English telescope
trick. *I saw the man with the telescope* must pick a meaning:

Instrument:

```
asrt ( vidi past exp spk thm ( pamo def ) ins ( teso def ) ) .
```

The man who has a telescope:

```
asrt ( vidi past exp spk thm ( pamo def = $1 rel ( havi agt $1 thm ( teso def ) ) ) ) .
```

`rel` is a relative clause hanging on the kind. You cannot write the English
sentence in Nex without choosing.

<details>
<summary>Answers</summary>

The dog is at the house:

```
asrt ( holi thm ( pugo def ) loc ( meso def ) ) .
```

I will go tomorrow:

```
asrt ( veli fut agt spk tmp ( after nowt ( qnt ( dieno ) 1 ) ) ) .
```

</details>

<!--ex
{"id": "09-here", "type": "match", "prompt": "Write Nex: The cat is here.", "hint": "holi thm loc here", "accept": ["asrt ( holi thm ( piko def ) loc here ) ."]}
-->

<!--ex
{"id": "09-yest", "type": "match", "prompt": "Write Nex: I saw the dog yesterday.", "hint": "tmp ( before nowt ( qnt ( dieno ) 1 ) )", "accept": ["asrt ( vidi past exp spk thm ( pugo def ) tmp ( before nowt ( qnt ( dieno ) 1 ) ) ) ."]}
-->

<!--ex
{"id": "09-scope", "type": "choice", "prompt": "“I saw the man with the telescope” as an instrument uses which role?", "choices": ["rel", "ins", "mod"], "answer": 1}
-->

# 10. And, or, if, then

Some heads are **operators**. They take bare frames as children, not
role-tagged ones. You can recognise many of them because they are short
closed-class atoms: `and`, `or`, `if`, `seq`.

```
asrt ( and
  ( hapa thm spk )
  ( guda thm ( mabo def ) )
) .
```

*I am happy and the book is good.*

```
asrt ( or
  ( veli fut agt spk gol ( meso def ) )
  ( voci fut agt spk loc here )
) .
```

*I will go to the house or I will stay here.* (`voci` = stay)

**If:** first child is the condition, second is the consequence.

```
asrt ( if
  ( vidi exp hrd thm ( pugo def ) )
  ( saki agt hrd rec spk cnt ( hapa thm hrd ) )
) .
```

*If you see the dog, tell me that you are happy.*

**Sequence** of events, in order:

```
asrt ( seq
  ( vini past agt $1 )
  ( vidi past exp $1 thm $2 )
  ( fali exp $1 thm $2 )
) .
```

*She came, she saw, she liked.*

Do not use English *and* between two events if you mean order. Use `seq`.
`and` does not promise time.

<details>
<summary>Answers</summary>

The cat is big and red — two qualities as heads, or two mods. Either:

```
asrt ( and ( biga thm ( piko def ) ) ( ruga thm ( piko def ) ) ) .
```

or, as modifiers:

```
asrt ( holi thm ( piko def mod ( biga ) mod ( ruga ) ) loc here ) .
```

</details>

<!--ex
{"id": "10-and", "type": "match", "prompt": "Write Nex: I am happy and you are happy.", "hint": "and ( hapa thm spk ) ( hapa thm hrd )", "accept": ["asrt ( and ( hapa thm spk ) ( hapa thm hrd ) ) ."]}
-->

<!--ex
{"id": "10-if", "type": "match", "prompt": "Write Nex: If you see the dog, I am happy.", "hint": "if ( vidi … ) ( hapa thm spk )", "accept": ["asrt ( if ( vidi exp hrd thm ( pugo def ) ) ( hapa thm spk ) ) ."]}
-->

<!--ex
{"id": "10-seq", "type": "choice", "prompt": "Use seq rather than and when…", "choices": ["you mean both are true, order irrelevant", "you mean events in a fixed order", "you are quoting English"], "answer": 1}
-->

# 11. All, some, none

Quantifiers are operators too. They take a bound variable-frame and then
a claim.

**Someone sees a dog:**

```
asrt ( some ( pamo = $1 ) ( vidi exp $1 thm ( pugo ind ) ) ) .
```

**Everyone is mortal** — we do not have *mortal*, so *everyone dies* as a
habit, or everyone is a person (too trivial). Use *everyone is happy*:

```
asrt ( all ( pamo = $1 ) ( hapa thm $1 ) ) .
```

**Nobody sees the dog:**

```
asrt ( none ( pamo = $1 ) ( vidi exp $1 thm ( pugo def ) ) ) .
```

Scope is **which operator wraps which**. English *nobody saw every dog*
is two Nex sentences:

There is no person who saw every dog:

```
asrt ( none ( pamo = $1 )
  ( all ( pugo = $2 ) ( vidi past exp $1 thm $2 ) )
) .
```

For every dog, nobody saw it:

```
asrt ( all ( pugo = $2 )
  ( none ( pamo = $1 ) ( vidi past exp $1 thm $2 ) )
) .
```

Those are different worlds. Nex will not let you write one string for both.

`exist` is “there is.” `one` is “exactly one.”

```
asrt ( exist ( piko = $1 ) ( holi thm $1 loc here ) ) .
```

*There is a cat here.*

<details>
<summary>Answers</summary>

Everyone sees the sun (`suno`):

```
asrt ( all ( pamo = $1 ) ( vidi exp $1 thm ( suno def ) ) ) .
```

</details>

<!--ex
{"id": "11-all", "type": "match", "prompt": "Write Nex: Everyone is happy.", "hint": "all ( pamo = $1 ) ( hapa thm $1 )", "accept": ["asrt ( all ( pamo = $1 ) ( hapa thm $1 ) ) ."]}
-->

<!--ex
{"id": "11-none", "type": "match", "prompt": "Write Nex: Nobody sees the dog.", "hint": "none ( pamo = $1 ) ( vidi exp $1 thm ( pugo def ) )", "accept": ["asrt ( none ( pamo = $1 ) ( vidi exp $1 thm ( pugo def ) ) ) ."]}
-->

<!--ex
{"id": "11-scope", "type": "choice", "prompt": "In Nex, quantifier scope is…", "choices": ["inferred from context", "which operator wraps which tree", "marked with gender"], "answer": 1}
-->

# 12. Growing words instead of minting them

A closed kernel is useless if you cannot say new things. Nex grows by
**wrapping**, not by inventing stems. Wrapping has a length cost, so there
are three rungs. Climb only as high as you need.

**Rung 1 — a feature or a derivational operator.** Two or three atoms.

| English | Nex | tokens |
| --- | --- | --- |
| faster | `( fasta more )` | 4 |
| not red | `( ruga not )` | 4 |
| happiness | `( koso ( hapa ) )` | 5 |
| unhappiness | `( koso ( hapa not ) )` | 6 |
| a reader | `( agto seni )` | 4 |
| a reader | `senu` | 1 |
| what is read | `( thmo seni )` | 4 |
| a place for reading | `( plao seni )` | 4 |

`agto` is English *-er*: the person who does the event. `thmo` is the
undergoer, `inso` the tool, `plao` the place. They are operators, so the
event can sit as a bare atom: `( agto seni )`, not a relative clause.

When you want one token, **pack** by changing the type vowel, not by
stealing another word’s shape:

| type | ending | example |
| --- | --- | --- |
| event | `-i` | `seni` read, `koli` remember |
| primitive kind | `-o` | `mabo` book, `tino` color |
| quality | `-a` | `ruga` red, `kola` cold |
| derived doer | `-u` | `senu` reader, `kolu` rememberer |

`seni` → `senu`, always. `koli` → `kolu`, always. There is no “unless that
slot is taken.” Derived nouns live in `-u`, primitive kinds live in `-o`,
so they cannot collide. If a future root would break that, the lexicon is
wrong — you rename the root, you do not add an exception.

**Rung 2 — an extra slot on the derived kind.** Still short.

```
( agto seni thm ( mabo ) )     a reader of books
( senu thm ( mabo ) )          the same, packed
```

**Rung 3 — a relative clause.** Use this when you need a full extra event,
not when you mean *-er*. This is legal, and too long for “reader”:

```
( pamo rel ( seni hab agt slf thm ( mabo ) ) )
```

That is “a person who habitually reads books,” which is a *definition*,
not a word. Definitions are allowed. They should not be your default.

`can` is an operator wrapping an event:

```
asrt ( can ( veli agt spk gol ( meso def ) ) ) .
```

*I can go to the house.*

`must` and `may` can also sit as features on the event itself:

```
asrt ( veli must agt spk gol ( meso def ) ) .
```

*I must go to the house.*

When you need a word you do not have, do this in order:

1. Is it a feature? (`not`, `more`, `pl`, `past`…)
2. Is it a derivation? (`agto`, `thmo`, `koso`, packed `senu`…)
3. Is it a role on that derived kind? (`thm`, `loc`…)
4. Only then a `rel` clause — a definition, not a lexeme.
5. Only then mint a root, with the right ending.

This is the same discipline you want in a model: compose, then pack.
Do not pay fourteen tokens for *-er*.

<!--ex
{"id": "12-can", "type": "match", "prompt": "Write Nex: I can eat the fish.", "hint": "can wraps pusi.", "accept": ["asrt ( can ( pusi agt spk thm ( pifo def ) ) ) ."]}
-->

<!--ex
{"id": "12-koso", "type": "choice", "prompt": "The Nex for “goodness” is…", "choices": ["guda-ness", "( koso ( guda ) )", "( guda koso )"], "answer": 1}
-->

<!--ex
{"id": "12-must", "type": "match", "prompt": "Write Nex: You must go to the house.", "hint": "veli must, or must as feature.", "accept": ["asrt ( veli must agt hrd gol ( meso def ) ) ."]}
-->

<!--ex
{"id": "12-reader", "type": "match", "prompt": "Write Nex for “a reader” (the person, not a sentence). Prefer the short form.", "hint": "Packed kind senu, or ( agto seni ).", "accept": ["( senu )", "( senu ind )", "( agto seni )", "( agto seni ind )"]}
-->

<!--ex
{"id": "12-long", "type": "choice", "prompt": "The relative clause ( pamo rel ( seni hab agt slf thm ( mabo ) ) ) is…", "choices": ["the normal word for “reader”", "a definition of a person who reads books, too long as a lexeme", "ungrammatical"], "answer": 1}
-->

# 13. A first reader

Read these out loud. Then hide the gloss and read them again.

### A greeting

```
asrt ( saki agt spk rec hrd cnt ( hapa thm spk ) ) .
ask ( hapa thm hrd ) .
```

I tell you I am happy. Are you happy?

### A gift

```
asrt ( doni past done
  agt ( pamo name maria = $1 )
  thm ( mabo def mod ( ruga ) = $2 )
  rec ( pamo name john = $3 )
  cau ( fali past exp $1 thm $3 )
) .
asrt ( seni ong agt $3 thm $2 ) .
```

Maria has given John the red book because she liked him. He is reading it.

### The house and the cat

```
asrt ( seq
  ( vini past agt ( pamo name john = $1 ) gol ( meso def ) )
  ( vidi past exp $1 thm ( piko def mod ( soma ) = $2 ) )
  ( holi thm $2 loc ( meso def ) )
  ( fali not exp $1 thm $2 )
) .
```

John came to the house, saw the small cat, the cat is at the house, he does
not like it. Life is unfair. Nex is not.

### Two readings you can now write

Instrument:

```
asrt ( vidi past exp spk thm ( pamo def ) ins ( teso def ) ) .
```

Possessor:

```
asrt ( vidi past exp spk thm ( pamo def = $1 rel ( havi agt $1 thm ( teso def ) ) ) ) .
```

<!--ex
{"id": "13-greet", "type": "choice", "prompt": "ask ( hapa thm hrd ) .", "choices": ["You are happy.", "Are you happy?", "Be happy."], "answer": 1}
-->

<!--ex
{"id": "13-seq", "type": "choice", "prompt": "In the house-and-cat story, fali not exp $1 thm $2 means…", "choices": ["the cat does not like John", "John does not like the cat", "the house does not like the cat"], "answer": 1}
-->

<!--ex
{"id": "13-write", "type": "match", "prompt": "Write Nex: John is reading the book.", "hint": "seni ong. Bindings not required.", "accept": ["asrt ( seni ong agt ( pamo name john ) thm ( mabo def ) ) ."]}
-->

# 14. Phrasebook

Keep this page. It is a kernel you can actually talk with.

**Deixis**

| Nex | English |
| --- | --- |
| `spk` | I / me / we |
| `hrd` | you |
| `slf` | oneself |
| `here` `there` | here, there |
| `nowt` | now |
| `this` `that` | this, that |
| `unk` | unspecified someone/something |

**Illocutions** — `asrt ask cmd opt exch`

**The twelve events worth memorising first**

| Nex | English |
| --- | --- |
| `vidi` | see |
| `saki` | say |
| `doni` | give |
| `veli` | go |
| `vini` | come |
| `pusi` | eat |
| `havi` | have |
| `kuni` | know |
| `kawi` | want |
| `fali` | like |
| `seni` | read |
| `holi` | be-at |

**The twelve kinds**

`pamo` person · `pabo` child · `pugo` dog · `piko` cat · `pifo` fish ·
`mabo` book · `meso` house · `loko` place · `dieno` day · `suno` sun ·
`moto` thing · `nexo` Nex

**The twelve qualities**

`guda` good · `bada` bad · `hapa` happy · `ruga` red · `blua` blue ·
`biga` big · `soma` small · `fasta` fast · `nova` new · `olda` old ·
`trua` true · `fala` false

**Features** — `not past now fut done ong hab may must def ind pl very more most`

**Operators** — `and or if seq all some none exist one can qnt before after`

**Skeleton**

```
ILLOC ( HEAD features = $N   ROLE ARG   ROLE ARG ) .
```

**Yesterday / tomorrow**

```
( before nowt ( qnt ( dieno ) 1 ) )
( after  nowt ( qnt ( dieno ) 1 ) )
```

<!--ex
{"id": "14-want", "type": "match", "prompt": "Write Nex: I want the book.", "hint": "kawi exp (want is felt, so exp).", "accept": ["asrt ( kawi exp spk thm ( mabo def ) ) ."]}
-->

<!--ex
{"id": "14-know", "type": "match", "prompt": "Write Nex: You know Maria.", "hint": "kuni exp hrd thm ( pamo name maria )", "accept": ["asrt ( kuni exp hrd thm ( pamo name maria ) ) ."]}
-->

# 15. How to keep going

You now have the whole grammar. The lexicon is small on purpose; the
[lexicon in the playground](/#lexicon) is the rest of the kernel. A few
habits separate people who can read Nex from people who can write it:

1. **Name the role before you name the argument.** If you cannot pick
   `agt` vs `exp` vs `thm`, you do not yet know the sentence.
2. **Bind on first mention.** If you hear yourself about to write *she*,
   you missed a `$n`.
3. **Features, not new roots.** Past, plural, not, very, more.
4. **One tree per meaning.** If English would wink at two readings, write
   two Nex sentences or refuse.
5. **Parse what you write.** The studio at `/` will tell you if the string
   is even a string. Pride is not a parser.

A last drill, as a farewell.

```
asrt ( kawi exp spk thm ( kuni exp hrd thm ( nexo ) ) ) .
```

I want that you know Nex.

<!--ex
{"id": "15-farewell", "type": "choice", "prompt": "asrt ( kawi exp spk thm ( kuni exp hrd thm ( nexo ) ) ) .", "choices": ["I know that you want Nex.", "I want you to know Nex.", "You want me to know Nex."], "answer": 1}
-->

<!--ex
{"id": "15-final", "type": "match", "prompt": "Write Nex: I know Nex.", "hint": "kuni exp spk thm ( nexo )", "accept": ["asrt ( kuni exp spk thm ( nexo ) ) ."]}
-->
