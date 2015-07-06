#!/usr/bin/env python3

from pysblgnt import morphgnt_rows

from stemming import Stemmer


IGNORE_LIST = [
    "σαβαχθάνι",
    "ἔνι",
    "χρή",
]


stemmer = Stemmer("lexicons/morphgnt.yaml")

for book_num in range(1, 28):
    for row in morphgnt_rows(book_num):
        ccat_pos = row["ccat-pos"]
        ccat_parse = row["ccat-parse"]
        norm = row["norm"]
        lemma = row["lemma"]

        if ccat_pos != "V-":
            continue

        if lemma in IGNORE_LIST:
            continue

        if ccat_parse[3] == "N":
            parse = ccat_parse[1:4]
        elif ccat_parse[3] == "P":
            parse = ccat_parse[1:4] + "." + ccat_parse[4:7]
        elif ccat_parse[3] == "I":
            parse = ccat_parse[1:4] + "." + ccat_parse[0] + ccat_parse[5]
        else:
            continue

        stemmer.stem(row["bcv"], lemma, parse, norm)
        stemmer.citation(row["bcv"], lemma)


stemmer.counter.results()
