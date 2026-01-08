#  Snack & Lift Gym Booking Automation

A Selenium + Python automation project that logs into a gym booking website, books Tuesday & Thursday 6 PM classes, joins waitlists when classes are full, and verifies bookings automatically.

This project demonstrates **real-world automation practices** such as session persistence, retry logic, and verification.

---

# Features

- Persistent login using a custom Chrome profile
- Automated login with explicit waits (no `time.sleep`)
- Books **Tuesday & Thursday 6 PM** classes
- Automatically joins waitlists if classes are full
- Avoids duplicate bookings
- Booking summary with detailed logs
- Verifies bookings on the **My Bookings** page
- Handles simulated network failures using retry logic
- Works even when dates are advanced (time-travel QA testing)

---

# Tech Stack

- Python  
- Selenium WebDriver  
- ChromeDriver  
- WebDriverWait & Expected Conditions

  # Setup Instructions

## Install Selenium
```bash
pip install selenium
