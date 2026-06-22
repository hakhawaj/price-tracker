# Modular Cross-Platform Price Tracker

A decoupled, automated web scraping solution built in Python to monitor and log commercial pricing fluctuations for consumer electronics across multiple retail platforms (including Lenovo and Amazon). The application extracts live promotional data using headless browser automation, logs time-series historical data into a local JSON store, and dispatches instant email alerts via secure SMTP gateways when a price drop is detected.

## 🚀 Features
* **Cross-Platform Scraping:** Dynamically handles both JavaScript-heavy client-side elements on Lenovo and complex, multi-layered screen-reader structures (`span.a-offscreen`) on Amazon.
* **Externalized Configuration:** Decouples application logic from data targets by storing monitored assets inside an easily scalable `config.json` file.
* **Isolated Factory Logging:** Features a dedicated `logger_factory` module providing a clean, relative path architecture safe for public repositories.
* **Enterprise Log Rotation:** Implements `RotatingFileHandler` instances enforcing a strict 5 MB cap per log file, protecting disk space while automatically separating operational metrics (`tracker.log`) from pipeline failures (`error.log`).
* **Background Automation:** Runs natively in the background as a headless macOS system daemon via `launchd`, using unbuffered output (`python -u`) for live streaming updates.

---

## 🛠️ Tech Stack & Architecture
* **Language:** Python 3.9+
* **Automation Engine:** Selenium WebDriver (Chrome)
* **Configuration Layer:** `python-dotenv` & Native JSON
* **Network Protocol:** `smtplib` / `email.mime` (TLS Encrypted SMTP)
* **Log Management:** Standard Python Logging (`RotatingFileHandler`)

---

## 📋 Repository Structure
```text
price-tracker/
├── tracker.py          # Main core runtime & orchestration engine
├── logger_factory.py   # Modular logging factory (handles paths & size limits)
├── config.json         # User configuration file containing target tracking URLs
├── prices.json         # Nested JSON database storing time-series historical data
├── .env.example        # Reference template for credentials and environment vars
├── .gitignore          # Excludes environments, execution logs, and secrets from Git
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
        <integer>18</integer>
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
You don't have to wait until 6:00 PM to verify that it works. You can tell your Mac to kick off an immediate test run right now using your configuration identifier:
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