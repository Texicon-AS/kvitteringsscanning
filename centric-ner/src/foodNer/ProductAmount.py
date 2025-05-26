#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position
"""
@file
@brief
@remarks
"""
from __future__ import annotations  #! used for "forward decleartions";
import json
from json import JSONEncoder
import dataclasses
from dataclasses import dataclass, field
from typing import List  # , ClassVar
from enum import Enum, unique
from typeguard import typechecked


@typechecked
@dataclass
class ProductUnitEntry:
    """
    @brief names a given unit
    """

    name: str
    longForm: str = field(
        default_factory=lambda: ""
    )  #! ie, "liter" for the shortform/default of "l"

    # TODO: add additioanl attirubtes (eg, synonums, language-support, ...)
    def __post_init__(self) -> None:
        if self.name == "":
            return
        assert self.longForm != self.name  #! thus, aoviding duplciates

    def describes(self, unitValue: str) -> bool:
        """
        @return True if the unitValue corresponds to the deion of this object
        """
        if self.name == unitValue:
            return True
        if self.longForm and (
            self.longForm == unitValue
        ):  #! ie, to handle the default case where the "longForm" is not set
            return True
        return False


#! Forward-delare the class (using the "annotations" iumprot above)
# pylint: disable=unused-argument
# mypy:  disable-error-code=empty-body
def f(var: "ProductUnit") -> int:  #! ie, a forward decleartion
    ...


@unique
@typechecked
class ProductUnit(Enum):
    """
    @brief
    @remarks
    - naming: the names are wrritne using a logn form. This, to simplify deubgging
    - order: our tests fails if the subset-terms (eg, "g" and "l") are placed beofre the sueprset (eg, "kg" and "ml") <-- TODO: write unit-tests to esnreu that thsi code-part is always sane <-- where + how?
    @todo update the below based on what we learn from the data
    """

    notSet = ProductUnitEntry("")
    kiloGram = ProductUnitEntry("kg", "kilogram")
    gram = ProductUnitEntry("g", "gr")
    grm = ProductUnitEntry("grm")
    milliLiter = ProductUnitEntry("ml", "milliliter")
    centiLiter = ProductUnitEntry("cl", "centiliter")
    deciLiter = ProductUnitEntry("dl", "deciliter")
    liter = ProductUnitEntry("l", "liter")
    ltr = ProductUnitEntry("lt", "ltr")

    def __repr__(self) -> str:
        return '"' + self.value.name + '"'  # TODO: correct?

    def __str__(self) -> str:
        return '"' + self.value.name + '"'  # TODO: correct?

    @classmethod
    def getUnitVocabTerms(cls) -> List[str]:
        """
        @brief get the vocabluar terms for the units
        @return a list of unique unit-terms, and correctly ordered wrt. their priorty
        """
        arrUnits: List[str] = []
        for entry in list(cls):
            if entry == cls.notSet:
                continue  #! ie, avoid adding an empty match, as this otheiwse would matcfh all, thus, break our system
            assert len(entry.value.name)  #! as we assume the otehr names are set
            assert entry.value.name not in arrUnits  #! ie, the uniquenss-critera
            arrUnits.append(entry.value.name)
            assert entry.value.describes(entry.value.name)  #! ie, a cosnsteincy check
            if entry.value.longForm:
                assert entry.value.longForm != entry.value.name
                assert (
                    entry.value.longForm not in arrUnits
                )  #! ie, the uniquenss-critera
                arrUnits.append(entry.value.longForm)
                assert entry.value.describes(
                    entry.value.longForm
                )  #! ie, a cosnsteincy check
        return arrUnits

    @classmethod
    def toEnum(cls, unitValue: str) -> ProductUnit:
        """
        @brief get an enum matching the given unit
        @param unitValue is the string we query for
        @return an enum corresponging to the enum
        """
        if not unitValue:
            return cls.notSet  #! ie, as it was not found, which is a valid outcome
        for unitDef in list(cls):
            if unitDef.value.describes(unitValue):
                return unitDef
        raise ValueError(
            f'!!\t[ProductUnit::toEnum]\t not any matches for the "{unitValue}" enum'
        )


@typechecked
@dataclass
class ProductAmount(JSONEncoder):
    """
    @brief relates the quanity (eg, "120") to the unit (eg, "gram")
    """

    quanityValue: (
        float  #! ie, the predicted quantity-value, intepreted usign the "unit"
    )
    unit: ProductUnit

    def __post_init__(self) -> None:
        assert self.isValid()

    def isValid(self) -> bool:
        """
        @return False if there are obviosu bugs in this object
        """
        if not isinstance(self.unit, ProductUnit):
            if isinstance(self.unit, str):
                self.unit = ProductUnit.toEnum(self.unit)
                assert isinstance(self.unit, ProductUnit)
            else:
                assert False  #! ie, an early heads-up
                return False
        if self.unit.value.name != "":
            if self.quanityValue == -1:
                self.unit = (
                    ProductUnit.notSet
                )  #! ie, as we then assume that the provuded unit was invlaid (eg, set to a "box" where the correct value should have meed "l" <-- FIXME: a better strategy than this?
            else:
                # print("... unit=", self.unit)
                assert (
                    self.quanityValue >= 0
                )  #! ?? cases where this does NOT need to hold?
        if not isinstance(self.quanityValue, float):
            assert False  #! ie, an early heads-up
            return False
        return True

    def getUnitName(self) -> str:
        """
        @return the unit-name (default)
        """
        return (
            self.unit.value.name
        )  # TODO: always correct to hse the short-form/name for the unit?

    def hasData(self) -> bool:
        if isinstance(self.unit, str):
            self.unit = ProductUnit.toEnum(self.unit)
            assert isinstance(self.unit, ProductUnit)
            assert not isinstance(self.unit, str)
        else:
            assert not isinstance(self.unit, str)
        assert not isinstance(self.unit, str)
        assert isinstance(self.unit, ProductUnit)
        productIsSet = (len(self.unit.name) > 0) and (self.quanityValue > 0)
        print("...  ProductAmount.py =  ", self, productIsSet)  # FIXME: remove!!!
        return productIsSet

    def quantityIsKnown(self) -> bool:
        """
        @brief
        @return True if theq uanity is known
        """
        if self.unit == ProductUnit.notSet:
            return False
        if self.quanityValue == 0:
            return False
        assert self.quanityValue > 0  #! ?? any cases where this is NOT required?
        return True

    def getQuantityAndUnit(
        self, useSeperatorBetweenQuantityAndUnit: bool = True
    ) -> str:
        """
        @return a nroamlized version of the 'quanity' + unit/metirc
        @remarks needed when using the "openfoodfacts_export.txt" for sanity-valdiation
        """
        if not self.quantityIsKnown():
            return ""  # TODO: instead raise a ValueError(...)?
        # return str(self.quanityValue) + " " + self.unit
        # return str(format(self.quanityValue, '.1f')) + " " + self.unit
        seperator = " "
        if not useSeperatorBetweenQuantityAndUnit:
            seperator = ""
        return str(format(self.quanityValue, ".0f")) + seperator + self.getUnitName()


# *******************************************
def main() -> None:
    """
    @brief Validate these classes
    """
    #!
    #! Pre: validate that we can export these results to json:
    data = ProductAmount(1.0, ProductUnit.gram)
    # print("data=", data)
    jsonData = json.dumps(data)
    # print("jsonData=", jsonData)    #! whichshoudl trigger an expion if failed
    assert ProductUnit.notSet.value.name == ""  #! ie, ie, the default assumption
    assert len(ProductUnit) > 1  #! ie, mulitple enum-entries
    arrUnitVocabTerms = ProductUnit.getUnitVocabTerms()
    assert arrUnitVocabTerms  #! ie, mulitple enum-entries
    assert (
        ProductUnit.notSet.value.name == ""
    )  #! ie, shoudl be unchagned after the above step

    #! Validate the uniquenss fo the enum-names:
    #! Pre: test cases which earlier triggered bugs, thus, simplify future deubgging:
    # print("ProductUnit.notSet.value=", ProductUnit.notSet.value)
    assert not ProductUnit.gram.value.describes(ProductUnit.notSet.value.name)
    assert ProductUnit.gram.value.describes(ProductUnit.gram.value.name)
    #! Then, an extenvie comparison:
    arrNamesSeen: List[str] = []
    for entry1 in list(ProductUnit):
        if entry1 == ProductUnit.notSet:
            assert entry1.value.name == ""
            assert entry1.value.longForm == ""
            continue
        # print("entry1.value.name=", entry1.value.name)
        # print("entry1.value.longForm=", entry1.value.longForm)
        assert entry1.value.name != entry1.value.longForm
        assert entry1.value.name not in arrNamesSeen
        arrNamesSeen.append(entry1.value.name)
        if entry1.value.longForm:
            assert entry1.value.longForm not in arrNamesSeen
            arrNamesSeen.append(entry1.value.longForm)
        #! Esnrue that a) we do NOT have any overlaps, and b) that the "describes(..)" funciton works as expected
        for entry2 in list(ProductUnit):
            if entry1 != entry2:
                # print("entry1=", entry1, "entry2=", entry2)
                # print("entry2.value.name=", entry1.value.name)
                # print("entry2.value.longForm=", entry1.value.longForm)
                assert not (entry1.value.describes(entry2.value.name))
                assert not (entry1.value.describes(entry2.value.longForm))
            else:
                # print("expected mathc\t\t entry1=", entry1, "entry2=", entry2)
                assert entry1.value.describes(entry2.value.name)
                if entry2.value.longForm:
                    assert entry1.value.describes(entry2.value.longForm)
    # TODO: add other tests


if __name__ == "__main__":
    main()
