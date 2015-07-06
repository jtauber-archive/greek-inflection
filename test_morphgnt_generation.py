#!/usr/bin/env python3

from pysblgnt import morphgnt_rows

from characters import strip_length

from verbs import Lexicon


lexicon = Lexicon("lexicons/morphgnt.yaml")

for book_num in range(1, 28):
    for row in morphgnt_rows(book_num):
        ccat_pos = row["ccat-pos"]
        ccat_parse = row["ccat-parse"]
        norm = row["norm"]
        lemma = row["lemma"]
        if ccat_pos != "V-":
            continue

        if ccat_parse[3] == "N":
            parse = ccat_parse[1:4]
        elif ccat_parse[3] == "P":
            parse = ccat_parse[1:4] + "." + ccat_parse[4:7]
        elif ccat_parse[3] == "I":
            parse = ccat_parse[1:4] + "." + ccat_parse[0] + ccat_parse[5]
        else:
            continue

        predicted = lexicon.generate(lemma, parse)
        if predicted is None:
            print("didn't know how to work out {} {} {}".format(lemma, parse, norm))
        elif norm not in [strip_length(p) for p in predicted.split("/")]:
            print("{} {} got {} instead of {}".format(lemma, parse, predicted, norm))
