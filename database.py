import sqlite3
import os

# ===========================
# Database Connection Handler
# ===========================

def get_db_connection():
    """
    מחזיר חיבור למסד הנתונים בהתאם לסביבה
    SQLite למקומי, PostgreSQL לפרודקשן
    """
    # בינתיים נשתמש רק ב-SQLite (גם לפיתוח וגם לפרודקשן)
    # נעדכן ל-PostgreSQL אחר כך ב-Railway
    try:
        from config import DATABASE_URL
        if DATABASE_URL:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn, 'postgresql'
    except:
        pass
    
    # SQLite (ברירת מחדל)
    from config import DB_NAME
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def execute_query(query, params=None, fetch=False, fetch_one=False):
    """
    מריץ שאילתא ומחזיר תוצאות
    """
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        else:
            result = None
        
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def init_database():
    """
    אתחול מסד הנתונים - יוצר טבלאות אם לא קיימות
    """
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    # הגדרת AUTO_INCREMENT בהתאם לסוג DB
    if db_type == 'postgresql':
        auto_increment = 'SERIAL PRIMARY KEY'
        text_type = 'TEXT'
    else:
        auto_increment = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        text_type = 'TEXT'
    
    # Create users table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            id {auto_increment},
            email {text_type} UNIQUE NOT NULL,
            password {text_type} NOT NULL,
            name {text_type},
            age INTEGER,
            gender {text_type},
            weight REAL,
            height REAL,
            activity_level {text_type},
            goal {text_type},
            allergies {text_type},
            health_conditions {text_type},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create foods table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS foods (
            id {auto_increment},
            name {text_type} NOT NULL,
            category {text_type},
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            fiber REAL,
            price REAL,
            unit {text_type},
            last_price_update TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create menus table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS menus (
            id {auto_increment},
            user_id INTEGER NOT NULL,
            name {text_type},
            menu_data {text_type},
            total_cost REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Database initialized successfully ({db_type})")