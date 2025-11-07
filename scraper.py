import os
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

RECIPIENTS = ["cherrytop3000@gmail.com", "3104866003@tmomail.net"]

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

# --- Brevo SMTP (TLS on port 587) ---
smtp_user = os.environ.get("BREVO_SMTP_USER")
smtp_pass = os.environ.get("BREVO_SMTP_PASS")
smtp_server = os.environ.get("BREVO_SMTP_SERVER")

if not smtp_user or not smtp_pass or not smtp_server:
    print("Missing Brevo SMTP credentials.")
    exit(1)

subject = f"{total} rooms available"
body = f"{total} rooms available\n"

msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = smtp_user
msg["To"] = ", ".join(RECIPIENTS)

try:
    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, RECIPIENTS, msg.as_string())
        print("Email & SMS sent successfully")

except Exception as e:
    print("Error sending email/SMS:", e)
