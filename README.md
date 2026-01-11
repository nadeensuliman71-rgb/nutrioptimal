# NutriOptimal - Fixed Version

## מה תוקן? (What was fixed?)

### תיקון עיקרי: קובץ `pricing/scrapers.py`
הבעיה העיקרית שזוהתה הייתה בקובץ הסקרייפרס:

1. **תיקון קידוד (Encoding Fix)**: הקובץ המקורי הכיל שורות בסגנון Windows (`\r\n`) שיכולים לגרום לבעיות בסביבות Linux/Unix
2. **תיקון תווים**: כל הטקסט בעברית עכשיו מוצג כראוי ללא בעיות Unicode
3. **הוספת ארגומנטים לדפדפן**: הוספתי את הארגומנטים הבאים לכל שלושת הסקרייפרס לשיפור יציבות:
   - `--no-sandbox`
   - `--disable-dev-shm-usage`
4. **תיקון פורמט**: תיקון מבנה הקוד והוספת הערות מסודרות

### שיפורים בוצעו ב:
- ✅ `get_prices_shufersal()` - סקרייפר לקניון שופרסל
- ✅ `get_prices_victory()` - סקרייפר לסופר ויקטורי
- ✅ `get_prices_from_rami_levy()` - סקרייפר לרמי לוי

## איך להשתמש (How to use)

### 1. התקנת דרישות מוקדמות
```bash
cd NutriOptimal_Fixed
pip install -r requirements.txt
```

### 2. הרצת האפליקציה
```bash
python app.py
```

האפליקציה תרוץ על: `http://localhost:5001`

### 3. עדכון מחירים
אחרי כניסה למערכת, לחץ על "עדכן מחירים" בדשבורד כדי לשלוף מחירים עדכניים מכל הסופרמרקטים.

## תלויות (Dependencies)
- Flask
- Flask-CORS
- Selenium
- webdriver-manager
- openpyxl

## מבנה הפרויקט
```
NutriOptimal_Fixed/
├── app.py                 # אפליקציית Flask ראשית
├── algorithm.py           # אלגוריתם אופטימיזציה
├── meal_utils.py          # כלי עזר לארוחות
├── pricing/
│   ├── scrapers.py        # סקרייפרס מחירים - הקובץ שתוקן ⭐
│   └── __init__.py
├── optimizer/             # מודל אופטימיזציה
├── templates/             # קבצי HTML
├── static/                # CSS, JS, תמונות
└── requirements.txt       # דרישות התקנה
```

## פתרון בעיות נפוצות

### אם המחירים לא מתעדכנים:
1. וודא שיש לך חיבור לאינטרנט
2. נסה להריץ מחדש את האפליקציה
3. בדוק את הלוגים בקונסולה למידע נוסף

### אם הדפדפן לא נפתח:
- וודא ש-Chrome מותקן במחשב
- webdriver-manager יוריד את הדרייבר המתאים אוטומטית

## גרסה
Fixed Version 1.0

## יוצר
Team NutriOptimal