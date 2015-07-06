#!/usr/bin/env python3

import re

from characters import strip_accents, strip_length
import yaml

from utils import Counter


class Stemmer:

    def __init__(self, lexicon):

        with open("stemming.yaml") as f:
            self.stemming_rules = yaml.load(f)

        with open(lexicon) as f:
            self.lexicon = yaml.load(f)

        self.counter = Counter()

    def regex_list(self, lemma, parse):
        result = None
        for k, v in self.lexicon[lemma]["stems"].items():
            regex = {
                "1-": "P",
                "1+": "I",
                "2-": "F[AM]",
                "3-": "A[AM][NP]",
                "3+": "A[AM][I]",
                "4-": "XA",
                "4+": "YA",
                "5-": "X[MP]",
                "5+": "Y[MP]",
                "6-": "AP[NP]",
                "6+": "AP[I]",
                "7-": "FP",
            }[k]
            if re.match(regex, parse):
                result = v
        for k, v in self.lexicon[lemma].get("stem_overrides", []):
            if re.match(k, parse):
                result = v
        return result

    def stem(self, location, lemma, parse, norm):
        stem_set = set()

        if parse in self.stemming_rules:
            pairs = self.stemming_rules[parse]
            while isinstance(pairs, dict) and "ref" in pairs:
                if pairs["ref"] in self.stemming_rules:
                    pairs = self.stemming_rules[pairs["ref"]]
                else:
                    self.counter.fail("ref to {} which doesn't exist".format(pairs["ref"]))
                    return
            for entry in pairs:
                if isinstance(entry, str):
                    s1, s234, s5 = entry.split("|")
                    s2, s34 = s234.split(">")
                    s3, s4 = s34.split("<")
                    s3 = s3.replace("(", "\\(")
                    s3 = s3.replace(")", "\\)")
                    s5 = s5.replace("(", "\\(")
                    s5 = s5.replace(")", "\\)")
                    regex_pair = ["(.*{}){}{}".format(s1, s3, s5), s2]
                else:
                    regex_pair = entry
                if re.match(regex_pair[0] + "$", norm):
                    stem_set.add(strip_accents(re.sub(regex_pair[0], r"\1" + regex_pair[1], norm)))
        else:
            self.counter.skip("no stemming rule for {} (form was {})".format(parse, norm))
            return

        predicted = self.regex_list(lemma, parse)
        if predicted:
            predicted = predicted.replace("|", "")
            if len(stem_set) > 0:
                if any([strip_length(s) in stem_set for s in predicted.split("/")]):
                    self.counter.success()
                else:
                    self.counter.fail("got {} for {} {} {} (lexicon has {})".format(", ".join(stem_set), lemma, parse, norm, predicted))
            else:
                self.counter.fail("[{}] didn't get any match for {} {} {}".format(location, lemma, parse, norm))
        else:
            self.counter.skip("[{}] couldn't predict {} {} {}; got stem_set: {}".format(location, lemma, parse, norm, stem_set))

    def citation(self, location, lemma):
        stem_set = set()

        if "citation" in self.stemming_rules:
            for regex_pair in self.stemming_rules["citation"]:
                if re.match(regex_pair[0] + "$", lemma):
                    stem_set.add(strip_accents(re.sub(regex_pair[0], r"\1" + regex_pair[1], lemma)))
        else:
            self.counter.fail("! no stemming rule (lemma was {})".format(lemma))
            return

        citation_parse = self.lexicon[lemma].get("citation", "PAI.1S")

        predicted = self.regex_list(lemma, citation_parse)
        if predicted:
            predicted = predicted.replace("|", "")
            if len(stem_set) > 0:
                if any([strip_length(s) in stem_set for s in predicted.split("/")]):
                    self.counter.success()
                else:
                    self.counter.fail("! got {} for {} citation (lexicon has {})".format(", ".join(stem_set), lemma, predicted))
            else:
                self.counter.fail("! [{}] didn't get any match for {}".format(location, lemma))
        else:
            self.counter.skip("! [{}] couldn't predict {}; got stem_set: {}".format(location, lemma, stem_set))
