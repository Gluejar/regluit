"""
BDD test configuration for live endpoint testing.

Uses pytest-base-url plugin for --base-url option.

Run against any unglue.it instance:
    pytest tests/bdd/ --base-url=https://unglue.it          # production
    pytest tests/bdd/ --base-url=https://test.unglue.it     # test
    pytest tests/bdd/ --base-url=https://dj42.unglue.it     # dj42

Compare all three:
    for url in https://unglue.it https://test.unglue.it https://dj42.unglue.it; do
        echo "=== $url ===" && pytest tests/bdd/ --base-url=$url -q; done
"""
import json

import pytest
import requests
from pytest_bdd import given, when, then, parsers


# ── pytest fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="session")
def http(base_url):
    """Requests session configured for the target instance."""
    session = requests.Session()
    session.headers.update({"User-Agent": "regluit-bdd-tests/1.0"})
    session.base_url = base_url.rstrip("/")
    return session


@pytest.fixture
def get(http):
    """Shortcut: get(path) -> response."""
    def _get(path, **kwargs):
        url = f"{http.base_url}{path}"
        return http.get(url, allow_redirects=kwargs.pop("follow", True), **kwargs)
    return _get


# ── step definitions ──────────────────────────────────────────────────

@given(parsers.parse('I visit "{path}"'), target_fixture="response")
def visit_path(get, path):
    return get(path)


@given(parsers.parse('I request JSON from "{path}"'), target_fixture="response")
def request_json(get, path):
    return get(path, headers={"Accept": "application/json"})


@given(parsers.parse('I request the HTTP version of "{path}"'), target_fixture="response")
def request_http(http, path):
    url = http.base_url.replace("https://", "http://") + path
    return http.get(url, allow_redirects=False)


@given(parsers.parse('I submit a POST to "{path}" with'), target_fixture="response")
def post_with_table(http, path, datatable):
    url = f"{http.base_url}{path}"
    get_resp = http.get(url)
    csrf = get_resp.cookies.get("csrftoken", "")
    data = {}
    # datatable is list of lists; row 0 is headers, rest are data
    headers_row = datatable[0]
    for row in datatable[1:]:
        row_dict = dict(zip(headers_row, row))
        data[row_dict["field"]] = row_dict["value"]
    data["csrfmiddlewaretoken"] = csrf
    return http.post(url, data=data, headers={"Referer": url})


@then(parsers.parse("the response status is {status:d}"))
def check_status(response, status):
    assert response.status_code == status, (
        f"Expected {status}, got {response.status_code} for {response.url}"
    )


@then(parsers.parse('the page contains "{text}"'))
def page_contains(response, text):
    assert text in response.text, (
        f"Expected '{text}' in response body from {response.url}"
    )


@then(parsers.parse('the page does not contain "{text}"'))
def page_not_contains(response, text):
    assert text not in response.text, (
        f"Did not expect '{text}' in response body from {response.url}"
    )


@then(parsers.parse('the content type contains "{content_type}"'))
def check_content_type(response, content_type):
    assert content_type in response.headers.get("Content-Type", ""), (
        f"Expected Content-Type containing '{content_type}', "
        f"got '{response.headers.get('Content-Type')}'"
    )


@then("the response is valid JSON")
def check_valid_json(response):
    try:
        json.loads(response.text)
    except json.JSONDecodeError as e:
        pytest.fail(f"Response is not valid JSON: {e}")


@then(parsers.parse('the response has a "{cookie_name}" cookie'))
def check_cookie(response, cookie_name):
    assert cookie_name in response.cookies, (
        f"Expected cookie '{cookie_name}' in response"
    )


@then(parsers.parse('the response header "{header}" is present'))
def check_header(response, header):
    assert header in response.headers, (
        f"Expected header '{header}' in response"
    )


@then("the response redirects to HTTPS")
def check_https_redirect(response):
    assert response.status_code in (301, 302), (
        f"Expected redirect, got {response.status_code}"
    )
    location = response.headers.get("Location", "")
    assert location.startswith("https://"), (
        f"Expected HTTPS redirect, got Location: {location}"
    )
