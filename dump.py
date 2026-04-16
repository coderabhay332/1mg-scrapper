from playwright.sync_api import sync_playwright

def dump_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        })
        page.goto("https://www.1mg.com/drugs/dolo-650-tablet-74467")
        page.wait_for_timeout(5000)
        html = page.content()
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(html)
        browser.close()

dump_html()
