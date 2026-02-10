# 📘 Activity 5.2 – Sales Computation Program & Validation

This README documents the work completed for **Activity 5.2**, including:

- Overview of the `computeSales.py` program
- Requirements and implementation details
- Validation of results using `validateResults.py`
- Evidence for Pylint, Flake8, and test case execution
- Rubric‑aligned scoring information

## Overview of the Program

The main script, `computeSales.py`, processes two JSON files:

```
python computeSales.py products.json sales.json [--no-messages] [--outdir PATH]
```

### ✔ Features Implemented

- Parses a product catalog (JSON)
- Parses a sales record (JSON)
- Computes totals for each line item
- Groups results by:
  - **SALE_Date** → **SALE_ID**
- Computes totals:
  - Per sale
  - Per date
  - Grand total
- Right‑aligned numeric formatting for readability
- Outputs to:
  - Console
  - A file named `SalesResults.txt` (custom output directory supported)
- Handles invalid data gracefully (warnings, errors)
- Optional:
  - `--no-messages` to hide warning/error summary blocks
  - `--outdir PATH` to choose output destination
- Fully compliant with **PEP 8**, **Pylint**, and **Flake8** requirements

## Project Structure

```
.
├── README.md
├── Results.txt
├── TC1
│   ├── SalesResults.txt
│   ├── TC1.ProductList.json
│   └── TC1.Sales.json
├── TC2
│   ├── SalesResults.txt
│   └── TC2.Sales.json
├── TC3
│   ├── SalesResults.txt
│   └── TC3.Sales.json
├── computeSales.py
├── run.sh
└── validateResults.py
```

Where:

- `computeSales.py`: is the Python program that creates the Sales Report from Product catalog and Sales entries
- `TC{N}` folders: contains the test cases `TC{N}.Sales.json` and the output of the program for each test case inside `SalesResults.txt``
  > Note: All test cases share the same product catalog (`TC1.ProductList.json`)
- `Results.txt`: contains the expected results for each test case
- `validateResults.py`: additional script to validate the actual results vs. expected results
- `run.sh`: utility script to run all test cases and perform the validations

## Running the Program and Validate Results

### Compute Sales for a Test Case

```
$ python computeSales.py TC1/TC1.ProductList.json TC1/TC1.Sales.json --outdir TC1
```

This produces: `TC1/SalesResults.txt` file.

```
SALES RESULTS REPORT
========================================================================
01/12/23                                                         $989.65
  SALE_ID: 1                                                      $83.39
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Rustic breakfast                        1     $21.32       $21.32
    2  Sandwich with salad                     2     $22.48       $44.96
    3  Raw legums                              1     $17.11       $17.11
------------------------------------------------------------------------
  SALE_ID: 2                                                      $67.57
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Fresh stawberry                         1     $28.59       $28.59
    2  Pears juice                             2     $19.49       $38.98
------------------------------------------------------------------------
  SALE_ID: 3                                                     $144.74
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Green smoothie                          3     $17.68       $53.04
    2  Cuban sandwiche                         2     $18.50       $37.00
    3  Hazelnut in black ceramic bowl          2     $27.35       $54.70
------------------------------------------------------------------------
  SALE_ID: 4                                                      $87.23
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Tomatoes                                1     $26.03       $26.03
    2  Plums                                   1     $19.18       $19.18
    3  Fresh blueberries                       2     $21.01       $42.02
------------------------------------------------------------------------
  SALE_ID: 5                                                      $94.33
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Green smoothie                          2     $17.68       $35.36
    2  Corn                                    3     $13.55       $40.65
    3  French fries                            1     $18.32       $18.32
------------------------------------------------------------------------
  SALE_ID: 6                                                     $239.04
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Ground beef meat burger                 1     $11.73       $11.73
    2  Hazelnut in black ceramic bowl          2     $27.35       $54.70
    3  Cherry                                  2     $14.35       $28.70
    4  Homemade bread                          1     $17.48       $17.48
    5  Smoothie with chia seeds                1     $25.26       $25.26
    6  Corn                                    1     $13.55       $13.55
    7  Peaches on branch                       2     $25.62       $51.24
    8  Pesto with basil                        2     $18.19       $36.38
------------------------------------------------------------------------
  SALE_ID: 7                                                     $182.11
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Plums                                   1     $19.18       $19.18
    2  Fresh blueberries                       2     $21.01       $42.02
    3  Green smoothie                          4     $17.68       $70.72
    4  Corn                                    1     $13.55       $13.55
    5  French fries                            2     $18.32       $36.64
------------------------------------------------------------------------
  SALE_ID: 8                                                      $91.24
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Ground beef meat burger                 3     $11.73       $35.19
    2  Hazelnut in black ceramic bowl          1     $27.35       $27.35
    3  Cherry                                  2     $14.35       $28.70
------------------------------------------------------------------------

02/12/23                                                       $1,492.21
  SALE_ID: 8                                                     $316.06
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Homemade bread                          5     $17.48       $87.40
    2  Smoothie with chia seeds                2     $25.26       $50.52
    3  Corn                                   10     $13.55      $135.50
    4  Rustic breakfast                        2     $21.32       $42.64
------------------------------------------------------------------------
  SALE_ID: 9                                                     $851.43
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Sandwich with salad                     3     $22.48       $67.44
    2  Raw legums                             20     $17.11      $342.20
    3  Fresh stawberry                         4     $28.59      $114.36
    4  Pears juice                             1     $19.49       $19.49
    5  Green smoothie                          8     $17.68      $141.44
    6  Cuban sandwiche                         9     $18.50      $166.50
------------------------------------------------------------------------
  SALE_ID: 10                                                    $324.72
    #  PRODUCT                               QTY      PRICE     SUBTOTAL
    1  Hazelnut in black ceramic bowl          2     $27.35       $54.70
    2  Tomatoes                                1     $26.03       $26.03
    3  Plums                                   2     $19.18       $38.36
    4  Fresh blueberries                       3     $21.01       $63.03
    5  Green smoothie                          5     $17.68       $88.40
    6  Corn                                    4     $13.55       $54.20
------------------------------------------------------------------------

========================================================================
GRAND TOTAL:                                                   $2,481.86
Time elapsed: 0.001 seconds
========================================================================
WARNINGS
------------------------------------------------------------------------
(none)

ERRORS
------------------------------------------------------------------------
(none)
========================================================================
```

> **Note**: Repeat for each Test Case by changing the sales file and output directory

### Validate Test Cases Against Expected Results

If you want to verify the results automatically, use the following command:

```
$ python validateResults.py --expected Results.txt --cases TC1 TC2 TC3
```

It produces the following report:

```
EXPECTED VS ACTUAL RESULTS
========================================================================
Tolerance: ±0.0010

CASE         EXPECTED            GOT         DIFF   PASS
------------------------------------------------------------------------
TC1         $2,481.86      $2,481.86        +0.00  ✅ Yes
TC2       $166,568.23    $166,568.23        +0.00  ✅ Yes
TC3       $165,235.37    $165,235.37        +0.00  ✅ Yes
------------------------------------------------------------------------
Passed: 3/3
========================================================================
```

## Static Analysis Evidence

### Pylint / PEP 8 Compliance

```
$ pylint computeSales.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

$ pylint validateResults.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

### Flake8 Compliance

```
$ flake8 computeSales.py
(no output)

$ flake8 validateResults.py
(no output)
```

## Conclusions

- The program fully satisfies all functional and technical requirements.
- The layout provides clear per-date and per-sale grouping, with aligned totals.
- Static analysis tools (Pylint & Flake8) report **zero errors**, satisfying PEP 8 style standards.
- All three test cases computed correctly and were verified with the automated validator.
- Complete documentation and validation scripts are included to simplify evaluation.
