.PHONY: lint test cov html

lint:
    flake8 src tests
    pylint src/reservation tests

test:
    coverage erase
    coverage run -m unittest discover -s tests -p "*_test.py" -v

cov: test
    coverage report -m --include="src/*"

html: test
    coverage html
