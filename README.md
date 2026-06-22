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
```

## 🔄 Automation Profile (macOS launchd)
To schedule this script to run silently on a persistent daily background interval, compile a system configurations .plist file within your LaunchAgents subsystem.

### Step 1: Create the Automation Configuration File (.plist)
macOS automation tasks are controlled by XML configuration files called Property Lists (.plist). They must live in a specific system folder inside your user account.
```bash
nano ~/Library/LaunchAgents/com.user.pricetracker.plist
```

Copy and paste this exact XML block into the editor:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.pricetracker</string>

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

    <key>StandardOutPath</key>
    <string>{price_tracker_file_directory}/tracker.log</string>
    <key>StandardErrorPath</key>
    <string>{price_tracker_file_directory}/error.log</string>
</dict>
</plist>
```

Save the file by pressing Control + O, hitting Enter, and exit with Control + X.

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

### Step 5: Verify the Telemetry Logs
After force-running it, look inside your project folder. You should see tracker.log, error.log, and an updated prices.json with a brand-new timestamp entry! To check your code's standard shell output printouts:
```bash
cat ~{price_tracker_file_directory}/tracker.log
```

To confirm nothing broke or threw missing environmental path errors:
```bash
cat ~{price_tracker_file_directory}/error.log
```

Your tracker is now officially automated!
Tip: If you ever want to completely turn off this automated background schedule in the future, just run:
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.pricetracker.plist
```