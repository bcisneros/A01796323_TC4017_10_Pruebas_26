#!/bin/bash

python computeSales.py TC1/TC1.ProductList.json TC1/TC1.Sales.json --outdir TC1
python computeSales.py TC1/TC1.ProductList.json TC2/TC2.Sales.json --outdir TC2
python computeSales.py TC1/TC1.ProductList.json TC3/TC3.Sales.json --outdir TC3

# Validate results

python validateResults.py --expected Results.txt --cases TC1 TC2 TC3