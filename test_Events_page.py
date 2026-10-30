import re
import pytest
from playwright.sync_api import Page, expect

EMAIL = "swarooparajbhan@gmail.com"          # your EventHub login
PASSWORD = "Swaru@123"    # your EventHub password


@pytest.fixture
def events_page(page: Page) -> Page:
    # Step 1: sign in and open Events from Browse Events
    page.goto("/login")
    page.get_by_label("Email").fill(EMAIL)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name=re.compile("sign in", re.I)).click()

    page.get_by_role("link", name="Browse Events", exact=True).click()
    expect(page).to_have_url(re.compile(r"/events"))
    return page


def test_events_page_locators(events_page: Page):
    page = events_page


    expect(page.get_by_role("heading", name="Upcoming Events")).to_be_visible()

    search = page.get_by_placeholder(re.compile("search", re.I))
    category = page.locator("select").filter(has=page.locator("option[value='Conference']"))
    city = page.locator("select").filter(has=page.locator("option[value='Hyderabad']"))

    search.fill("World")
    category.select_option("Conference")
    city.select_option("Hyderabad")

    expect(page).to_have_url(re.compile(r"search=World"))
    expect(page).to_have_url(re.compile(r"city=Hyderabad"))
    expect(category).to_have_value("Conference")


    cards = page.locator("article")
    expect(cards.first).to_be_visible()

    matching = cards.filter(has_text="World Tech Summit")
    expect(matching).to_have_count(1)
    card = matching.first

    #capture from that card only
    title = card.get_by_role("heading").first.inner_text().strip()
    price_text = card.get_by_text(re.compile(r"\$")).first.inner_text().strip()
    seats_text = card.get_by_text(re.compile(r"seats? left", re.I)).first.inner_text().strip()


    assert title == "World Tech Summit"
    assert "$" in price_text
    seats_match = re.search(r"\d+", seats_text)
    assert seats_match, f"No number found in seats text: {seats_text!r}"
    assert int(seats_match.group()) > 0
    card.get_by_role("link", name="Book Now").click()

    expect(page).to_have_url(re.compile(r"/events/\d+"))
    expect(page.get_by_role("heading", level=1)).to_have_text(title)
    expect(page.get_by_text(price_text).first).to_be_visible()

    #back to the list, reset filters
    page.get_by_test_id("nav-events").click()
    expect(page).to_have_url(re.compile(r"/events$"))
    expect(page.get_by_role("heading", name="Upcoming Events")).to_be_visible()

    search = page.get_by_placeholder(re.compile("search", re.I))
    category = page.locator("select").filter(has=page.locator("option[value='Conference']"))
    city = page.locator("select").filter(has=page.locator("option[value='Hyderabad']"))

    search.fill("")
    category.select_option("")   # All Categories
    city.select_option("")       # All Cities
    expect(category).to_have_value("")
    expect(city).to_have_value("")

    cards = page.locator("article")
    expect(cards.nth(2)).to_be_visible()   # auto-waits for at least 3 cards


    first = cards.first.get_by_role("heading").first
    second = cards.nth(1).get_by_role("heading").first
    last = cards.last.get_by_role("heading").first

    expect(first).not_to_be_empty()
    expect(second).not_to_be_empty()
    expect(last).not_to_be_empty()
    assert first.inner_text().strip() != last.inner_text().strip()