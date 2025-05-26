"""!
@file
@brief
@remarks
- The data in kassalappen api is of varying quality, this utility is meant to give options to exclude and filter out not desired data. 
"""

import json

import os
from typing import Dict, List, TypedDict, Optional


class Category(TypedDict):
    """
    Support subclass for data from Kassalappen API.
    """

    id: int
    depth: Optional[int]
    name: str


class KassalappenProduct(
    TypedDict, total=False
):  # total=False makes all fields optional by default
    """
    Support class for shape of data from Kassalappen API.
    """

    # Mandatory fields
    id: int
    name: str
    # Optional fields
    category: List[Category]
    weight: Optional[int]
    weight_unit: Optional[str]


def dataWithCategories(inputPath: str) -> List[KassalappenProduct]:
    """
    Gives back data with categories in them.
    """
    with open(inputPath, "r", encoding="utf-8") as f:
        data: List[KassalappenProduct] = json.load(f)

    filteredData = [f for f in data 
                    if "category" in f 
                    and f["category"] is not None 
                    and f["category"] != []]

    return filteredData


def dataWithWeights(inputPath: str) -> List[KassalappenProduct]:
    """
    Gives back data with weights in them.
    """
    with open(inputPath, "r", encoding="utf-8") as f:
        data: List[KassalappenProduct] = json.load(f)

    weightData: List[KassalappenProduct] = []

    for _item in data:
        weight = _item.get("weight")
        weight_unit = _item.get("weight_unit")

        if weight not in (None, "") and weight_unit not in (None, ""):
            weightData.append(item)

    return weightData


def getCategories(inputPath: str) -> Dict[int, Category]:
    """
    Flattens category list for all of Kassalappen data and 
    return a dict of id and category.
    """
    with open(inputPath, "r", encoding="utf-8") as f:
        data: List[KassalappenProduct] = json.load(f)

    assert(data)
    filteredData : List[Category] = [
        category
        for f in data
        if "category" in f 
        and f["category"] != []
        for category in f["category"]
    ]

    uniqCategories : Dict[int ,Category] = {}

    for item in filteredData:
        if not uniqCategories.get(item['id']):
            uniqCategories[item["id"]] = item


    return uniqCategories 

def filterByCategory(inputPath: str, categories: List[int]) -> List[KassalappenProduct]:
    """
    Filters Kassalappen data by desired categories.
    """
    with open(inputPath, "r", encoding="utf-8") as f:
        data: List[KassalappenProduct] = json.load(f)

    result : List[KassalappenProduct] = []

    # Category is a list, need to iter thru and check if any of the categories match desired categories
    for item in data:
        if "category" in item and item["category"]:
            cat_ids = [cat["id"] for cat in item["category"]]
            if any(cat_id in categories for cat_id in cat_ids):
                result.append(item)

    return result



if __name__ == "__main__":
    data = dataWithCategories("../../sample_data/kassalappen/foods.json")
    assert(len(data) > 0)
    with open("../../sample_data/kassalappen/foods_w_categories.json", 'w',encoding="utf-8") as f:
        f.write("[")
        for i in range(0,len(data)):
            item = data[i]
            json.dump(item,f)
            if i != len(data) -1:
                f.write(',\n')
        f.write("]")
    

    #! TODO explore ways to filter out categories that are not of type "food" LLM?
    categories :Dict[int,Category] = getCategories("../../sample_data/kassalappen/foods_w_categories.json")
    sorted_categories = dict(sorted(categories.items()))
    with open("../../sample_data/kassalappen/categories.json", 'w',encoding="utf-8") as f:
        f.write("[")
        _len =len(sorted_categories.keys())
        for i, (key,value) in enumerate(sorted_categories.items()):
            json.dump(value,f)
            if i != _len -1:
                f.write(',\n')
        f.write("]")

    #! FIXME perhaps it should also be filtered by the names of the categories, we cannot guarantee that ids are always consistent.
    catIdsNonFood : List[int]=[] 

    # non_food_categories.json was made by uploading categories.json to a big llm with prompt:
    # "Given this file, give me ids, and names of all the objects that do not belong to food category in json format".
    # The output has been manually reviewed to not contain any food categories that were mis-categorized.
    with open("../../sample_data/kassalappen/non_food_categories.json", 'r',encoding="utf-8") as f:
        _data = json.load(f)
        for item in _data:
            if 'id' in item:
                catIdsNonFood.append(item['id'])

    print(catIdsNonFood)
    print("original data len: {}", len(data))
    # Filter out data for items in non food categories:
    # The resulting data is data that has categories and categories that are filtered by the non_food_categories.json
    filteredData : List[KassalappenProduct]= []

    # for i in range(10):
        # product = data[i]
        # print(product)
    for product in data:
        _categories = product.get("category") or []
        has_non_food = False
        
        for category in _categories:
            if category["id"] in catIdsNonFood:
                has_non_food = True
                break
                
        if not has_non_food:
            if product.get("weight") != None and product.get("weight_unit") != None:
                filteredData.append(product)

    print("filtered data length: {}",len(filteredData))

    with open("../../sample_data/kassalappen/filtered_foods_with_weights.json", 'w',encoding="utf-8") as f:
        f.write("[")
        for i in range(0,len(filteredData)):
            item = filteredData[i]
            json.dump(item,f)
            if i != len(filteredData) -1:
                f.write(',\n')
        f.write("]")

    



