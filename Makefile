test:
	python yatdlm/manage.py test yatdlm

test_debug:
	python yatdlm/manage.py test --pdb yatdlm

test_fast:
	python yatdlm/manage.py test --keepdb yatdlm

dev:
	python yatdlm/manage.py runserver

lock:
	poetry lock --no-update

lock_update:
	poetry lock

pylint:
	pylint $$(git diff --name-only --cached)

lint:
	isort $$(git diff --name-only --cached)
	black $$(git diff --name-only --cached)
