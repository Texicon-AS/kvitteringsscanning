"""
@file
@brief
@remarks
- API: https://docs.python.org/3/library/csv.html
- challgen:
"""
from typing import List, Any
from dataclasses import dataclass, field
import csv

@dataclass
class LoadData:
    """
    @brief
    @remarks
    """
    filePath : str
    def __post_init__(self):
        self.rows = self.__parse(self.filePath)
    @staticmethod
    def __parse(filePath : str) -> List[Any]:
        with open(filePath, newline='') as csvfile:
            data = csv.reader(csvfile, delimiter=';', quotechar='|')
            #print(', '.join(row))
            rows : List[Any] = []
            for row in data:
                rows.append(row)
            return rows
    #def rows(self) -> List[Any]:
    #    return arrRows

@dataclass
class ProductAndQuantity:
    """
    @brief
    @remarks
    """
    productString : str
    quanity : str

@dataclass
class MatrixOfProductAndQuantity:
    """
    @brief
    @remarks
    """
    _data : List[ProductAndQuantity] =  field(default_factory=lambda: [])
    def __post_init__(self):
        filePath : str = "../../sample_data/openfoodfacts_export.csv"
        matrix = LoadData(filePath).rows
        for row in matrix:
            assert(len(row) == 2)
            self._data.append(ProductAndQuantity(row[0], row[1]))
    @property
    def rows(self) -> List[ProductAndQuantity]:
        return self._data


if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    objData = MatrixOfProductAndQuantity()
    assert(len(objData.rows))
    for entry in objData.rows:
        #print("data=", objData.rows)
        print("data=", entry.productString)
    #assert(False) # FIXME: complete ""
    assert(False) # FIXME: update "tut-enumerateMatches.py"
