import pulp
from pulp import PULP_CBC_CMD
import copy


def build_model(excluded_foods=None, run_number=0):
    """
    בניית מודל MILP לאופטימיזציה
    משתמש במשתנים גלובליים שהוגדרו ב-algorithm.py
    """
    if excluded_foods is None:
        excluded_foods = set()
    
    # קבלת משתנים גלובליים
    import builtins
    foods = builtins.foods
    meals = builtins.meals
    protein = builtins.protein
    calories = builtins.calories
    carbs = builtins.carbs
    fat = builtins.fat
    price = builtins.price
    carb_foods = builtins.carb_foods
    protein_foods = builtins.protein_foods
    vegetables = builtins.vegetables
    fruits = builtins.fruits
    allowed_foods = builtins.allowed_foods
    min_protein = builtins.min_protein
    max_protein = builtins.max_protein
    min_calories = builtins.min_calories
    max_calories = builtins.max_calories
    min_fat = builtins.min_fat
    max_fat = builtins.max_fat
    max_carbs = builtins.max_carbs
    max_qty = builtins.max_qty
    min_carb_qty = builtins.min_carb_qty
    min_protein_qty = builtins.min_protein_qty
    min_fruit_qty = builtins.min_fruit_qty
    min_veg_qty = builtins.min_veg_qty
    min_calories_meal_pct = builtins.min_calories_meal_pct
    max_calories_meal_pct = builtins.max_calories_meal_pct

    model = pulp.LpProblem(f"תפריט_תזונתי_אופטימלי_{run_number}", pulp.LpMinimize)

    # משתנים רציפים לכמויות המזון (גרמים)
    x = {}
    # משתני בינארי לזיהוי אם המזון נבחר כפחמימה, חלבון, פרי, ירק בארוחה
    y_carb = {}
    y_protein = {}
    y_fruit = {}
    y_veg = {}

    # יצירת משתנים
    for j, meal in enumerate(meals):
        for i, food in enumerate(foods):
            allowed = (food in allowed_foods[meal]) and (food not in excluded_foods)
            x[(i, j)] = pulp.LpVariable(f"x_{i}_{j}_{run_number}", lowBound=0, upBound=max_qty if allowed else 0)

    # אילוץ שהמזונות לא מותרים בארוחה יקבלו 0
    for j, meal in enumerate(meals):
        for i, food in enumerate(foods):
            if food not in allowed_foods[meal]:
                model += x[(i, j)] == 0, f"exclude_food_{i}_{meal}_{run_number}"

    # משתני בינארי רק למזונות שמתאימים לתפקידם בארוחה
    for j, meal in enumerate(meals):
        for i, food in enumerate(foods):
            if food in carb_foods and food in allowed_foods[meal] and food not in excluded_foods:
                y_carb[(i, j)] = pulp.LpVariable(f"y_carb_{i}_{j}_{run_number}", cat="Binary")
            else:
                y_carb[(i, j)] = None

            if food in protein_foods and food in allowed_foods[meal] and food not in excluded_foods:
                y_protein[(i, j)] = pulp.LpVariable(f"y_protein_{i}_{j}_{run_number}", cat="Binary")
            else:
                y_protein[(i, j)] = None

            # פרי - רק בתוספות
            if meal == "תוספות" and food in fruits and food in allowed_foods[meal] and food not in excluded_foods:
                y_fruit[(i, j)] = pulp.LpVariable(f"y_fruit_{i}_{j}_{run_number}", cat="Binary")
            else:
                y_fruit[(i, j)] = None

            # ירק - בכל הארוחות מלבד תוספות
            if meal != "תוספות" and food in vegetables and food in allowed_foods[meal] and food not in excluded_foods:
                y_veg[(i, j)] = pulp.LpVariable(f"y_veg_{i}_{j}_{run_number}", cat="Binary")
            else:
                y_veg[(i, j)] = None

    # פונקציית מטרה - מינימום עלות כוללת
    model += pulp.lpSum(price[i] * x[(i, j)] for i, j in x), f"עלות_כוללת_{run_number}"

    # אילוצי תזונה כלליים על סך כל הארוחות
    model += pulp.lpSum(protein[i] * x[(i, j)] for i, j in x) >= min_protein, f"min_protein_{run_number}"
    model += pulp.lpSum(protein[i] * x[(i, j)] for i, j in x) <= max_protein, f"max_protein_{run_number}"

    model += pulp.lpSum(calories[i] * x[(i, j)] for i, j in x) >= min_calories, f"min_calories_{run_number}"
    model += pulp.lpSum(calories[i] * x[(i, j)] for i, j in x) <= max_calories, f"max_calories_{run_number}"

    model += pulp.lpSum(carbs[i] * x[(i, j)] for i, j in x) <= max_carbs, f"max_carbs_{run_number}"

    model += pulp.lpSum(fat[i] * x[(i, j)] for i, j in x) >= min_fat, f"min_fat_{run_number}"
    model += pulp.lpSum(fat[i] * x[(i, j)] for i, j in x) <= max_fat, f"max_fat_{run_number}"

    # אילוצי קלוריות לפי ארוחה - מינימום ומקסימום באחוזים מתוך סך הקלוריות
    for j, meal in enumerate(meals):
        min_pct = min_calories_meal_pct[meal]
        max_pct = max_calories_meal_pct[meal]
        model += pulp.lpSum(calories[i] * x[(i, j)] for i in range(len(foods))) >= min_pct * min_calories, f"min_calories_{meal}_{run_number}"
        model += pulp.lpSum(calories[i] * x[(i, j)] for i in range(len(foods))) <= max_pct * max_calories, f"max_calories_{meal}_{run_number}"

    # --- אילוצים לפי ארוחה ---

    # בוקר, צהריים וערב: בדיוק פחמימה אחת + בדיוק חלבון אחד + לפחות ירק אחד
    for meal_name in ["בוקר", "צהריים", "ערב"]:
        j = meals.index(meal_name)

        # בדיוק פחמימה אחת
        carb_indices = [i for i in range(len(foods)) if foods[i] in carb_foods and foods[i] in allowed_foods[meal_name]]
        model += pulp.lpSum(y_carb[(i, j)] for i in carb_indices if y_carb[(i, j)] is not None) == 1, f"exactly_one_carb_{meal_name}_{run_number}"

        # בדיוק חלבון אחד
        protein_indices = [i for i in range(len(foods)) if foods[i] in protein_foods and foods[i] in allowed_foods[meal_name]]
        model += pulp.lpSum(y_protein[(i, j)] for i in protein_indices if y_protein[(i, j)] is not None) == 1, f"exactly_one_protein_{meal_name}_{run_number}"

        # לפחות ירק אחד
        veg_indices = [i for i in range(len(foods)) if foods[i] in vegetables and foods[i] in allowed_foods[meal_name]]
        model += pulp.lpSum(y_veg[(i, j)] for i in veg_indices if y_veg[(i, j)] is not None) >= 1, f"min_one_veg_{meal_name}_{run_number}"

    # תוספות: לפחות פרי אחד
    j = meals.index("תוספות")
    fruit_indices = [i for i in range(len(foods)) if foods[i] in fruits and foods[i] in allowed_foods["תוספות"]]
    model += pulp.lpSum(y_fruit[(i, j)] for i in fruit_indices if y_fruit[(i, j)] is not None) >= 1, f"min_one_fruit_tosafot_{run_number}"

    # --- חיבור בין משתני בינארי לכמויות ---

    for j, meal in enumerate(meals):
        for i, food in enumerate(foods):
            if y_carb.get((i, j)) is not None:
                model += x[(i, j)] >= min_carb_qty * y_carb[(i, j)], f"carb_min_qty_{i}_{j}_{run_number}"
                model += x[(i, j)] <= max_qty * y_carb[(i, j)], f"carb_max_qty_{i}_{j}_{run_number}"

            if y_protein.get((i, j)) is not None:
                model += x[(i, j)] >= min_protein_qty * y_protein[(i, j)], f"protein_min_qty_{i}_{j}_{run_number}"
                model += x[(i, j)] <= max_qty * y_protein[(i, j)], f"protein_max_qty_{i}_{j}_{run_number}"

            if y_fruit.get((i, j)) is not None:
                model += x[(i, j)] >= min_fruit_qty * y_fruit[(i, j)], f"fruit_min_qty_{i}_{j}_{run_number}"
                model += x[(i, j)] <= max_qty * y_fruit[(i, j)], f"fruit_max_qty_{i}_{j}_{run_number}"

            if y_veg.get((i, j)) is not None:
                model += x[(i, j)] >= min_veg_qty * y_veg[(i, j)], f"veg_min_qty_{i}_{j}_{run_number}"
                model += x[(i, j)] <= max_qty * y_veg[(i, j)], f"veg_max_qty_{i}_{j}_{run_number}"

    # אילוץ בוקר vs ערב - מזון יכול להיות רק באחד מהם
    j_boker = meals.index("בוקר")
    j_erev = meals.index("ערב")

    for i, food in enumerate(foods):
        if food in allowed_foods["בוקר"] and food in allowed_foods["ערב"]:
            z = pulp.LpVariable(f"z_boker_erev_{i}_{run_number}", cat="Binary")

            # אם z = 1 אז המזון רק בערב, אם z = 0 אז רק בבוקר
            model += x[(i, j_boker)] <= max_qty * (1 - z), f"limit_boker_{i}_{run_number}"
            model += x[(i, j_erev)] <= max_qty * z, f"limit_erev_{i}_{run_number}"

    return model, x