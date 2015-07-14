from collections import namedtuple
import re

from characters import strip_accents, remove_redundant_macron, strip_length

import yaml


StemInfo = namedtuple("StemInfo", ["stem", "stem_type", "used_override"])


class Lexicon:

    def __init__(self, lexicon_file):
        with open(lexicon_file) as f:
            self.lexicon = yaml.load(f)

    def stem_info(self, lemma, parse, context=None):
        lexical_entry = self.lexicon[lemma]

        result = None

        for stem_key, stem in lexical_entry["stems"].items():
            if "/" in stem_key:
                stem_key, context_to_match = stem_key.split("/")
                if not (context and re.match(context_to_match, context)):
                    continue
            regex = {
                "1-": "P",
                "1+": "I",
                "2-": "F[AM]",
                "3-": "A[AM][NP]",
                "3+": "A[AM][I]",
                "4-": "XA",
                "4-S": "XAI..S",
                "4-P": "XAI..P",
                "4-NP": "XA[NP]",
                "4+": "YA",
                "5-": "X[MP]",
                "5+": "Y[MP]",
                "6-": "AP[NP]",
                "6+": "AP[I]",
                "7-": "FP",
            }[stem_key]
            if re.match(regex, parse):
                result = StemInfo(stem, stem_key, None)

        for parse_regex, stem in lexical_entry.get("stem_overrides", []):
            if re.match(parse_regex, parse):
                result = StemInfo(stem, None, parse_regex)

        if not result:
            return

        result_set = set()

        for stem in result.stem.split("/"):
            result_set.add(StemInfo(stem, result.stem_type, result.used_override))

        return result_set


def debreath(word):
    word = word.replace("εἷ", "hεῖ")
    word = word.replace("εἵ", "hεί")
    word = word.replace("εἱ", "hει")
    word = word.replace("ἕ", "hέ")
    word = word.replace("ἑ", "hε")

    return word


def rebreath(word):
    word = word.replace("hεῖ", "εἷ")
    word = word.replace("hεί", "εἵ")
    word = word.replace("hει", "εἱ")
    word = word.replace("hέ", "ἕ")
    word = word.replace("hε", "ἑ")
    # word = add_necessary_breathing(word)
    word = remove_redundant_macron(word)

    return word


EndingInfo = namedtuple("EndingInfo", ["stem", "components"])


class Endings:

    def __init__(self, endings_file):
        with open(endings_file) as f:
            self.endings = yaml.load(f)

    def ending_info(self, form, parse, test_length=False):
        stem_set = set()

        form = debreath(form)

        if parse in self.endings:
            pairs = self.endings[parse]

            while isinstance(pairs, dict) and "ref" in pairs:
                if pairs["ref"] in self.endings:
                    pairs = self.endings[pairs["ref"]]
                else:
                    raise Exception("ref to {} which doesn't exist".format(pairs["ref"]))

            for entry in pairs:
                if not test_length:
                    entry = strip_length(entry)
                s1, s234, s5 = entry.split("|")
                s2, s34 = s234.split(">")
                s3, s4 = s34.split("<")
                s3 = s3.replace("(", "\\(")
                s3 = s3.replace(")", "\\)")
                s5 = s5.replace("(", "\\(")
                s5 = s5.replace(")", "\\)")
                regex_pair = ("(.*{}){}{}$".format(s1, s3, s5), s2)

                if re.match(regex_pair[0], form):
                    stem = rebreath(
                        strip_accents(
                            re.sub(regex_pair[0], r"\1" + regex_pair[1], form)))

                    stem_set.add(EndingInfo(stem, (s1, s2, s3, s4, s5)))
        else:
            return None

        return stem_set
