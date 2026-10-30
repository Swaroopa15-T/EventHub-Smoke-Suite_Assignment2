import re
from playwright.sync_api import Page, expect

EMAIL = "swarooparajbhan@gmail.com"          # your EventHub login
PASSWORD = "Swaru@123"    # your EventHub password

CUSTOMER_NAME = "Test Customer"
CUSTOMER_EMAIL = "test.customer@example.com"
CUSTOMER_PHONE = "9876543210"


def login(page: Page):
    page.goto("/login")
    page.get_by_label("Email").fill(EMAIL)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name=re.compile("sign in", re.I)).click()
    expect(page.get_by_role("button", name="Logout")).to_be_visible()


def filter_events(page: Page, search: str, category: str, city: str):
    page.goto("/events")
    page.get_by_placeholder(re.compile("search", re.I)).fill(search)
    page.locator("select").filter(has=page.locator(f"option[value='{category}']")).select_option(category)
    page.locator("select").filter(has=page.locator(f"option[value='{city}']")).select_option(city)
    expect(page).to_have_url(re.compile(f"search={search}"))
    expect(page).to_have_url(re.compile(f"city={city}"))
    return page.locator("article")


def make_booking(page: Page, search: str, category: str, city: str, qty: int) -> dict:
    cards = filter_events(page, search, category, city)
    expect(cards).to_have_count(1)
    card = cards.first
    title = card.get_by_role("heading").first.inner_text().strip()

    card.get_by_role("link", name="Book Now").click()
    expect(page).to_have_url(re.compile(r"/events/\d+"))
    expect(page.get_by_role("heading", level=1)).to_have_text(title)

    # Quantity starts at 1, so click "+" (qty - 1) times
    for _ in range(qty - 1):
        page.get_by_role("button", name="+").click()
    expect(page.locator("main")).to_contain_text(re.compile(rf"×\s*{qty}\s*tickets?"))

    page.get_by_placeholder("Your full name").fill(CUSTOMER_NAME)
    page.get_by_placeholder("you@email.com").fill(CUSTOMER_EMAIL)
    page.get_by_placeholder("+91 98765 43210").fill(CUSTOMER_PHONE)
    page.get_by_role("button", name="Confirm Booking").click()

    # Wait for the confirmation (auto-waits)
    expect(page.get_by_role("heading", name=re.compile("Booking Confirmed"))).to_be_visible()

    text = page.locator("main").inner_text()
    m = re.search(
        r"Booking Ref\s*(\S+)\s*Customer\s*(.+?)\s*Tickets\s*(\d+)\s*Total\s*(\$[\d,]+(?:\.\d+)?)",
        text, re.S,
    )
    assert m, f"Could not read the confirmation:\n{text}"

    return {
        "title": title,
        "ref": m.group(1),
        "tickets": int(m.group(3)),
        "total": m.group(4),
        "email": CUSTOMER_EMAIL,
    }


def find_card(page: Page, ref: str):
    """Find a booking card by reference text only: the nearest ancestor of the
    reference badge that also contains the View Details button."""
    badge = page.get_by_text(ref, exact=True)
    expect(badge).to_have_count(1)
    return badge.locator("xpath=ancestor::*[.//*[normalize-space()='View Details']][1]")


def payment_summary(page: Page):
    """The Payment Summary block: the container holding the heading, tickets and total."""
    return page.locator("main").locator(
        "xpath=//h2[normalize-space()='Payment Summary']/parent::*"
    )


def test_two_bookings_reconcile(page: Page):
    login(page)

    # Steps 1-3
    b1 = make_booking(page, "World", "Conference", "Hyderabad", qty=1)
    assert b1["title"] == "World Tech Summit"
    assert b1["ref"].strip() != ""
    assert b1["tickets"] == 1

    # Steps 4-5
    b2 = make_booking(page, "Dilli", "Festival", "Delhi", qty=2)
    assert b2["ref"] != b1["ref"]
    assert b2["title"] != b1["title"]
    assert b2["tickets"] == 2

    # Steps 6-8
    page.goto("/bookings")
    for b in (b1, b2):
        card = find_card(page, b["ref"])
        expect(card).to_be_visible()
        expect(card).to_contain_text(re.compile("confirmed", re.I))
        expect(card).to_contain_text(b["title"])
        expect(card).to_contain_text(re.compile(rf"\b{b['tickets']}\s*tickets?\b", re.I))
        expect(card).to_contain_text(b["total"])

    # Step 9: first booking detail page
    find_card(page, b1["ref"]).get_by_text("View Details").click()
    expect(page).to_have_url(re.compile(r"/bookings/\d+"))
    booking_id = re.search(r"/bookings/(\d+)", page.url).group(1)
    assert booking_id.isdigit()

    expect(page.get_by_text(b1["ref"]).first).to_be_visible()
    expect(page.get_by_role("heading", level=1)).to_contain_text(b1["title"])
    expect(page.locator("main")).to_contain_text(b1["email"])
    summary = payment_summary(page)
    expect(summary).to_contain_text(re.compile(rf"Tickets\s*{b1['tickets']}(?!\d)"))
    expect(summary).to_contain_text(b1["total"])

    # Step 10: second booking, found again by reference
    page.goto("/bookings")
    find_card(page, b2["ref"]).get_by_text("View Details").click()
    expect(page).to_have_url(re.compile(r"/bookings/\d+"))

    expect(page.get_by_text(b2["ref"]).first).to_be_visible()
    expect(page.get_by_role("heading", level=1)).to_contain_text(b2["title"])
    summary = payment_summary(page)
    expect(summary).to_contain_text(re.compile(rf"Tickets\s*{b2['tickets']}(?!\d)"))
    expect(summary).to_contain_text(b2["total"])
    expect(page.locator("body")).not_to_contain_text(b1["ref"])