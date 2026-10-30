#The page fixture gives each test one ready-to-use page that Playwright creates and cleans up automatically.
#A browser context is a separate session container: it holds its own cookies, local storage, and cache, and can contain one or more pages.
#A fresh context starts with isolated state, so nothing typed or stored in another context or page (such as the email I filled in on the fixture page) carries over.
#That is why the email field in the new context starts empty.


import re
from playwright.sync_api import Page, Browser, expect


def test_login_page_smoke(page: Page):

    page.goto("/login")
    expect(page).to_have_title(re.compile("EventHub", re.IGNORECASE))
    expect(page.get_by_label("Email")).to_be_visible()
    expect(page.get_by_role("button", name="Sign In")).to_be_visible()



def test_page_fixture_vs_isolated_context(page: Page, browser: Browser, base_url: str):

    page.goto("/login")
    email = page.get_by_label("Email")
    email.fill("beginner@sample.com")
    expect(email).to_have_value("beginner@sample.com")


    context = browser.new_context()
    isolated_page = context.new_page()
    isolated_page.goto(f"{base_url}/login")

    expect(
        isolated_page.get_by_role("heading", name="Sign in to EventHub")
    ).to_be_visible()
    expect(isolated_page.get_by_label("Email")).to_have_value("")
    context.close()