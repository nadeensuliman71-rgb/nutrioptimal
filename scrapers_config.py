from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

def get_chrome_driver():
    """
    מחזיר Chrome WebDriver מוגדר כראוי לסביבת הפרודקשן או הפיתוח
    """
    options = Options()
    
    # הגדרות בסיסיות
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    
    # הגדרות נוספות לייצוב
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # אם רצים ב-Railway
    if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('CHROME_BIN'):
        chrome_bin = os.getenv('CHROME_BIN')
        if chrome_bin:
            options.binary_location = chrome_bin
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"⚠️ Error with Railway Chrome: {e}")
    
    # פיתוח מקומי
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    return driver