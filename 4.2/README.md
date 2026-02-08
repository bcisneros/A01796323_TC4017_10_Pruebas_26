# Activity 4.2 – Programming Exercises (Python, PEP‑8, PyLint)

## 📘 Overview

This repository contains the implementation of the **three programming exercises** required for **Activity 4.2**:

1. Descriptive Statistics Calculator
2. Decimal to Binary/Hexadecimal Converter
3. Word Frequency Counter

All programs:

- ✔ Are implemented in Python
- ✔ Follow PEP‑8 standards
- ✔ Have been validated using PyLint
- ✔ Use basic algorithms only (no math/statistics or conversion libraries)
- ✔ Generate both console output and results files
- ✔ Include error handling
- ✔ Display execution time

The assignment focuses on:

- Understanding the importance of coding style.
- Identifying errors through static analysis tools.
- Applying recognized industry coding standards.
- Running and documenting all test cases for the three programs.

## 🧮 Program 1 — Compute Statistics

### Purpose

Reads a file of numeric values and computes:

- Count
- Mean
- Median
- Mode (supports multiple modes)
- Population & Sample Variance
- Population & Sample Standard Deviation
- Elapsed execution time

### Key Features

- Detects **invalid tokens** (letters mixed with numbers, commas, malformed entries, etc.).
- Supports **very large numbers** (e.g., TC6, TC7) with high‑precision processing.
- Implements both **population** and **sample** formulas.
- Fully compliant with **PEP‑8** and validated with **PyLint**.
- Support multiple files

### Example

File Content:

```
10
20
30
10
40
50
60
70
80
100
```

Execute program:

```
$ cd P1
$ python source/computeStatistics.py tests/example.txt
=== Descriptive Statistics (tests/example.txt) ===

Metric                  |      Value
------------------------+-----------
Count                   |         10
Mean                    |         47
Median                  |         45
Mode                    |         10
Population Std Dev      |         29
Population Variance     |        841
Sample Std Dev          |  30.568684
Sample Variance         |  934.44444
Elapsed Time (seconds)  |  0.0019343

=== Batch Summary ===
Files processed: 1
Total elapsed time (seconds): 0.001976
```

### ✔ Program Requirements Check

- ✔ **Req 1**: The program is be invoked from the command line and receives a file as parameter.
  The file contains a list of items (presumably numbers).
- ✔ **Req 2**: The program computes all descriptive statistics using basic algorithms only:
  - Mean
  - Median
  - Mode
  - Standard Deviation
  - Variance

  The results are printed both on screen and in a file named `StatisticsResults.txt`.

- ✔ **Req 3**: The program handles invalid data inside the file. Errors are displayed on the console, and execution continues.

- ✔ **Req 4**: The program name is `computeStatistics.py`

- ✔ **Req 5**: The invocation format is:

  ```
  python computeStatistics.py fileWithData.txt
  ```

- ✔ **Req 6**: The program supports files with hundreds to thousands of data items.

- ✔ **Req 7**: Execution time is displayed and written into the results file.

- ✔ **Req 8**: The program IS PEP‑8 compliant.

### Skills Demonstrated

- Control structures
- Console I/O
- Mathematical computation
- File management
- Error handling

## 🔢 Program 2 — Converter (Decimal → Binary / Hex)

### Purpose

Converts decimal integers (positive, negative, and invalid cases) into:

- Binary
- Hexadecimal

### Key Features

- Preserves the input order.
- Invalid entries are reported as **#VALUE!** as shown in the expected output files.
- Supports negative numbers.
- Outputs formatted conversion tables.
- Fully PEP‑8 compliant and validated with PyLint.
- Support multiple files

### Example

File Content:

```
1
5
10
23
45
128
256
9999
10299
```

Execute program:

```
$ cd P2
$ python source/convertNumbers.py tests/example.txt
=== tests/example.txt Conversions (Line, Decimal → Binary, Hex) ===

Line  |  Decimal  |          Binary  |   Hex
------+-----------+------------------+------
   1  |        1  |               1  |     1
   2  |        5  |             101  |     5
   3  |       10  |            1010  |     A
   4  |       23  |           10111  |    17
   5  |       45  |          101101  |    2D
   6  |      128  |        10000000  |    80
   7  |      256  |       100000000  |   100
   8  |     9999  |  10011100001111  |  270F
   9  |    10299  |  10100000111011  |  283B

Total valid items: 9
Elapsed Time (seconds): 0.000279
```

### ✔ Program Requirements Check

- ✔ **Req 1**: Program is invoked from command line with a file containing numbers.
- ✔ **Req 2**: Convert each number to:
  - Binary (base 2)
  - Hexadecimal (base 16)

  using basic algorithms only (no built‑in converters).
  Output is printed on screen and in: `ConvertionResults.txt`

- ✔ **Req 3**: Invalid data is detected and reported on console. Program continues execution.
- ✔ **Req 4**: Program name is `convertNumbers.py`
- ✔ **Req 5**: The invocation format is:

  ```
  python convertNumbers.py fileWithData.txt
  ```

- ✔ **Req 6**: Process files ranging from hundreds to thousands of items.
- ✔ **Req 7**: Execution time is shown and written into the results file.
- ✔ **Req 8**: Strictly follows PEP‑8.

### Skills Demonstrated

- Control structures
- Console I/O
- Error handling

## 📝 Program 3 — Count Words

### Purpose

Processes a text file and generates a frequency table of unique words.

### Operations

- Removes non‑alphabetic characters.
- Counts total valid words and distinct words.
- Orders output by:
  - Higher frequency
  - Alphabetically
- Support multiple files

### Example

File Content:

```
four
one
two
three
four
two
three
four
three
four
```

Execute program:

```
$ cd P3
$ python source/wordCount.py tests/example.txt
=== tests/example.txt — Word Count (Distinct Words & Frequencies) ===

No.  |  Word   |  Frequency
-----+---------+-----------
  1  |  four   |          4
  2  |  three  |          3
  3  |  two    |          2
  4  |  one    |          1

Total valid words: 10
Distinct words: 4
Elapsed Time (seconds): 0.000198
```

### ✔ Program Requirements Check

- ✔ **Req 1**: The program is invoked from a command line. The program receives a file as parameter. The file will contain a words (presumable between spaces).

- ✔ **Req 2**: The program identifies all distinct words and the frequency of them (how many times the word “X” appears in the file). The results are printed on a screen and on a file named `WordCountResults.txt`. All computation is calculated using the basic algorithms, not functions or libraries.

- ✔ **Req 3**: The program includes the mechanism to handle invalid data in the file. Errors are displayed in the console and the execution continues.
- ✔ **Req 4**: The name of the program is `wordCount.py`
- ✔ **Req 5**: The minimum format to invoke the program is as follows:
  ```
  python wordCount.py fileWithData.txt
  ```
- ✔ **Req 6**: The program manages files having from hundreds of items to thousands of items.
- ✔ **Req 7**: The program includes at the end of the execution the time elapsed for the execution and calculus of the data. This number is included in the results file and on the screen.
- ✔ **Req 8**: Is compliant with PEP8.
