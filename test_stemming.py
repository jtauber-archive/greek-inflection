import yaml

from characters import strip_length

from stemming import Stemmer


def test_stemming(test_file, lexicon_file):
    stemmer = Stemmer(lexicon_file)

    with open(test_file) as f:
        for test in yaml.load(f):
            lemma = strip_length(test.pop("lemma"))
            test_length = test.pop("test_length", True)
            location = test.pop("location", "")

            for parse, form in test.items():
                stemmer.stem(location, lemma, parse, form, test_length)

    stemmer.counter.results()
