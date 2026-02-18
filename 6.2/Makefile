SHELL := /bin/bash

.PHONY: lint test cov html clean

lint:
	@echo "🔎 Linting with flake8 and pylint..."
	flake8 src tests
	pylint src/reservation tests

test:
	@echo "🧪 Running unit tests with coverage..."
	coverage erase
	coverage run -m unittest discover -s tests -p "*_test.py" -v

cov: test
	@echo "📈 Coverage (text report)"
	coverage report -m --include="src/*"

html: test
	@echo "🌐 Generating HTML coverage..."
	coverage html
	@echo "Open: htmlcov/index.html"

clean:
	@echo "🧹 Cleaning coverage artifacts..."
	rm -rf .coverage htmlcov