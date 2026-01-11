from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import urllib.parse
import re
import time
from scrapers_config import get_chrome_driver

def get_prices_shufersal(products):

    # ===============================
    # המרה למחיר ל־גרם
    # ===============================
    def convert_to_per_gram(price_text):
        if price_text is None:
            return 0
        try:
            price = float(price_text.split()[0])
        except:
            return 0

        unit = price_text
        if "1 ק&quot;ג" in unit or "1 יחידה" in unit:
            return price / 1000
        if "100 גרם" in unit or "100 מ&quot;ל" in unit:
            return price / 100
        return price / 1000
    # ===============================
    # פתיחת דפדפן
    # ===============================
    driver = get_chrome_driver()

    # ===============================
    # שליפה מתוך HTML
    # ===============================
    def extract_price(item):
        try:
            extra = item.find_element(By.CSS_SELECTOR, "div.smallText.pricePerUnit")
            text = extra.text.strip()
            is_unit = ("יח" in text)
            return text, is_unit
        except:
            pass

        try:
            number = item.find_element(By.CSS_SELECTOR, "span.number").text.strip()
        except:
            return None, None

        try:
            unit = item.find_element(By.CSS_SELECTOR, "span.priceUnit").text.strip()
        except:
            unit = ""

        is_unit = ("יח" in unit)
        return f"{number} {unit}".strip(), is_unit


    
    wait = WebDriverWait(driver, 15)
    price_per_gram_list = []

    # ===============================
    # לולאת החיפוש
    # ===============================
    for product in products:
        url = f"https://www.shufersal.co.il/online/he/search?text={urllib.parse.quote(product)}"
        driver.get(url)
        time.sleep(2)

        try:
            items = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-product-code]"))
            )
        except:
            price_per_gram_list.append(0)
            continue

        if len(items) == 0:
            price_per_gram_list.append(0)
            continue

        first_price, first_unit = extract_price(items[0])

        if not first_unit:
            chosen_price = first_price
        else:
            if len(items) > 1:
                second_price, second_unit = extract_price(items[1])
                chosen_price = second_price if not second_unit else first_price
            else:
                chosen_price = first_price

        per_gram = convert_to_per_gram(chosen_price)
        price_per_gram_list.append(round(per_gram, 4))

    driver.quit()
    return price_per_gram_list


def get_prices_victory(products):
    # ===============================
    # חילוץ מספר
    # ===============================
    def extract_number(text):
        m = re.search(r"([\d.]+)", text)
        return float(m.group(1)) if m else None

    # ===============================
    # המרה למחיר ל־גרם
    # ===============================
    def convert_to_per_gram(price_text):
        if not price_text:
            return 0

        price = extract_number(price_text)
        if price is None:
            return 0

        if  'ק"ג' in price_text or "יחידה" in price_text:
            return price / 1000

        if "100" in price_text:
            return price / 100

        return 0

    # ===============================
    # שליפת מחיר
    # ===============================
    def extract_price(item):

        # ק"ג
        try:
            text = item.find_element(By.CSS_SELECTOR, "span.price").text.strip()
            if 'ק"ג' in text:
                return f"₪{extract_number(text)} לק\"ג"
        except:
            pass

        # 100 גרם
        try:
            text = item.find_element(By.CSS_SELECTOR, "span.normalize-price").text.strip()
            if "100" in text:
                return f"₪{extract_number(text)} ל־100 גרם"
        except:
            pass

        # יחידה
        try:
            text = item.find_element(By.CSS_SELECTOR, "span.price").text.strip()
            if extract_number(text) is not None:
                return f"₪{extract_number(text)} ליחידה"
        except:
            pass

        return None

    # ===============================
    # פתיחת דפדפן
    # ===============================
    driver = get_chrome_driver()

    wait = WebDriverWait(driver, 15)
    price = []

    # ===============================
    # לולאת חיפוש
    # ===============================
    for product in products:
        url = f"https://www.victoryonline.co.il/search/{urllib.parse.quote(product)}"
        driver.get(url)
        time.sleep(2)

        found_price_text = None

        try:
            name_divs = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.name"))
            )
        except:
            price.append(0)
            continue

        for name_div in name_divs:
            try:
                item = name_div.find_element(
                    By.XPATH, "ancestor::*[contains(@class,'product')]"
                )
                price_text = extract_price(item)
                if price_text:
                    found_price_text = price_text
                    break
            except:
                continue

        if not found_price_text:
            price.append(0)
        else:
            price.append(round(convert_to_per_gram(found_price_text), 4))

    driver.quit()
    return price


def get_prices_from_rami_levy(products):
    def get_unit_type(card):
        try:
            spans = card.find_elements(By.CSS_SELECTOR, "span.xs-text.mr-1.weight-500")
            for s in spans:
                t = s.text.strip()
                if 'ק"ג' in t:
                    return 'kg'
                if 'יח' in t:
                    return 'unit'
        except:
            pass
        return None

    # ===============================
    # מחיר רגיל
    # ===============================
    def extract_regular_price(card):
        text = card.text.replace("₪", " ").replace(",", ".")
        m = re.search(r"\d+\.\d{1,2}", text)
        return float(m.group()) if m else None

    # ===============================
    # מחיר ל־100 גרם
    # ===============================
    def extract_price_100g(card):
        try:
            span = card.find_element(
                By.CSS_SELECTOR, "span.gray-dark.xs-text.font-weight-light"
            )
            text = span.text.replace("₪", "").replace(",", ".")
            m = re.search(r"\d+\.\d{1,2}", text)
            return float(m.group()) if m else None
        except:
            return None

    # ===============================
    # פתיחת דפדפן
    # ===============================
    driver = get_chrome_driver()

    wait = WebDriverWait(driver, 25)

    price = []

    # ===============================
    # לולאת חיפוש
    # ===============================
    for product in products:
        url = f"https://www.rami-levy.co.il/he/online/search?q={urllib.parse.quote(product)}"
        driver.get(url)

        try:
            items = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div[role='list'] div.product-flex")
                )
            )
        except:
            price.append(0)
            continue

        if not items:
            price.append(0)
            continue

        card = items[0]  # פריט ראשון
        unit_type = get_unit_type(card)

        # ---------- לוגיקה ----------
        if unit_type == 'unit':
            # אם יחידה – ננסה 100 גרם
            p100 = extract_price_100g(card)
            if p100 is not None:
                price.append(round(p100 / 100, 4))  # /100
            else:
                pr = extract_regular_price(card)
                if pr is not None:
                    price.append(round(pr / 1000, 4))  # /1000 גם ליחידה
                else:
                    price.append(0)
        else:
            # ק״ג (או לא ידוע)
            pr = extract_regular_price(card)
            if pr is not None:
                price.append(round(pr / 1000, 4))  # /1000
            else:
                price.append(0)

    driver.quit()

    # ===============================
    # הפלט היחיד
    # ===============================
    return price