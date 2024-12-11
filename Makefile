sources = src tests 

.venv:
	rm -rf .venv
	uv venv
	uv pip install -e '.[dev]'
	echo 'venv created'

.PHONY: lint
lint: .venv
	@echo 'linting' & \
	uv run ruff check src & \
	uv run ruff format --check src & \
	echo 'linting done' & \
	uv run mypy src

.PHONY: run
run: .venv
	@echo 'running' & \
	uv run python src/main.py & \
	echo 'running done'