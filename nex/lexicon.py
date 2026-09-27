"""Nex lexicon.

Closed-class items are part of the grammar (roles, features, operators).
Open-class roots are events, kinds, and qualities. Form encodes type,
and the type vowels are disjoint on purpose — a derived noun cannot
land on a primitive kind:

    events              end in -i
    primitive kinds     end in -o
    qualities           end in -a
    derived agent kinds end in -u   (seni → senu, never seno)

First consonant loosely marks semantic field so similar meanings share
form — a featural hint for character-aware models and for embedding init.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Entry:
    form: str
    kind: str  # evt | kind | qual | role | feat | op | illoc | deictic | struct
    field: str
    gloss: str
    english: tuple[str, ...] = ()
    roles: tuple[str, ...] = ()  # expected roles, in canonical order
    notes: str = ""


def _e(
    form: str,
    kind: str,
    field: str,
    gloss: str,
    english: str = "",
    roles: str = "",
    notes: str = "",
) -> Entry:
    return Entry(
        form=form,
        kind=kind,
        field=field,
        gloss=gloss,
        english=tuple(w for w in english.split("/") if w),
        roles=tuple(r for r in roles.split() if r),
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Closed class — disjoint inventories, part of the grammar
# ---------------------------------------------------------------------------

ILLOCUTIONS: tuple[Entry, ...] = (
    _e("asrt", "illoc", "speech", "assert", "assert/say-that"),
    _e("ask", "illoc", "speech", "ask", "ask/question"),
    _e("cmd", "illoc", "speech", "command", "command/tell-to"),
    _e("opt", "illoc", "speech", "wish", "wish/hope-that"),
    _e("exch", "illoc", "speech", "exclaim", "exclaim"),
)

ROLES: tuple[Entry, ...] = (
    _e("agt", "role", "role", "agent", "agent/who-did", notes="doer, causer of event"),
    _e("exp", "role", "role", "experiencer", "experiencer", notes="feeler, perceiver"),
    _e("rec", "role", "role", "recipient", "recipient/to-whom"),
    _e("thm", "role", "role", "theme", "theme/patient/what", notes="affected or discussed"),
    _e("cnt", "role", "role", "content", "content/about"),
    _e("ins", "role", "role", "instrument", "instrument/with-what"),
    _e("mnr", "role", "role", "manner", "manner/how"),
    _e("src", "role", "role", "source", "source/from"),
    _e("path", "role", "role", "path", "path/through"),
    _e("gol", "role", "role", "goal", "goal/to-place"),
    _e("loc", "role", "role", "location", "location/at"),
    _e("tmp", "role", "role", "time", "time/when"),
    _e("cau", "role", "role", "cause", "cause/because"),
    _e("prp", "role", "role", "purpose", "purpose/in-order-to"),
    _e("ben", "role", "role", "beneficiary", "beneficiary/for-whom"),
    _e("pos", "role", "role", "possessor", "possessor/of"),
    _e("rel", "role", "role", "relative", "who/that/which", notes="relative clause"),
    _e("mod", "role", "role", "modifier", "modifier"),
    _e("name", "role", "role", "name", "named"),
    _e("unit", "role", "role", "unit", "unit"),
)

FEATURES: tuple[Entry, ...] = (
    _e("not", "feat", "polarity", "not", "not/n't/never/no"),
    _e("past", "feat", "tense", "past", "past/-ed"),
    _e("now", "feat", "tense", "present", "present/now"),
    _e("fut", "feat", "tense", "future", "will/shall/going-to"),
    _e("done", "feat", "aspect", "complete", "have/-en/already"),
    _e("ong", "feat", "aspect", "ongoing", "-ing/currently"),
    _e("hab", "feat", "aspect", "habitual", "usually/used-to"),
    _e("may", "feat", "mood", "possible", "may/might/maybe"),
    _e("must", "feat", "mood", "necessary", "must/have-to/should"),
    _e("seen", "feat", "evid", "witnessed", "I-saw"),
    _e("heard", "feat", "evid", "heard", "I-heard"),
    _e("said", "feat", "evid", "reported", "they-say"),
    _e("inf", "feat", "evid", "inferred", "must-be"),
    _e("def", "feat", "det", "definite", "the"),
    _e("ind", "feat", "det", "indefinite", "a/an/some"),
    _e("mass", "feat", "det", "mass", "some-mass"),
    _e("sg", "feat", "number", "singular", "singular"),
    _e("pl", "feat", "number", "plural", "plural/-s"),
    _e("very", "feat", "degree", "very", "very/really"),
    _e("more", "feat", "degree", "more", "more/-er"),
    _e("most", "feat", "degree", "most", "most/-est"),
)

OPERATORS: tuple[Entry, ...] = (
    _e("and", "op", "logic", "and", "and/both", notes="conjoin frames"),
    _e("or", "op", "logic", "or", "or/either"),
    _e("if", "op", "logic", "if", "if/when-if"),
    _e("then", "op", "logic", "then", "then/so"),
    _e("seq", "op", "logic", "sequence", "then/after-that"),
    _e("all", "op", "quant", "all", "all/every/each"),
    _e("some", "op", "quant", "some", "some/there-is"),
    _e("exist", "op", "quant", "exists", "exists/there-is"),
    _e("none", "op", "quant", "none", "no/none/nobody"),
    _e("one", "op", "quant", "exactly-one", "one/a-single"),
    _e("mostq", "op", "quant", "most-of", "most-of"),
    _e("can", "op", "modal", "able", "can/able-to"),
    _e("cause", "op", "logic", "cause", "cause/make-happen"),
    _e("same", "op", "rel", "identical", "same-as/is"),
    _e("sim", "op", "rel", "similar", "similar/as-if"),
    _e("qnt", "op", "quant", "quantity", "quantity/amount"),
    _e("num", "op", "quant", "number", "number"),
    _e("spell", "op", "struct", "spell", "spelled"),
    _e("before", "op", "time", "before", "before/ago"),
    _e("after", "op", "time", "after", "after/later"),
    _e("dur", "op", "time", "duration", "for/lasting"),
    # derivational operators — English -er/-ee without a relative clause
    _e("agto", "op", "derive", "doer-of", "doer/-er", notes="( agto seni ) = reader"),
    _e("thmo", "op", "derive", "undergoer-of", "patient/-ee", notes="( thmo seni ) = what is read"),
    _e("inso", "op", "derive", "instrument-of", "tool-for", notes="( inso seni ) = reading-tool"),
    _e("plao", "op", "derive", "place-of", "place-for", notes="( plao seni ) = reading-place"),
)

DEICTICS: tuple[Entry, ...] = (
    _e("spk", "deictic", "deixis", "speaker", "I/me/my/we/us"),
    _e("hrd", "deictic", "deixis", "hearer", "you/your"),
    _e("slf", "deictic", "deixis", "reflexive", "self/himself/herself"),
    _e("this", "deictic", "deixis", "this", "this/these"),
    _e("that", "deictic", "deixis", "that", "that/those"),
    _e("here", "deictic", "deixis", "here", "here"),
    _e("there", "deictic", "deixis", "there", "there"),
    _e("nowt", "deictic", "deixis", "now", "now"),
    _e("unk", "deictic", "deixis", "unspecified", "someone/something/unspecified"),
)

STRUCT: tuple[Entry, ...] = (
    _e("(", "struct", "struct", "open-frame"),
    _e(")", "struct", "struct", "close-frame"),
    _e(".", "struct", "struct", "end-statement"),
    _e("=", "struct", "struct", "bind"),
)

# ---------------------------------------------------------------------------
# Open class — events (-i)
# ---------------------------------------------------------------------------

EVENTS: tuple[Entry, ...] = (
    # transfer / doing  d-
    _e("doni", "evt", "transfer", "give", "give/gave/given/giving", "agt thm rec"),
    _e("daki", "evt", "transfer", "take", "take/took/taken/taking", "agt thm src"),
    _e("dami", "evt", "transfer", "put", "put/putting", "agt thm gol"),
    _e("dofi", "evt", "transfer", "make", "make/made/making/create/created", "agt thm"),
    _e("deki", "evt", "transfer", "do", "do/did/done/doing/act", "agt thm"),
    _e("dusi", "evt", "transfer", "use", "use/used/using", "agt thm ins"),
    _e("duri", "evt", "transfer", "work", "work/worked/working", "agt loc"),
    _e("doli", "evt", "transfer", "play", "play/played/playing", "agt thm"),
    _e("deni", "evt", "transfer", "send", "send/sent/sending", "agt thm rec"),
    _e("dovi", "evt", "transfer", "open", "open/opened/opening", "agt thm"),
    _e("duci", "evt", "transfer", "close", "close/closed/closing", "agt thm"),
    _e("dabi", "evt", "transfer", "break", "break/broke/broken/breaking", "agt thm"),
    _e("daji", "evt", "transfer", "join", "join/joined/joining/connect", "agt thm"),
    _e("diki", "evt", "transfer", "cut", "cut/cutting", "agt thm ins"),
    _e("dopi", "evt", "transfer", "buy", "buy/bought/buying", "agt thm src"),
    _e("desi", "evt", "transfer", "sell", "sell/sold/selling", "agt thm rec"),
    _e("dapi", "evt", "transfer", "pay", "pay/paid/paying", "agt thm rec"),
    _e("duli", "evt", "transfer", "help", "help/helped/helping", "agt thm"),
    _e("debi", "evt", "transfer", "hit", "hit/hitting/strike", "agt thm ins"),
    _e("dafi", "evt", "transfer", "hold", "hold/held/holding", "agt thm"),
    _e("duxi", "evt", "transfer", "find", "find/found/finding", "agt thm"),
    _e("deti", "evt", "transfer", "wait", "wait/waited/waiting", "agt thm"),
    _e("dayi", "evt", "transfer", "try", "try/tried/trying", "agt thm"),
    _e("degi", "evt", "transfer", "get", "get/got/gotten/getting/receive", "agt thm src"),
    # motion  v-
    _e("voni", "evt", "motion", "move", "move/moved/moving", "agt path"),
    _e("veli", "evt", "motion", "go", "go/went/gone/going", "agt gol src"),
    _e("vini", "evt", "motion", "come", "come/came/coming", "agt gol src"),
    _e("vaki", "evt", "motion", "run", "run/ran/running", "agt gol"),
    _e("visi", "evt", "motion", "sit", "sit/sat/sitting", "agt loc"),
    _e("vosi", "evt", "motion", "stand", "stand/stood/standing", "agt loc"),
    _e("vupi", "evt", "motion", "carry", "carry/carried/carrying/bring/brought", "agt thm gol"),
    _e("vali", "evt", "motion", "turn", "turn/turned/turning", "agt gol"),
    _e("vefi", "evt", "motion", "fall", "fall/fell/fallen/falling", "thm loc"),
    _e("voxi", "evt", "motion", "fly", "fly/flew/flown/flying", "agt gol"),
    _e("voyi", "evt", "motion", "swim", "swim/swam/swum/swimming", "agt gol"),
    _e("voti", "evt", "motion", "walk", "walk/walked/walking", "agt gol"),
    _e("vuli", "evt", "motion", "leave", "leave/left/leaving", "agt src"),
    _e("vani", "evt", "motion", "arrive", "arrive/arrived/arriving", "agt gol"),
    _e("voci", "evt", "motion", "stay", "stay/stayed/staying/remain", "agt loc"),
    # perception / speech  s-
    _e("vidi", "evt", "sense", "see", "see/saw/seen/seeing/look/looked", "exp thm ins"),
    _e("suli", "evt", "sense", "hear", "hear/heard/hearing/listen", "exp thm"),
    _e("somi", "evt", "sense", "smell", "smell/smelled/smelling", "exp thm"),
    _e("sati", "evt", "sense", "taste", "taste/tasted", "exp thm"),
    _e("suci", "evt", "sense", "touch", "touch/touched/touching", "agt thm"),
    _e("saki", "evt", "speech", "say", "say/said/saying/tell/told", "agt cnt rec"),
    _e("suji", "evt", "speech", "ask", "ask/asked/asking", "agt cnt rec"),
    _e("sowi", "evt", "speech", "answer", "answer/answered", "agt cnt rec"),
    _e("sari", "evt", "speech", "write", "write/wrote/written/writing", "agt thm rec"),
    _e("seni", "evt", "speech", "read", "read/reading", "agt thm"),
    _e("sugi", "evt", "speech", "call", "call/called/calling", "agt thm"),
    _e("soti", "evt", "speech", "shout", "shout/shouted/yell", "agt cnt"),
    _e("sini", "evt", "speech", "mean", "mean/meant/meaning", "agt cnt"),
    # cognition  k-
    _e("kuni", "evt", "cognition", "know", "know/knew/known/knowing", "exp thm"),
    _e("keni", "evt", "cognition", "think", "think/thought/thinking", "exp cnt"),
    _e("kabi", "evt", "cognition", "believe", "believe/believed", "exp cnt"),
    _e("koli", "evt", "cognition", "remember", "remember/remembered", "exp thm"),
    _e("kefi", "evt", "cognition", "forget", "forget/forgot/forgotten", "exp thm"),
    _e("kedi", "evt", "cognition", "learn", "learn/learned/learnt", "agt thm"),
    _e("kaci", "evt", "cognition", "teach", "teach/taught/teaching", "agt thm rec"),
    _e("kawi", "evt", "cognition", "want", "want/wanted/wanting/wish", "exp thm"),
    _e("nidi", "evt", "cognition", "need", "need/needed/needing", "exp thm"),
    _e("kiri", "evt", "cognition", "decide", "decide/decided", "agt cnt"),
    _e("kuxi", "evt", "cognition", "understand", "understand/understood", "exp thm"),
    _e("kifi", "evt", "cognition", "doubt", "doubt/doubted", "exp cnt"),
    _e("kopi", "evt", "cognition", "hope", "hope/hoped/hoping", "exp cnt"),
    # feeling  f-
    _e("fili", "evt", "feeling", "feel", "feel/felt/feeling", "exp thm"),
    _e("fali", "evt", "feeling", "like", "like/liked/liking/love/loved", "exp thm"),
    _e("fori", "evt", "feeling", "fear", "fear/feared/afraid", "exp thm"),
    _e("fegi", "evt", "feeling", "anger", "anger/angry-at", "exp thm"),
    _e("fosi", "evt", "feeling", "sad", "sad-about/grieve", "exp thm"),
    _e("feni", "evt", "feeling", "pain", "hurt/hurts/pain", "exp thm"),
    # life  p-
    _e("pivi", "evt", "life", "live", "live/lived/living", "agt loc"),
    _e("podi", "evt", "life", "die", "die/died/dying/dead", "thm"),
    _e("pusi", "evt", "life", "eat", "eat/ate/eaten/eating", "agt thm"),
    _e("pibi", "evt", "life", "drink", "drink/drank/drunk/drinking", "agt thm"),
    _e("posi", "evt", "life", "sleep", "sleep/slept/sleeping", "agt loc"),
    _e("pawi", "evt", "life", "wake", "wake/woke/woken/awake", "agt"),
    _e("pefi", "evt", "life", "breathe", "breathe/breathed", "agt"),
    _e("paxi", "evt", "life", "be-born", "born/birth", "thm"),
    # change / being  h-
    _e("hazi", "evt", "change", "happen", "happen/happened/occur", "thm loc tmp"),
    _e("heni", "evt", "change", "become", "become/became/becoming", "thm mod"),
    _e("hosi", "evt", "change", "start", "start/started/begin/began", "agt thm"),
    _e("hofi", "evt", "change", "end", "end/ended/finish/finished/stop/stopped", "agt thm"),
    _e("havi", "evt", "change", "have", "have/had/has/having/own/owned", "agt thm"),
    _e("holi", "evt", "change", "be-at", "be/is/are/was/were/being/located", "thm loc"),
    _e("haci", "evt", "change", "cause", "cause/caused/causing", "agt thm"),
    _e("huti", "evt", "change", "change", "change/changed/changing", "agt thm"),
    _e("hexi", "evt", "change", "exist", "exist/exists/existed", "thm loc"),
    # ready / consume (for classic ambiguity examples)
    _e("redi", "evt", "change", "be-ready", "ready", "thm prp"),
)

# ---------------------------------------------------------------------------
# Open class — kinds (-o)
# ---------------------------------------------------------------------------

KINDS: tuple[Entry, ...] = (
    _e("pamo", "kind", "people", "person", "person/man/woman/human/someone/who"),
    _e("pino", "kind", "people", "people", "people/humans"),
    _e("peko", "kind", "people", "body", "body"),
    _e("pabo", "kind", "people", "child", "child/kid/boy/girl"),
    _e("palto", "kind", "people", "adult", "adult"),
    _e("pexo", "kind", "life", "animal", "animal/creature"),
    _e("pugo", "kind", "life", "dog", "dog"),
    _e("piko", "kind", "life", "cat", "cat"),
    _e("pico", "kind", "life", "bird", "bird"),
    _e("pifo", "kind", "life", "fish", "fish"),
    _e("puko", "kind", "life", "chicken", "chicken"),
    _e("suno", "kind", "life", "sun", "sun"),
    _e("wino", "kind", "life", "wind", "wind"),
    _e("moto", "kind", "matter", "thing", "thing/object/something/what"),
    _e("miko", "kind", "matter", "tool", "tool/device"),
    _e("mabo", "kind", "matter", "book", "book"),
    _e("melo", "kind", "matter", "food", "food/meal"),
    _e("mowo", "kind", "matter", "water", "water"),
    _e("mafo", "kind", "matter", "fire", "fire"),
    _e("mazo", "kind", "matter", "air", "air"),
    _e("mexo", "kind", "matter", "earth", "earth/ground/soil"),
    _e("meso", "kind", "matter", "house", "house/home/building"),
    _e("mako", "kind", "matter", "machine", "machine/computer"),
    _e("muko", "kind", "matter", "cloak", "cloak/coat/garment"),
    _e("teso", "kind", "matter", "telescope", "telescope"),
    _e("wodo", "kind", "info", "word", "word/words"),
    _e("wixo", "kind", "info", "idea", "idea/thought"),
    _e("weso", "kind", "info", "story", "story"),
    _e("wako", "kind", "info", "language", "language"),
    _e("nexo", "kind", "info", "Nex", "nex"),
    _e("loko", "kind", "place", "place", "place/where"),
    _e("lano", "kind", "place", "land", "land/country"),
    _e("livo", "kind", "place", "city", "city/town"),
    _e("laro", "kind", "place", "room", "room"),
    _e("lefo", "kind", "place", "side", "side"),
    _e("liso", "kind", "place", "inside", "inside/interior"),
    _e("laso", "kind", "place", "outside", "outside"),
    _e("toko", "kind", "time", "time", "time/when"),
    _e("dieno", "kind", "time", "day", "day/yesterday/tomorrow"),
    _e("noco", "kind", "time", "night", "night"),
    _e("yaro", "kind", "time", "year", "year"),
    _e("horo", "kind", "time", "hour", "hour"),
    _e("mino", "kind", "time", "minute", "minute"),
    _e("koso", "kind", "abstract", "state", "ness/state/hood", notes="nominalizer for qualities"),
    _e("evo", "kind", "abstract", "event", "event", notes="nominalizer for events"),
    _e("relo", "kind", "abstract", "relation", "relation"),
    _e("sovo", "kind", "sense", "sound", "sound"),
    _e("luxo", "kind", "sense", "light", "light"),
    _e("tino", "kind", "sense", "color", "color/colour"),
    _e("hato", "kind", "abstract", "way", "way/manner"),
    _e("qeso", "kind", "abstract", "question", "question"),
    _e("toso", "kind", "matter", "tree", "tree"),
    _e("roso", "kind", "matter", "rock", "rock/stone"),
    _e("paso", "kind", "matter", "path", "path/road/way-path"),
    _e("mano", "kind", "people", "hand", "hand"),
    _e("hedo", "kind", "people", "head", "head"),
    _e("eyo", "kind", "people", "eye", "eye"),
    _e("namo", "kind", "info", "name", "name"),
)


def agent_form(event: str) -> str | None:
    """seni → senu. Derived kinds use -u, never the primitive -o space."""
    if len(event) < 2 or not event.endswith("i"):
        return None
    return event[:-1] + "u"


def _agent_english(e: Entry) -> str:
    w = e.english[0] if e.english else e.gloss
    if w.endswith("e"):
        return w + "r"
    if w.endswith("y"):
        return w[:-1] + "ier"
    return w + "er"


def _derived_agent_kinds(reserved: set[str]) -> tuple[Entry, ...]:
    """One-token -er nouns. Same stem as the event; type vowel flips i→o."""
    out: list[Entry] = []
    taken = set(reserved)
    for e in EVENTS:
        form = agent_form(e.form)
        if not form:
            raise RuntimeError(f"cannot derive agent kind from {e.form}")
        if form in taken:
            raise RuntimeError(
                f"derived {form} from {e.form} collides with a primitive — "
                f"type vowels are supposed to make this impossible"
            )
        er = _agent_english(e)
        out.append(
            _e(
                form,
                "kind",
                e.field,
                er,
                f"{er}/{e.gloss}-er",
                notes=f"packed ( agto {e.form} )",
            )
        )
        taken.add(form)
    return tuple(out)

# ---------------------------------------------------------------------------
# Open class — qualities (-a)
# ---------------------------------------------------------------------------

QUALS: tuple[Entry, ...] = (
    _e("guda", "qual", "value", "good", "good/well/nice"),
    _e("bada", "qual", "value", "bad", "bad/evil/wrong"),
    _e("hapa", "qual", "value", "happy", "happy/glad"),
    _e("sada", "qual", "value", "sad", "sad/unhappy"),
    _e("trua", "qual", "value", "true", "true/real"),
    _e("fala", "qual", "value", "false", "false/untrue"),
    _e("biga", "qual", "phys", "big", "big/large/great"),
    _e("soma", "qual", "phys", "small", "small/little/tiny"),
    _e("nova", "qual", "phys", "new", "new"),
    _e("olda", "qual", "phys", "old", "old"),
    _e("ruga", "qual", "phys", "red", "red"),
    _e("blua", "qual", "phys", "blue", "blue"),
    _e("grea", "qual", "phys", "green", "green"),
    _e("wita", "qual", "phys", "white", "white"),
    _e("blaka", "qual", "phys", "black", "black"),
    _e("yela", "qual", "phys", "yellow", "yellow"),
    _e("hota", "qual", "phys", "hot", "hot/warm"),
    _e("kola", "qual", "phys", "cold", "cold/cool"),
    _e("fasta", "qual", "phys", "fast", "fast/quick/quickly"),
    _e("slowa", "qual", "phys", "slow", "slow/slowly"),
    _e("hara", "qual", "phys", "hard", "hard/difficult"),
    _e("sofa", "qual", "phys", "soft", "soft/easy"),
    _e("sama", "qual", "rel", "same", "same"),
    _e("ota", "qual", "rel", "other", "other/another/different"),
    _e("neara", "qual", "space", "near", "near/close"),
    _e("fara", "qual", "space", "far", "far/distant"),
    _e("fulla", "qual", "phys", "full", "full"),
    _e("ema", "qual", "phys", "empty", "empty"),
    _e("opena", "qual", "phys", "open", "open"),
    _e("klosa", "qual", "phys", "closed", "closed/shut"),
    _e("aliva", "qual", "life", "alive", "alive/living"),
    _e("deda", "qual", "life", "dead", "dead"),
    _e("longa", "qual", "phys", "long", "long"),
    _e("kuta", "qual", "phys", "short", "short"),
    _e("higa", "qual", "phys", "high", "high/tall"),
    _e("lowa", "qual", "phys", "low", "low"),
    _e("stroa", "qual", "phys", "strong", "strong"),
    _e("weka", "qual", "phys", "weak", "weak"),
    _e("reda", "qual", "value", "ready", "ready"),
    _e("fria", "qual", "value", "free", "free"),
    _e("equa", "qual", "rel", "equal", "equal"),
    _e("mana", "qual", "quant", "many", "many/much/lots"),
    _e("fewa", "qual", "quant", "few", "few"),
    _e("sura", "qual", "value", "sure", "sure/certain"),
    _e("northa", "qual", "space", "north", "north/northern"),
    _e("warma", "qual", "phys", "warm", "warm"),
    _e("tita", "qual", "phys", "tight", "tight"),
    _e("lusa", "qual", "phys", "loose", "loose"),
)

DIGITS = tuple(_e(str(i), "struct", "quant", str(i), str(i)) for i in range(10))
LETTERS = tuple(_e(ch, "struct", "spell", ch, ch) for ch in "abcdefghijklmnopqrstuvwxyz")


_RESERVED_FOR_DERIVED = {
    e.form
    for e in (
        *ILLOCUTIONS,
        *ROLES,
        *FEATURES,
        *OPERATORS,
        *DEICTICS,
        *STRUCT,
        *EVENTS,
        *KINDS,
        *QUALS,
        *DIGITS,
        *LETTERS,
    )
}
DERIVED_AGENTS: tuple[Entry, ...] = _derived_agent_kinds(_RESERVED_FOR_DERIVED)


def _all_entries() -> list[Entry]:
    return [
        *ILLOCUTIONS,
        *ROLES,
        *FEATURES,
        *OPERATORS,
        *DEICTICS,
        *STRUCT,
        *EVENTS,
        *KINDS,
        *DERIVED_AGENTS,
        *QUALS,
        *DIGITS,
        *LETTERS,
    ]


def _build() -> dict[str, Entry]:
    table: dict[str, Entry] = {}
    collisions: list[str] = []
    for e in _all_entries():
        if e.form in table and table[e.form].kind != e.kind:
            collisions.append(e.form)
        # prefer first (closed class wins because we add it first)
        if e.form not in table:
            table[e.form] = e
    if collisions:
        raise RuntimeError(f"lexicon form collisions: {collisions}")
    return table


LEXICON: dict[str, Entry] = _build()

CLOSED_KINDS = {"illoc", "role", "feat", "op", "deictic", "struct"}


def closed_class() -> dict[str, Entry]:
    return {f: e for f, e in LEXICON.items() if e.kind in CLOSED_KINDS}


def open_class() -> dict[str, Entry]:
    return {f: e for f, e in LEXICON.items() if e.kind not in CLOSED_KINDS}


def lookup(form: str) -> Entry | None:
    return LEXICON.get(form)


def is_role(form: str) -> bool:
    e = LEXICON.get(form)
    return bool(e and e.kind == "role")


def is_feature(form: str) -> bool:
    e = LEXICON.get(form)
    return bool(e and e.kind == "feat")


def is_operator(form: str) -> bool:
    e = LEXICON.get(form)
    return bool(e and e.kind == "op")


def is_illoc(form: str) -> bool:
    e = LEXICON.get(form)
    return bool(e and e.kind == "illoc")


def is_deictic(form: str) -> bool:
    e = LEXICON.get(form)
    return bool(e and e.kind == "deictic")


def english_to_root() -> dict[str, Entry]:
    m: dict[str, Entry] = {}
    for e in LEXICON.values():
        if e.kind == "struct":
            continue
        for w in e.english:
            key = w.lower()
            # first mapping wins — closed class is inserted first
            m.setdefault(key, e)
    return m


ENGLISH_MAP = english_to_root()

# event form → packed agent kind (seni → senu)
AGENT_UNPACK: dict[str, str] = {
    e.form: e.form[:-1] + "i" for e in DERIVED_AGENTS if e.form.endswith("u")
}
AGENT_PACK: dict[str, str] = {v: k for k, v in AGENT_UNPACK.items()}


ROLE_ORDER = (
    "agt",
    "exp",
    "rec",
    "thm",
    "cnt",
    "ins",
    "mnr",
    "src",
    "path",
    "gol",
    "loc",
    "tmp",
    "cau",
    "prp",
    "ben",
    "pos",
    "name",
    "unit",
    "rel",
    "mod",
)

FEAT_ORDER = (
    "not",
    "must",
    "may",
    "past",
    "now",
    "fut",
    "done",
    "ong",
    "hab",
    "seen",
    "heard",
    "said",
    "inf",
    "def",
    "ind",
    "mass",
    "sg",
    "pl",
    "very",
    "more",
    "most",
)


def field_hue(field: str) -> str:
    return {
        "speech": "#e07a5f",
        "role": "#7b8cde",
        "polarity": "#c77dff",
        "tense": "#c77dff",
        "aspect": "#c77dff",
        "mood": "#c77dff",
        "evid": "#c77dff",
        "det": "#c77dff",
        "number": "#c77dff",
        "degree": "#c77dff",
        "logic": "#c77dff",
        "quant": "#c77dff",
        "modal": "#c77dff",
        "rel": "#81b29a",
        "struct": "#9a8c7a",
        "deixis": "#f2cc8f",
        "time": "#e9c46a",
        "transfer": "#e07a5f",
        "motion": "#e9c46a",
        "sense": "#81b29a",
        "cognition": "#7b8cde",
        "feeling": "#e07a5f",
        "life": "#81b29a",
        "change": "#e07a5f",
        "people": "#81b29a",
        "matter": "#b08968",
        "info": "#7b8cde",
        "place": "#81b29a",
        "abstract": "#9a8c7a",
        "value": "#f2cc8f",
        "phys": "#f2cc8f",
        "space": "#81b29a",
        "spell": "#9a8c7a",
        "derive": "#81b29a",
    }.get(field, "#c4b8a8")


def lexicon_public() -> list[dict]:
    """JSON-serialisable lexicon for the playground (skip digits/letters)."""
    skip = set("0123456789abcdefghijklmnopqrstuvwxyz()") | {".", "="}
    out = []
    for e in LEXICON.values():
        if e.form in skip:
            continue
        out.append(
            {
                "form": e.form,
                "kind": e.kind,
                "field": e.field,
                "gloss": e.gloss,
                "english": list(e.english),
                "roles": list(e.roles),
                "notes": e.notes,
                "hue": field_hue(e.field),
            }
        )
    kind_rank = {
        "illoc": 0,
        "role": 1,
        "feat": 2,
        "op": 3,
        "deictic": 4,
        "evt": 5,
        "kind": 6,
        "qual": 7,
        "struct": 8,
    }
    out.sort(key=lambda r: (kind_rank.get(r["kind"], 9), r["form"]))
    return out


def validate_lexicon() -> list[str]:
    """Return a list of problems (empty if healthy)."""
    problems: list[str] = []
    forms = list(LEXICON)
    # type endings for open class
    for e in LEXICON.values():
        if e.kind == "evt" and not e.form.endswith("i"):
            problems.append(f"event {e.form} should end in -i")
        if e.kind == "kind":
            derived = {d.form for d in DERIVED_AGENTS}
            if e.form in derived:
                if not e.form.endswith("u"):
                    problems.append(f"derived kind {e.form} should end in -u")
            elif not e.form.endswith("o"):
                problems.append(f"primitive kind {e.form} should end in -o")
        if e.kind == "qual" and not e.form.endswith("a"):
            problems.append(f"quality {e.form} should end in -a")
    # disjoint closed classes
    buckets: dict[str, str] = {}
    for e in (*ILLOCUTIONS, *ROLES, *FEATURES, *OPERATORS, *DEICTICS):
        if e.form in buckets:
            problems.append(f"closed-class collision {e.form} in {buckets[e.form]} and {e.kind}")
        buckets[e.form] = e.kind
    return problems
