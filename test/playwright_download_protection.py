"""
Playwright integration tests for PR #1091 download protection.

Tests run against a live server (default: test.unglue.it).
Requires: pip install playwright && playwright install chromium

Usage:
    # Against test.unglue.it (default)
    python test/playwright_download_protection.py

    # Against local dev
    BASE_URL=http://localhost:8000 python test/playwright_download_protection.py

Tests 1-4 use the browser. Tests 5-6 use curl-style HTTP requests.

Note on Test 1/4 and headless mode:
    With a real Cloudflare sitekey, Turnstile detects headless browsers and
    withholds the token. This is expected — it proves Turnstile is working.
    With the test sitekey (1x00000000000000000000BB), the token is always
    issued even in headless mode, enabling full CI coverage.

See frontend/tests.py for Django unit tests of server-side logic (no network needed).
"""

import asyncio
import os
import sys
import urllib.request

from playwright.async_api import async_playwright

BASE_URL = os.environ.get('BASE_URL', 'https://test.unglue.it')

# 23rd Century Romance — has 3 S3-hosted ebook files
WORK_ID = 130413
EBOOK_ID = 1132
DOWNLOAD_PAGE = f"{BASE_URL}/work/{WORK_ID}/download/"
DOWNLOAD_URL = f"{BASE_URL}/download_ebook/{EBOOK_ID}/"

PASS = "\033[32m✓ PASS\033[0m"
FAIL = "\033[31m✗ FAIL\033[0m"
NOTE = "\033[33m  NOTE\033[0m"

results = []


def record(name, passed, detail=''):
    results.append((name, passed, detail))
    status = PASS if passed else FAIL
    print(f"  {status}: {name}")
    if detail:
        print(f"         {detail}")


async def run_browser_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # --- Test 1: Turnstile widget present with correct attributes ---
        print("\nTest 1: Turnstile widget present on download page")
        await page.goto(DOWNLOAD_PAGE, wait_until="load")

        # The base template also has a cf-turnstile widget (search, enableSubmit).
        # Target specifically the download widget by data-callback attribute.
        widget = await page.query_selector("div.cf-turnstile[data-callback='enableDownloads']")
        if widget:
            callback = await widget.get_attribute("data-callback")
            appearance = await widget.get_attribute("data-appearance")
            sitekey = await widget.get_attribute("data-sitekey")
            record(
                "download widget has correct attributes",
                callback == "enableDownloads" and appearance == "interaction-only",
                f"callback={callback}, appearance={appearance}, sitekey={sitekey[:15]}..."
            )
        else:
            record("download widget present", False,
                   "cf-turnstile[data-callback=enableDownloads] not found")

        fn_defined = await page.evaluate("typeof enableDownloads === 'function'")
        record("enableDownloads function defined", fn_defined)

        # Check if token was appended (only works with test sitekey in headless mode)
        await page.wait_for_timeout(3000)
        links = await page.query_selector_all("a[href*='/download_ebook/']")
        token_found = False
        for link in links:
            href = await link.get_attribute("href") or ""
            if "cf-turnstile-response" in href:
                token_found = True
                break
        if token_found:
            record("Turnstile issued token and appended to download links", True)
        else:
            print(f"{NOTE}: no token in links — expected with real sitekey in headless mode")
            print(f"         (Turnstile correctly detected headless browser)")
            print(f"         With test sitekey (1x00000000000000000000BB) this would pass in CI")

        # --- Test 2: Direct URL without token redirects to download page ---
        print("\nTest 2: Direct URL without token redirects to download page")
        await page.goto(DOWNLOAD_URL, wait_until="domcontentloaded")
        final_url = page.url
        passed = "/work/" in final_url and "/download/" in final_url
        record(
            "no-token redirect to download page",
            passed,
            f"landed at: {final_url}"
        )

        # --- Test 3: Fake token is rejected ---
        print("\nTest 3: Fake token rejected by Cloudflare siteverify")
        await page.goto(f"{DOWNLOAD_URL}?cf-turnstile-response=FAKEFAKE",
                        wait_until="domcontentloaded")
        final_url = page.url
        passed = "/work/" in final_url and "/download/" in final_url
        record(
            "fake token rejected, redirected back",
            passed,
            f"landed at: {final_url}"
        )

        # --- Test 4: Page structure correct for real users ---
        print("\nTest 4: Download page structure correct for real users")
        await page.goto(DOWNLOAD_PAGE, wait_until="load")
        download_links = await page.query_selector_all("a[href*='/download_ebook/']")
        record(
            "download links present on page",
            len(download_links) > 0,
            f"found {len(download_links)} download link(s)"
        )

        await page.screenshot(path="/tmp/download_page_test.png", full_page=True)
        print(f"  Screenshot: /tmp/download_page_test.png")

        await browser.close()


def run_curl_tests():
    # --- Test 5: Known bot UA → 403 ---
    print("\nTest 5: Known bot UA is blocked (403)")
    bot_uas = [
        ('GPTBot/1.0', 'OpenAI GPTBot'),
        ('Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)', 'Anthropic ClaudeBot'),
        ('Mozilla/5.0 (compatible; PerplexityBot/1.0)', 'PerplexityBot'),
    ]
    for ua, name in bot_uas:
        req = urllib.request.Request(DOWNLOAD_URL, headers={'User-Agent': ua})
        try:
            urllib.request.urlopen(req)
            record(f"{name} blocked", False, "got 200 — not blocked!")
        except urllib.error.HTTPError as e:
            record(f"{name} blocked", e.code == 403, f"HTTP {e.code}")
        except urllib.error.URLError as e:
            record(f"{name} blocked", False, str(e))

    # --- Test 6: Normal UA → 302, not 403 ---
    print("\nTest 6: Normal browser UA gets 302, not 403")
    normal_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    # Use requests-style: disable redirects by catching the 302 as an HTTPError
    class NoRedirect(urllib.request.HTTPErrorProcessor):
        def http_response(self, request, response):
            return response
        https_response = http_response

    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(DOWNLOAD_URL, headers={'User-Agent': normal_ua})
    try:
        resp = opener.open(req)
        code = resp.status
        record("normal UA redirected (not hard-blocked)", code == 302, f"HTTP {code}")
    except urllib.error.HTTPError as e:
        record("normal UA not hard-blocked", e.code != 403, f"HTTP {e.code}")


async def main():
    print(f"\n{'='*60}")
    print(f"Download Protection Tests — {BASE_URL}")
    print(f"{'='*60}")

    run_curl_tests()
    await run_browser_tests()

    print(f"\n{'='*60}")
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    print(f"Results: {passed}/{total} passed")
    if passed < total:
        print("Failed:")
        for name, p, detail in results:
            if not p:
                print(f"  ✗ {name}: {detail}")
    print(f"{'='*60}\n")

    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
