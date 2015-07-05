import re

from characters import accent, strip_length
from accentuation import recessive, persistent, on_penult, make_oxytone

import yaml

from phonology import phon_pre, phon_post
from utils import remove_duplicates


with open("rules.yaml") as f:
    rules = yaml.load(f)

with open("endings.yaml") as f:
    endings = yaml.load(f)


class Lexicon:

    def __init__(self, lexicon):
        self.lexicon = {}

        with open(lexicon) as f:
            self.lexicon.update(yaml.load(f))

    def regex_list(self, lemma, parse):
        result = None
        if "stems" not in self.lexicon[lemma]:
            raise KeyError(lemma)
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

    def generate(self, lemma, parse, allow_form_override=True):
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

            stems = self.regex_list(lemma, parse)

            if "." in parse:
                accents = self.lexicon[lemma].get("accents", {}).get(parse.split(".")[0])
                if accents == "enclitic":
                    is_enclitic = True
                else:
                    accent_override = accents

            ending_override = self.lexicon[lemma].get("endings", {}).get(parse)

        if stems is None:
            stems = self.stems_from_parts.stems(lemma, parse)
        else:
            stems = stems.split("/")

        if stems is None:
            return

        if "." in parse:
            tvm, pn = parse.split(".")
        else:
            tvm = parse
            pn = None

        if tvm not in rules:
            return

        for stem in stems:
            for rule in rules[tvm]:
                steps = rule.split(" + ")

                if steps[0].startswith("stem"):
                    ending_set = steps[1]

                if steps[0] == "stem":
                    base = stem
                elif steps[0].startswith("stem/"):
                    regex = steps[0].split("/")[1]
                    m = re.match(regex, stem)
                    if m:
                        base = m.group(1)
                    else:
                        continue
                else:
                    continue

                if ending_override:
                    ending_list = ending_override.split("/")
                else:
                    if pn:
                        if pn not in endings[ending_set]:
                            return
                        ending_list = endings[ending_set][pn].split("/")
                    else:
                        ending_list = endings[ending_set].split("/")

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
                        if tvm[2] == "P":
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
                            elif tvm == "AAP" and parse != "AAP.NSM":
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
                            elif tvm == "PAP" and parse != "PAP.NSM":
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
                        elif tvm in ["AAN", "XAN", "XMN", "XPN"]:
                            for word in phon_pre(base + ending):
                                answers.extend(
                                    phon_post(on_penult(word, default_short=True)))
                        elif tvm == "PAN" and stem.endswith("!"):
                            for word in phon_pre(base + ending):
                                answers.extend(
                                    phon_post(on_penult(word, default_short=True)))
                        else:
                            for word in phon_pre(base + ending):
                                answers.extend(
                                    phon_post(recessive(word, default_short=True)))

        return "/".join(remove_duplicates(answers))
