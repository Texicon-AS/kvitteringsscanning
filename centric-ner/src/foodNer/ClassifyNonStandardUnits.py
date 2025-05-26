#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position,bad-indentation
"""
@file
@brief uses regular expressions to detect patterns in the text
@remarks a permeation of the below is included into our "ClassifyProduct.py"
"""
import re
import traceback
from typing import ClassVar
from typing import List  # , Dict
from typing import Tuple
from dataclasses import dataclass, field
import spacy
from spacy.language import Language  #! needd when using "mypy"
from spacy.matcher import Matcher
from typeguard import typechecked
from spacy.tokens import Doc
from spacy.util import filter_spans
import json

#! Local files:
from foodNer.PredictedProduct import PredictedProduct


@Language.component("insert_space_after_abbrev")
def insert_space_after_abbrev(doc):
    text = doc.text
    # Period "Hvetem.1kg" -> "Hvetem. 1kg".
    text = re.sub(r"([A-Za-z]+\.)(\d)", r"\1 \2", text)
    # Comma "Hvetemel,1kg" -> Hvetemel, 1kg
    text = re.sub(r"(?<=[A-Za-z]),(?=\d)", " ", text)
    return Doc(doc.vocab, words=text.split())


@Language.component("insert_space_between_word_and_measure")
def insert_space_between_word_and_measure(doc):
    # "Granola Jordbær400g Axa" -> "Granola Jordbær 400g Axa"
    # Except: Multiplikator x eller pk, keep: "0,5lx6", "10pk320g"
    fixed_text = re.sub(
        r"(?<![xX×])(?<![pP][kK])(?<=[A-Za-zÆØÅæøå])(?=\d)", " ", doc.text
    )
    return Doc(doc.vocab, words=fixed_text.split())


@Language.component("remove_percentage_info")
def remove_percentage_info(doc):
    # "Tine melk 4,5% 1l" -> "Tine melk 1l"
    cleaned_text = re.sub(r"\d+(?:[.,]\d+)?\s*%", "", doc.text)
    return Doc(doc.vocab, words=cleaned_text.split())


@Language.component("split_compound_tokens")
def split_compound_tokens(doc):
    # Complex compounds "70gx6stk" -> ["70", "g", "x", "6", "stk"]
    pattern = re.compile(
        r"^(?P<num1>\d+(?:[.,]\d+)?)(?P<unit1>[A-Za-z]+)(?P<op>[xX×])(?P<num2>\d+(?:[.,]\d+)?)(?P<unit2>[A-Za-z]+)$"
    )
    new_words = []
    for token in doc:
        m = pattern.match(token.text)
        if m:
            new_words.extend(
                [
                    m.group("num1"),
                    m.group("unit1"),
                    m.group("op"),
                    m.group("num2"),
                    m.group("unit2"),
                ]
            )
        else:
            new_words.append(token.text)
    return Doc(doc.vocab, words=new_words)


PACKAGE_VOCAB_TERMS = [
    "stk",
    "stykk",
    "st",
    "bit",
    "pk",
    "bx",
    "pakke",
    "pakker",
    "pkn",
    "pck",
    "pack",
    "packs",
    "pos",
    "poser",
    "bg",
    "kapsel",
    "kapsler",
    "fl",
    "flaske",
    "flasker",
]


@typechecked
@dataclass
class ClassifyQuantityAndUnit:
    """
    @brief a partially abstract class for identifying the volume/quantity and metric (which describes the 'quantity')
    """

    NerLabelProductQuantAndUnit: ClassVar[str] = "productQuantAndUnit-merged"
    nlp: Language = field(default_factory=lambda: spacy.load("en_core_web_lg"))

    def predict(self, productString: str) -> Tuple[str, str]:
        raise NotImplementedError()

    @property
    def unitVocabTerms(self) -> List[str]:
        return PredictedProduct.unitVocabTerms

    @staticmethod
    def normalizeProduct(
        productString: str, productAndUnit: str, unitTerm: str
    ) -> Tuple[str, str]:
        """
        @brief Extract the quantity-value and the unit/metric
        @return the (quantityValue, unit) tuple
        """
        # FIXME: get the below out-commented example to work ... then write the below steps: <-- when is this complexity needed?
        # with doc.retokenize() as retokenizer:
        #   heads = [(doc[3], 1), doc[2]]
        #   retokenizer.split(doc[4], ["OnePlus", "7"],heads=heads)

        try:
            productAndUnit = productAndUnit.strip()

            # "5-pk", "3 pack"
            simple_pkg_pattern = re.compile(
                r"^\s*(?P<multiplier>\d+(?:[.,]\d+)?)\s*[-]?\s*(?P<unit>"
                + "|".join(PACKAGE_VOCAB_TERMS)
                + r")\s*$",
                re.IGNORECASE,
            )
            m_simple = simple_pkg_pattern.match(productAndUnit)
            if m_simple:
                quantityValue = m_simple.group("multiplier").replace(",", ".")
                unit = m_simple.group("unit")
                return quantityValue, unit

            # Multiply
            if re.search(r"(x|pk)", productAndUnit, re.IGNORECASE):

                pattern = re.compile(
                    r"^(?P<multiplier>\d+(?:[.,]\d+)?)(?P<operator>(?i:pk)|[xX×])\s*(?P<value>\d+(?:[.,]\d+)?)(?P<unit>[A-Za-z]+)$"
                )
                pattern_reversed = re.compile(
                    r"^(?P<value>\d+(?:[.,]\d+)?)(?P<unit>[A-Za-z]+)[xX×](?P<multiplier>\d+)$"
                )
                m_normal = pattern.match(productAndUnit)
                m_reversed = pattern_reversed.match(productAndUnit)
                if m_normal or m_reversed:
                    m = m_normal if m_normal else m_reversed
                    multiplier_value = float(m.group("multiplier").replace(",", "."))
                    per_unit_value = float(m.group("value").replace(",", "."))
                    unit_found = m.group("unit")
                    total_value = multiplier_value * per_unit_value
                    quantityValue = (
                        str(int(total_value))
                        if total_value.is_integer()
                        else str(round(total_value, 2))
                    )
                    return quantityValue, unit_found

            standard_pattern = re.compile(
                r"^((?:\d+(?:[.,]\d+)?|\d+/\d+))[ ]*(?i:"
                + re.escape(unitTerm)
                + r")[ ]*,?$"
            )
            m_std = standard_pattern.match(productAndUnit)
            if m_std:
                quantity_str = m_std.group(1)
                # Fractions "Melk 1/4l"
                if "/" in quantity_str:
                    try:
                        num, denom = quantity_str.split("/")
                        quantity_value = float(num) / float(denom)
                        quantity_str = str(quantity_value)
                    except Exception as e:
                        quantity_str = quantity_str
                else:
                    quantity_str = quantity_str.replace(",", ".")
                return quantity_str, unitTerm

            return "", ""

        except Exception as e:
            print(f"Error normalizing product '{productString}': {e}")
            return "", ""


@typechecked
@dataclass
class ClassifyNonStandardUnits(ClassifyQuantityAndUnit):
    """
    @brief handle non-starndard/efualt units (eg, "l" and "ml")
    @remarks
    @TODO figure out if there are better strateiges for hadnling ases which is not resovled/suppoprted by the standard spacy-appraoch
    """

    def __post_init__(self) -> None:
        super().__init__()
        allUnits = self.unitVocabTerms + PACKAGE_VOCAB_TERMS

        strRegexUnitVocab = "(" + "|".join(allUnits) + ")"

        unit_priority = {}
        for idx, term in enumerate(self.unitVocabTerms):
            unit_priority[term.lower()] = idx
        for idx, term in enumerate(PACKAGE_VOCAB_TERMS):
            unit_priority[term.lower()] = 100 + idx
        self.unit_priority = unit_priority

        self.nlp.add_pipe("insert_space_after_abbrev", first=True)
        self.nlp.add_pipe("insert_space_between_word_and_measure", first=True)
        self.nlp.add_pipe("remove_percentage_info", first=True)
        self.nlp.add_pipe("split_compound_tokens", first=True)

        patternQuantityUnitCase1: List[dict] = [
            {"LIKE_NUM": True},
            {
                "TEXT": {"REGEX": "^(?i:" + strRegexUnitVocab + r")[,\.]?$"},
                "OP": "+",
            },
        ]

        patternQuantityUnitCase2: List[dict] = [
            {
                "TEXT": {
                    "REGEX": r"^((?:\d+(?:[.,]\d+)?|\d+/\d+))(?i:"
                    + strRegexUnitVocab
                    + ")$"
                },
                "OP": "+",
            },
        ]

        # Multiplier single token  "2x133g"
        patternMultiplierSingleToken: List[dict] = [
            {"TEXT": {"REGEX": r"^\d+[xX×]\d+(?:[.,]\d+)?[A-Za-z]+$"}}
        ]

        # Multiplier two tokens ["2x133", "g"]
        patternMultiplierTwoTokens: List[dict] = [
            {"TEXT": {"REGEX": r"^\d+[xX×]\d+(?:[.,]\d+)?$"}},
            {"TEXT": {"REGEX": r"^(?i:" + strRegexUnitVocab + ")$"}},
        ]
        # Reversed multiplier "1,5lx4"
        patternMultiplierReversedSingleToken: List[dict] = [
            {"TEXT": {"REGEX": r"^\d+(?:[.,]\d+)?[A-Za-z]+[xX×]\d+$"}}
        ]
        # Reversed two tokens ["1,5l", "4"]
        patternMultiplierReversedTwoTokens: List[dict] = [
            {"TEXT": {"REGEX": r"^\d+(?:[.,]\d+)?(?![xX×])[A-Za-z]+$"}},
            {"TEXT": {"REGEX": r"^\d+$"}},
        ]
        # "50-pk"
        pattern_pkg = [
            {"TEXT": {"REGEX": r"^\d+(?:[.,]\d+)?$"}},  # number "50"
            {"TEXT": {"REGEX": r"^[-]$"}},  # hyphen "-"
            {"TEXT": {"REGEX": r"^(?i:" + strRegexUnitVocab + ")$"}},  # "pk"
        ]

        self.__matcher = Matcher(self.nlp.vocab, validate=True)
        self.__matcher.add("simplePackage", [pattern_pkg])
        self.__matcher.add("multiplierSingleToken", [patternMultiplierSingleToken])
        self.__matcher.add("multiplierTwoTokens", [patternMultiplierTwoTokens])
        self.__matcher.add(
            "multiplierReversedTwoTokens", [patternMultiplierReversedTwoTokens]
        )
        self.__matcher.add(
            "multiplierReversedSingleToken", [patternMultiplierReversedSingleToken]
        )
        self.__matcher.add("productQuantAndUnit", [patternQuantityUnitCase1])
        self.__matcher.add(self.NerLabelProductQuantAndUnit, [patternQuantityUnitCase2])

    def predict(self, productString: str) -> Tuple[str, str]:
        """
        @brief
        @return
        """

        doc = self.nlp(productString)
        matches = self.__matcher(doc)
        candidates = []

        for matchId, start, end in matches:
            span = doc[start:end]
            label = self.nlp.vocab.strings[matchId]
            span_text = span.text

            for unitTerm in self.unitVocabTerms + PACKAGE_VOCAB_TERMS:
                if unitTerm.lower() in span_text.lower():
                    if label == "multiplierTwoTokens":
                        combined = "".join(token.text for token in doc[start:end])
                        q, u = self.normalizeProduct(productString, combined, unitTerm)
                    else:
                        q, u = self.normalizeProduct(productString, span_text, unitTerm)
                    if q and u:
                        candidate_priority = (
                            start
                            + len(span_text)
                            + self.unit_priority.get(u.lower(), 0)
                        )
                        candidates.append(
                            {
                                "quantity": q,
                                "unit": u,
                                "span_text": span_text,
                                "label": label,
                                "priority": candidate_priority,
                            }
                        )

        if candidates:
            sorted_candidates = sorted(
                candidates, key=lambda c: c["priority"], reverse=True
            )
            best = sorted_candidates[0]
            # Package are prioritized, but if package=1 then use unit ??
            # "Brun saus 3pk 330g" -> "3pk"
            # "Brun saus 1pk 330g" -> "330g"
            if float(best["quantity"]) == 1 and len(sorted_candidates) > 1:
                best = sorted_candidates[1]
            return best["quantity"], best["unit"]

        else:
            return "", ""

    def areSimilar(self, text1: str, text2: str) -> bool:
        """
        @brief
        @return
        """
        assert False  # FIXME: adjust the below example <-- pre: get sample-data to idneify the thresholds for this <-- move this funciton to "ClassifyEntry.py"? <-- what use-case can this code-template be applied/used for?
        cmp1 = self.nlp(text1)
        cmp2 = self.nlp(text2)
        simScore = cmp1.similarity(cmp2)
        threshold: float = 1.7  # FIXME: adjust this!
        return simScore > threshold


if __name__ == "__main__":
    """
    @brief caldiates the logics in this module
    """
    nlp = spacy.load("en_core_web_sm")
    classify = ClassifyNonStandardUnits(nlp)

    texts = [
        #! Below: patterns we have earlier found challeingg to idnietyf:
        "Vaniljeis 3l First Price",  # FIXME: validate that a different class handles this!
        "Explo Mango Passion Sukkerfri 0,5l boks Mack",
        "Xtra mack 0,5l boks",
        "Xtra mack 0,5 l boks",
        "Hansa Øl 1 l",
        "Hansa Øl 1l",
        "Idyll Sjokoladeis Plantebasert 500ml Hennig-Olsen",
        "Idyll Sjokoladeis Plantebasert 500 ml Hennig-Olsen",
        "Royal Is Sjokolade 0.9l Diplom-Is",  #! which exemplfiues a case where "." is used instead of a "," decimal-sperator
        "Gilde Ovnsbakt Leverpostei med Bacon 180g",
        "Chickpeas in brine",
        "Stabburet Firkantpizza Kebab 12x690g",
        "Proteinfabrikken Flytende Eggehvite 1000ml",
    ]
    print("TEST 1 (Should have quantity and unit):")
    for text in texts:
        try:
            (quantityValue, unit) = classify.predict(text)
            assert quantityValue != ""
            assert unit != ""
            print(f"✅ '{text}' => '{quantityValue} {unit}'")
        except Exception as e:
            print(f"🛑 '{text}' failed, quantity:'{quantityValue}', unit:'{unit}'")

    # #! Validate robustness of our approach:
    textsWithoutQuant = [
        "Chickpeas in brine",
        "Cut chicken filet",
        "Big 100 Cookie Dough",
        "Store Tortillalefser",
        "Gilde Ovnsbakt Leverpostei med Bacon 180g",
    ]
    print("TEST 2 (Should NOT have quantity or unit):")
    for text in textsWithoutQuant:
        try:
            (quantityValue, unit) = classify.predict(text)
            assert quantityValue == ""  #! as an eception was NTO raied
            assert unit == ""  #! as an eception was NTO raied
            print(f"✅ '{text}' => '{quantityValue},{unit}'")
        except Exception as e:
            print(f"🛑 '{text}' failed, quantity:'{quantityValue}', unit:'{unit}'")

    print("TEST 3:")
    json_file_path = "../sample_data/kassalappen/filtered_foods_with_weights.json"
    # json_file_path = "../sample_data/product_FoodManager.json"
    with open(json_file_path, "r", encoding="utf-8") as file:
        products = json.load(file)

    tests = 0
    correct = 0
    incorrect = 0

    for product in products[0:1000]:
        product_name = product.get("name", "")
        if re.search(r"\d", product_name) is None:
            continue

        tests += 1
        quantity, unit = classify.predict(product_name)

        if quantity and unit:
            # print(f"✅ '{product_name}' => '{quantity}{unit}'")
            correct += 1
        else:
            incorrect += 1
            print(
                f"🛑 {tests} Test failed for product: '{product_name}'. Returned quantity: '{quantity}', unit: '{unit}'"
            )
    print(f"Tested: {tests}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {incorrect}")
    print(f"Percentage: {correct / tests * 100}%")
