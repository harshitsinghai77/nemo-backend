# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports nemo
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place nemo --exclude=__init__.py
black .
isort .
mypy nemo
isort nemo
flake8
black nemo
