#!/usr/bin/env python3

import yaml

from characters import strip_length

from parse import Lexicon, Endings


TEST_FILE = "tests/pratt.yaml"
LEXICON_FILE = "lexicons/pratt.yaml"
ENDINGS_FILE = "stemming.yaml"


lexicon = Lexicon(LEXICON_FILE)
endings = Endings(ENDINGS_FILE)


if __name__ == "__main__":

    with open(TEST_FILE) as f:
        for test in yaml.load(f):
            lemma = strip_length(test.pop("lemma"))
            test_length = test.pop("test_length", True)
            location = test.pop("location", None)

            for parse, form in test.items():
                stem_info = lexicon.stem_info(lemma, parse, context=location)
                if stem_info is None:
                    print("couldn't get stem info for {} {}".format(lemma, parse))
                    continue
                ending_info = endings.ending_info(form, parse)
                valid_stems = (
                    set(strip_length(info.stem) for info in stem_info) &
                    set(info.stem for info in ending_info))

                if len(valid_stems) != 1:
                    print(form, parse, lemma)
                    print("    {}".format(stem_info))
                    print("    {}".format(ending_info))
                    for valid_stem in valid_stems:
                        for info in stem_info:
                            if info.stem == valid_stem:
                                print("    {}".format(info))
                        for info in ending_info:
                            if info.stem == valid_stem:
                                print("    {}".format(info))
