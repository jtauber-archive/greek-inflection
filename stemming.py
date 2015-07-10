import re

from characters import strip_accents, strip_length
import yaml

from utils import Counter

from verbs import stemming_rules, debreath, rebreath, Base


class Stemmer(Base):

    def __init__(self, lexicon):
        with open(lexicon) as f:
            self.lexicon = yaml.load(f)

        self.counter = Counter()

    def get_stem_set(self, parse, norm, test_length):
        stem_set = set()

        norm = debreath(norm)

        if parse in stemming_rules:
            pairs = stemming_rules[parse]
            while isinstance(pairs, dict) and "ref" in pairs:
                if pairs["ref"] in stemming_rules:
                    pairs = stemming_rules[pairs["ref"]]
                else:
                    raise Exception("ref to {} which doesn't exist".format(pairs["ref"]))
            for entry in pairs:
                if isinstance(entry, str):
                    if not test_length:
                        entry = strip_length(entry)
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
                    stem_set.add(rebreath(strip_accents(re.sub(regex_pair[0], r"\1" + regex_pair[1], norm))))
        else:
            return None

        return stem_set

    def stem(self, location, lemma, parse, norm, test_length):
        stem_set = self.get_stem_set(parse, norm, test_length)
        if stem_set is None:
            self.counter.skip("no stemming rule for {} (form was {})".format(parse, norm))
            return

        predicted = self.regex_list(lemma, parse, context=location)
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
        stem_set = self.get_stem_set("citation", lemma, False)
        if stem_set is None:
            self.counter.fail("! no stemming rule (lemma was {})".format(lemma))
            return

        citation_parse = self.lexicon[lemma].get("citation", "PAI.1S")

        predicted = self.regex_list(lemma, citation_parse, context=location)
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
