test:
	pytest -vv
.PHONY: test

lint:
	flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
.PHONY: lint

run_local:
	echo 'running local'
	python src/georgstage/cli.py
.PHONY: run_local
