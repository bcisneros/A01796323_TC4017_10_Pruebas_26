#!/bin/bash
python source/convertNumbers.py tests/TC1.txt tests/TC2.txt tests/TC3.txt tests/TC4.txt

python source/validateResults.py --debug