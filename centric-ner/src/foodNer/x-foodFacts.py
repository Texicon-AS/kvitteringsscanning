"""
@file
@brief tries to correctly classify using our foodFacts and Kassalappen data-set
@remarks
-
- challenge:
"""
from typing import List #, Any
import traceback
from typeguard import typechecked

#from dataclasses import dataclass, field
#! Local files:
from stopWords.StopWordRemoval import StopWordRemoval
from foodNer.PredictedProduct import PredictedProduct
from loadData.LoadData import MatrixOfProductAndQuantity
from loadData.LoadData import ProductAndQuantity
from foodNer.ClassifyEntry import ClassifyEntry
from foodNer.ClassifyEntry import ClassifyEntryMultiLang, WriteProduct

@typechecked
def identifyNerAccuracy(classify : ClassifyEntryMultiLang, arrProdEntries : List[ProductAndQuantity], testDescription : str) -> None:
    """
    @brief performs logics to investigate the number of problematic entries
    @remarks
    """
    assert(arrProdEntries)
    if(True):
        for entry in arrProdEntries:
            #print("data=", objData.rows)
            print("data=", entry.productString)
    #classify = ClassifyEntryMultiLang()
    cntPassed : int = 0
    cntExceptions : int = 0
    cntUnkownQuantity : int = 0 #! ie, the prdocuts which requres a DB-lookups for knowing the amount
    cntErrorsWrongNumberIdentified : int = 0 #! ie, the number of predicotns which produced the wrong number
    cntTotal : int = 0
    print(f"[ClassifyEntry::testClassification]\t applies tests for {len(arrProdEntries)} tests; these are focused towards {testDescription}")
    for productDef in arrProdEntries:
        #print(f"predicted({productString}): ", classify.predict(productString))
        try:
            productString = productDef.productString
            product : PredictedProduct = classify.predict(productString)
            # TODO: use gold-data to udpate the below count
            parsingWasCorrect : bool = True
            if(productDef.quanity): #! then we assume the godl-result was provided:
                parsedValue = product.getQuantityAndUnit()
                if(productDef.quanity != parsedValue):
                    print(f"!!\t[x-foodFacts.py]\t Parsing produced wrong results. Expected:'{productDef.quanity}' while our system produced '{parsedValue}'") # TODO: how to give this error an empahssised/cirtial attention?
                    parsingWasCorrect = False
                    assert(False) #! ie, heads-up

            if(product.quantityIsKnown() and parsingWasCorrect):
                print(f"predicted({productString}): ", product)
                cntPassed += 1
            else:
                if(parsingWasCorrect): #! then the quantiy was unkown
                    print(f"!!\t(failed) quantity is unkown given input:\"{productString}\"): ", product)
                    cntUnkownQuantity += 1
                else:
                    assert(False) #! ie, heads-up
                    cntErrorsWrongNumberIdentified += 1
        except Exception as e:
            print(f"!!\t(failed) quantity is unkown given input:\"{productString}\"). Probelm due to the following exception", e)
            print("!!\t\t Exception due to: " +  traceback.format_exc())
            cntUnkownQuantity += 1
        except Exception as _: # TODO: indietyf mroe specific expetions
            #except:
            strErr = f"!!\t[ClassifyEntry.py::main]\t failed to analyse \"{productString}\""
            strErr += traceback.format_exc()
            print(strErr)
            cntExceptions += 1
        cntTotal += 1
    print(f"========================\n\nOK({testDescription}): {cntPassed}/{cntTotal} tests completed; had {cntErrorsWrongNumberIdentified} cases where the wrong value was idneifed  (critical!); had {cntExceptions} exceptions raised, while {cntUnkownQuantity} products missed information of quantity (thus, requring DB-lookups)")
    #classify.predict(productString)

@typechecked
def main() -> None:
    """
    @brief
    @remarks
    """

    #! -----------------------
    #! Task:
    productWriter = WriteProduct("res-foodFacts-kassalappen.txt")
    classify = ClassifyEntryMultiLang(_productWriter = productWriter)
    objData = MatrixOfProductAndQuantity(filePaths=["../../sample_data/openfoodfacts_export.txt","../../sample_data/kassalappen/foods.json"])
    identifyNerAccuracy(classify, objData.rows, "openfoodfacts-kassalappen")
    # # --------------------------------------------------------------
    # # --------------------------------------------------------------
    # # --------------------------------------------------------------
    # #! Finalize the tests
    # productWriter.closeFile()


if __name__ == "__main__":
    """
    @brief
    @remarks
    """
    main()
    #assert(False) # FIXME: validate the above!

    #! -----------------------
    #! Task:
    assert(False) # FIXME: parse: case_splitProductAndVolumenNormalizeName.txt <-- a list of strings
    assert(False) # FIXME: parse:
    assert(False) # FIXME: rewrite the above ... add stuff into this

    assert(False) # FIXME: update ""
    assert(False) # FIXME: update ""

assert(False) # FIXME:
assert(False) # FIXME: take all the files as input, and idneiwy which failed
assert(False) # FIXME:
