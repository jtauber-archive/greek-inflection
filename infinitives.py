#!/usr/bin/env python3

from collections import defaultdict

from pyuca import Collator
from pysblgnt import morphgnt_rows
from verbs import Lexicon

from characters import strip_length

words = {}
collator = Collator()

IGNORE_LIST = [
    "ἔνι",
    "σαβαχθάνι",
    "χρή",
]

for book_num in range(1, 28):
    for row in morphgnt_rows(book_num):
        ccat_pos = row["ccat-pos"]
        ccat_parse = row["ccat-parse"]
        lemma = row["lemma"]
        norm = row["norm"]

        if ccat_pos != "V-":
            continue

        if lemma in IGNORE_LIST:
            continue

        if lemma not in words:
            words[lemma] = defaultdict(set)

        if ccat_parse[1:4] == "PAN":
            words[lemma]["present.act.actual"].add(norm)

        if ccat_parse[1:4] == "PMN":
            words[lemma]["present.mp1.actual"].add(norm)

        if ccat_parse[1:4] == "PPN":
            words[lemma]["present.mp1.actual"].add(norm)

        if ccat_parse[1:4] == "AAN":
            words[lemma]["aorist.act.actual"].add(norm)

        if ccat_parse[1:4] == "AMN":
            words[lemma]["aorist.mp1.actual"].add(norm)

        if ccat_parse[1:4] == "APN":
            words[lemma]["aorist.mp2.actual"].add(norm)


lexicon = Lexicon("lexicons/morphgnt.yaml")

for k in sorted(words.keys(), key=collator.sort_key):
    PAN_generated = lexicon.generate(k, "PAN")
    PMN_generated = lexicon.generate(k, "PMN")
    PPN_generated = lexicon.generate(k, "PPN")
    AAN_generated = lexicon.generate(k, "AAN")
    AMN_generated = lexicon.generate(k, "AMN")
    APN_generated = lexicon.generate(k, "APN")

    if PAN_generated:
        if "present.act.actual" not in words[k]:
            words[k]["present.act.generated"].add(strip_length(PAN_generated))
    if PMN_generated:
        if "present.mp1.actual" not in words[k]:
            words[k]["present.mp1.generated"].add(strip_length(PMN_generated))
    if PPN_generated:
        if "present.mp1.actual" not in words[k]:
            words[k]["present.mp1.generated"].add(strip_length(PPN_generated))
    if AAN_generated:
        if "aorist.act.actual" not in words[k]:
            words[k]["aorist.act.generated"].add(strip_length(AAN_generated))
    if AMN_generated:
        if "aorist.mp1.actual" not in words[k]:
            words[k]["aorist.mp1.generated"].add(strip_length(AMN_generated))
    if APN_generated:
        if "aorist.mp2.actual" not in words[k]:
            words[k]["aorist.mp2.generated"].add(strip_length(APN_generated))

    if words[k]:
        print("{}:".format(k))
        for kk, v in sorted(words[k].items()):
            print("    {}: {}".format(kk, "/".join(sorted(v, key=collator.sort_key))))
