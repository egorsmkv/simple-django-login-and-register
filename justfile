check:
	./.venv/bin/ruff check

fmt:
	./.venv/bin/ruff format
	git ls-files -z -- '*.html' | xargs -0 ./.venv/bin/djade --target-version '5.1'
