# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports noiist
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place noiist --exclude=__init__.py
black .
isort noiist
mypy noiist
isort --check-only noiist
flake8
black noiist --check
