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
from dataclasses import dataclass, field
from enum import Enum
import json
from typeguard import typechecked

#! Local files:
from loadData.LoadData import LoadData
from loadData.Matvaretabellen import MatrixOfFoods, FoodEntry
#from loadData.Matvaretabellen import
from foodNer.MatchedEntry import MatchedLabel #! where the "MatchedLabel" is manually updated with the classes we idneify <-- TODO: a better approach?



if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    objData = MatrixOfFoods()
    assert(len(objData.rows))
    arrCategories = []
    for entry in objData.rows:
        print(entry)
        #print("data=", objData.rows)
        #print("data=", entry.productString)
        pass
    print("metrics used to quantify the products: ", objData.metricName)
