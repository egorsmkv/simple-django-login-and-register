check:
	ruff check

mypy:
	cd source && PYTHONPATH=. mypy . --check-untyped-defs

pyrefly:
	pyrefly check

fmt:
	ruff format
	find source/ -name '*.html' | xargs djade --target-version '5.2'
