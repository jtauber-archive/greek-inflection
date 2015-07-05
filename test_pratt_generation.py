#!/usr/bin/env python3

import yaml

from characters import strip_length

from verbs import Lexicon


TEST_FILES = [
    "tests/pratt.yaml",
]


lexicon = Lexicon("lexicons/pratt.yaml")

for TEST_FILE in TEST_FILES:
    with open(TEST_FILE) as f:
        for test in yaml.load(f):
            lemma = test.pop("lemma")
            location = test.pop("location", "")
            test_length = test.pop("test_length", True)
            for parse, form in test.items():
                predicted = lexicon.generate(lemma, parse)
                if predicted is None:
                    print("didn't know how to work out {} {} {}".format(lemma, parse, form))
                elif strip_length(form) == strip_length(predicted):
                    continue
                elif strip_length(form) not in [strip_length(p) for p in predicted.split("/")]:
                    print("{} {} got {} instead of {} in {}".format(lemma, parse, predicted, form, location))
