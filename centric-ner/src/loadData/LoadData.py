"""
@file
@brief
@remarks
- API: https://docs.python.org/3/library/csv.html
- challgen:
"""
import json
from typing import List, Any
from typing import cast
from dataclasses import dataclass, field
import csv
from typeguard import typechecked

@typechecked
@dataclass
class LoadData:
    """
    @brief
    @remarks
    """
    filePaths : List[str]
    def __post_init__(self):
        self.rows = []
        for path in self.filePaths:
            if path.endswith(".txt"):
                self.rows.extend(self.__parse(path))
            else:
                self.rows.extend(self.__parseJson(path))
    @staticmethod
    def __parse(filePath : str) -> List[Any]:
        with open(filePath, newline='') as csvfile:
            data = csv.reader(csvfile, delimiter=';', quotechar='|')
            #print(', '.join(row))
            rows : List[Any] = []
            for row in data:
                rows.append(row)
            return rows
    
    @staticmethod
    def __parseJson(filePath: str) -> List[Any]:
        with open(filePath,"r", encoding="utf-8") as f:
            data = json.load(f)
        
        rows : List[Any] = []
        for i, item in enumerate(data):
            if i > 1000: #! FIXME remove 1000 item limit after testing
                break
            try:
                # Check if name exists and is not empty
                if not item.get("name"):
                    print(f"Skipping item {i}: Missing name field")
                    continue
                    
                # Cast to strings and strip whitespace
                name = str(item["name"]).strip()
                weight = str(item.get("weight", "")).strip()
                unit = str(item.get("weight_unit", "")).strip()
                
                # Validate name is not empty after stripping
                if not name:
                    print(f"Skipping item {i}: Empty name after processing")
                    continue
                    
                # If both weight and unit are empty, append only name
                if not weight and not unit:
                    rows.append([name])
                else:
                    rows.append([name, weight + unit])
                
            except Exception as e:
                print(f"Error processing item {i}: {e}")
        return rows




    @classmethod
    def parseListOfStrings(cls, filePath : str) -> List[str]:
        """
        @return a list of rows
        """
        parser = cls([filePath])
        rowsRaw = parser.rows
        arrRows : List[str] = []
        for row in rowsRaw:
            if(isinstance(row, list)):
                assert(len(row) == 1) #! ie, the expected usage <-- when need extend to other funcoianrities
                string = row[0]
            else:
                string = cast(str, row)
            assert(isinstance(string, str))
            arrRows.append(string)
        return arrRows

@typechecked
@dataclass
class ProductAndQuantity:
    """
    @brief
    @remarks
    """
    productString : str
    quanity : str
    def __post_init__(self):
        self.quanity = self.quanity.strip() #! ie, remvoe any whtie space paddings

@typechecked
@dataclass
class MatrixOfProductAndQuantity:
    """
    @brief
    @remarks
    """
    filePaths : List[str] = field(default_factory=lambda : ["../../sample_data/openfoodfacts_export.txt","../../sample_data/kassalappen/filtered_foods_with_weights.json"])
    _data : List[ProductAndQuantity] =  field(default_factory=lambda: [])
    def __post_init__(self):
        matrix = LoadData(self.filePaths).rows
        for row in matrix:
            assert(len(row) == 2)
            self._data.append(ProductAndQuantity(row[0], row[1]))
    @property
    def rows(self) -> List[ProductAndQuantity]:
        return self._data

@typechecked
def main():
    """
    @brief
    @remarks
    """
    objData = MatrixOfProductAndQuantity()
    assert(len(objData.rows))
    for entry in objData.rows:
        #print("data=", objData.rows)
        #print("data=", entry.productString)
        pass

    #! Validate loading of a file:
    filePath : str = "../../sample_data/case_splitProductAndVolumenNormalizeName.txt"
    arrProdEntries = LoadData.parseListOfStrings(filePath)
    assert(arrProdEntries)

if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    main()
