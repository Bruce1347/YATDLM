test:
	python yatdlm/manage.py test yatdlm

test_fast:
	python yatdlm/manage.py test --keepdb yatdlm

lock:
	poetry lock --no-update

lock_update:
	poetry lock

lint:
	isort $$(git diff --name-only --cached)
	black $$(git diff --name-only --cached)