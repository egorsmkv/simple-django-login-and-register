check:
	ruff check

mypy:
	PYTHONPATH=source mypy source/

fmt:
	ruff format
	find source/ -name '*.html' | xargs djade --target-version '5.2'
