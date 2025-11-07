import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from zoneinfo import ZoneInfo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# --- Configuration ---
URL = "https://live.ipms247.com/booking/book-rooms-hollywoodviphotel"
TARGET_HOURS_PT = [15, 18, 21]  # 3pm, 6pm, 9pm PT

FORMSPREE_ENDPOINT = os.environ.get("FORMSPREE_ENDPOINT")

if not FORMSPREE_ENDPOINT:
    print("Missing Formspree endpoint.")
    exit(1)

# --- PST/PDT Time Check ---
pst_now = datetime.now(ZoneInfo("America/Los_Angeles"))
current_hour = pst_now.hour

if current_hour not in TARGET_HOURS_PT:
    print(f"Current PT hour ({current_hour}) is not a target hour. Exiting.")
    exit()

# --- Scrape numbers ---
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    print("Loading page...")
    driver.get(URL)
    driver.implicitly_wait(5)

    num1 = int(driver.find_element(By.CSS_SELECTOR, "#leftroom_0").text.strip())
    num2 = int(driver.find_element(By.CSS_SELECTOR, "#leftroom_4").text.strip())
    total = num1 + num2

    print(f"Scraped values: {num1}, {num2} | Total: {total}")

finally:
    driver.quit()

# --- Send notification via Formspree ---
message = f"{total} rooms available"

try:
    response = requests.post(
        FORMSPREE_ENDPOINT,
        data={"message": message},
        timeout=10
    )
    if response.status_code in [200, 202]:
        print("Notification sent successfully via Formspree!")
    else:
        print(f"Formspree returned {response.status_code}: {response.text}")

except Exception as e:
    print("Error sending Formspree notification:", e)
