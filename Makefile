.PHONY: ci.update-version-in-pyproject
ci.update-version-in-pyproject:
	python scripts/update_version_in_pyproject.py $(CHANGELOG_FILENAME)
	python scripts/update_version_txt.py utt/version.txt
