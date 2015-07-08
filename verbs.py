import re

from characters import accent, strip_length
from characters import strip_accents, remove_redundant_macron
from accentuation import recessive, persistent, on_penult, make_oxytone
from syllabify import add_necessary_breathing

import yaml

# from phonology import phon_pre, phon_post
from utils import remove_duplicates


with open("stemming.yaml") as f:
    stemming_rules = yaml.load(f)


def rep(strings, search, replacements, remove_accent=False):
    result = []
    for string in strings:
        if search in string and remove_accent:
            string = strip_accents(string)
        for replacement in replacements:
            word = string.replace(search, replacement)
            result.append(word)
    return result


def phon_pre(word):
    words = [word]

    words = rep(words, "εἷ", ["hεῖ"])
    words = rep(words, "εἵ", ["hεί"])
    words = rep(words, "εἱ", ["hει"])
    words = rep(words, "ἕ", ["hέ"])
    words = rep(words, "ἑ", ["hε"])

    return words


def phon_post(word):
    words = [word]

    words = rep(words, "hεῖ", ["εἷ"])
    words = rep(words, "hεί", ["εἵ"])
    words = rep(words, "hει", ["εἱ"])
    words = rep(words, "hέ", ["ἕ"])
    words = rep(words, "hε", ["ἑ"])

    words = rep(words, "+", [""])

    words = [add_necessary_breathing(w) for w in words]
    words = [remove_redundant_macron(w) for w in words]

    return words


class Lexicon:

    def __init__(self, lexicon):
        self.lexicon = {}

        with open(lexicon) as f:
            self.lexicon.update(yaml.load(f))

    def regex_list(self, lemma, parse, context):
        result = None
        if "stems" not in self.lexicon[lemma]:
            raise KeyError(lemma)
        for k, v in self.lexicon[lemma]["stems"].items():
            if "/" in k:
                k, context_to_match = k.split("/")
                if not re.match(context_to_match, context):
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
            }[k]
            if re.match(regex, parse):
                result = v
        for k, v in self.lexicon[lemma].get("stem_overrides", []):
            if re.match(k, parse):
                result = v
        return result

    def generate(self, lemma, parse, allow_form_override=True, context=None):
        answers = []
        stems = None
        accent_override = None
        is_enclitic = False
        ending_override = None

        if lemma in self.lexicon:
            if allow_form_override:
                answer = self.lexicon[lemma].get("forms", {}).get(parse)
                if answer:
                    return answer

            stems = self.regex_list(lemma, parse, context)

            if "." in parse:
                accents = self.lexicon[lemma].get("accents", {}).get(parse.split(".")[0])
                if accents == "enclitic":
                    is_enclitic = True
                else:
                    accent_override = accents

            ending_override = self.lexicon[lemma].get("endings", {}).get(parse)

        if stems is None:
            return
        else:
            stems = stems.split("/")

        if parse not in stemming_rules:
            return

        for stem in stems:
            stem = phon_pre(stem)[0]  # @@@
            pairs = stemming_rules[parse]
            while isinstance(pairs, dict) and "ref" in pairs:
                if pairs["ref"] in stemming_rules:
                    pairs = stemming_rules[pairs["ref"]]
                else:
                    # @@@ raise error?
                    return
            base_endings = []
            default = []
            for rule in pairs:
                s1, s234, s5 = rule.split("|")
                s2, s34 = s234.split(">")
                s3, s4 = s34.split("<")

                if stem.endswith(strip_accents(s1 + s2)):
                    if s2:
                        base = stem[:-len(s2)]
                    else:
                        base = stem
                else:
                    continue

                if ending_override:
                    ending_list = ending_override.split("/")
                else:
                    ending_list = [s3 + s5]

                if s1 + s2:
                    base_endings.append((base, ending_list))
                else:
                    default.append((base, ending_list))

            # only use default if there are no other options
            if len(base_endings) == 0 and len(default) > 0:
                base_endings = default

            for base, ending_list in base_endings:
                for ending in ending_list:
                    if accent(ending):
                        for word in phon_pre(base + ending):
                            answers.extend(
                                phon_post(word.replace("|", "")))
                    elif is_enclitic:
                        for word in phon_pre(base + ending):
                            answers.extend(
                                phon_post(make_oxytone(word).replace("|", "")))
                    else:
                        # print(base, ending)

                        if parse[2] == "P":
                            if accent_override:
                                for word in phon_pre(base + ending):
                                    answers.extend(
                                        phon_post(persistent(word, accent_override)))
                            elif parse == "AAP.NSM" and ending == "ων":
                                for word in phon_pre(base + ending):
                                    answers.extend(
                                        phon_post(make_oxytone(word).replace("|", "")))
                            elif parse == "AAP.NSM" and ending == "_3+ς":
                                for word in phon_pre(base + ending):
                                    answers.extend(
                                        phon_post(make_oxytone(word).replace("|", "")))
                            elif parse == "PAP.NSM" and ending == "_3+ς":
                                for word in phon_pre(base + ending):
                                    answers.extend(
                                        phon_post(make_oxytone(word).replace("|", "")))
                            elif parse[0:3] == "AAP" and parse != "AAP.NSM":
                                # calculate NSM
                                nsms = self.generate(lemma, "AAP.NSM").split("/")
                                for nsm in nsms:
                                    if nsm.endswith(("ών", "ούς")):
                                        for word in phon_pre(base + ending):
                                            answers.extend(
                                                phon_post(persistent(word, nsm)))
                                    else:
                                        for word in phon_pre(base + ending):
                                            answers.extend(
                                                phon_post(persistent(word, lemma)))
                            elif parse[0:3] == "PAP" and parse != "PAP.NSM":
                                # calculate NSM
                                nsms = self.generate(lemma, "PAP.NSM").split("/")
                                for nsm in nsms:
                                    nsm = strip_length(nsm)
                                    for word in phon_pre(base + ending):
                                        answers.extend(
                                            phon_post(persistent(word, nsm)))
                            else:
                                for word in phon_pre(base + ending):
                                    answers.extend(
                                        phon_post(recessive(word, default_short=True)))
                        elif parse[0:3] in ["AAN", "XAN", "XMN", "XPN"]:
                            for word in phon_pre(base + ending):
                                answers.extend(
                                    phon_post(on_penult(word, default_short=True)))
                        elif parse[0:3] == "PAN" and stem.endswith("!"):
                            for word in phon_pre(base + ending):
                                answers.extend(
                                    phon_post(on_penult(word, default_short=True)))
                        else:
                            for word in phon_pre(base + ending):
                                answers.extend(
                                    phon_post(recessive(word, default_short=True)))

        return "/".join(remove_duplicates(answers))
