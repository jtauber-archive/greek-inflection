import re

from characters import accent, strip_length
from characters import strip_accents, remove_redundant_macron
from accentuation import recessive, persistent, on_penult, make_oxytone
# from syllabify import add_necessary_breathing

import yaml

from utils import remove_duplicates


with open("stemming.yaml") as f:
    stemming_rules = yaml.load(f)


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


class Base:

    def regex_list(self, lemma, parse, context):
        result = None
        if "stems" not in self.lexicon[lemma]:
            raise KeyError(lemma)
        for k, v in self.lexicon[lemma]["stems"].items():
            if "/" in k:
                k, context_to_match = k.split("/")
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
            }[k]
            if re.match(regex, parse):
                result = v
        for k, v in self.lexicon[lemma].get("stem_overrides", []):
            if re.match(k, parse):
                result = v
        return result


class Lexicon(Base):

    def __init__(self, lexicon):
        with open(lexicon) as f:
            self.lexicon = yaml.load(f)

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
            stem = debreath(stem)
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
                        answers.append((base + ending).replace("|", ""))
                    elif is_enclitic:
                        answers.append(make_oxytone(base + ending).replace("|", ""))
                    else:
                        if parse[2] == "P":
                            if accent_override:
                                answers.append(persistent(base + ending, accent_override))
                            elif parse == "AAP.NSM" and ending == "ων":
                                answers.append(make_oxytone(base + ending).replace("|", ""))
                            elif parse == "AAP.NSM" and ending == "_3+ς":
                                answers.append(make_oxytone(base + ending).replace("|", ""))
                            elif parse == "PAP.NSM" and ending == "_3+ς":
                                answers.append(make_oxytone(base + ending).replace("|", ""))
                            elif parse[0:3] == "AAP" and parse != "AAP.NSM":
                                # calculate NSM
                                nsms = self.generate(lemma, "AAP.NSM", context=context)
                                nsms = nsms.split("/")
                                for nsm in nsms:
                                    if nsm.endswith(("ών", "ούς")):
                                        answers.append(persistent(base + ending, nsm))
                                    else:
                                        answers.append(persistent(base + ending, lemma))
                            elif parse[0:3] == "PAP" and parse != "PAP.NSM":
                                # calculate NSM
                                nsms = self.generate(lemma, "PAP.NSM").split("/")
                                for nsm in nsms:
                                    nsm = strip_length(nsm)
                                    answers.append(persistent(base + ending, nsm))
                            else:
                                answers.append(recessive(base + ending, default_short=True))
                        elif parse[0:3] in ["AAN", "XAN", "XMN", "XPN"]:
                            answers.append(on_penult(base + ending, default_short=True))
                        elif parse[0:3] == "PAN" and stem.endswith("!"):
                            answers.append(on_penult(base + ending, default_short=True))
                        else:
                            answers.append(recessive(base + ending, default_short=True))

        return "/".join([rebreath(w) for w in remove_duplicates(answers)])
