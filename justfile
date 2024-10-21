list:
    @just --list

# Install the application
install:
    @poetry install

# Run the application
run *args:
    @poetry run beepy_network_manager {{args}}

# Run the tests
test:
    @poetry run pytest tests

# Initialize the application
init:
    poetry install
    echo "Application initialized successfully."
    poetry run pre-commit install
    echo "Pre-commit hooks set up."

# Format the code
format:
    @poetry run black .
    @poetry run isort .

# Type check the code
type-check:
    @poetry run mypy src tests

# Lint the code
lint:
    @poetry run flake8 src tests

# Run all checks (format, type-check, lint, test)
check-all:
    @just format
    @just type-check
    @just lint
    @just test
