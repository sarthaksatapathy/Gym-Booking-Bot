import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# -------------------- CONSTANTS --------------------
ACCOUNT_EMAIL = "your_email@test.com"
ACCOUNT_PASSWORD = "your_password"
GYM_URL = "https://appbrewery.github.io/gym/"

TARGET_DAYS = ["Tuesday", "Thursday"]
TARGET_TIME = "6:00 PM"

# -------------------- CHROME SETUP --------------------
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

# -------------------- RETRY WRAPPER --------------------
def retry(func, retries=7, description=""):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"⚠️ Retry {attempt+1}/{retries} failed: {description}")
            time.sleep(1)
    raise Exception(f" Failed after {retries} retries: {description}")

# -------------------- LOGIN --------------------
def login():
    driver.get(GYM_URL)

    login_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "login-button"))
    )
    login_btn.click()

    email_input = wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    password_input = driver.find_element(By.ID, "password")

    email_input.clear()
    email_input.send_keys(ACCOUNT_EMAIL)
    password_input.clear()
    password_input.send_keys(ACCOUNT_PASSWORD)
    password_input.send_keys(Keys.ENTER)

    wait.until(
        EC.presence_of_element_located((By.ID, "class-schedule-page"))
    )

    print("Logged in successfully")

# -------------------- BOOK CLASS --------------------
def book_class(card):
    class_name = card.find_element(By.CSS_SELECTOR, "h3").text
    day = card.find_element(By.CSS_SELECTOR, "p[id^='class-day-']").text
    time_text = card.find_element(By.CSS_SELECTOR, "p[id^='class-time-']").text

    button = card.find_element(By.TAG_NAME, "button")
    button_text = button.text.lower()

    label = f"{class_name} on {day} at {time_text}"

    if "booked" in button_text:
        return ("already", f"✓ Already booked: {label}")
    elif "waitlisted" in button_text:
        return ("already", f"✓ Already on waitlist: {label}")
    elif "waitlist" in button_text:
        button.click()
        return ("waitlist", f"✓ Joined waitlist for: {label}")
    else:
        button.click()
        return ("booked", f"✓ Successfully booked: {label}")

# -------------------- PROCESS CLASSES --------------------
def process_classes():
    booked = waitlisted = already = 0
    detailed_log = []

    cards = driver.find_elements(By.CSS_SELECTOR, "div[id^='class-card-']")

    for card in cards:
        try:
            day = card.find_element(By.CSS_SELECTOR, "p[id^='class-day-']").text
            time_text = card.find_element(By.CSS_SELECTOR, "p[id^='class-time-']").text

            if day in TARGET_DAYS and TARGET_TIME in time_text:
                status, message = retry(
                    lambda: book_class(card),
                    description="Booking class"
                )

                print(message)
                detailed_log.append(message)

                if status == "booked":
                    booked += 1
                elif status == "waitlist":
                    waitlisted += 1
                else:
                    already += 1

        except Exception:
            continue

    print("\n--- BOOKING SUMMARY ---")
    print(f"New bookings: {booked}")
    print(f"New waitlist entries: {waitlisted}")
    print(f"Already booked/waitlisted: {already}")
    print(f"Total Tuesday & Thursday 6pm classes: {booked + waitlisted + already}")

    print("\n--- DETAILED CLASS LIST ---")
    for log in detailed_log:
        print(" •", log)

    return booked + waitlisted + already

# -------------------- VERIFY BOOKINGS --------------------
def verify_bookings(expected):
    driver.find_element(By.ID, "my-bookings-link").click()

    wait.until(
        EC.presence_of_element_located((By.ID, "my-bookings-page"))
    )

    bookings = driver.find_elements(By.CSS_SELECTOR, "div[id^='booking-card-']")
    found = 0

    print("\n--- VERIFYING ON MY BOOKINGS PAGE ---")

    for booking in bookings:
        try:
            day = booking.find_element(By.CSS_SELECTOR, "p[id^='booking-day-']").text
            time_text = booking.find_element(By.CSS_SELECTOR, "p[id^='booking-time-']").text

            if day in TARGET_DAYS and TARGET_TIME in time_text:
                print(" ✓ Verified:", booking.text.split("\n")[0])
                found += 1
        except NoSuchElementException:
            continue

    print("\n--- VERIFICATION RESULT ---")
    print(f"Expected: {expected} bookings")
    print(f"Found: {found} bookings")

    if expected == found:
        print("SUCCESS: All bookings verified!")
    else:
        print(f"MISMATCH: Missing {expected - found} bookings")

# -------------------- RUN SCRIPT --------------------
retry(login, description="Login")

total_attempted = process_classes()

verify_bookings(total_attempted)
