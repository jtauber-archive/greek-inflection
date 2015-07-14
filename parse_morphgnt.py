#!/usr/bin/env python3

from characters import strip_length

from pysblgnt import morphgnt_rows

from parse import Lexicon, Endings


IGNORE_LIST = [
    "σαβαχθάνι",
    "ἔνι",
    "χρή",
]


LEXICON_FILE = "lexicons/morphgnt.yaml"
ENDINGS_FILE = "stemming.yaml"


lexicon = Lexicon(LEXICON_FILE)
endings = Endings(ENDINGS_FILE)


if __name__ == "__main__":

    for book_num in range(1, 28):
        for row in morphgnt_rows(book_num):
            ccat_pos = row["ccat-pos"]
            ccat_parse = row["ccat-parse"]
            form = row["norm"]
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

            stem_info = lexicon.stem_info(lemma, parse, context=row["bcv"])
            if stem_info is None:
                print("couldn't get stem info for {} {}".format(lemma, parse))
                continue
            ending_info = endings.ending_info(form, parse)
            valid_stems = (
                set(strip_length(info.stem.replace("|", "")) for info in stem_info) &
                set(info.stem for info in ending_info))

            if len(valid_stems) != 1:
                print(form, parse, lemma, len(valid_stems))
                print("    {}".format(stem_info))
                print("    {}".format(ending_info))
                for valid_stem in valid_stems:
                    for info in stem_info:
                        if info.stem == valid_stem:
                            print("    {}".format(info))
                    for info in ending_info:
                        if info.stem == valid_stem:
                            print("    {}".format(info))
