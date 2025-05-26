#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position,superfluous-parens,bad-indentation
"""
@file
@brief
@remarks
- API: https://spacy.io/usage/rule-based-matching
- challgen: the below basic Spacy-use examplies/udnelrines that basic NER-matching does not work, thus, need for grammar and/or AI-training.
- usage: a permtaution of the belwo is included into our "ClassifyProduct.py"
@remarks compilation
- beofre running this scirp the first time, run the "x-installer.bash" (found in the root of this project)
"""
import pathlib
import os
import json
import traceback
from typing import List, Union, Tuple, Any, cast
import dataclasses
from dataclasses import dataclass, field
from typeguard import typechecked
import spacy
from spacy import displacy
from spacy.language import Language  #! needd when using "mypy"

# from spacy.matcher import Matcher

#! Local files:
from stopWords.StopWordRemoval import StopWordRemoval
from loadData.LoadData import LoadData
from loadData.LoadData import ProductAndQuantity
from foodNer.PredictedProduct import PredictedProduct
from foodNer.ClassifyNonStandardUnits import ClassifyNonStandardUnits
from foodNer.ShapeUnitClassification import ShapeUnitClassification
from foodNer.ProductAmount import ProductAmount, ProductUnit
from foodNer.MatchedEntry import MatchedEntry, MatchedEntryArr, MatchedLabel


@typechecked
@dataclass
class ClassifyEntry:
    """
    @brief
    @remarks
    - @TODO to make the below classifciaont mroe acucarte, then train consturct a new "nlp" based on a traiend data-set
    """

    nlp: Language = field(default_factory=lambda: spacy.load("en_core_web_lg"))

    # stopRemoval : StopWordRemoval = field(default_factory = lambda :  StopWordRemoval())
    # nlpProductSpecific = spacy.load("en_core_web_lg")
    def __post_init__(self) -> None:
        self.__classifyNonStandardUnits = ClassifyNonStandardUnits(self.nlp)
        self.__classifyProductsByShape = ShapeUnitClassification(self.nlp)
        # print("type(nlp)=", type(self.nlp))
        # self.nlpProductSpecific.add_pipe("merge_noun_chunks") # TODO: this seems to areldy exist ...
        # Merge noun phrases and entities for easier analysis
        # FIXME: how does the "spacy" pipes work? what is the point (of the pipes)? how do they changE=improve the predictins? <-- a nested filter?
        # nlp.add_pipe("merge_entities")
        # arr_patterns = []
        # pattern = [
        #     {"LOWER": "databases"}, {"LEMMA": "be"}, {"POS": "ADV", "OP": "*"}, {"POS": "ADJ"}
        # ]
        # arr_patterns.append(pattern)

    @staticmethod
    def normalizeQuantityAndUnit(quantity: str) -> Tuple[str, float]:
        """
        @brief
        @return a tuple of (quantity, quantityValue)
        """
        if quantity == "":
            return ("", -1.0)
        quantity: str = quantity.replace(",", ".")  # type: ignore[no-redef]  #! ie, to handel Nowegian comma-zeperators <-- FIXME: attach ifnroation of language to avodi this causing erros for enclish (where "," is used as thousand-speerator).
        try:
            quantityValue = float(quantity)
            return (quantity, quantityValue)
        except ValueError as e:
            print(
                f"!!\t[ClassifyEntry.py]\t Unable to convert value:'{quantity}' to a float; as a first step, validate that the value was seperated from the unit/metric: "
                + str(e)
            )
            # raise e
            quantity = ""  #! as it was not correctly extracted
            return ("", -1)

    def __findProductTypeSpecific(self, productString: str) -> str:
        """
        @brief finds the "ROOT" of a sentence https://spacy.io/usage/linguistic-features a.k.a the most important word in the sentence where rest of the sentence is built upon.
        @return
        """
        # FIXME: update the bleow ... use a mdoel trained on our data (eg, from "Matvaretabellen")?
        # docProductSpecific = self.nlpProductSpecific(productString)
        docProductSpecific = self.nlp(productString)
        for token in docProductSpecific:
            print("token: ", token, token.dep_)
            if token.dep_ == "ROOT":
                productTypeSpecific = token.text  #! eg, "hamburgerrygg"
        try:
            return productTypeSpecific
        except:
            return (
                ""  # TODO: thow warning if the productTypeSpecific value was NOT found?
            )

    def __debugString(self, productString: str) -> None:
        """
        @brief
        @return
        """
        doc = self.nlp(productString)
        print(
            "lemma; ", [token.lemma_ for token in doc]
        )  #! eg, ['Mills', 'Peanut', 'Butter', '350', 'g']
        if True:
            # FIXME: what does the below describe?
            for (
                np
            ) in (
                doc.noun_chunks
            ):  #! [https://stackoverflow.com/questions/36698769/chunking-with-rule-based-grammar-in-spacy?rq=1]
                print(np.text)
            # for ent in nlp(text).ents:
            # print(ent.label_, ent, sep="\t")
        if True:
            svg = displacy.render(doc, style="dep")
            # pathToResultImage = pathlib.Path(os.path.join("./", "sentence.svg"))
            pathToResultImage = pathlib.Path(os.path.join("./", "sentence.png"))
            with open(
                pathToResultImage, "w", encoding="utf-8", newline=""
            ) as imageFile:
                imageFile.write(
                    svg
                )  #! [https://stackoverflow.com/questions/55723812/when-i-save-the-output-of-displacy-renderdoc-style-dep-to-a-svg-file-there]
                # pathToResultImage.open('w', encoding="utf-8").write(svg) #! [https://stackoverflow.com/questions/55723812/when-i-save-the-output-of-displacy-renderdoc-style-dep-to-a-svg-file-there]
        # FIXME: merge this and the below appraoches <-- pre: figure out the best pracise for deubbing these
        if True:
            print("Entities:")
            for index, ent in enumerate(doc.ents):
                print(
                    f"{index}\t {ent.text}, {ent.start_char}, {ent.end_char}, {ent.label_} ({ent});"
                )
            #! Document level
            ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
            print("Entities(text, startChar, endChar, label)=", ents)
            #! At the token-level:
            # token level
            ent_san = [doc[0].text, doc[0].ent_iob_, doc[0].ent_type_]
            ent_francisco = [doc[1].text, doc[1].ent_iob_, doc[1].ent_type_]
            print(ent_san)  # ['San', 'B', 'GPE']
            print(ent_francisco)  # ['Francisco', 'I', 'GPE']
        if False:
            print("\n\n# Word vectors and semantic similarity:")
            for token in doc:
                # fIXME: what is the meanign fo the below "token.vector_norm"?
                print(token.text, token.has_vector, token.vector_norm, token.is_oov)
        # matches = matcher(doc)
        # print("matches=", matches)

    def normalizeInputString(self, productString: str) -> str:
        """
        @return a normalized veriosn of the input-string
        @remarks importna when bulidng the patterns of matches, for whioch we need that the input-text is consistent
        """
        if (
            False
        ):  # FIXME: write a new class responbiel for this ... then get it to work <-- pre: describe a compelte set of thiese rewrite-rukles (thus, to identify the gammar we need for this task)
            assert False  # FIXME: pre: get the below to work
            # with doc.retokenize() as retokenizer:
            #   attrs = {"POS": "PROPN"} # FIXME: adjust this
            #   retokenizer.merge(doc[0:2], attrs=attrs) # FIXME: this uses only ngram=2? ... if yes, possilbe makign this even mroe flexible?
        else:  # FIXME: remove the below when the above scaffold works!
            productString = productString.replace(
                "X-tra", "Xtra"
            )  # FIXME: any databases which gives clues ... to autoamte this ... to audo-add these? <-- a better approach?
        return productString

    def predict(self, productString: str) -> PredictedProduct:
        """
        @brief
        @return
        @remarks
        """
        # print("\n--------------- productString=", productString)
        # lemmatizer = self.nlp.get_pipe("lemmatizer") # FIXME: what is the effect of this? <--.- write TUTs exploing this
        # productString = productString.replace("Uten Sukker", "utenSukker")
        # print("productString=", productString)
        # assert(False)
        productString = self.normalizeInputString(productString)
        try:
            self.__debugString(productString)  # TODO: disable
        except:
            pass  #! ie, as such as enrror is not itnerpreted as critical
        # print(lemmatizer.mode)  # 'rule'

        productType = self.__findProductTypeSpecific(productString)
        productTypeSpecific = productType

        doc = self.nlp(productString)
        arrCompound: List[str] = []  # TODO: figure out how using this
        arrModifierKeys: List[str] = []
        quantity: Union[str, int, float] = ""
        unit: str = ""
        quantityValue = 0.0

        # Bruk kun ClassifyNonStandardUnits til å hente ut mengde og enhet:
        (quantity, unit) = self.__classifyNonStandardUnits.predict(productString)
        (_quantity, _quantityValue) = self.normalizeQuantityAndUnit(str(quantity))
        if _quantity:
            quantityValue = _quantityValue
            quantity = _quantity

        # print("quantity=", quantity, quantityValue)
        # print("unit=", unit)

        for token in doc:
            if token.dep_ == "ROOT":
                productType = token.text
            elif token.dep_ == "nummod":
                unit_candidate = token.head.text
                if quantity == "":
                    quantity = token.text
                else:
                    unit_candidate = token.text
                arrModifierKeys.append(unit_candidate)
            else:
                if token.text not in arrCompound:
                    arrCompound.append(token.text)
                for child in token.children:
                    if child.text not in arrCompound and child.dep_ in [
                        "compound",
                        "ROOT",
                    ]:
                        arrCompound.append(child.text)

        arrCompoundFiltered = []
        for word in arrCompound:
            if word not in arrModifierKeys:
                arrCompoundFiltered.append(word)

                # Fjern den uttrukne enheten fra compound-listen
        arrCompoundFiltered = [
            word for word in arrCompoundFiltered if word.lower() != unit.lower()
        ]

        # print("arrCompoundFiltered=", arrCompoundFiltered)
        # print("productType=", productType)

        # for token in doc:
        #     # print("token: ", token, token.dep_)
        #     # if(token.ent.label_ == "DRV"):
        #     # continue # FIXME: correct <-- added to avoid the ?? "3xl" from being added (given inptu-string: "3xl Grov Ostepølse 180g Stabburet") <-- FIXME: how to correctly handel this ... we should have peromed a "180g * 3" --- are there otehr cases simialr to this?
        #     if token.dep_ == "ROOT":
        #         productType = token.text  #! eg, "hamburgerrygg"
        #     elif (
        #         token.dep_ == "nummod"
        #     ):  #! then the value does NOT feref to a count <-- TODO: autoamte this proceudre ... adding a mapping-table for this <-- how?
        #         # if("xl" in token.head.text):
        #         if (
        #             ("xl" in token.text)
        #             or ("6x1" in token.text)
        #             or ("12x690g" in token.text)
        #         ):  # FIXME: correct <-- added to avoid the ?? "3xl" from being added (given inptu-string: "3xl Grov Ostepølse 180g Stabburet") <-- FIXME: how to correctly handel this ... we should have peromed a "180g * 3" --- are there otehr cases simialr to this?
        #             continue
        #         unit = (
        #             token.head.text
        #         )  # TODO: replace the "unit" with an enum <-- a list of which enusm are valid (ie, the complete unit-set for foods)?
        #         if quantity == "":
        #             quantity = token.text
        #         else:
        #             # print(f"!!\t quantity:{quantity} while valueToSet:{token.text}")
        #             unit = token.text
        #         # print(f"!!\t quantity:{quantity} while unit:{unit}")
        #         arrModifierKeys.append(unit)  #! as this is NOT a compound
        #     else:
        #         # aCompound : bool = (token.text not in arrModifierKeys) # TODO: suggesitons for fhow using this?
        #         # print(f"--- token({token}) w/text={token.text}", token.dep_, aCompound, arrModifierKeys)
        #         # print("; children:")
        #         if token.text not in arrCompound:
        #             arrCompound.append(token.text)
        #         for child in token.children:
        #             # print("\t....", child.dep_, child.text)
        #             pass
        #     # if(token.dep_ in ["ROOT"]):
        #     # if(aCompound):
        #     #    arrCompound.append(token.text)
        #     # print("token.children: ", token.text, token.dep_, token.head.text, token.head.pos_,
        #     # [child for child in token.children])
        #     for child in token.children:
        #         if child.text in arrCompound:
        #             continue  #! as it was already added
        #         if child.dep_ in ["compound", "ROOT"]:
        #             # print(f"{child} is compound to {tok}")
        #             arrCompound.append(child.text)
        #     # else:
        #     # ; # print("\t- (not-a-compound)\t ", child)

        # arrCompoundFiltered: List[str] = []
        # for compound in arrCompound:
        #     if compound in arrModifierKeys:
        #         continue
        #     arrCompoundFiltered.append(compound)
        # print(
        #     "arrCompound=", arrCompoundFiltered
        # )  # TODO: how can this list be used for searching?
        # print("productType=", productType)
        # print("productTypeSpecific=", productTypeSpecific)
        # print("quantity=", quantity)
        # quantityValue = 0.0
        # if quantity != "":
        #     (quantity, quantityValue) = self.normalizeQuantityAndUnit(str(quantity))
        # if quantity == "":
        #     text = productString  # TODO: instead use the subset of componetsn dienfied above?
        #     for productClassif in [
        #         self.__classifyNonStandardUnits,
        #         self.__classifyProductsByShape,
        #     ]:  # TODO: figure otu the best order ... ie, what of these 'extra' classes procusese sthe most prceise answer?
        #         if (quantity != "") and (unit != ""):
        #             continue  #! as we have then found it
        #         (quantity, unit) = productClassif.predict(text)
        #         print(
        #             f"[ClassifyEntry.py::predict::fallback]\t '{text}' => unit:'{unit}' and quantityValue:'{quantity}'"
        #         )
        #         (_quantity, _quantityValue) = self.normalizeQuantityAndUnit(quantity)
        #         if _quantity:
        #             quantityValue = _quantityValue
        #             assert quantityValue > 0  # TODO: correct?
        #             quantity = _quantity

        try:
            unitEnum = ProductUnit.toEnum(unit)
        except ValueError as e:
            print(
                f"!!\t[ClassifyEntry.py]\t Invalid unit({unit}), thus, consider to investigate. Error: ",
                e,
            )
            raise e
        # TODO: validate the below assignment
        if quantity == "":
            quantityValue = -1.0  # TODO: better using "0.0"?
        product = PredictedProduct(
            productString,
            productType,
            productAmount=ProductAmount(quantityValue, unitEnum),
            arrCompound=arrCompoundFiltered,
            productTypeSpecific=productTypeSpecific,
        )  # , self.stopRemoval)
        # if(quantityValue):
        # assert(product.quantityIsKnown()) # TODO: cases where this is not correcT?
        # print("[ClassifyEntry::predict]\t return product=", product)
        return product


@typechecked
@dataclass
class WriteProduct:
    """
    @brief writes a product to a file
    @remarks
    """

    fileNameResult: str
    stopRemoval: StopWordRemoval = field(default_factory=lambda: StopWordRemoval())

    def __post_init__(self) -> None:
        self.fileResult = open(
            self.fileNameResult, "w"
        )  # TODO: how can we use the "with" pattern here?

    def writeProduct(self, product: PredictedProduct) -> None:
        # f.write("Created using write mode.")
        data = dataclasses.asdict(product)
        compundsXmtStopWords = product.getCompounds(
            stopRemoval=self.stopRemoval, useStopWords=True
        )
        data["compundsXmtStopWords"] = compundsXmtStopWords
        # print("data=", data)
        data["productAmount"] = repr(product.productAmount)
        print("data=", data["productAmount"])
        jsonData = json.dumps(data)
        print("jsonData=", jsonData)
        self.fileResult.write(jsonData + "\n")

    def closeFile(self) -> None:
        self.fileResult.close()

    @classmethod
    def unitTest(cls) -> None:
        """
        @brief validate/test challenging patterns
        """
        _ = cls  # tODO: use this
        for data in [
            {
                "productString": "3xl Grov Ostepølse 180g Stabburet",
                "product": "Stabburet",
                "productAmount": {"quanityValue": 180.0, "unit": "g"},
                "arrCompound": ["Grov", "Ostepølse"],
                "productTypeSpecific": "Stabburet",
            },
            {
                "productString": "3xl Grov Ostepølse 180g Stabburet",
                "product": "Stabburet",
                "productAmount": {"quanityValue": 180.0, "unit": "g"},
                "arrCompound": ["Grov", "Ostepølse"],
                "productTypeSpecific": "Stabburet",
            },
        ]:
            jsonData = json.dumps(data)  #! whcih has earlier triggeredbugs
            print("jsonData=", jsonData)


@typechecked
@dataclass
class ClassifyEntryMultiLang:
    """
    @brief
    @remarks
    - @TODO to make the below classifciaont mroe acucarte, then train consturct a new "nlp" based on a traiend data-set
    """

    _productWriter: WriteProduct = field(
        default_factory=lambda: WriteProduct("res-ClassifyEntryMultiLang.txt")
    )
    _arrClassifiers: List[ClassifyEntry] = field(default_factory=lambda: [])

    def __post_init__(self) -> None:
        for lang in [
            "nb_core_news_lg",
            "en_core_web_lg",
        ]:  # TODO: suggesiton for others to add?
            nlp = spacy.load(lang)
            self._arrClassifiers.append(ClassifyEntry(nlp))

    def normalizeInputString(self, productString: str) -> str:
        """
        @return a normalized veriosn of the input-string
        @remarks importna when bulidng the patterns of matches, for whioch we need that the input-text is consistent
        """
        return self._arrClassifiers[0].normalizeInputString(productString)

    def predict(self, productString: str) -> PredictedProduct:
        """
        @brief
        @return
        @remarks
        """
        assert self._arrClassifiers
        print("...... ClassifyEntryMultiLang::predict")
        for classif in self._arrClassifiers:
            # try:
            product = classif.predict(productString)
            assert product.isValid()
            if product.quantityIsKnown():
                self._productWriter.writeProduct(product)
                return product
            print(
                "[ClassifyEntryMultiLang::predict]\t product does NOT have a correct quanity, given: ",
                product,
            )
        raise ValueError(
            f"!!\t[ClassifyEntry.py]\t Did not find any valid quantity--unit mapping for '{productString}'"
        )

    def getMatches(self, text: str) -> MatchedEntryArr:
        """
        @brief
        @return the collection of matched entries
        """
        assert self._arrClassifiers
        arrMatched: MatchedEntryArr = MatchedEntryArr(self.normalizeInputString(text))
        print("...... ClassifyEntryMultiLang::predict")
        for classify in self._arrClassifiers:
            # FIXME: based on how this fucniotn is used ... handel exceptions? <-- if yes, then rewrite our "testClassification" ... then merge the ecpetion-handling in this + the latter
            product: PredictedProduct = classify.predict(text)
            # classif.getMatches(arrMatched)
            # print(".... product.productString=", product.productString, "text=", text)
            # assert(product.productString == text) # as we otherwise needs adjsuting the "product.getMatchedEntry()" with the "text" argument, This, to correctly get our nlp-pattersn to work 8ie, what this fucniton-result is used for) <-- TODO: figure otu a better appraoch, as the product.productString is partuially imrpoved
            assert product.isValid()
            if product.productAmount.hasData():
                matchedEntry: MatchedEntry = product.getMatchedEntry()
                arrMatched.append(matchedEntry)
        # FIXME: add a sanity-step where we avlaidate that the arrMatched object is cosnistne!
        return arrMatched


def testClassification(
    classify: ClassifyEntryMultiLang, arrProdEntries: List[str], testDescription: str
) -> None:
    """
    @brief perfomrs logics to investgiate the number of problematic entries
    @remarks
    """
    # classify = ClassifyEntryMultiLang()
    cntPassed: int = 0
    cntExceptions: int = 0
    cntUnkownQuantity: int = (
        0  #! ie, the prdocuts which requres a DB-lookups for knowing the amount
    )
    cntTotal: int = 0
    print(
        f"[ClassifyEntry::testClassification]\t applies tests for {len(arrProdEntries)} tests; these are focused towards {testDescription}"
    )
    for productString in arrProdEntries:
        # print(f"predicted({productString}): ", classify.predict(productString))
        try:
            product: PredictedProduct = classify.predict(productString)

            # TODO: use gold-data to udpate the below count
            if product.quantityIsKnown():
                print(f"predicted({productString}): ", product)
                cntPassed += 1
                #! Valdiate that the idnetification of the span(start, end) works;
                #! Note: we use this logic when training our NLP model, thus, its importance.
                # FIXME: add logics for detecting erros + ecpetions in the below
                matchedEntry: MatchedEntry = product.getMatchedEntry()
                print("matchedEntry=", matchedEntry)
                try:
                    arrMatched: MatchedEntryArr = classify.getMatches(productString)
                except ValueError as e:
                    cntUnkownQuantity += 1
                    # assert(arrMatched) #! ie, as we at this exec-point assumes that at least one quanityt--unit/metric relationship should have been identied
            else:
                print(
                    f'!!\t(failed) quantity is unkown given input:"{productString}"): ',
                    product,
                )
                cntUnkownQuantity += 1
        except ValueError as e:
            print(
                f'!!\t(failed) quantity is unkown given input:"{productString}"): ', e
            )
            print("!!\t\t Traceback:", traceback.format_exc())
            cntUnkownQuantity += 1
        # except Exception as _: # TODO: indietyf mroe specific expetions
        #     #except:
        #     strErr = f"!!\t[ClassifyEntry.py::main]\t failed to analyse \"{productString}\""
        #     strErr += traceback.format_exc()
        #     print(strErr)
        #     cntExceptions += 1
        cntTotal += 1
        #!

    print(
        f"========================\n\nOK({testDescription}): {cntPassed}/{cntTotal} tests completed; had {cntExceptions} exceptions raised, while {cntUnkownQuantity} products missed information of quantity (thus, requring DB-lookups)"
    )
    # classify.predict(productString)


@typechecked
@dataclass
class StoreResults:
    """
    @brief holds the test-data which is analyzed
    @remarks later used as input to our model training
    """

    resultFileClassification: str
    arrInputText: List[str] = field(default_factory=lambda: [])

    def append(self, arrText: List[str]) -> None:
        for text in arrText:
            self.arrInputText.append(text)


@typechecked
def main() -> StoreResults:
    """
    @brief applies the grammar to the test-data
    @return the data which is analyzed
    """
    mainResult = StoreResults("res-classifyEntries.txt")
    #! Pre: validate chalengiong patterns:
    WriteProduct.unitTest()
    # ********************************
    #!
    #! Analayze the data, and thereby trigger internal snaity-funcitons:
    productWriter = WriteProduct(mainResult.resultFileClassification)
    classify = ClassifyEntryMultiLang(_productWriter=productWriter)
    # --------------
    arrProdEntries: List[str] = [
        "3xl Grov Ostepølse 180g Stabburet",  # FIXME: describe how to inreprt this <-- assumption: needs to infer that amound="3 * 180g" <--- what is the wrok-rpiroty for this edge-case?
        "Gilde Ovnsbakt Leverpostei med Bacon 180g",  #! ie, which the "ShapeUnitClassification.py" is repsonbie for solving
        "Mills Peanut Butter 350g",
        "Fløtemysost Lettere skivet 130g Tine",
        "Vita Hjertego Lettmargarin 370g",
    ]
    mainResult.append(arrProdEntries)
    testClassification(classify, arrProdEntries, "challenging units")
    # FIXME: seems like the above was correclty parsed ... why NOT dienfied?
    # assert(False) #! get above to work! ... then re-includ ethe cases!
    arrProdEntries: List[str] = [  # type: ignore[no-redef]
        "Explo Mango Passion Sukkerfri 0,5l boks Mack",
        "Vaniljeis 3l First Price",
        # # FIXME: below:   [ClassifyEntry.py]   Did not find any valid products for 'Royal Is Sjokolade 0.9l Diplom-Is
        "Royal Is Sjokolade 0.9l Diplom-Is",
        # #! Case: handle this case where quantity is not described
        "Surdeig baguette",
        "Sausage",
    ]
    testClassification(classify, arrProdEntries, "challenging units")
    # assert(False) #! get above to work! ... then re-includ ethe cases!

    #! Validate basic input-cases:
    arrProdEntries: List[str] = [  # type: ignore[no-redef]
        "Mills Peanut Butter 350g",
        # TODO: how can we extraact "ost" from "Fløtemysost"?
        "Fløtemysost Lettere skivet 130g",  # ;130 g",
        "Fløtemysost Lettere skivet 130g Tine",  # ;130 g",
        "Vita Hjertego Lettmargarin 370g",
        "Oreo Sjokoladetrukket 246 g",
        "X-tra Røkt Kjøttpølse 1,2kg",  # FIXME: merge "x-tra" into one word <-- a manual step? better appraoch?
        "Coop Hamburgerrygg 100g",  # FIXME: why is unit "hamburgerrygg"?
        "Toro Lofoten Fiskesuppe 70g",
        "Leverpostei 160g Metervare",
        "Majones Ekte 160g Tube Mills",  # FIXME: productType= Ekte and productTypeSpecific= Majones Ekte
        "Explo Mango Passion Sukkerfri 0,5l boks Mack",
        "Freia Sitrongele Uten Sukker 14g",  # FIXME: how to merge "uten sukker" in one word? <-- when needed?
        "Coop Grøtris 1kg",
        "Kulinaris Iskrem Salt Karamel&Cookies 0,5l",
        "Jordbærgele 1l Piano",
        "Daim Iskake 0,9l Hennig-Olsen",
        "Sjokoladepudding 1l Piano",
        "Sørlandsis Krokan 2l Hennig-Olsen",
        "Knorr Chicken Curry 321g",
        "Royal Is Sjokolade 0.9l Diplom-Is",
        "Vaniljeis 3l First Price",
        "Surdeig baguette",
        "Sausage",
        "Laksefilet Naturell",
        "Cut chicken filet",
        "Big 100 Cookie Dough",
        "Store Tortillalefser",
        "Chickpeas in brine",
    ]
    mainResult.append(arrProdEntries)
    testClassification(classify, arrProdEntries, "basic patterns")
    arrProdEntries: List[str] = [  # type: ignore[no-redef]
        # FIXME: get below to work <-- pre: integrate our ""
        "Idyll Sjokoladeis Plantebasert 500ml Hennig-Olsen",
        "Knorr Chicken Curry 321g",  #! where unit is wrongly "Curry"? <-- how resolving this case?
        "Royal Is Sjokolade 0.9l Diplom-Is",
        "Vaniljeis 3l First Price",
        "Surdeig baguette",  # FIXME: always classify this as unit=item and quantity=1 ??? <-- the same for "Sausage"?
        "Sausage",
        "Laksefilet Naturell",
        "Cut chicken filet",  # FIXME: use ["filet", "baguette", "lefser"...] to accept cases where unit="item"? <-- is there a seperate prodcut-cateogrty covering these items (ie, a set of wrods to aldready use?)?
        "Big 100 Cookie Dough",  # FIXME: wrongly classiqied as quantity=100 and unit=Dough <-- how fixing this?
        "Store Tortillalefser",
    ]
    mainResult.append(arrProdEntries)
    testClassification(
        classify,
        arrProdEntries,
        "Difficult entries, where many lack quanutity-information",
    )

    #! ------------------------
    #! Case: load rows from a file, and then analyze these:
    filePath: str = "../../sample_data/case_splitProductAndVolumenNormalizeName.txt"
    arrProdEntries = LoadData.parseListOfStrings(filePath)
    assert arrProdEntries
    mainResult.append(arrProdEntries)
    testClassification(
        classify, arrProdEntries, "Unkown entries loaded from " + filePath
    )
    # --------------------------------------------------------------
    # --------------------------------------------------------------
    # --------------------------------------------------------------
    #! Finalize the tests
    productWriter.closeFile()
    return mainResult


if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    main()
