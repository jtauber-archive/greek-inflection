from syllabify import add_necessary_breathing
from characters import strip_accents, remove_redundant_macron


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

    words = rep(words, "ο_1", ["ω"])
    words = rep(words, "ε_1", ["η"])
    words = rep(words, "α_1", ["η"])

    words = rep(words, "υ_1", ["ῡ"])

    words = rep(words, "εἰ_1", ["εἰ"])
    words = rep(words, "ει_1", ["ει"])

    words = rep(words, "ο_2", ["ου"])
    words = rep(words, "ε_2", ["ει"])
    words = rep(words, "ἑ_2", ["εἱ"])
    words = rep(words, "α_2", ["η"])

    words = rep(words, "υ_2", ["ῡ"])

    words = rep(words, "α_3", ["ᾱ"])
    words = rep(words, "ο_3", ["ου"])
    words = rep(words, "ε_3", ["ει"])
    words = rep(words, "ἑ_3", ["εἱ"])

    words = rep(words, "υ_3", ["ῡ"])
    words = rep(words, "ῡ_3", ["ῡ"])

    return words


def phon_post(word):

    words = [word]

    words = rep(words, "α+σο", ["ω"])
    words = rep(words, "ε+σο", ["ου"])
    words = rep(words, "ο+σο", ["ου"])

    words = rep(words, "ε+σαι", ["ῃ", "ει"])

    ##

    words = rep(words, "ά+ε+ε", ["ᾶ"])
    words = rep(words, "έ+ε+ε", ["εῖ"])
    words = rep(words, "ό+ε+ε", ["οῦ"])
    words = rep(words, "ή+ε+ε", ["ῆ"])

    words = rep(words, "έ+ω", ["ῶ"])
    words = rep(words, "έ+ῃ", ["ῇ"])

    words = rep(words, "έ+ει", ["εῖ"])
    words = rep(words, "έ+ε", ["εῖ"])
    words = rep(words, "ε+ε", ["ει"])

    words = rep(words, "έ+ου", ["οῦ"])
    words = rep(words, "ε+ού", ["ού"])
    words = rep(words, "ε+ου", ["ου"])
    words = rep(words, "έ+ο", ["οῦ"])
    words = rep(words, "ε+ό", ["ού"])
    words = rep(words, "ε+ο", ["ου"])

    words = rep(words, "ά+ω", ["ῶ"])
    words = rep(words, "α+ώ", ["ώ"])
    words = rep(words, "ά+ῃ", ["ᾷ"])

    words = rep(words, "ά+ει", ["ᾷ"])
    words = rep(words, "ά+ε", ["ᾶ"])
    words = rep(words, "α+ε", ["ᾱ"])

    words = rep(words, "ά+ου", ["ῶ"])
    words = rep(words, "α+ού", ["ώ"])
    words = rep(words, "α+ου", ["ω"])
    words = rep(words, "ά+ο", ["ῶ"])
    words = rep(words, "ᾶ+ο", ["ῶ"])
    words = rep(words, "α+ό", ["ώ"])
    words = rep(words, "α+ο", ["ω"])

    words = rep(words, "ά+α", ["ᾶ"])

    words = rep(words, "ό+ω", ["ῶ"])
    words = rep(words, "ό+ῃ", ["οῖ"])

    words = rep(words, "ό+ει", ["οῖ"])
    words = rep(words, "ό+ε", ["οῦ"])
    words = rep(words, "ο+έ", ["ού"])
    words = rep(words, "ο+ε", ["ου"])

    words = rep(words, "ό+ου", ["οῦ"])
    words = rep(words, "ο+ού", ["ού"])
    words = rep(words, "ο+ου", ["ου"])
    words = rep(words, "ό+ο", ["οῦ"])
    words = rep(words, "ο+ό", ["ού"])
    words = rep(words, "ο+ο", ["ου"])

    words = rep(words, "ή+ω", ["ῶ"])
    words = rep(words, "η+ω", ["ω"])
    words = rep(words, "ή+ου", ["ῶ"])
    words = rep(words, "η+ου", ["ω"])
    words = rep(words, "ῆ+ο", ["ῶ"])
    words = rep(words, "ή+ο", ["ῶ"])
    words = rep(words, "η+ό", ["ώ"])
    words = rep(words, "η+ο", ["ω"])

    words = rep(words, "ή+ει", ["ῇ"])
    words = rep(words, "η+ει", ["ῃ"])
    words = rep(words, "ή+ε", ["ῆ"])
    words = rep(words, "η+ε", ["η"])
    words = rep(words, "η+ῃ", ["ῃ"])

    ##

    words = rep(words, "μπ+μ", ["μμ"])

    words = rep(words, "π+μ", ["μμ"])
    words = rep(words, "β+μ", ["μμ"])
    words = rep(words, "φ+μ", ["μμ"])
    words = rep(words, "ν+μ", ["μμ"])  # @@@
    words = rep(words, "π+τ", ["πτ"])
    words = rep(words, "β+τ", ["πτ"])
    words = rep(words, "φ+τ", ["πτ"])
    words = rep(words, "πσθ", ["φθ"])
    words = rep(words, "βσθ", ["φθ"])
    words = rep(words, "πσ", ["ψ"])
    # @@@ other bilabials

    words = rep(words, "θ+μ", ["σμ"])
    words = rep(words, "θσ", ["σ"])
    words = rep(words, "θ+τ", ["στ"])
    # words = rep(words, "σσθ", ["σθ"])
    # @@@ other dentals

    words = rep(words, "κ+μ", ["γμ"])
    words = rep(words, "χ+μ", ["γμ"])
    words = rep(words, "χσθ", ["χθ"])
    words = rep(words, "γσθ", ["χθ"])
    words = rep(words, "κσθ", ["χθ"])
    words = rep(words, "χσ", ["ξ"])
    words = rep(words, "χ+τ", ["κτ"])
    # @@@ other velars

    ##

    words = rep(words, "δσθ", ["σθ"])
    words = rep(words, "σσθ", ["σθ"])  # @@@

    ##

    words = rep(words, "#ει", ["εῖ"], True)
    words = rep(words, "#ε", ["εῖ"], True)
    words = rep(words, "#ου", ["οῦ"], True)
    words = rep(words, "#ο", ["οῦ"], True)
    words = rep(words, "#ω", ["ῶ"], True)

    ##

    words = rep(words, "αᾱ", ["ᾱ"])
    words = rep(words, "άᾱ", ["ᾶ"])

    ##

    words = rep(words, "+", [""])

    words = [add_necessary_breathing(w) for w in words]
    words = [remove_redundant_macron(w) for w in words]

    return words
