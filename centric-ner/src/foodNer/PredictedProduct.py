#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position
"""
@file
@brief holds information of a predicted product
@remarks
1. NLP-training: used to build sets of hints/matches whtich the training-pipline makes use of
2. model-classifciaotn (after the NLP-training): ...??... <-- TODO: update after our NLP-training works
@todo update this documentaton after our NLP-training wors
"""
import re
from dataclasses import dataclass  # , field
from typing import List, ClassVar
from typeguard import typechecked

#! Local files:
from stopWords.StopWordRemoval import StopWordRemoval
from foodNer.MatchedEntry import MatchedEntry, MatchedLabel
from foodNer.ProductAmount import ProductAmount, ProductUnit


@typechecked
@dataclass
class PredictedProduct:
    """
    @brief
    @remarks
    - relatedness: the below is used in our IngredientAddedOrRemoved class for updating the entries <-- TODO: add a hard compiletime-detable relationship ... to simplify/ease amaince? <-- or, better to keep seperation to avoid having a DB-failture when parsing texts?
    """

    productString: str  #! ie, the input-name used as bassi for this analsyssi
    product: str  #! ie, the product we idneitfy
    productAmount: ProductAmount
    # quanityValue : float #! ie, the predicted quantity-value, intepreted usign the "unit"
    arrCompound: List[
        str
    ]  # FIXME: suggestiosn to how this can be sued? <-- eg, to query for entries when NOT having ane xact match?
    productTypeSpecific: str  #! which descrbies ?? <-- FIXME: update this <-- use an imrpvoed NER (eg, after having udpated our "ClassifyEntry" with data from "Matvaretabellen"?)?
    unitVocabTerms: ClassVar[List[str]] = ProductUnit.getUnitVocabTerms()

    def __post_init__(self) -> None:
        assert self.isValid()

    def isValid(self) -> bool:
        """
        @return False if there are obviosu bugs in this object
        """
        if not self.unitVocabTerms:
            assert False  #! ie, an early heads-up
            return False
        if not isinstance(self.productAmount, ProductAmount):
            assert False  #! ie, an early heads-up
            return False
        if not self.productAmount.isValid():
            assert False  #! ie, an early heads-up
            return False
        return True

    def __repr__(self) -> str:
        return f"({self.productString}, {self.product}, {repr(self.productAmount)}, {self.arrCompound}, {self.productTypeSpecific})"  # TODO: correct?

    def quantityIsKnown(self) -> bool:
        """
        @brief
        @return True if theq uanity is known
        """
        return self.productAmount.quantityIsKnown()

    def getQuantityAndUnit(
        self, useSeperatorBetweenQuantityAndUnit: bool = True
    ) -> str:
        """
        @return a nroamlized version of the 'quanity' + unit/metirc
        @remarks needed when using the "openfoodfacts_export.txt" for sanity-valdiation
        """
        return self.productAmount.getQuantityAndUnit(
            useSeperatorBetweenQuantityAndUnit=useSeperatorBetweenQuantityAndUnit
        )

    def getCompounds(
        self,
        stopRemoval: StopWordRemoval,
        useStopWords: bool = True,
        removeQuanitityInformation: bool = True,
    ) -> List[str]:
        # FIXME: the use of stop-wrods does NOT seem to ahve an effect ... suggestion for a better appraoch?
        # TODO: move the below step into a new 'getter'; this to aovid errors in the top-word-step from cltutering the analsysis <-- tempraorily addded here to get early warnigns when problems related to the stop-word filterin
        if useStopWords:
            arrCompound = stopRemoval.predict(self.arrCompound)
        else:
            arrCompound = self.arrCompound
        if removeQuanitityInformation:
            for word in list(
                arrCompound
            ):  # iterating on a copy since removing will mess things up
                #! SrC: https://stackoverflow.com/questions/29771168/how-to-remove-words-from-a-list-in-python
                if word in self.unitVocabTerms:
                    arrCompound.remove(word)
                # if word in ["-",
                elif re.match(r"^[\W-]+$", word):
                    arrCompound.remove(word)
                elif re.match(r"^[\d\.\,]+$", word):
                    arrCompound.remove(word)
                else:
                    # print(f"str({self.quanityValue})) VS ", word)
                    for quantAndProduct in [
                        self.getQuantityAndUnit(True),
                        self.getQuantityAndUnit(False),
                    ]:
                        if quantAndProduct in word:
                            arrCompound.remove(word)
        return arrCompound

    def getMatchedEntry(self) -> MatchedEntry:
        """
        @brief identify the matched entries
        @return the matched entry
        @TODO the code-pattern we here use here is crude, thus, needs refinements in the future. However, as understanding requires cases where it fails, the code-improvement should be delayed until needed
        """

        return MatchedEntry(
            label=MatchedLabel.QuanityAndWeight,
            posStart=0,
            posEnd=len(self.productString),
        )

        # # rewrite this function ... try updating our above "predict(..)" with this ifnroatmion ... then makign the below mroe specifci <-- add information of the start-pos of the text <-- update latter, adding extra return-values, then call this ... prodcue a result-data-set ... use directly
        # quantityValue: str = str(self.productAmount.quanityValue)
        # posStart = self.productString.find(
        #     quantityValue
        # )  #! [https://www.geeksforgeeks.org/python-string-find/]
        # if posStart == -1:  #! then try remvoing the decimals
        #     quantityValue: str = str(int(self.productAmount.quanityValue))  # type: ignore[no-redef]
        #     posStart = self.productString.find(
        #         quantityValue
        #     )  #! [https://www.geeksforgeeks.org/python-string-find/]
        # if (
        #     posStart == -1
        # ):  # Most likely a case where we have multiple of a thing f.e. 3x180 =540, cannot find string directly.
        #     pattern = pattern = r"(\d+)[x/]+(\d+)"  # finds 3x180, 1/2
        #     match = re.search(pattern, self.productString)
        #     assert match is not None
        #     posStart = match.start()
        # print(
        #     f"[PredictedProduct.py::getMatchedEntry]\t posStart({posStart}) given productString({self.productString}) and needle({quantityValue})"
        # )
        # assert (
        #     posStart > -1
        # )  #! as it should be found; toerhwise, we need adjsuting this
        # unitName = self.productAmount.getUnitName()
        # assert len(unitName)  #! as we assume the unit is set
        # posEnd = self.productString.find(
        #     unitName, posStart + len(quantityValue)
        # )  # FIXME: cases where there can be mroe than one match? <-- ye, propably. However, figure out how to detec these, thus, haivng a better udnestand f what it takes to handle these
        # print(
        #     f"[PredictedProduct.py::getMatchedEntry]\t posStart({posStart}), posEnd({posEnd}) given productString({self.productString}) and needle({unitName})"
        # )
        # assert posEnd > -1  #! as it should be found; toerhwise, we need adjsuting this
        # posEnd += 1  #! ie, to get past the last matched char
        # # (posStart, posEnd) = self.getStartEndPosOfMatch()
        # matchedEntry: MatchedEntry = MatchedEntry(
        #     label=MatchedLabel.QuanityAndWeight, posStart=posStart, posEnd=posEnd
        # )
        # return matchedEntry


if __name__ == "__main__":
    """
    @brief Validate the compound-filtering
    """
    assert (
        PredictedProduct.unitVocabTerms
    )  #! ie, at least one item; a test used to vdliate taht the static-init-appraoch wors
    # productWriter = WriteProduct("tmp-PredictedProduct.txt")
    stopRemoval = StopWordRemoval()
    product1 = PredictedProduct(
        "Sørlandsis Krokan 2l Hennig-Olsen",
        "Krokan",
        productAmount=ProductAmount(quanityValue=2.0, unit=ProductUnit.liter),
        arrCompound=["S\u00f8rlandsis", "2l", "Hennig-Olsen"],
        productTypeSpecific="Krokan",
    )
    compundsXmtStopWords = product1.getCompounds(stopRemoval)
    print("compundsXmtStopWords=", compundsXmtStopWords)
    assert "2l" not in compundsXmtStopWords
    assert "-" not in compundsXmtStopWords
    assert product1.getMatchedEntry().isValid(product1.productString)

    product2 = PredictedProduct(
        "Dahls 0.5l",
        "Dahls",
        productAmount=ProductAmount(quanityValue=0.5, unit=ProductUnit.liter),
        arrCompound=["Dahls", "0.5l"],
        productTypeSpecific="Dahls",
    )
    assert product2.getMatchedEntry().isValid(product2.productString)
    compundsXmtStopWords = product2.getCompounds(stopRemoval)
    print("compundsXmtStopWords=", compundsXmtStopWords)
    assert "2l" not in compundsXmtStopWords
    assert "-" not in compundsXmtStopWords
