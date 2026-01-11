#!/usr/bin/env python3
"""
קובץ בדיקה ישיר - מריץ את הסקרייפרים ומציג את התוצאות במסוף
כך תוכלי לראות בדיוק מה קורה בלי להריץ את האתר
"""

from pricing.scrapers import (
    get_prices_shufersal,
    get_prices_victory,
    get_prices_from_rami_levy
)

# ניקח את רשימת המוזונות מה-app
foods = [
    # חלבונים (2)
    {"id": "1", "name": "ביצים", "protein": 12.6, "calories": 155, "carbs": 1.0, "fat": 11.0, "price": 4.16, "category": "protein"},
    {"id": "2", "name": "חזה עוף", "protein": 31.0, "calories": 165, "carbs": 0.0, "fat": 3.6, "price": 4.00, "category": "protein"},
    
    # פחמימות (2)
    {"id": "3", "name": "לחם מלא", "protein": 9.0, "calories": 247, "carbs": 41.0, "fat": 3.4, "price": 1.00, "category": "carb"},
    {"id": "4", "name": "אורז לבן", "protein": 2.7, "calories": 130, "carbs": 28.0, "fat": 0.3, "price": 0.60, "category": "carb"},
    
    # ירקות (2)
    {"id": "5", "name": "מלפפון", "protein": 0.7, "calories": 10, "carbs": 4.0, "fat": 0.0, "price": 1.00, "category": "vegetable"},
    {"id": "6", "name": "גזר", "protein": 0.9, "calories": 41, "carbs": 10.0, "fat": 0.2, "price": 0.60, "category": "vegetable"},
    
    # פירות (2)
    {"id": "7", "name": "תפוח", "protein": 0.3, "calories": 52, "carbs": 14.0, "fat": 0.2, "price": 0.80, "category": "fruit"},
    {"id": "8", "name": "בננה", "protein": 1.1, "calories": 89, "carbs": 23.0, "fat": 0.3, "price": 0.60, "category": "fruit"},
]

print("=" * 80)
print("בדיקת סקרייפרים - מציג את התוצאות ישירות במסוף")
print("=" * 80)
print()

# הוספת שדה מחירים לכל מזון
for food in foods:
    food["prices"] = {
        "manual": food.pop("price"),
        "shufersal": None,
        "victory": None,
        "rami_levy": None
    }

# רשימת שמות המוצרים
product_names = [food["name"] for food in foods]

print(f"מספר מוצרים לבדיקה: {len(product_names)}")
print(f"שמות המוצרים: {', '.join(product_names)}")
print()
print("=" * 80)
print()

# ==================== שופרסל ====================
print("1️⃣  בודק סקרייפר שופרסל...")
print("-" * 80)
try:
    shufersal_prices = get_prices_shufersal(product_names)
    print("✅ הסקרייפר רץ בהצלחה!")
    print()
    print("תוצאות:")
    for i, price in enumerate(shufersal_prices):
        food = foods[i]
        if price > 0:
            price_per_kg = price * 1000
            print(f"  ✓ {food['name']}: {price} ₪/גרם (= {price_per_kg:.2f} ₪/ק״ג)")
        else:
            print(f"  ✗ {food['name']}: לא נמצא מחיר")
except Exception as e:
    print(f"❌ שגיאה בסקרייפר שופרסל: {e}")
    import traceback
    traceback.print_exc()
    shufersal_prices = [0] * len(product_names)

print()
print("=" * 80)
print()

# ==================== ויקטורי ====================
print("2️⃣  בודק סקרייפר ויקטורי...")
print("-" * 80)
try:
    victory_prices = get_prices_victory(product_names)
    print("✅ הסקרייפר רץ בהצלחה!")
    print()
    print("תוצאות:")
    for i, price in enumerate(victory_prices):
        food = foods[i]
        if price > 0:
            price_per_kg = price * 1000
            print(f"  ✓ {food['name']}: {price} ₪/גרם (= {price_per_kg:.2f} ₪/ק״ג)")
        else:
            print(f"  ✗ {food['name']}: לא נמצא מחיר")
except Exception as e:
    print(f"❌ שגיאה בסקרייפר ויקטורי: {e}")
    import traceback
    traceback.print_exc()
    victory_prices = [0] * len(product_names)

print()
print("=" * 80)
print()

# ==================== רמי לוי ====================
print("3️⃣  בודק סקרייפר רמי לוי...")
print("-" * 80)
try:
    rami_prices = get_prices_from_rami_levy(product_names)
    print("✅ הסקרייפר רץ בהצלחה!")
    print()
    print("תוצאות:")
    for i, price in enumerate(rami_prices):
        food = foods[i]
        if price > 0:
            price_per_kg = price * 1000
            print(f"  ✓ {food['name']}: {price} ₪/גרם (= {price_per_kg:.2f} ₪/ק״ג)")
        else:
            print(f"  ✗ {food['name']}: לא נמצא מחיר")
except Exception as e:
    print(f"❌ שגיאה בסקרייפר רמי לוי: {e}")
    import traceback
    traceback.print_exc()
    rami_prices = [0] * len(product_names)

print()
print("=" * 80)
print()

# ==================== סיכום ====================
print("📊 סיכום כל המחירים:")
print("=" * 80)
print(f"{'מוצר':<15} | {'מחיר ידני':<12} | {'שופרסל':<12} | {'ויקטורי':<12} | {'רמי לוי':<12}")
print("-" * 80)

for i, food in enumerate(foods):
    manual_price = food['prices']['manual']
    shufersal_price = shufersal_prices[i] if shufersal_prices[i] > 0 else "לא נמצא"
    victory_price = victory_prices[i] if victory_prices[i] > 0 else "לא נמצא"
    rami_price = rami_prices[i] if rami_prices[i] > 0 else "לא נמצא"
    
    print(f"{food['name']:<15} | {manual_price:<12} | {shufersal_price:<12} | {victory_price:<12} | {rami_price:<12}")

print()
print("=" * 80)
print()

# ==================== ניתוח תוצאות ====================
print("🔍 ניתוח תוצאות:")
print("=" * 80)

# ספירת הצלחות
shufersal_success = sum(1 for p in shufersal_prices if p > 0)
victory_success = sum(1 for p in victory_prices if p > 0)
rami_success = sum(1 for p in rami_prices if p > 0)

print(f"שופרסל: מצא {shufersal_success}/{len(product_names)} מחירים")
print(f"ויקטורי: מצא {victory_success}/{len(product_names)} מחירים")
print(f"רמי לוי: מצא {rami_success}/{len(product_names)} מחירים")
print()

# בדיקת מחירים לא הגיוניים
print("בדיקת מחירים חריגים (יותר מ-50 ₪/ק״ג או פחות מ-0.1 ₪/ק״ג):")
print("-" * 80)

for i, food in enumerate(foods):
    for supermarket, prices in [("שופרסל", shufersal_prices), ("ויקטורי", victory_prices), ("רמי לוי", rami_prices)]:
        price = prices[i]
        if price > 0:
            price_per_kg = price * 1000
            if price_per_kg > 50:
                print(f"⚠️  {food['name']} ({supermarket}): מחיר גבוה מאוד - {price_per_kg:.2f} ₪/ק״ג")
            elif price_per_kg < 0.1:
                print(f"⚠️  {food['name']} ({supermarket}): מחיר נמוך מאוד - {price_per_kg:.2f} ₪/ק״ג")

print()
print("=" * 80)
print()

# ==================== דוגמאות מעשיות ====================
print("💡 דוגמאות מעשיות:")
print("=" * 80)

# ביצים
if shufersal_prices[0] > 0:
    egg_price_per_gram = shufersal_prices[0]
    egg_price_per_12 = egg_price_per_gram * 750  # בערך 750 גרם ל-12 ביצים
    print(f"ביצים (12 יחידות) בשופרסל: ~{egg_price_per_12:.2f} ₪")

# חזה עוף
if shufersal_prices[1] > 0:
    chicken_price_per_kg = shufersal_prices[1] * 1000
    print(f"חזה עוף בשופרסל: {chicken_price_per_kg:.2f} ₪/ק״ג")

print()
print("=" * 80)
print("✅ סיימנו! תסתכלי על התוצאות למעלה")
print("=" * 80)