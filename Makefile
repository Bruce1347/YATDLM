test:
	poetry run python yatdlm/manage.py test --settings=yatdlm.test_settings yatdlm

test_debug:
	poetry run python yatdlm/manage.py test --settings=yatdlm.test_settings --pdb yatdlm

test_fast:
	poetry run python yatdlm/manage.py test --settings=yatdlm.test_settings --keepdb --durations=0 -v 3 --parallel 8 yatdlm

test_fast_failed:
	poetry run python yatdlm/manage.py test --settings=yatdlm.test_settings --failed --keepdb -v 3 --parallel 8 yatdlm

coverage:
	poetry run coverage run
	poetry run coverage html

dev:
	poetry run python yatdlm/manage.py runserver

lock:
	poetry lock --no-update

lock_update:
	poetry lock

pylint:
	poetry run pylint $$(git diff --name-only --cached)

lint:
	poetry run isort $$(git diff --name-only --cached)
	poetry run black $$(git diff --name-only --cached)
