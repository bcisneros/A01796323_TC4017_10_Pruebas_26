#!/bin/bash
python source/wordCount.py tests/TC1.txt tests/TC2.txt tests/TC3.txt tests/TC4.txt tests/TC5.txt

# Validar todo con trazas
python source/validateResults.py \
  --results results/WordCountResults.txt \
  --expected-dir tests \
  --pattern "TC*.Results.txt" \
  --debug=0