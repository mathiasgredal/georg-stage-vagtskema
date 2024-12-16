venv:
	rm -rf .venv
	python3 -m venv venv
	pip install -e '.[dev]'
	echo 'venv created'

.PHONY: lint
lint: venv
	@echo 'linting' & \
	venv/bin/ruff check src & \
	venv/bin/ruff format --check src & \
	echo 'linting done' & \
	venv/bin/mypy src

.PHONY: run
run: venv
	@echo 'running' & \
	venv/bin/python src/georgstage & \
	echo 'running done'