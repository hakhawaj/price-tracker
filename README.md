# Automated Price Tracker

A lightweight, automated web scraping solution built in Python to monitor and log commercial pricing fluctuations for items on the web. The application extracts live, dynamic promotional data, logs time-series historical data into a local JSON store, and dispatches instant email alerts via secure SMTP gateways when a price drop is detected.

## 🚀 Features
* **Dynamic Web Scraping:** Employs Selenium WebDriver to handle JavaScript-heavy, client-side rendered e-commerce elements cleanly.
* **Smart Filter Logic:** Automatically targets primary sale containers (`span.price-title`) while filtering out deceptive MSRP elements (`strike-through-price`).
* **Time-Series Data Modeling:** Appends localized execution timestamps alongside current valuation metrics inside a unified data layer (`prices.json`).
* **Decoupled Security Architecture:** Isolates sensitive target metrics and transactional app configurations within an untracked local `.env` ecosystem.
* **Automated Scheduling:** Fully optimized to run quietly in the background as a headless macOS system daemon via `launchd`.

---

## 🛠️ Tech Stack & Architecture
* **Language:** Python 3.9+
* **Automation Engine:** Selenium (Chrome WebDriver)
* **Configuration Layer:** `python-dotenv` (Environment-variable encapsulation)
* **Network Protocol:** `smtplib` / `email.mime` (TLS Encrypted transactional email delivery)
* **Data Storage:** Structured JSON Flat-File

---

## 📋 Repository Structure
```text
price-tracker/
├── tracker.py          # Main application engine & orchestration logic
├── .env.example        # Shared blueprint for configuration keys
├── .gitignore          # Strict directory filters (excludes venv, secrets, and data)
└── README.md           # Documentation asset