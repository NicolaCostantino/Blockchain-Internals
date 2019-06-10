# Global Makefile

### Variables ###

# Default test target
TEST_TARGET = ./blockchains/

### Rules ###

install:
	pipenv install

develop:
	pipenv install --dev

clean:
	pipenv --rm

jupyter:
	pipenv run jupyter

jupyter_lab:
	pipenv run jupyter lab

test:
	pipenv run pytest --cov=$(TEST_TARGET) --cov-branch $(TEST_TARGET) -s

test_cov:
	pipenv run pytest --cov=$(TEST_TARGET) --cov-branch $(TEST_TARGET) -s

test_cov_html:
	pipenv run pytest --cov=$(TEST_TARGET) --cov-branch --cov-report=html $(TEST_TARGET) -s
