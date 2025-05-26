#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, bad-whitespace,bad-continuation,wrong-import-position
"""
@file
@brief our API for accessing the "Matvaretabellens" data [https://www.matvaretabellen.no/api/]
@remarks
"""
from typing import List, Any
from typing import cast
from typing import Union
from typing import ClassVar
from dataclasses import dataclass, field
from enum import Enum
import json
from typeguard import typechecked

#! Local files:
from loadData.LoadData import LoadData


@typechecked
class FoodLanguage(Enum):
    """
    @brief
    @remarks
    """
    Norwegian = "No"
    English   = "En"

@typechecked
@dataclass
class FoodGroupEntry:
    foodGroupId : str # TODO: instead reprenet as an int?
    name : str

@typechecked
@dataclass
class FoodGroups:
    """
    @brief
    @remarks
    """
    _data : List[FoodGroupEntry] =  field(default_factory=lambda: [])
    def __post_init__(self):

        # FIXME: pre: parse "../../sample_data/matvareTabellen/food-groups_no.json" to get the "foodGroupId"
        self.__addData("../../sample_data/matvareTabellen/food-groups_no.json", FoodLanguage.Norwegian)
        # FIXME: what use-case argues for adding the below?
        # self.__addData( "../../sample_data/matvareTabellen/food-groups_en.json", FoodLanguage.English)

    def __addData(self, filePath : str, language : FoodLanguage):
        with open(filePath, 'r') as fileP:
            data = json.load(fileP)
            matrix = data["foodGroups"]
            for row in matrix:
                self._data.append(FoodGroupEntry(row["foodGroupId"], row["name"]))
    def idToName(self, foodGroupId : str) -> str:
        """
        @brief
        @return
        """
        # TODO: if the below becoems a bottleneck, then opmmize the bleow
        for group in self._data:
            if(group.foodGroupId == foodGroupId):
                return group.name
        assert(False) # as this was not foudn <-- TODO: any valid cases where this can arise?
        raise ValueError(f"!!\t {foodGroupId} not found")

@typechecked
@dataclass
class FoodEntry:
    """
    @brief
    @remarks
    """
    #language : FoodLanguage
    # FIXME: adjust below
    foodGroup : str
    category : str
    foodName : str
    arrMetricsUsed : List[str]  =  field(default_factory=lambda: []) # FIXME: make use of this <-- where?

@typechecked
@dataclass
class MatrixOfFoods:
    """
    @brief
    @remarks
    """
    _data : List[FoodEntry] =  field(default_factory=lambda: [])
    # FIXME: use the _metricName in our system .. fine-tuning our existing
    _metricName : List[str] =  field(default_factory=lambda: [])
    def __post_init__(self):
        self._foodGroups = FoodGroups()
        # FIXME: pre: parse "../../sample_data/matvareTabellen/food-groups_no.json" to get the "foodGroupId"
        self.__addData("../../sample_data/matvareTabellen/foods_no.json", FoodLanguage.Norwegian)
        # FIXME: what use-case argues for adding the below?
        # self.__addData( "../../sample_data/matvareTabellen/foods_en.json", FoodLanguage.English)

    def __addData(self, filePath : str, language : FoodLanguage):
        with open(filePath, 'r') as fileP:
            data = json.load(fileP)
            matrix = data["foods"]
            for row in matrix:
                keyWord = row["searchKeywords"]
                foodName = row["foodName"]
                portions : List[dict] = row["portions"]
                foodGroupId = row["foodGroupId"]
                foodGroup = self._foodGroups.idToName(foodGroupId)
                product = FoodEntry(
                    #language,
                    foodGroup = foodGroup,
                    category = keyWord, foodName = foodName)
                self._data.append(product)
                for portion in portions:
                    unit = portion["unit"]
                    if(unit not in self._metricName):
                        self._metricName.append(unit)
                    if(unit not in product.arrMetricsUsed):
                        product.arrMetricsUsed.append(unit)
                #print("row: ", row)
                #assert(len(row) == 2)
                # FIXME: include below!
                # row:  {'searchKeywords': ['belgfrukt'], 'calories': {'sourceId': 'MI0115', 'quantity': 25, 'unit': 'kcal'}, 'portions': [{'portionName': 'stk', 'portionUnit': 'stk', 'quantity': 3.0, 'unit': 'g'}], 'ediblePart': {'percent': 100, 'sourceId': '0'}, 'langualCodes': ['N0001', 'G0003', 'A0152', 'M0001', 'H0001', 'K0003', 'C0158', 'E0150', 'F0018', 'P0024', 'B1371', 'A0831', 'J0136'], 'energy': {'sourceId': 'MI0114', 'quantity': 105.0, 'unit': 'kJ'}, 'foodName': 'Aspargesbønner, fryst',
                # self._data.append(ProductAndQuantity(row[0], row[1]))



    @property
    def rows(self) -> List[FoodEntry]:
        return self._data

    @property
    def metricName(self) -> List[str]:
        return self._metricName


if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    #objEnsamble = MatchCategories()
    objData = MatrixOfFoods()
    assert(len(objData.rows))
    for entry in objData.rows:
        print(entry)
        #print("data=", objData.rows)
        #print("data=", entry.productString)
        pass
    print("metrics used to quantify the products: ", objData.metricName)
