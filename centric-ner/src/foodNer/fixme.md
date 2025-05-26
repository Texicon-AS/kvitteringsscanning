The NER-test scripts:
1. [x] tut-readFile.py
1. [x]
1. [x]
1. [x]
1. [x]

## FIXME:
1. [] ClassifyEntry ---- then move
   1. [] "": a new module based on the above
   1. [] "":
   1. [] "":
   1. [] "ClassifyProduct.py":  update this based on the above
1. [] "tut-extractCardinalAndMetric.py":
   1. [] "":
   1. [] "":
1. ClassifyProduct.py
   1. [] "":
   1. [] "":
1. tut-matcher.py
1. tut-regexToClassify.py
1. tut-callback.py
1. tmp2.py
1. tut-productGrammar.py
1. tut-dependency.py
1. tmp.py
1.
1.
1.


Task. A new iteration on the spacy-grammar:
1. [] "tut-productGrammar.py"
   1. [] ?? ignroe-case pattern?
   1. [] ??
   1. [] ??
   1. [] ??

---------------
Task. Get the updated API to work:
1. [x]
1. [x]
1. [x]
1. [x]

Task. move the API from the tut-folder to the soruce-folder:
1. [x]
1. [x]
1. [x]
1. [x]

Data: apply the following data-sets to the updated API
1. openfoodfacts_export.txt
1. case_normalizeProductNames.txt
1. case_splitProductAndVolumenNormalizeName.txt
1. case_noneFoodItems.txt

-------------------------
README.md:
- update the README.md file with the above


*************************
## FIXME: answer the following:
### Searchesin the product-DB
1. how can we extraact "ost" from term="Fløtemysost" (eg, extracted from "Fløtemysost Lettere skivet 130g Tine")?
   1. pre: go through the exampels + documetnaiton at:
      1. https://spacy.io/usage/rule-based-matching
1. "Freia Sitrongele Uten Sukker 14g", # FIXME: challnging case: how to resolve/idneitfy? <-- use algorithmn-tranining for ths partciular case? <-- a better approach? <-- and, how to merge "uten sukker" in one word? <-- when needed?
1. "Majones Ekte 160g Tube Mills", # FIXME: productType= Ekte and productTypeSpecific= Majones Ekte
1. "Big 100 Cookie Dough)" # FIXME:  wrongly interprted as: PredictedProduct(product='Dough', quanityValue=100.0, unit='Dough', arrCompound=['Big', 'Cookie'], productTypeSpecific='Dough') <-- any grammar which can auto-detect this issue? <-- or, do we have a complete list of valid "units"? and the mapping between Norweigna and English?

### Stopwords
1. [ ] "tut-stop-1.py" and "": suggestions for where to get a list of product-component-pasudo-.stopwrods to use/add?
1. [ ] "productString": "Rotfrukter med Laks 8m 190g", "product": "Rotfrukter", "quanityValue": 8.0, "unit": "m", "arrCompound": ["med", "Laks", "190", "g"], "productTypeSpecific": "Rotfrukter", "compundsXmtStopWords": ["lak"]} <-- FIXME: is the "lak" issue due to "stemming"? <-- what does the "8m" mean? <-- suggestiosnf for a gammar to seperate tehse two cases? <-- eg, use the " med " word to detect this issue? a better suggesiton? <--- any broader test-set we caan use (for thsi stiatuion where we have muliple usub-products 'in one prodcut')?

### Matvaretabellen:
1. [ ] how to use information of nutrients, eg, https://www.matvaretabellen.no/adzukibonner-torr/ ?
1. [ ] go through "src/loadData/res_Matvaretabellen.txt": when + how to use this for filtering?
   1. [ ] use "sample_data/matvareTabellen/nutrients_no.json" to idneitfy non-food items? a better approach?

*************************
## AI-training
1. pre: descirbe how we can NER-train our appraoch <-- find templates to sue as a ttarting-point

*************************
## Interseting the above 'extracted elements' with the product-database. Suggestions
1. what: use the ?? db to filter for ??

1. use a vector-database togehter witht eh already added ?? DB <-- how? <--
   1. solves: queries goes fast <-- suggesitosnf ro pre-rpocessing?
   1. how: the algorithm:
      1. use our NER-approach to extract the PredictedProduct entries from the ?? DB
      1. insert these elements into a Vector-DBMS
      1. query these (when a 'kvittering' is received)
      1.

## Merge terminology
1. what terms (eg, food-names, products, metrics, ...) are overlapping? <-- then use "tut-0-normalizer.py" to update our code