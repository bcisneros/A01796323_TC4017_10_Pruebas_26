#!/bin/bash

echo "Checking P1/source/computeStatistics.py with pylint"
pylint P1/source/computeStatistics.py

echo "Checking P2/source/convertNumbers.py with pylint"
pylint P2/source/convertNumbers.py

echo "Checking P3/source/wordCount.py with pylint"
pylint P3/source/wordCount.py