"""
בדיקה מהירה של האלגוריתם
Quick Test for the MILP Algorithm
"""

from algorithm import MenuOptimizer

# נתונים לבדיקה - מזונות פשוטים
test_foods = [
    # חלבונים
    {"id": "1", "name": "ביצים", "protein": 12.6, "calories": 155, "carbs": 1.0, "fat": 11.0, "price": 4.16, "category": "protein", "allowed_meals": ["breakfast", "dinner"]},
    {"id": "8", "name": "חזה עוף", "protein": 31.0, "calories": 165, "carbs": 0.0, "fat": 3.6, "price": 4.00, "category": "protein", "allowed_meals": ["lunch", "dinner"]},
    {"id": "10", "name": "טונה", "protein": 26.0, "calories": 198, "carbs": 0.0, "fat": 8.0, "price": 2.50, "category": "protein", "allowed_meals": ["lunch", "dinner"]},
    
    # פחמימות
    {"id": "21", "name": "לחם מלא", "protein": 9.0, "calories": 247, "carbs": 41.0, "fat": 3.4, "price": 1.00, "category": "carb", "allowed_meals": ["breakfast", "lunch", "dinner"]},
    {"id": "24", "name": "אורז", "protein": 2.7, "calories": 130, "carbs": 28.0, "fat": 0.3, "price": 0.60, "category": "carb", "allowed_meals": ["lunch", "dinner"]},
    {"id": "32", "name": "שיבולת שועל", "protein": 2.4, "calories": 71, "carbs": 12.0, "fat": 1.4, "price": 0.50, "category": "carb", "allowed_meals": ["breakfast"]},
    
    # ירקות
    {"id": "35", "name": "מלפפון", "protein": 0.7, "calories": 10, "carbs": 4.0, "fat": 0.0, "price": 1.00, "category": "vegetable", "allowed_meals": ["breakfast", "lunch", "dinner"]},
    {"id": "36", "name": "עגבנייה", "protein": 0.9, "calories": 20, "carbs": 5.0, "fat": 0.0, "price": 1.00, "category": "vegetable", "allowed_meals": ["breakfast", "lunch", "dinner"]},
    {"id": "37", "name": "חסה", "protein": 1.4, "calories": 15, "carbs": 3.0, "fat": 0.0, "price": 0.80, "category": "vegetable", "allowed_meals": ["breakfast", "lunch", "dinner"]},
    
    # פירות
    {"id": "47", "name": "תפוח", "protein": 0.3, "calories": 52, "carbs": 14.0, "fat": 0.2, "price": 0.80, "category": "fruit", "allowed_meals": ["breakfast", "snacks"]},
    {"id": "48", "name": "בננה", "protein": 1.1, "calories": 89, "carbs": 23.0, "fat": 0.3, "price": 0.60, "category": "fruit", "allowed_meals": ["breakfast", "snacks"]},
]

# פרמטרים לבדיקה
test_params = {
    'min_protein': 60,
    'max_protein': 100,
    'min_calories': 2000,
    'max_calories': 2500,
    'min_fat': 60,
    'max_fat': 90,
    'max_carbs': 250
}

def test_single_day():
    """בדיקת יום אחד"""
    print("\n" + "="*60)
    print("🧪 בדיקה 1: יצירת תפריט ליום אחד")
    print("="*60)
    
    optimizer = MenuOptimizer(test_foods, test_params)
    result = optimizer.generate_menu(1)
    
    if result['success']:
        print("✅ הצלחה!")
        print(f"\n💰 עלות: ₪{result['total_cost']:.2f}")
        
        day = result['days'][0]
        print(f"\n📊 נתונים תזונתיים:")
        print(f"   חלבון: {day['nutrition']['protein']:.1f}g")
        print(f"   קלוריות: {day['nutrition']['calories']:.0f}")
        print(f"   פחמימות: {day['nutrition']['carbs']:.1f}g")
        print(f"   שומן: {day['nutrition']['fat']:.1f}g")
        
        print(f"\n🍽️ ארוחות:")
        for meal_he, items in day['meals'].items():
            if items:
                print(f"\n   {meal_he}:")
                for food_name, qty in items:
                    print(f"      • {food_name}: {qty:.0f}g")
        
        return True
    else:
        print(f"❌ כשלון: {result.get('message', 'לא ידוע')}")
        return False

def test_multiple_days():
    """בדיקת מספר ימים"""
    print("\n" + "="*60)
    print("🧪 בדיקה 2: יצירת תפריט ל-3 ימים")
    print("="*60)
    
    optimizer = MenuOptimizer(test_foods, test_params)
    result = optimizer.generate_menu(3)
    
    if result['success']:
        print("✅ הצלחה!")
        print(f"\n💰 עלות כוללת: ₪{result['total_cost']:.2f}")
        print(f"💰 עלות ממוצעת ליום: ₪{result['avg_cost_per_day']:.2f}")
        print(f"\n📅 ימים שנוצרו: {result['days_generated']}")
        
        for idx, day in enumerate(result['days'], 1):
            print(f"\n📆 יום {idx}:")
            print(f"   חלבון: {day['nutrition']['protein']:.1f}g | "
                  f"קלוריות: {day['nutrition']['calories']:.0f} | "
                  f"עלות: ₪{day['cost']:.2f}")
        
        return True
    else:
        print(f"❌ כשלון: {result.get('message', 'לא ידוע')}")
        return False

def run_all_tests():
    """הרצת כל הבדיקות"""
    print("\n🚀 מתחיל בדיקות אלגוריתם...")
    
    tests_passed = 0
    tests_total = 2
    
    if test_single_day():
        tests_passed += 1
    
    if test_multiple_days():
        tests_passed += 1
    
    print("\n" + "="*60)
    print(f"📊 תוצאות: {tests_passed}/{tests_total} בדיקות עברו בהצלחה")
    print("="*60)
    
    if tests_passed == tests_total:
        print("\n✅ כל הבדיקות עברו! האלגוריתם עובד מצוין! 🎉")
    else:
        print("\n⚠️ יש בדיקות שנכשלו. בדוק את הקוד.")

if __name__ == "__main__":
    run_all_tests()