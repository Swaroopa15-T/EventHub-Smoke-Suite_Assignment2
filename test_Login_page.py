                                #README
#Playwright: Core Package vs Test Runner Package

#1.playwright (Core Package):
#This is the fundamental automation library.
#It exposes the raw Python API to launch browsers, manage browser contexts,
#and manipulate pages (e.g., sync_api or async_api). It contains no testing framework,
#assertion engine, or test lifecycle management tools.

#2.pytest-playwright (Test Runner Plugin):
#This plugin couples Playwright with pytest (the industry-standard Python test runner).
#It provides automated web-first assertions (expect), manages execution loops,
#generates visual HTML reports, and yields built-in fixtures
#like page directly into your test functions.

from playwright.sync_api import Page, expect


def test_login_page(page : Page):
    page.goto("https://eventhub.rahulshettyacademy.com")
    expect(page.get_by_role("heading", name = "Sign in to EventHub")).to_be_visible()
    expect(page.get_by_placeholder("you@email.com")).to_be_visible()
    expect(page.get_by_role("button", name= "Sign In")).to_be_visible()


def test_login_page_smoke_check(page: Page):
    page.goto("https://eventhub.rahulshettyacademy.com")
    expect(page.get_by_label("password")).to_be_visible()
    page.goto("https://eventhub.rahulshettyacademy.com/login")
    expect(page.get_by_role("heading", name="Sign in to EventHub")).to_be_visible()


