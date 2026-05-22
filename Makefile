.PHONY: ci ci-image ci-inner lint format format-check test

CI_IMAGE ?= nyrkio-ci
CI_DOCKERFILE ?= Dockerfile.ci

ci-image:
	docker build -t $(CI_IMAGE) -f $(CI_DOCKERFILE) .

ci:
	$(MAKE) ci-image
	docker run --rm $(CI_IMAGE)

ci-inner: lint format-check test

lint:
	cd backend && poetry run ruff check . --exclude hunter

format:
	cd backend && poetry run ruff format . --exclude hunter

format-check:
	cd backend && poetry run ruff format . --exclude hunter --check

test:
	cd backend && poetry run pytest tests
