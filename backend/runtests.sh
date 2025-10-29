#!/bin/bash

function poetry_func () {
  echo "poetry install..."
  poetry install --no-interaction
}

function lint() {
  echo "Lint backend code..."
  ruff check --exclude hunter $lintargs .
}

function format() {
  echo "Format python code..."
  ruff format --exclude hunter $ruffargs .
}

function unit() {
  echo "Run unit tests..."
  poetry run pytest tests
}

function integration() {
  echo "Run integration tests..."
  poetry run pytest integration_tests
}

function perf() {
  echo "Run performance tests..."
  if [ "$deploy" = "true" ]
  then
    cd ..
    docker compose -f docker-compose.dev.yml up -d
    cd backend
  fi

  pytest --benchmark-disable-gc --benchmark-warmup=on --benchmark-max-time=10 --benchmark-save=results benches/

  if [ "$deploy" = "true" ]
  then
    # Dump the logs in case of failure
    docker compose -f docker-compose.dev.yml logs
    docker compose -f docker-compose.dev.yml down
  fi

}

fix=false
deploy=false

for opt in "$@"; do
  echo "$opt"

  case ${opt} in
    --fix)
      fix=true
      ;;
    --deploy)
      deploy=true
      ;;
    format)
      if [ "$fix" = "true" ]
      then
        ruffargs=""
      else
        ruffargs="--check"
      fi
      format
      ;;
    lint)
      if [ "$fix" = "true" ]
      then
        lintargs="--fix"
      else
        lintargs=""
      fi
      lint
      ;;
    poetry)
      poetry_func
      ;;
    unit)
      unit
      ;;
    int)
      integration
      ;;
    perf)
      perf
      ;;
    all)
      format
      lint
      poetry_func
      unit
      # perf
      ;;
    ?)
      echo "Invalid option: ${opt}."
      echo "Usage: runtests.sh format|lint|unit|all"
      exit 1
      ;;
  esac
done
