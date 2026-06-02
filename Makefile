.PHONY: ci ci-image ci-inner lint format format-check test perf perf-inner perf-process-inner

CI_IMAGE ?= nyrkio-ci
CI_DOCKERFILE ?= Dockerfile.ci
EXTRA_INFO ?= /repo/extra_info.json
PERF_COMPOSE_PROJECT ?= nyrkio-perf
PERF_NETWORK ?= $(PERF_COMPOSE_PROJECT)_default
TEST_HOST ?= http://nginx

CI_RUN = docker run --rm -v $(CURDIR):/repo -w /repo
CI_RUN_PERF = docker run --rm --network $(PERF_NETWORK) -v $(CURDIR):/repo -w /repo
PERF_ENV = \
	-e NYRKIO_ENV_TESTING \
	-e NYRKIO_USERNAME \
	-e NYRKIO_PASSWORD \
	-e PULL_NUMBER \
	-e GIT_COMMIT \
	-e IMAGE_TAG \
	-e GITHUB_TOKEN \
	-e GIT_TARGET_BRANCH \
	-e TEST_HOST=$(TEST_HOST)

ci-image:
	if docker buildx version >/dev/null 2>&1; then \
		docker buildx build --load -t $(CI_IMAGE) -f $(CI_DOCKERFILE) . ; \
	else \
		docker build -t $(CI_IMAGE) -f $(CI_DOCKERFILE) . ; \
	fi

ci:
	$(MAKE) ci-image
	$(CI_RUN) $(CI_IMAGE) make ci-inner

lint: ci-image
	$(CI_RUN) $(CI_IMAGE) make lint-inner

format: ci-image
	$(CI_RUN) $(CI_IMAGE) make format-inner

format-check: ci-image
	$(CI_RUN) $(CI_IMAGE) make format-check-inner

test: ci-image
	$(CI_RUN) $(CI_IMAGE) make test-inner

perf: ci-image
	@if [ -z "$${NYRKIO_ENV_TESTING:-}" ]; then \
		echo "NYRKIO_ENV_TESTING must be set for perf tests"; \
		exit 1; \
	fi
	@if [ -d "p/frontend/src/static" ] && [ "$$(ls -A p/frontend/src/static 2>/dev/null)" ]; then mv p/frontend/src/static/* p/; fi
	@lscpu -J > extra_info.json
	@printf '%s\n' "$$NYRKIO_ENV_TESTING" > .env.backend
	@set -e; \
	trap 'docker compose -p $(PERF_COMPOSE_PROJECT) -f compose.dev.yml logs || true; docker compose -p $(PERF_COMPOSE_PROJECT) -f compose.dev.yml down || true' EXIT; \
	docker compose -p $(PERF_COMPOSE_PROJECT) -f compose.dev.yml up -d; \
	$(CI_RUN_PERF) $(PERF_ENV) $(CI_IMAGE) make perf-inner; \
	$(CI_RUN) $(PERF_ENV) $(CI_IMAGE) make perf-process-inner

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

perf-inner:
	@if [ "$${CI_IN_CONTAINER:-}" != "1" ]; then \
		$(MAKE) perf; \
	else \
		cd backend && poetry run pytest --benchmark-disable-gc --benchmark-warmup=on --benchmark-max-time=10 --benchmark-save=results benches/; \
	fi

perf-process-inner:
	@if [ "$${CI_IN_CONTAINER:-}" != "1" ]; then \
		$(MAKE) perf; \
	else \
		cd backend && poetry run python benches/process_results.py $$(find .benchmarks -name "*.json") $(EXTRA_INFO); \
	fi
