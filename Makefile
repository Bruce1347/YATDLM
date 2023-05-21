test:
	python yatdlm/manage.py test yatdlm

test_fast:
	python yatdlm/manage.py test --keepdb yatdlm

lint:
	isort $$(git diff --name-only --cached)
	black $$(git diff --name-only --cached)