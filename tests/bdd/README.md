# BDD Smoke Tests

HTTP-level smoke tests for unglue.it instances using pytest-bdd. These tests verify endpoints return expected status codes and content — they don't require a local Django environment.

## Setup

```bash
pip install -r tests/bdd/requirements.txt
```

## Running

```bash
# Against production (default)
pytest --rootdir=tests/bdd

# Against a specific instance
pytest --rootdir=tests/bdd --base-url=https://test.unglue.it
pytest --rootdir=tests/bdd --base-url=https://dj42.unglue.it

# Compare all instances
for url in https://unglue.it https://test.unglue.it https://dj42.unglue.it; do
    echo "=== $url ===" && pytest --rootdir=tests/bdd --base-url=$url -q
done
```

The `--rootdir=tests/bdd` flag is required to avoid importing the root `regluit` package (which pulls in Celery and Django settings).
