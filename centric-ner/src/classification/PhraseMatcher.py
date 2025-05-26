"""
Uses DatasetBuilder to create a phraseMatcher for classification of ingredients.
"""

from dataclasses import dataclass
from typing import List, Dict
import spacy
import json
from spacy.matcher import PhraseMatcher
from classification.DatasetBuilder import FoodItem, GroupsOfFoodItem


@dataclass
class FailedMatch:
    name :str
    categories : List[str]

    def to_dict(self):
        return {"name": self.name, "categories": self.categories}


def loadData(matvareTabell:str, kassalapp : str) -> Dict[str, GroupsOfFoodItem]:
    """
    # TODO: return Dict[str List[str]] to speed up loading of data.
    Loads matvareTabell and Kassalappen data and creates phrase list from them.
    """
    phraseList: Dict[str,GroupsOfFoodItem] = {} 
    returnList: Dict[str,List[FoodItem]] = {}
    with open(file=matvareTabell, mode="r", encoding="utf-8") as file:
        data = json.load(file)
    for item in data:
        _food : GroupsOfFoodItem = GroupsOfFoodItem(**data[item])
        phraseList[_food.name] =_food
        returnList[_food.name] = _food.foodList
    with open(file=kassalapp, mode="r", encoding="utf-8") as file:
        _kData = json.load(file)
    for item in _kData:
        _food : GroupsOfFoodItem = GroupsOfFoodItem(**_kData[item])
        # grabs existing entry or creates new one
        existing_food = phraseList.setdefault(_food.name,_food) 
        if existing_food != _food:
            existing_food.foodList.extend(_food.foodList)
            # print(f"Found overlap! :{_food.name}")

    return phraseList

if __name__ == "__main__":

    nlp = spacy.load("../trainer/centricFoodModel_en.spacy") # TODO: swap this with out pretrained model.
    matcher = PhraseMatcher(nlp.vocab)
    phraseList: Dict[str,GroupsOfFoodItem] = loadData("./matvaretabell_grupper.json","./kassalapp_grupper.json")

    for (name,groupsofFood) in phraseList.items():
        patterns = [nlp(food["foodName"]) for food in groupsofFood.foodList]
        matcher.add(name,patterns)
    
    
    with open("../../sample_data/kassalappen/filtered_foods.json") as file:
        testData = json.load(file)

    failedList : List[FailedMatch] = []

    for item in testData:
        doc = nlp(item["name"])
        categories = item["category"]
        catList = []
        for cat in categories:
            catList.append(cat["name"])
        matches = matcher(doc)
        if not matches:
            failedList.append(FailedMatch(name=item["name"],categories=catList))
            print(item["name"], " failed to match \n")

        for match_id, start, end in matches:
            match_id_str = nlp.vocab.strings[match_id]
            phrase = doc[start:end].text


    print(f"{len(failedList)} failed out of {len(testData)}")
    with open("failed-matches.json", "w", encoding="utf-8") as file:
        json.dump([item.to_dict() for item in failedList], file)
