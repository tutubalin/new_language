# Nex — specification for machine translation

Nex is a constructed language. One string ↔ one parse tree. Translate meaning, not English wording. If English is ambiguous, pick one reading and encode it; never emit an ambiguous Nex string.

Do not invent roots. If a concept is missing, compose (features, `agto`/`koso`/`rel`). Unknown proper names stay as `name` atoms, lowercase.

## 1. Orthography

- Lowercase ASCII `[a-z][a-z0-9]*`. No capitals, no apostrophes.
- Tokens: atoms, `$N` (N≥1), decimal integers, `( ) = .`
- Whitespace-separated. `.` ends a statement.
- Type vowels (open class only): event `-i`, primitive kind `-o`, quality `-a`, derived doer `-u`. Closed class has no type vowel.
- Primitive open-class stems are unique. Shared stem ⇒ derivation (`seni`/`senu`, `reda`/`redi`), never coincidence.

## 2. Grammar

```
program     := statement+
statement   := illocution frame "."
illocution  := asrt | ask | cmd | opt | exch     # default asrt if omitted
frame       := "(" head feature* binding? item* ")"
head        := ATOM
feature     := not|past|now|fut|done|ong|hab|may|must
             | seen|heard|said|inf|def|ind|mass|sg|pl|very|more|most
binding     := "=" $N
item        := ROLE arg                          # non-operator heads
             | arg                               # operator heads only
             | frame                             # sugar ⇒ role mod
arg         := frame | $N | ATOM | NUMBER
ROLE        := agt|exp|rec|thm|cnt|ins|mnr|src|path|gol|loc|tmp|cau|prp|ben|pos|rel|mod|name|unit
```

- Unique parse (PEG). Role order is free; canonicalize on output (see §8).
- Operators take bare args (frames/atoms/numbers), optionally role-tagged except `name`.
- Nested frame without a role ⇒ `mod` (sugar). Prefer explicit `mod` in output.
- Open-class atoms appear only as heads (or as `name`/`spell` material). Closed-class atoms are the lists above plus deictics and operators.

## 3. Illocutions

| atom | force |
| asrt | statement |
| ask | question |
| cmd | command |
| opt | wish |
| exch | exclamation |

## 4. Roles

| atom | meaning | typical |
| agt | doer/causer | give, go, eat |
| exp | feeler/perceiver | see, know, want, like |
| rec | recipient | give, say, send |
| thm | theme/patient/about | almost all |
| cnt | content said/thought | say, think |
| ins | instrument | see-with, cut |
| mnr | manner | |
| src | source/from | leave, take |
| path | path/through | move |
| gol | goal/to-place | go, come |
| loc | location/at | be-at, sit |
| tmp | when | |
| cau | because | |
| prp | in order to | ready, go |
| ben | for-whom | |
| pos | possessor | |
| rel | relative clause | on a kind |
| mod | modifier | quality on a kind |
| name | proper name | on pamo/loko |
| unit | unit of measure | |

Omit unused roles. Do not infer roles from word order when reading Nex.

## 5. Features (on the head they modify)

Polarity: `not`
Tense: `past` `now` `fut`  — `now` = present tense, not the deictic *now* (`nowt`)
Aspect: `done` complete/perfect · `ong` ongoing · `hab` habitual
Mood: `may` possible · `must` necessary
Evidential: `seen` `heard` `said` `inf`
Det: `def` the · `ind` a/some · `mass`
Number: `sg` `pl`  — omit sg unless contrast required
Degree (on qualities): `very` `more` `most`

No irregular verbs. `go/went/gone/going` = `veli` / `veli past` / `veli past done` / `veli ong`.

No copula for qualities: “the book is red” = `( ruga thm ( mabo def ) )`. Location uses `holi`. Identity uses operator `same`.

## 6. Deictics (args, not heads)

`spk` I/me/we · `hrd` you · `slf` oneself · `this` `that` · `here` `there` · `nowt` now · `unk` unspecified someone/something

English dummy *it* (*it is raining*, *what time is it*) is dropped, not `unk`.

## 7. Operators (heads)

Logic: `and` `or` `if` `then` `seq` `cause` `can` `same` `sim`
Quant: `all` `some` `exist` `none` `one` `mostq` `qnt` `num`
Time: `before` `after` `dur`
Struct: `spell`
Derive: `agto` doer-of · `thmo` undergoer-of · `inso` tool-of · `plao` place-of

`if` args: condition, then consequence [, else].
`seq` args: events in order. `and` does not imply order.
`all`/`some`/`none`/`exist`/`one`/`mostq`: `( all ( KIND = $N ) ( CLAIM... ) )`.
Scope = wrapping. Different wrap ⇒ different meaning.
`qnt`: `( qnt ( UNIT ) NUMBER )`.
`num`: digits as separate args, MSD first: `( num 1 2 3 )` = 123. Bare integers allowed as args and mean the same.
`before`/`after`: `( before nowt ( qnt ( dieno ) 1 ) )` = yesterday; `after` = tomorrow.
`can`: wraps an event. `must`/`may` may instead be features on the event.
`agto`: `( agto EVENT )` or packed kind in `-u` (§10). Extra roles allowed: `( agto seni thm ( mabo ) )`.

## 8. Canonical output (when writing Nex)

1. Features in this order: not must may past now fut done ong hab seen heard said inf def ind mass sg pl very more most
2. Binding immediately after features: `= $N`
3. Roles in this order: agt exp rec thm cnt ins mnr src path gol loc tmp cau prp ben pos name unit rel mod
4. One space between tokens. Pretty-print nested frames if helpful; parse ignores layout.
5. Prefer packed `-u` kinds over `( agto EVT )` when the pack exists.
6. Prefer explicit `mod` over nested-frame sugar.
7. First mention binds `= $N`; later mentions are `$N` only. Number from `$1` up; do not reuse a number for a new referent. No gendered pronouns.

## 9. Names, OOV, numbers

- Person name: `( pamo name maria = $1 )` — name atom lowercase, no capitals.
- Unknown name still one atom after `name` if `[a-z]+`. Else `( name ( spell m a r i a ) )`.
- Unknown common noun: `( moto name stem )` or compose; do not mint a type-vowel root.
- Numbers: integer args, or `( num 1 2 3 4 5 )`. Never a fused multi-digit token in the model stream; in text, `12345` as one number atom is accepted.

## 10. Derivation and packing

| want | write | pack |
| *-er* person who Vs | `( agto V )` | drop `-i`, add `-u`: `seni`→`senu` |
| undergoer | `( thmo V )` | (no pack) |
| tool-for | `( inso V )` | |
| place-for | `( plao V )` | |
| quality-as-thing | `( koso mod ( QUAL ) )` | |
| event-as-thing | `( evo mod ( EVT ) )` | |
| relative clause | `( KIND = $N rel ( ... $N ... ) )` | definition, not a lexeme |

`rel` only when you need a full extra event. “Reader” is `senu` / `( agto seni )`, not a relative clause.

Every kernel event has a packed doer (`doni`→`donu`, `koli`→`kolu`, …). If `-u` would clash, the lexicon is wrong — do not skip.

## 11. Closed-class complete lists

Illoc: asrt ask cmd opt exch
Roles: agt exp rec thm cnt ins mnr src path gol loc tmp cau prp ben pos rel mod name unit
Features: not past now fut done ong hab may must seen heard said inf def ind mass sg pl very more most
Ops: and or if then seq all some exist none one mostq can cause same sim qnt num spell before after dur agto thmo inso plao
Deix: spk hrd slf this that here there nowt unk
Struct: ( ) = .

## 12. Events (head `-i`) — gloss · default roles

doni give agt,thm,rec · daki take agt,thm,src · dami put agt,thm,gol · dofi make agt,thm · deki do agt,thm · dusi use agt,thm,ins · duri work agt,loc · doli play agt,thm · deni send agt,thm,rec · dovi open agt,thm · duci close agt,thm · dabi break agt,thm · daji join agt,thm · diki cut agt,thm,ins · dopi buy agt,thm,src · desi sell agt,thm,rec · dapi pay agt,thm,rec · duli help agt,thm · debi hit agt,thm,ins · dafi hold agt,thm · duxi find agt,thm · deti wait agt,thm · dayi try agt,thm · degi get agt,thm,src
voni move agt,path · veli go agt,gol,src · vini come agt,gol,src · vaki run agt,gol · visi sit agt,loc · vosi stand agt,loc · vupi carry agt,thm,gol · vali turn agt,gol · vefi fall thm,loc · voxi fly agt,gol · voyi swim agt,gol · voti walk agt,gol · vuli leave agt,src · vani arrive agt,gol · voci stay agt,loc
vidi see exp,thm,ins · suli hear exp,thm · nusi smell exp,thm · sati taste exp,thm · suci touch agt,thm · saki say agt,cnt,rec · suji ask(utter) agt,cnt,rec · sowi answer agt,cnt,rec · sari write agt,thm,rec · seni read agt,thm · sugi call agt,thm · soti shout agt,cnt · sini mean agt,cnt
kuni know exp,thm · keni think exp,cnt · kabi believe exp,cnt · koli remember exp,thm · kefi forget exp,thm · kedi learn agt,thm · kaci teach agt,thm,rec · kawi want exp,thm · nidi need exp,thm · kiri decide agt,cnt · kuxi understand exp,thm · kifi doubt exp,cnt · kopi hope exp,cnt
fili feel exp,thm · fali like/love exp,thm · fori fear exp,thm · fegi anger-at exp,thm · fosi sad-about exp,thm · feni pain/hurt exp,thm
pivi live agt,loc · podi die thm · pusi eat agt,thm · pibi drink agt,thm · posi sleep agt,loc · pawi wake agt · pefi breathe agt · paxi be-born thm
hazi happen thm,loc,tmp · heni become thm,mod · hosi start agt,thm · hofi end/stop agt,thm · havi have/own agt,thm · holi be-at thm,loc · haci cause agt,thm · huti change agt,thm · hexi exist thm,loc · redi be-ready thm,prp

Perceiver verbs use `exp` not `agt`. `suji` = speech-act ask; illocution `ask` is the sentence force.

## 13. Primitive kinds (`-o`)

pamo person · pino people · peko body · pabo child · palto adult · pexo animal · pugo dog · piko cat · pico bird · pifo fish · puko chicken · suno sun · wino wind
moto thing · miko tool · mabo book · melo food · mowo water · mafo fire · mazo air · mexo earth · meso house · mako machine · muko cloak/coat · teso telescope
wodo word · wixo idea · weso story · wako language · nexo Nex · namo name
loko place · lano land · livo city · laro room · lefo side · liso inside · laso outside
toko time · dieno day · noco night · yaro year · horo hour · mino minute
koso state (nominalizer) · evo event (nominalizer) · relo relation · sovo sound · luxo light · tino color · hato way · qeso question · toso tree · roso rock · paso path · mano hand · hedo head · eyo eye

## 14. Qualities (`-a`)

guda good · bada bad · hapa happy · sada sad · trua true · erza false
biga big · soma small · nova new · olda old · longa long · kuta short · higa high · lowa low · stroa strong · weka weak
ruga red · blua blue · grea green · wita white · blaka black · yela yellow
hota hot · niva cold · warma warm · fasta fast · slowa slow · hara hard/difficult · sofa soft/easy · fulla full · ema empty · opena open · klosa closed · tita tight · lusa loose
sama same · ota other · neara near · fara far · northa north
aliva alive · deda dead · reda ready · fria free · equa equal · multa many · fewa few · sura sure

Predicative: `( QUAL thm X )`. Attributive: `( KIND mod ( QUAL ) )`.

## 15. English → Nex

Resolve before writing:

1. Attachment (*with the telescope*): `ins` vs `rel ( havi ... )`. Never leave both.
2. *ready to eat*: purpose `prp ( pusi agt unk thm $1 )` vs `prp ( pusi agt $1 thm unk )`.
3. Quantifier scope: wrap explicitly (`none` over `all` ≠ `all` over `none`).
4. Pronouns: bind on first name/description; `he`/`she`/`they` become `$N` by referent, not gender.
5. Tense/aspect from morphology: -ed ⇒ `past` (and `done` if perfect); -ing ⇒ `ong`; will ⇒ `fut`; can ⇒ operator `can` or leave as ability event.
6. Articles: the⇒`def`, a/an⇒`ind`. Drop dummy *it*.
7. *yesterday* = `( before nowt ( qnt ( dieno ) 1 ) )`; *tomorrow* = `after`; *today* = `( dieno def )`; *now* = `nowt`.
8. *What time is it (now)?* = `ask ( toko = $1 tmp nowt ) .`
9. WH: bind an unbound kind (`pamo` who, `moto` what, `loko` where, `toko` when) as `$N` under `ask`.
10. Commands: `cmd`, agent usually `hrd`.
11. Missing root: compose; do not output English words as Nex heads.

## 16. Nex → English

- Gloss roles into a natural English sentence; do not say “agent=”.
- `$N` → the English NP last bound to that index (name or description). If unbound, “they/that”.
- Features → English morphology (*gave*, *the*, *not*, *will*).
- `agto`/`-u` → *-er* (*reader*). `koso` → *-ness*.
- One Nex tree → one English reading. Do not reintroduce the ambiguity you removed.

## 17. Examples

EN Maria gave John the red book yesterday because she liked him.
NX `asrt ( doni past done agt ( pamo name maria = $1 ) thm ( mabo def mod ( ruga ) ) rec ( pamo name john = $2 ) tmp ( before nowt ( qnt ( dieno ) 1 ) ) cau ( fali past exp $1 thm $2 ) ) .`

EN I saw the man with the telescope. [instrument]
NX `asrt ( vidi past exp spk thm ( pamo def ) ins ( teso def ) ) .`

EN I saw the man with the telescope. [possessor]
NX `asrt ( vidi past exp spk thm ( pamo def = $1 rel ( havi agt $1 thm ( teso def ) ) ) ) .`

EN The chicken is ready to eat. [to be eaten]
NX `asrt ( redi thm ( puko def = $1 ) prp ( pusi agt unk thm $1 ) ) .`

EN Nobody saw every dog. [no person saw all dogs]
NX `asrt ( none ( pamo = $1 ) ( all ( pugo = $2 ) ( vidi past exp $1 thm $2 ) ) ) .`

EN Unhappiness faded.
NX `asrt ( hofi past thm ( koso mod ( hapa not ) ) ) .`

EN a reader
NX `( senu )` or `( agto seni )`

EN What time is it now?
NX `ask ( toko = $1 tmp nowt ) .`

EN Go to the house.
NX `cmd ( veli agt hrd gol ( meso def ) ) .`

EN I want you to know Nex.
NX `asrt ( kawi exp spk thm ( kuni exp hrd thm ( nexo ) ) ) .`
