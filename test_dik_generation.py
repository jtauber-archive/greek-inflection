#!/usr/bin/env python3

from characters import strip_length
import yaml

from utils import Counter

from verbs import Lexicon


TEST_FILES = [
    "tests/dik.yaml",
]


lexicon = Lexicon("lexicons/dik.yaml")

counter = Counter()

for TEST_FILE in TEST_FILES:
    with open(TEST_FILE) as f:
        for test in yaml.load(f):
            lemma = test.pop("lemma")
            location = test.pop("location", "")
            test_length = test.pop("test_length", True)
            for parse, form in test.items():
                predicted = lexicon.generate(lemma, parse, context=location)
                if predicted is None:
                    counter.fail("didn't know how to work out {} {} {}".format(lemma, parse, form))
                elif strip_length(form) == strip_length(predicted):
                    counter.success()
                    continue
                elif strip_length(form) not in [strip_length(p) for p in predicted.split("/")]:
                    counter.fail("{} {} got {} instead of {} in {}".format(lemma, parse, predicted, form, location))
                else:
                    counter.skip("{} {} {} {} {}".format(lemma, parse, form, predicted, location))

counter.results()
