#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position
"""
@file
@brief
@remarks
@FIXME updat ethe docuemtnion ... write conrete example ... for this use the following tempalte: ("Walmart is a leading e-commerce company", {"entities": [(0, 7, "ORG")]}),
"""
from dataclasses import dataclass, field
from typing import List
from enum import Enum, unique
from typeguard import typechecked

@typechecked
@unique
class MatchedLabel(Enum):
    """
    @brief label/name the entites we use for NLP model-training
    @remarks
    - unique VS auto(): we hard-code the enum-values to simplify deubgging (thus, explaining the use of "@unique" rather than "auto()")
    - food-labels: partially auto-generated from our "x-autoGenerate-MatchedLabel-enums.py"
    @todo adjsut the bewlow ... use a class instead of the below numbers for the value-part ... <-- when needed?
    """
    # TODO: what other labels/parts to use/include?
    QuanityAndWeight = 1

    @classmethod
    def getColors(cls) -> dict: # type: ignore[type-arg]
        """
        @brief get teh colros assicated with the enums
        @remarks used during vvisualition, eg, from our trainer/TrainModel.py
        """
        arrColors = ["#F67DE3", "#7DF6D9", "#FFFFFF"] #! ie, the RGB hex-color
        arrEnums = list(cls)
        assert(len(arrEnums) <= len(arrColors)) #! as we otehrise needs to add colros <-- when doing tthis, idnietyf colros which gives the seperation needed by the caller ... eg, use a colro-shceme which captrues the simairlity + relateness of the above labels?
        dictResult = {}
        for index, entry in enumerate(arrEnums):
            dictResult[entry.name] = arrColors[index]
        return dictResult


@typechecked
@dataclass
class MatchedEntry:
    """
    @brief label a
    @remarks
    """
    label : MatchedLabel
    posStart : int
    posEnd : int
    def __post_init__(self) -> None:
        assert(self.posStart < self.posEnd)
        assert(self.posStart >= 0)
    def isValid(self, text : str) -> bool:
        """
        @return True if this object has a valid entry for the provided input-test
        """
        assert(self.label.name) #! ie, the
        assert(text)
        assert(self.posStart < len(text))
        assert(self.posEnd <= len(text))
        if(not(self.label.name and text and (self.posStart < len(text)) and (self.posEnd <= len(text)) )):
            assert(False) # FIXME: never should be triggered if the above asserts are cosnstent with this if-loop
            return False #! to handle case where code is compiled with the "O2" optmizaiotn-param
        return True

@typechecked
@dataclass
class MatchedEntryArr:
    """
    @brief a collection of MatchedEntry items
    @remarks
    """
    text : str
    __arrEntries : List[MatchedEntry] = field(default_factory = lambda : [])
    def __post_init__(self) -> None:
        assert(self.text) #! ie, at least one char deescribing the label
        for entry in self.__arrEntries:
            assert(entry.isValid(self.text))
    def hasEntry(self, entryToCheck : MatchedEntry) -> bool:
        """
        @return False if the entry is Not present
        @remarks base-usage is to know if we are to append the given entry into the list
        """
        for entry in self.__arrEntries:
            if(entry == entryToCheck):
                return True
        return False
    def append(self, entry : MatchedEntry) -> None:
        if(self.hasEntry(entry)):
            return #! as it already exists, thus, to avoid adding a duplicte
        self.__arrEntries.append(entry)

    def __len__(self) -> int:
        return len(self.__arrEntries)

    @property
    def entries(self) -> List[MatchedEntry]:
        return self.__arrEntries

@typechecked
def main() -> None:
    """
    @brief validate our ability to remember text-labels
    """
    #! Explore a crude/basic pattern for fidning the word-boundary:
    text = "|a text with a label;"
    posStart = text.find(text[0]) #! [https://www.geeksforgeeks.org/python-string-find/]
    assert(posStart > -1) #! as it should be found; toerhwise, we need adjsuting this
    assert(posStart == 0) #! as expected in this exampel
    posEnd = text.find(text[-1])
    assert(posEnd > -1) #! as it should be found; toerhwise, we need adjsuting this
    posEnd += 1 #! ie, to get past the last matched char
    assert(posEnd > posStart)
    assert(posEnd == len(text)) #! as expected in this exampel

    #! Add it to the set:
    arrMatched : MatchedEntryArr = MatchedEntryArr(text)
    matchedEntry : MatchedEntry = MatchedEntry(label = MatchedLabel.QuanityAndWeight, posStart = posStart, posEnd = posEnd)
    arrMatched.append(matchedEntry)
    assert(len(arrMatched) == 1)


if __name__ == "__main__":
    """
    @brief validate our ability to remember text-labels
    """
    main()
