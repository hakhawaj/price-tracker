# Intelligent Cross-Platform Price Tracker with Semantic AI Extraction

An automated web scraping solution built in Python to monitor and log commercial pricing fluctuations for consumer electronics across multiple retail platforms (including Lenovo and Amazon). By utilizing a hybrid scraping and artificial intelligence architecture, the application extracts live promotional data without relying on fragile hardcoded CSS class layouts. It records time-series historical data into a local JSON store and dispatches encrypted email alerts via secure SMTP gateways when a price drop is detected.

## 🚀 Features
* **Semantic AI Scraping:** Eliminates fragile CSS selector strings. The engine grabs raw webpage states and utilizes **Gemini 2.5 Flash** to extract exact retail target pricing details contextually.
* **Decoupled Configuration:** Separates application orchestration logic from physical targets by externalizing monitored e-commerce URLs inside an easily scalable `config.json` file.
* **Isolated Factory Logging:** Implements a standalone `logger_factory` module managing relative operational paths, safely allowing repository deployment without leaking user home directory paths.
* **Enterprise Log Rotation:** Enforces a strict 5 MB cap per file layout using `RotatingFileHandler` instances, cleanly separating runtime metrics (`tracker.log`) from system processing failures (`error.log`).
* **Headless Background Automation:** Built to run unattended as a native macOS background daemon via `launchd`.

---

## 🛠️ Tech Stack & Architecture
* **Language:** Python 3.9+
* **AI Extraction Layer:** Google GenAI SDK (`gemini-2.5-flash`)
* **DOM Preprocessing:** BeautifulSoup4 (Strips script/style noise to optimize context tokens)
* **Automation Engine:** Selenium WebDriver (Headless Chrome)
* **Data Layer:** Native JSON Time-Series Store
* **Alert System:** Encrypted TLS SMTP (`smtplib` / `email.mime`)

---

## 📋 Repository Structure
```text
price-tracker/
├── tracker.py          # Main core runtime & automation orchestration engine
├── ai_extractor.py     # DOM preprocessing layer & Gemini Flash extraction engine
├── logger_factory.py   # Modular logging factory (handles paths & size rotation)
├── config.json         # User configuration file containing target tracking URLs
├── prices.json         # Nested JSON database storing time-series historical data
├── .env.example        # Reference template for credentials and API keys
├── .gitignore          # Prevents tracking environments, execution logs, and secrets
└── README.md           # Documentation asset
```

## 🔄 Automation Profile (macOS launchd)
To schedule this script to run silently on a persistent daily background interval, compile a system configurations .plist file within your LaunchAgents subsystem.

### Step 1: Create the Automation Configuration File (.plist)
macOS automation tasks are controlled by XML configuration files called Property Lists (.plist). They must live in a specific system folder inside your user account.
```bash
code ~/Library/LaunchAgents/com.user.pricetracker.plist
```

Copy and paste this exact XML block into the editor (and remember to modify the variables):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{user}.pricetracker</string>

    <key>ProgramArguments</key>
    <array>
        <string>{python_directory}</string>
        <string>{price_tracker_file_directory}/tracker.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>{price_tracker_file_directory}</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>12</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

### Step 2: Set Strict File Permissions
macOS will refuse to run automation scripts if the file configuration is modifiable by external apps. You must lock down permissions so only your user profile can read/write it:
```bash
chmod 644 ~/Library/LaunchAgents/com.user.pricetracker.plist
```

### Step 3: Register and Activate the Job
Now, tell your Mac's operating system engine to read the file and append it to your active background schedule processing queue:
```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.pricetracker.plist
```

### Step 4: Test a Force-Execution Manually
You don't have to wait until 12:00 PM to verify that it works. You can tell your Mac to kick off an immediate test run right now using your configuration identifier:
```bash
launchctl kickstart -k gui/$(id -u)/com.user.pricetracker
```

Your tracker is now officially automated!

### Notes: 
* If you ever want to completely turn off this automated background schedule in the future, just run:
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.pricetracker.plist
```

* Whenever you modify your schedule inside the .plist file, remember to run launchctl bootout before running launchctl bootstrap again to flash the changes into active system memory.