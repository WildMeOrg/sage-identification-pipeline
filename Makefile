all: build ## Build sage_identification_pipeline wheel

setup: ## Install dependencies
	python3 -m venv .venv
	./.venv/bin/python -m pip install --upgrade pip
	./.venv/bin/python -m pip install -r requirements.txt
	./.venv/bin/python -m pip install --editable .

poetry: ## Install dependencies
	poetry install -vvv

purge: ## Purge previous build
	rm -rf build dist sage_identification_pipeline.egg-info

clean: purge ## Clean
	rm -rf app-data
	rm -rf .venv poetry.lock .pytest_cache h2o_wave.state
	find . -type d -name "__pycache__" -exec rm -rf \;

reset:
	rm -rf app-data
	rm -rf .pytest_cache h2o_wave.state
	find . -type d -name "__pycache__" -exec rm -rf \;

run: ## Run the app with no reload
	./.venv/bin/wave run --no-reload sage_identification_pipeline/app.py

dev: ## Run the app with active reload
	./.venv/bin/wave run sage_identification_pipeline/app.py

help: ## List all make tasks
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
