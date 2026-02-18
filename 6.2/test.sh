#!/bin/bash
coverage erase
coverage run -m unittest discover -s tests -p "*_test.py" -v
coverage report -m --include="src/*"