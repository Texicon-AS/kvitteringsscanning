# The Trainer for the Food Manager project

## The structure
1. [x] Adjust the grammar-defs:
   1. [x] "MatchedEntry.py"
      1. [x] "MatchedLabel": a new class
      1. [x] "MatchedEntry": a new class
      1. [x] "MatchedEntryArr": a new class
      1. [x] write unit-tests
      1. [x] apply pylint, and resolve issues
   2. [x] "ProductAmount.py":
      1. [x] update all users of teh "unitVocabTerms" variable
      1. [x] unit-tests: updae + get to work
      1. [x] write unit-tests
      1. [x] apply pylint, and resolve issues
   3. [x] "PredictedProduct.py":
      1. [x] a new "product.getMatchedEntry()" funciotn
      1. [x] unit-tests: updae + get to work
      1. [x] write unit-tests
      1. [x] apply pylint, and resolve issues
   4. [x] "ClassifyEntry.py":
      1. [x] add test-logics for this, and a wrapper funciotn to validate the logics
      1. [x] unit-tests: updae + get to work
      1. [x] write unit-tests
      1. [x] apply pylint, and resolve issues
   5. [x] Clean the folder:
      1. [x] "ClassifyNonStandardUnits.py": <-- remvoe the assert(false); get the unit-tests to pass
         1. [x] get unit-tests to pass
         1. [x] remove print-statements
         1. [x] apply pylint, and remvoe FIXMEs
         1. [x] update the documetnaton
      1. [x] "ShapeUnitClassification.py":  <-- remvoe the assert(false); get the unit-tests to pass
         1. [x] get unit-tests to pass
         1. [x] remove print-statements
         1. [x] apply pylint, and remvoe FIXMEs
         1. [x] update the documetnaton
      1. [x] "PredictedProduct.py": replace the below "quanityValue, unit" with a reference to our new-added ProductAmount ... udpate all code using this ... then get all the unti-tests to pass
      1. [x] update the docuemtation of:
         1. [x] concrete examples of the span-idneiteis we idneityf
   2. [x] Code-sanity: update all our classes with the "@typechecked" decorator
2. [x] Build patterns:
   1. [x] "PredictNer.py": -- FIXME: merge "PredictNer.py"
      1. [x] get to work
      1. [x] remold into what we need. Then apply lininting
      1. [x] get to work
      1. [x] replace data with those from "PatternsToFind.py". Get to work
3. [x] Training:
   1. [x] "CommandLineTrainer.py":
   1. [x] "CommandLine.py":
   1. [x] "TrainModel.py"
   1. [x] "Trainer.py": configure the (model-training)[TrainModel.py]

## FUTURE: Manual Sanity Evalution and Assessment
1. Challenging cases: explore why the following cases were unable to be handeld: <-- is our "TrainModel.py" able to classify these .,.. and/or any local configurations we can set (to enable this)?
```txt
           (PredictNer.py::prediction failed for)  Yt Restitusjon Banan&Jordbær 330ml
                (PredictNer.py::prediction failed for)  Oksekraft 250ml Jacobs Utvalgte
                (PredictNer.py::prediction failed for)  Smoothie Mango&Pasjon 250ml Bendit
                (PredictNer.py::prediction failed for)  Bearnaisesaus 250ml Jacobs Utvalgte
                (PredictNer.py::prediction failed for)  Kyllingkraft 250ml Jacobs Utvalgte
                (PredictNer.py::prediction failed for)  Idyll Sjokoladeis Plantebasert 500ml Hennig-Olsen
                (PredictNer.py::prediction failed for)  Margarin Flytende u/Melk 500ml Eldorado
                (PredictNer.py::prediction failed for)  Maggi Klar Kyllingkraft 500ml
                (PredictNer.py::prediction failed for)  Fader Martin Selskapsdressing 500ml
                (PredictNer.py::prediction failed for)  Tine YT Restitusjonsdrikk Kakao 330ml
                (PredictNer.py::prediction failed for)  Maggi Klar Kyllingkraft 500ml
                (PredictNer.py::prediction failed for)  Toro Bearnaise Kjølt 300ml
                (PredictNer.py::prediction failed for)  Idyll Sjokoladeis Plantebasert 500ml Hennig-Olsen
                (PredictNer.py::prediction failed for)  Sweet Chilisaus Thai 500ml Go-Tan
                (PredictNer.py::prediction failed for)  Idyll Saltkaramell Plantebasert 500ml Hennig-Olsen
```