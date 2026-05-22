.PHONY: ci ci-image ci-inner lint format format-check test

CI_IMAGE ?= nyrkio-ci
CI_DOCKERFILE ?= Dockerfile.ci

CI_RUN = docker run --rm -v $(CURDIR):/repo -w /repo $(CI_IMAGE)

ci-image:
	if docker buildx version >/dev/null 2>&1; then \
		docker buildx build --load -t $(CI_IMAGE) -f $(CI_DOCKERFILE) . ; \
	else \
		docker build -t $(CI_IMAGE) -f $(CI_DOCKERFILE) . ; \
	fi

ci:
	$(MAKE) ci-image
	$(CI_RUN) make ci-inner

lint: ci-image
	$(CI_RUN) make lint-inner

format: ci-image
	$(CI_RUN) make format-inner

format-check: ci-image
	$(CI_RUN) make format-check-inner

test: ci-image
	$(CI_RUN) make test-inner

ci-inner: lint-inner format-check-inner test-inner

lint-inner:
	@if [ "$${CI_IN_CONTAINER:-}" != "1" ]; then \
		$(MAKE) lint; \
	else \
		cd backend && poetry run ruff check . --exclude hunter; \
	fi

format-inner:
	@if [ "$${CI_IN_CONTAINER:-}" != "1" ]; then \
		$(MAKE) format; \
	else \
		cd backend && poetry run ruff format . --exclude hunter; \
	fi

format-check-inner:
	@if [ "$${CI_IN_CONTAINER:-}" != "1" ]; then \
		$(MAKE) format-check; \
	else \
		cd backend && poetry run ruff format . --exclude hunter --check; \
	fi

test-inner:
	@if [ "$${CI_IN_CONTAINER:-}" != "1" ]; then \
		$(MAKE) test; \
	else \
		cd backend && poetry run pytest tests; \
	fi
