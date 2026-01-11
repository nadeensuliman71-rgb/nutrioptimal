import pulp
import random
import copy
from pulp import LpVariable, LpProblem, LpMinimize, LpStatusOptimal, PULP_CBC_CMD

# 🔧 הגדרת seed קבוע לתוצאות עקביות\nRANDOM_SEED = 42


class MenuOptimizer:
    """
    כיתה לאופטימיזציה של תפריט תזונתי באמצעות MILP
    """

    def __init__(self, foods_db, user_params):

        # 🔧 הגדרת seed קבוע לתוצאות עקביות\n        random.seed(RANDOM_SEED)
        """
        אתחול האופטימייזר

        Args:
            foods_db: רשימת מזונות ממסד הנתונים
            user_params: פרמטרים מהמשתמש (קלוריות, חלבון, וכו')
        """
        # המרת מזונות ממסד הנתונים לפורמט של האלגוריתם
        self.foods = []
        self.protein = []
        self.calories = []
        self.carbs = []
        self.fat = []
        self.price = []
        self.food_categories = {}

        for food in foods_db:
            name = food["name"]
            self.foods.append(name)

            # 🔹 כל הערכים הם ל־100 גרם → מחלקים ב־100 כדי לקבל ל־גרם
            self.protein.append(food["protein"] / 100)
            self.calories.append(food["calories"] / 100)
            self.carbs.append(food["carbs"] / 100)
            self.fat.append(food["fat"] / 100)

            # ✅ מחיר פעיל לאלגוריתם
            if "price" in food and food["price"] is not None:
                active_price = food["price"]   # ⭐ מחיר מסופר ספציפי
            else:
                prices = food.get("prices", {}) or {}
                active_src = food.get("active_price_source", None)
                active_price = prices.get(active_src) if active_src else None

            if active_price is None:
                raise ValueError(f"❌ אין מחיר פעיל למזון: {name}")

# 🔹 מחיר ל־100 גרם → לגרם
            self.price.append(active_price / 100)


            self.food_categories[name] = food["category"]

        # ארוחות
        self.meals = ["בוקר", "צהריים", "ערב", "תוספות"]

        # סיווג מזונות לפי קטגוריות
        self.carb_foods = {food for food, cat in self.food_categories.items() if cat == "carb"}
        self.protein_foods = {food for food, cat in self.food_categories.items() if cat == "protein"}
        self.fruits = {food for food, cat in self.food_categories.items() if cat == "fruit"}
        self.vegetables = {food for food, cat in self.food_categories.items() if cat == "vegetable"}

        # הגדרת מזונות מותרים בכל ארוחה
        self.original_allowed_foods = self._build_allowed_foods(foods_db)
        self.allowed_foods = copy.deepcopy(self.original_allowed_foods)

        # פרמטרים מהמשתמש
        self.min_calories = user_params.get("min_calories", 1500)
        self.max_calories = user_params.get("max_calories", 2000)
        self.min_protein = user_params.get("min_protein", 100)
        self.max_protein = user_params.get("max_protein", 150)
        self.min_carbs = user_params.get("min_carbs", 150)
        self.max_carbs = user_params.get("max_carbs", 250)
        self.min_fat = user_params.get("min_fat", 50)
        self.max_fat = user_params.get("max_fat", 70)

        # אחוזי קלוריות לארוחה
        self.min_calories_meal_pct = {
            "בוקר": 0.20,
            "צהריים": 0.30,
            "ערב": 0.25,
            "תוספות": 0.10
        }

        self.max_calories_meal_pct = {
            "בוקר": 0.30,
            "צהריים": 0.40,
            "ערב": 0.35,
            "תוספות": 0.20
        }

        # כמויות מינימליות (בגרמים)
        self.min_carb_qty = 30
        self.min_protein_qty = 50
        self.min_fruit_qty = 50
        self.min_veg_qty = 30
        self.max_qty = 500

        # שמירת רשימות מקוריות
        self.original_foods = self.foods[:]
        self.original_protein = self.protein[:]
        self.original_calories = self.calories[:]
        self.original_carbs = self.carbs[:]
        self.original_fat = self.fat[:]
        self.original_price = self.price[:]

        # ✅ מפת אינדקסים כדי לא להשתמש ב-index() (מונע list index out of range)
        self.food_index = {food: i for i, food in enumerate(self.foods)}

        print("DEBUG lengths:")
        print("foods     =", len(self.foods))
        print("calories  =", len(self.calories))
        print("protein   =", len(self.protein))
        print("price     =", len(self.price))

    def _build_allowed_foods(self, foods_db):
        """
        ✅ בונה מילון של מזונות מותרים בכל ארוחה.
        תומך בזה ש-allowed_meals יכול להגיע:
        - באנגלית: breakfast/lunch/dinner/snacks
        - בעברית: בוקר/צהריים/ערב/תוספות
        - או ערבוב של שניהם
        """

        # מיפוי מכל ערך אפשרי לערך עברי "סטנדרטי"
        normalize = {
            "breakfast": "בוקר",
            "lunch": "צהריים",
            "dinner": "ערב",
            "snacks": "תוספות",
            "בוקר": "בוקר",
            "צהריים": "צהריים",
            "ערב": "ערב",
            "תוספות": "תוספות",
        }

        allowed = {meal: set() for meal in self.meals}

        for food in foods_db:
            meals_list = food.get("allowed_meals", []) or []
            if not isinstance(meals_list, list):
                meals_list = [meals_list]

            for m in meals_list:
                m_norm = normalize.get(str(m).strip())
                if m_norm in allowed:
                    allowed[m_norm].add(food["name"])

        return allowed

    def build_model(self, excluded_foods=None, run_number=0):
        """
        בונה את המודל של MILP
        """
        if excluded_foods is None:
            excluded_foods = set()

        model = pulp.LpProblem("תפריט_תזונתי_אופטימלי", pulp.LpMinimize)

        # משתנים רציפים לכמויות המזון (גרמים)
        x = {}
        # משתני בינארי לזיהוי אם המזון נבחר כפחמימה, חלבון, פרי, ירק בארוחה
        y_carb = {}
        y_protein = {}
        y_fruit = {}
        y_veg = {}

        # יצירת משתנים
        for j, meal in enumerate(self.meals):
            for i, food in enumerate(self.foods):
                allowed = (food in self.allowed_foods[meal]) and (food not in excluded_foods)
                x[(i, j)] = pulp.LpVariable(
                    f"x_{i}_{j}",
                    lowBound=0,
                    upBound=self.max_qty if allowed else 0
                )

        # אילוץ שהמזונות לא מותרים בארוחה יקבלו 0
        for j, meal in enumerate(self.meals):
            for i, food in enumerate(self.foods):
                if food not in self.allowed_foods[meal]:
                    model += x[(i, j)] == 0, f"exclude_food_{food}_{meal}_{run_number}"

        # משתני בינארי רק למזונות שמתאימים לתפקידם בארוחה
        for j, meal in enumerate(self.meals):
            for i, food in enumerate(self.foods):
                if food in self.carb_foods and food in self.allowed_foods[meal] and food not in excluded_foods:
                    y_carb[(i, j)] = pulp.LpVariable(f"y_carb_{i}_{j}", cat="Binary")
                else:
                    y_carb[(i, j)] = None

                if food in self.protein_foods and food in self.allowed_foods[meal] and food not in excluded_foods:
                    y_protein[(i, j)] = pulp.LpVariable(f"y_protein_{i}_{j}", cat="Binary")
                else:
                    y_protein[(i, j)] = None

                # פרי - רק בתוספות
                if meal == "תוספות" and food in self.fruits and food in self.allowed_foods[meal] and food not in excluded_foods:
                    y_fruit[(i, j)] = pulp.LpVariable(f"y_fruit_{i}_{j}", cat="Binary")
                else:
                    y_fruit[(i, j)] = None

                # ירק - בכל הארוחות מלבד תוספות
                if meal != "תוספות" and food in self.vegetables and food in self.allowed_foods[meal] and food not in excluded_foods:
                    y_veg[(i, j)] = pulp.LpVariable(f"y_veg_{i}_{j}", cat="Binary")
                else:
                    y_veg[(i, j)] = None

        # פונקציית מטרה - מינימום עלות כוללת
        model += pulp.lpSum(self.price[i] * x[(i, j)] for (i, j) in x), f"עלות_כוללת_{run_number}"

        # אילוצי תזונה כלליים על סך כל הארוחות
        model += pulp.lpSum(self.protein[i] * x[(i, j)] for (i, j) in x) >= self.min_protein, f"min_protein_{run_number}"
        model += pulp.lpSum(self.protein[i] * x[(i, j)] for (i, j) in x) <= self.max_protein, f"max_protein_{run_number}"

        model += pulp.lpSum(self.calories[i] * x[(i, j)] for (i, j) in x) >= self.min_calories, f"min_calories_{run_number}"
        model += pulp.lpSum(self.calories[i] * x[(i, j)] for (i, j) in x) <= self.max_calories, f"max_calories_{run_number}"

        model += pulp.lpSum(self.carbs[i] * x[(i, j)] for (i, j) in x) <= self.max_carbs, f"max_carbs_{run_number}"

        model += pulp.lpSum(self.fat[i] * x[(i, j)] for (i, j) in x) >= self.min_fat, f"min_fat_{run_number}"
        model += pulp.lpSum(self.fat[i] * x[(i, j)] for (i, j) in x) <= self.max_fat, f"max_fat_{run_number}"

        # אילוצי קלוריות לפי ארוחה
        for j, meal in enumerate(self.meals):
            min_pct = self.min_calories_meal_pct[meal]
            max_pct = self.max_calories_meal_pct[meal]
            model += pulp.lpSum(self.calories[i] * x[(i, j)] for i in range(len(self.calories))) >= min_pct * self.min_calories, f"min_calories_{meal}_{run_number}"
            model += pulp.lpSum(self.calories[i] * x[(i, j)] for i in range(len(self.calories))) <= max_pct * self.max_calories, f"max_calories_{meal}_{run_number}"

        # --- אילוצים לפי ארוחה ---
        for meal_name in ["בוקר", "צהריים", "ערב"]:
            j = self.meals.index(meal_name)

            carb_indices = [i for i in range(len(self.foods))
                            if self.foods[i] in self.carb_foods and self.foods[i] in self.allowed_foods[meal_name]]
            model += pulp.lpSum(y_carb[(i, j)] for i in carb_indices if y_carb[(i, j)] is not None) == 1, f"exactly_one_carb_{meal_name}_{run_number}"

            protein_indices = [i for i in range(len(self.foods))
                               if self.foods[i] in self.protein_foods and self.foods[i] in self.allowed_foods[meal_name]]
            model += pulp.lpSum(y_protein[(i, j)] for i in protein_indices if y_protein[(i, j)] is not None) == 1, f"exactly_one_protein_{meal_name}_{run_number}"

            veg_indices = [i for i in range(len(self.foods))
                           if self.foods[i] in self.vegetables and self.foods[i] in self.allowed_foods[meal_name]]
            model += pulp.lpSum(y_veg[(i, j)] for i in veg_indices if y_veg[(i, j)] is not None) >= 1, f"min_one_veg_{meal_name}_{run_number}"

        # תוספות: לפחות פרי אחד
        j = self.meals.index("תוספות")
        fruit_indices = [i for i in range(len(self.foods))
                         if self.foods[i] in self.fruits and self.foods[i] in self.allowed_foods["תוספות"]]
        model += pulp.lpSum(y_fruit[(i, j)] for i in fruit_indices if y_fruit[(i, j)] is not None) >= 1, f"min_one_fruit_tosafot_{run_number}"

        # --- חיבור בין משתני בינארי לכמויות ---
        for j, meal in enumerate(self.meals):
            for i, food in enumerate(self.foods):
                if y_carb.get((i, j)) is not None:
                    model += x[(i, j)] >= self.min_carb_qty * y_carb[(i, j)], f"carb_min_qty_{i}_{j}_{run_number}"
                    model += x[(i, j)] <= self.max_qty * y_carb[(i, j)], f"carb_max_qty_{i}_{j}_{run_number}"

                if y_protein.get((i, j)) is not None:
                    model += x[(i, j)] >= self.min_protein_qty * y_protein[(i, j)], f"protein_min_qty_{i}_{j}_{run_number}"
                    model += x[(i, j)] <= self.max_qty * y_protein[(i, j)], f"protein_max_qty_{i}_{j}_{run_number}"

                if y_fruit.get((i, j)) is not None:
                    model += x[(i, j)] >= self.min_fruit_qty * y_fruit[(i, j)], f"fruit_min_qty_{i}_{j}_{run_number}"
                    model += x[(i, j)] <= self.max_qty * y_fruit[(i, j)], f"fruit_max_qty_{i}_{j}_{run_number}"

                if y_veg.get((i, j)) is not None:
                    model += x[(i, j)] >= self.min_veg_qty * y_veg[(i, j)], f"veg_min_qty_{i}_{j}_{run_number}"
                    model += x[(i, j)] <= self.max_qty * y_veg[(i, j)], f"veg_max_qty_{i}_{j}_{run_number}"

        # מניעת אותו מזון בבוקר וגם בערב (אם מותר בשניהם)
        j_boker = self.meals.index("בוקר")
        j_erev = self.meals.index("ערב")

        for i, food in enumerate(self.foods):
            if food in self.allowed_foods["בוקר"] and food in self.allowed_foods["ערב"]:
                z = pulp.LpVariable(f"z_boker_erev_{i}_{run_number}", cat="Binary")
                model += x[(i, j_boker)] <= self.max_qty * (1 - z), f"limit_boker_{i}_{run_number}"
                model += x[(i, j_erev)] <= self.max_qty * z, f"limit_erev_{i}_{run_number}"

        return model, x

    def shuffle_and_filter_meals(self, meals_list, target_days):
        max_attempts = 100
        attempt = 0

        def serialize_day(day):
            return tuple(
                (meal, tuple(sorted(day.get(meal, [])))) for meal in ["בוקר", "צהריים", "ערב", "תוספות"]
            )

        while attempt < max_attempts:
            attempt += 1
            random.shuffle(meals_list)
            filtered = []
            prev_day_foods = set()
            prev_day_serialized = None

            for day in meals_list:
                current_day_foods = set()
                for meal_name in ["בוקר", "צהריים", "ערב", "תוספות"]:
                    for food_name, qty in day.get(meal_name, []):
                        current_day_foods.add(food_name)

                non_veg_today = {food for food in current_day_foods if food not in self.vegetables}
                non_veg_prev = {food for food in prev_day_foods if food not in self.vegetables}

                serialized = serialize_day(day)
                if serialized == prev_day_serialized:
                    continue

                if non_veg_today & non_veg_prev:
                    continue

                filtered.append(day)
                prev_day_foods = current_day_foods
                prev_day_serialized = serialized

                if len(filtered) == target_days:
                    return filtered

        print(f"\n⚠️ לא הצלחנו למצוא {target_days} ימים אחרי {max_attempts} נסיונות – נמצאו {len(filtered)} בלבד.")

        prev_day_serialized = serialize_day(filtered[-1]) if filtered else None
        while len(filtered) < target_days:
            day_to_add = random.choice(meals_list)
            serialized = serialize_day(day_to_add)
            if serialized == prev_day_serialized:
                continue
            filtered.append(copy.deepcopy(day_to_add))
            prev_day_serialized = serialized

        return filtered

    def generate_menu(self, num_days=7):
        try:

            # 🔧 הגדרת seed קבוע לתוצאות עקביות\n            
            random.seed(42)
            max_days = num_days
            all_days_meals = []
            saved_meals = []
            saved_days_full = []
            pizza = 0
            fail_count = 0
            run = 0
            total_cost_alldays = 0

            while run < max_days:
                if pizza == 1:
                    self.allowed_foods = copy.deepcopy(self.original_allowed_foods)

                if run > 0:
                    for day_meals in all_days_meals:
                        for meal_name in ["בוקר", "צהריים", "ערב"]:
                            for food_name, qty in day_meals[meal_name]:
                                if food_name in self.allowed_foods[meal_name] and (
                                        food_name not in self.vegetables or food_name == "גזר"):
                                    self.allowed_foods[meal_name].remove(food_name)

                    prev_day = all_days_meals[-1]
                    prev_veg_lunch = {food for food, qty in prev_day["צהריים"] if food in self.vegetables}
                    self.allowed_foods["צהריים"] -= prev_veg_lunch

                    prev_tosafot = {food for food, qty in prev_day["תוספות"]}
                    self.allowed_foods["תוספות"] -= prev_tosafot

                model, x = self.build_model(run_number=run)

                # y: האם מזון i נבחר בארוחה j
                y = {}
                max_qty = self.max_qty

                for i in range(len(self.foods)):
                    for j in range(len(self.meals)):
                        y[(i, j)] = pulp.LpVariable(f"y_{i}_{j}", cat="Binary")

                # קישור y ל-x
                for i in range(len(self.foods)):
                    for j in range(len(self.meals)):
                        model += x[(i, j)] <= max_qty * y[(i, j)]
                        model += x[(i, j)] >= 0.001 * y[(i, j)]

                # ✅ מניעת שכפול ארוחה
                for prev_day in saved_meals:
                    for meal_name in ["בוקר", "צהריים", "ערב"]:
                        prev_foods_set = set(food for food, qty in prev_day.get(meal_name, []))
                        if not prev_foods_set:
                            continue

                        j = self.meals.index(meal_name)

                        safe_indices = []
                        for food in prev_foods_set:
                            if food in self.food_index:
                                safe_indices.append(self.food_index[food])

                        if safe_indices:
                            model += pulp.lpSum([y[(idx, j)] for idx in safe_indices]) <= len(safe_indices) - 1

                model.solve(pulp.PULP_CBC_CMD(msg=False))

                if model.status == pulp.LpStatusOptimal:
                    total_cost = pulp.value(model.objective)
                    total_cost_alldays += total_cost
                    run += 1

                    day_meals = {meal: [] for meal in self.meals}

                    for j, meal in enumerate(self.meals):
                        for i, food in enumerate(self.foods):
                            var = x.get((i, j))
                            if var is not None and var.varValue is not None and var.varValue > 0:
                                day_meals[meal].append((food, var.varValue))

                    all_days_meals.append(day_meals)

                    # שמירה ל-saved_meals ללא תוספות
                    day_without_tosafot = {}
                    for meal_name in day_meals:
                        if meal_name != "תוספות":
                            filtered_foods = [(food, qty) for food, qty in day_meals[meal_name] if food not in self.vegetables]
                            day_without_tosafot[meal_name] = filtered_foods

                    saved_meals.append(day_without_tosafot)
                    saved_days_full.append(copy.deepcopy(day_meals))

                    pizza = 0
                    fail_count = 0
                else:
                    print("לא נמצא פתרון אופטימלי ביום", run + 1)
                    pizza = 1
                    fail_count += 1

                    if fail_count >= 2:
                        print("\n⚠️ לא נמצא פתרון אופטימלי פעמיים ברצף")

                        if len(saved_days_full) == 0:
                            return {
                                "success": False,
                                "message": "לא נמצא אף פתרון אפילו ליום אחד. בדקי אילוצים או מזונות מותרים."
                            }

                        days_needed = max_days - len(saved_meals)
                        all_meals_to_use = saved_days_full * ((days_needed // len(saved_days_full)) + 1)
                        all_meals_to_use = all_meals_to_use[:days_needed]
                        

                        for day in all_meals_to_use:
                            day_meals = {meal: [] for meal in self.meals}
                            for meal_name in self.meals:
                                for food_name, qty in day.get(meal_name, []):
                                    day_meals[meal_name].append((food_name, qty))
                            all_days_meals.append(day_meals)
                            run += 1

                        break

                    continue

            # תוצאות סופיות
            formatted_days = []
            for day in all_days_meals:
                day_protein = day_calories = day_fat = day_carbs = 0

                formatted_day = {
                    "breakfast": [],
                    "lunch": [],
                    "dinner": [],
                    "snacks": []
                }

                for meal_name, english_name in [("בוקר", "breakfast"), ("צהריים", "lunch"), ("ערב", "dinner"), ("תוספות", "snacks")]:
                    for food, qty in day.get(meal_name, []):
                        formatted_day[english_name].append((food, qty))
                        if food not in self.food_index:
                            continue
                        i = self.food_index[food]
                        day_protein += self.protein[i] * qty
                        day_calories += self.calories[i] * qty
                        day_fat += self.fat[i] * qty
                        day_carbs += self.carbs[i] * qty

                formatted_day["nutrition"] = {
                    "protein": round(day_protein, 1),
                    "calories": round(day_calories, 1),
                    "carbs": round(day_carbs, 1),
                    "fat": round(day_fat, 1)
                }

                formatted_days.append(formatted_day)

            avg_cost_per_day = total_cost_alldays / num_days if num_days > 0 else 0

            return {
                "success": True,
                "days": formatted_days,
                "total_cost": round(total_cost_alldays, 2),
                "avg_cost_per_day": round(avg_cost_per_day, 2)
            }

        except Exception as e:
            print(f"❌ שגיאה בחישוב: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"שגיאה בחישוב: {str(e)}"
            }
