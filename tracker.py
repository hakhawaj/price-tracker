import os
import time
import smtplib
import json
from email.mime.text import MIMEText

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

load_dotenv()

# --- CONFIGURATION ---
URLS = {
    "Legion Pro 5i": "https://www.lenovo.com/ca/en/p/laptops/legion-laptops/legion-pro-series/legion-pro-5i-gen-10-16-inch-intel/83f3000aus",
    "Legion Pro 7i": "https://www.lenovo.com/ca/en/p/laptops/legion-laptops/legion-pro-series/legion-pro-7i-gen-10-16-inch-intel/83f500alcc"
}

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
        
        # 1. Prioritize the exact discounted sale span class first
        # 2. Fallback to generic final selectors if layout shifts
        price_selectors = ["span.price-title", ".final-price", ".saleprice"]
        price_text = None
        
        for selector in price_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # Sanity Check: Skip the element if it's part of a strike-through class
                    parent_classes = element.get_attribute("class") or ""
                    if "strike" in parent_classes.lower():
                        continue
                        
                    if element.is_displayed() and element.text:
                        price_text = element.text
                        break
                if price_text:
                    break
            except:
                continue
                
        if price_text:
            # Strip out symbols/commas and convert to a clean float
            cleaned_price = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
            return cleaned_price
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
    print(f"Email alert sent for {laptop_name}!")

def main():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {}

    for name, url in URLS.items():
        print(f"Checking price for {name}...")
        current_price = fetch_price(url)
        
        if current_price:
            print(f"Current price: ${current_price:.2f}")
            old_price = history.get(name)
            
            if old_price and current_price < old_price:
                send_alert(name, old_price, current_price)
                
            history[name] = current_price
        else:
            print(f"Failed to extract price for {name}")

    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4)

if __name__ == "__main__":
    main()