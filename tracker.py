import os
import time
import smtplib
import json
from datetime import datetime
from email.mime.text import MIMEText
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from logger_factory import get_logger

logger = get_logger("tracker")
load_dotenv()

# --- DYNAMIC PATH & CONFIG RESOLUTION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
DATA_FILE = os.path.join(BASE_DIR, "prices.json")

# Load the target URLs dynamically from config.json
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config_data = json.load(f)
        URLS = config_data.get("URLS", {})
else:
    logger.error(f"Configuration file missing at {CONFIG_FILE}")
    URLS = {}

# Use environment variables or paste your credentials here securely
EMAIL_SENDER = os.environ.get("TRACKER_EMAIL")
EMAIL_PASSWORD = os.environ.get("TRACKER_PASSWORD")
EMAIL_RECEIVER = os.environ.get("PERSONAL_RECEIVER")
DATA_FILE = "prices.json"

def fetch_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(5)  # Allow dynamic price matrices to finish loading
        
        # Expanded to cover Lenovo's tags and Amazon's nested standard wrappers
        price_selectors = [
            "span.price-title",
            ".priceToPay span.a-offscreen",  # Targets Amazon's clean text node directly
            "span.priceToPay",               # Fallback outer wrapper for Amazon
            ".final-price", 
            ".saleprice"
        ]
        price_text = None
        
        for selector in price_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # Sanity Check: Skip the element if it's part of a strike-through class
                    parent_classes = element.get_attribute("class") or ""
                    if "strike" in parent_classes.lower():
                        continue
                    
                    # get_attribute('textContent') extracts text even if it's visually hidden via CSS/Aria
                    text_value = element.get_attribute("textContent") or element.text
                    if text_value and any(char.isdigit() for char in text_value):
                        price_text = text_value
                        break
                if price_text:
                    break
            except:
                continue
                
        if price_text:
            # Cleans "$414..99" or " $414.99 " safely into float 414.99
            # Resolving any double decimals caused by text flattening splits
            cleaned_string = ''.join(c for c in price_text if c.isdigit() or c == '.')
            if cleaned_string.count('.') > 1:
                # Fixes potential formatting edge cases with split elements
                parts = cleaned_string.split('.')
                cleaned_string = f"{parts[0]}.{parts[1]}"
                
            return float(cleaned_string)
        return None
        
    finally:
        driver.quit()

def send_alert(laptop_name, old_price, new_price):
    subject = f"🚨 Price Drop Alert: {laptop_name}!"
    body = f"The price for the {laptop_name} has dropped!\n\nOld Price: ${old_price:.2f}\nNew Price: ${new_price:.2f}\n\nCheck it out here: {URLS[laptop_name]}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    # Gmail SMTP server setup
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, [EMAIL_RECEIVER], msg.as_string())
    logger.info(f"Email alert sent for {laptop_name}!")

def main():
    # Load existing history matrix or initialize a clean state
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    for name, url in URLS.items():
        logger.info(f"Checking price for {name}...")
        current_price = fetch_price(url)

        # Grab execution timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if current_price:
            logger.info(f"Current price for {name}: ${current_price:.2f}")
            
            # Setup a clean record for the laptop if it's the first run ever
            if name not in data:
                data[name] = {
                    "latest_price": None,
                    "history": []
                }
            
            old_price = data[name]["latest_price"]
            
            # Check for a drop compared to the last record
            if old_price and current_price < old_price:
                send_alert(name, old_price, current_price)
                
            # Update values and log the timestamped historical snapshot
            data[name]["latest_price"] = current_price
            data[name]["history"].append({
                "timestamp": current_time,
                "price": current_price
            })
        else:
            logger.warning(f"Failed to extract price for {name}")

    # Write the clean data model structure back to disk
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()