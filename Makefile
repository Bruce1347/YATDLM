test:
	python yatdlm/manage.py test yatdlm

lint:
	isort $$(git diff --name-only --cached)
	black $$(git diff --name-only --cached)