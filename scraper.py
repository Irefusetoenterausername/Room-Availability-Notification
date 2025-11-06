import os
from datetime import datetime
from zoneinfo import ZoneInfo
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from playwright.sync_api import sync_playwright

# --------------------------
# Configuration
# --------------------------

# Hours to send notification (Pacific Time)
TARGET_HOURS_PT = [15, 18, 21]  # 3pm, 6pm, 9pm

URL = "https://live.ipms247.com/booking/book-rooms-hollywoodviphotel"
SELECTOR_1 = "#leftroom_0"
SELECTOR_2 = "#leftroom_4"

# SendGrid configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = "cherrytop3000@gmail.com"
TO_EMAILS = ['3104866003@tmomail.net', 'cherrytop3000@gmail.com']

# --------------------------
# Functions
# --------------------------

def scrape_numbers():
    """Launch a headless browser, load the page, and read the two numbers."""
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        print("Loading page...")
        page.goto(URL, timeout=60000)

        # Wait for the elements to appear (adjust timeout if needed)
        page.wait_for_selector(SELECTOR_1, timeout=20000)
        page.wait_for_selector(SELECTOR_2, timeout=20000)

        num1_text = page.inner_text(SELECTOR_1).strip()
        num2_text = page.inner_text(SELECTOR_2).strip()
        browser.close()

        print(f"Scraped values: {num1_text}, {num2_text}")
        try:
            num1 = float(num1_text)
            num2 = float(num2_text)
        except ValueError:
            raise ValueError(f"Could not parse numbers: {num1_text}, {num2_text}")
        return num1 + num2


def send_email(total):
    """Send results via SendGrid."""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAILS,
        subject="",  # No subject
        plain_text_content=f"{total} rooms available",
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


# --------------------------
# Main Execution
# --------------------------

now_pt = datetime.now(ZoneInfo("America/Los_Angeles"))
current_hour = now_pt.hour

print("Testing mode — forcing run")
total = scrape_numbers()
send_email(total)
