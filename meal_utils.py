import random
import copy


def shuffle_and_filter_meals(meals_list, target_days, vegetables):
    """
    פונקציה לערבוב וסינון ימי תפריט
    מוודאת שאין חזרה על מזונות (מלבד ירקות) בימים עוקבים
    
    Args:
        meals_list: רשימת ימים עם ארוחות
        target_days: מספר הימים המבוקש
        vegetables: רשימת ירקות שמותר לחזור עליהם
        
    Returns:
        רשימה מסוננת של ימים
    """
    max_attempts = 100
    attempt = 0

    def serialize_day(day):
        """יצירת חתימה ייחודית ליום"""
        meals = ["בוקר", "צהריים", "ערב", "תוספות"]
        return tuple(
            (meal, tuple(sorted(day.get(meal, []))))
            for meal in meals
        )

    while attempt < max_attempts:
        attempt += 1
        random.shuffle(meals_list)

        filtered = []
        prev_day_foods = set()
        prev_day_serialized = None

        for day in meals_list:
            current_day_foods = set()

            # איסוף כל המזונות של היום הנוכחי
            for meal_name in ["בוקר", "צהריים", "ערב", "תוספות"]:
                meal_items = day.get(meal_name, [])
                for item in meal_items:
                    # item יכול להיות tuple (food, qty) או dict
                    if isinstance(item, tuple):
                        food_name = item[0]
                    elif isinstance(item, dict):
                        food_name = item.get('food', '')
                    else:
                        continue
                    current_day_foods.add(food_name)

            # מזונות שאינם ירקות
            non_veg_today = {f for f in current_day_foods if f not in vegetables}
            non_veg_prev = {f for f in prev_day_foods if f not in vegetables}

            serialized = serialize_day(day)

            # בדיקה: האם היום זהה ליום הקודם?
            if serialized == prev_day_serialized:
                continue

            # בדיקה: האם יש חפיפה במזונות (לא ירקות)?
            if non_veg_today & non_veg_prev:
                continue

            # היום מתאים!
            filtered.append(day)
            prev_day_foods = current_day_foods
            prev_day_serialized = serialized

            # האם הגענו למספר הימים המבוקש?
            if len(filtered) == target_days:
                return filtered

    # אם לא הצלחנו למצוא מספיק ימים, נוסיף ימים אקראיים
    print(f"\n⚠️ לא הצלחנו למצוא {target_days} ימים - נמצאו {len(filtered)} בלבד.")

    if len(filtered) == 0:
        return meals_list[:target_days]

    prev_day_serialized = serialize_day(filtered[-1]) if filtered else None
    while len(filtered) < target_days:
        day_to_add = random.choice(meals_list)
        serialized = serialize_day(day_to_add)

        if serialized == prev_day_serialized:
            continue

        filtered.append(copy.deepcopy(day_to_add))
        prev_day_serialized = serialized

    return filtered