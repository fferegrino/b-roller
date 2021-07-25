TOOL_RUN=poetry run

style:
	$(TOOL_RUN) black .
	$(TOOL_RUN) isort .

lint:
	$(TOOL_RUN) pflake8 .
	$(TOOL_RUN) isort . --check-only
	$(TOOL_RUN) black . --check

patch:
	$(TOOL_RUN) bumpversion patch

minor:
	$(TOOL_RUN) bumpversion minor

major:
	$(TOOL_RUN) bumpversion major

test:
	echo "No tests for now!"
