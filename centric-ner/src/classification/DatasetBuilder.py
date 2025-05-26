"""
@file
@brief uses food_groups.json and foods_no.json to create training data for entity label. Also 
@remarks 
"""
from dataclasses import dataclass, asdict
import json
import os
from typing import List, Dict, Optional
import re


class CustomEncoder(json.JSONEncoder):
    """
    Custom encoder for the dataclasses to write into json format properly.
    """
    def default(self, o):
        if hasattr(o, "to_dict"):  # If object has to_dict(), use it
            return o.to_dict()
        return super().default(o)


@dataclass
class FoodGroup:
    foodGroupId : str
    name: str
    parentId: Optional[str] = None


@dataclass
class FoodItem:
    """
    Data shape from MatvareTabell, commented out fields that does not give us any value currently.
    """
    # calories: Calories
    # portions: List[Portion]
    # ediblePart: EdiblePart
    # langualCodes: List[str]
    # energy: Energy
    foodName: str
    # latinName: str
    # constituents: List[Constituent]
    # uri: str
    foodGroupId: str
    foodId: str
    searchKeywords: Optional[List[str]] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class GroupsOfFoodItem:
    """
    Data shape including group and foods belongind to that group, merged into a single data object
    """
    foodGroupId : str
    name: str
    foodList: List[FoodItem] 

    def to_dict(self):
        return {
            "foodGroupId": self.foodGroupId,
            "name": self.name,
            "foodList": self.foodList
        }



def loadGroups(path: str) -> List[FoodGroup]:
    """
        Parses json and returns a list of food groups from MatvareTabell
        TODO: make use of api/ make a check if the list should be updated
    """
    with open(path,'r', encoding='utf-8') as file:
        data  = json.load(file)
        data = data["foodGroups"]
   
    assert len(data) != 0
    returnGroups : List[FoodGroup] = [FoodGroup(**item) for item in data]
    return returnGroups 

def loadFoods(path: str) -> List[FoodItem]:
    """
        Parses json and returns a list of food  from MatvareTabell
        TODO: make use of api/ make a check if the list should be updated
    """
    with open(path,'r', encoding='utf-8') as file:
        data = json.load(file)
        data = data["foods"]
   
    assert len(data) != 0
    returnFoods: List[FoodItem] = []
    for item in data:
        val =item["foodName"].split(',')[0] # TODO: investigate a more elegant way of extracting a proper name for matvaretabell food names.
        returnFoods.append(FoodItem(
            searchKeywords=item.get("searchKeyWords",None),
            foodName=val, 
            foodGroupId=item["foodGroupId"],
            foodId=item["foodId"]))

    return returnFoods 


def mergeData(groups : List[FoodGroup], foods: List[FoodItem]) -> Dict[str,GroupsOfFoodItem]:
    """
    Merges data with categories, for easier labeling. Main groups that are whole numbers, will be empty, this 
    is because the all of the entries are in subcategories. Hierarchy can be restored when sending back the api request,
    for training there is no need to include all the parent groups.
    """

    returnList :  Dict[str,GroupsOfFoodItem]= {}

    for item in groups:
        temp = GroupsOfFoodItem(foodGroupId=item.foodGroupId, name=item.name, foodList=[])
        returnList[item.foodGroupId] = temp 
    
    for food in foods:
        _group = returnList[food.foodGroupId]
        assert(_group != None)
        assert(_group.foodGroupId == food.foodGroupId)
        _group.foodList.append(food)
    
    return returnList

def extractName(sentence: str) -> str:
    """
    Kasallap data appears to follow the formula of 
    [Name] [amount] [producer]
    where amount starts with with a number.
    Therefore, by cutting of the string when the first number appears, we are able to 
    extract the name of the product. There is also a case where Ca/ca is used right before the number.
    """
    digit_match = re.search(r'\d',sentence)
    ca_match = re.search(r'[Cc]a\d+',sentence)
    match_count = len(re.findall(r'\d',sentence))
    if ca_match:
        return sentence[:ca_match.start()]
    if digit_match:
        if digit_match.start() == 0 and match_count == 1:
            return sentence
        if digit_match.start() == 0:
           # print(sentence)
           all_matches = re.finditer(r'\d', sentence)
           _ = next(all_matches) # throw away the first match
           second_match = next(all_matches) 
           return sentence[:second_match.start()]
        return sentence[:digit_match.start()]
    return sentence 


def loadKassalapData(path: str):
    list :Dict[str,GroupsOfFoodItem] = {} 
    with open(path,"r",encoding="utf-8") as file:
        data = json.load(file)
    
    for item in data:
        categories = item["category"]
        name = extractName(item["name"]) 
        foodId = item["id"]
        for cat in categories:
            _id = cat["id"]
            entry = list.get(_id)
            if entry is None:
                list[_id] =GroupsOfFoodItem(foodGroupId=_id,name=cat["name"],foodList=[FoodItem(foodName=name,foodGroupId=_id,foodId=foodId)])
            else:
                entry.foodList.append(FoodItem(foodName=name,foodGroupId=_id,foodId=foodId))
    return list 

def fastLoad(srcPath:str) -> Dict[str,List[str]]:
    """
    A different way of stroing data, such that you do not need to manipulate it to add it to phraseMathcer.
    """
    _groups : List[FoodGroup] = loadGroups(os.path.join(srcPath,"sample_data","matvareTabellen","food-groups_no.json"))
    # print(len(_groups))

    _foods : List[FoodItem] = loadFoods(os.path.join(srcPath,"sample_data","matvareTabellen","foods_no.json"))
    # print(len(_foods))
    
    _merged = mergeData(groups=_groups, foods=_foods)


    _kassalappData = loadKassalapData(os.path.join(srcPath,"sample_data","kassalappen","filtered_foods.json"))

    returnList: Dict[str,List[str]] = {}
    
    for _,_group in _merged.items():
        returnList[_group.name] = [item.foodName for item in _group.foodList]
        
    for _,_group in _kassalappData.items():
        _list =  [item.foodName for item in _group.foodList]
        # grabs existing entry or creates new one
        existing_list = returnList.setdefault(_group.name,_list)
        if existing_list != _list:
            existing_list.extend(_list)

    # Dump it if you need to debug the outuput.
    # with open("./classification/fast_load.json", "w", encoding="utf-8") as file3:
        # json.dump(returnList,file3, cls=CustomEncoder)

    return returnList


def main():
    _groups : List[FoodGroup] = loadGroups("../sample_data/matvareTabellen/food-groups_no.json")
    print(len(_groups))

    _foods : List[FoodItem] = loadFoods("../sample_data/matvareTabellen/foods_no.json")
    print(len(_foods))
    
    _merged = mergeData(groups=_groups, foods=_foods)

    for k,v in _merged.items():
        if len(v.foodList) == 0:
            print(k, v.name)
        
    # from observation in "MELK" category, only the first word is the product name, everything after first comma is additional details.
    with open("./classification/matvaretabell_grupper.json","w", encoding="utf-8") as file:
        json.dump(_merged,file, cls=CustomEncoder)

    _kassalappData = loadKassalapData("../sample_data/kassalappen/filtered_foods.json")
    with open("./classification/kassalapp_grupper.json", "w", encoding="utf-8") as file3:
        json.dump(_kassalappData,file3, cls=CustomEncoder)

if __name__ == "__main__":
    main()

