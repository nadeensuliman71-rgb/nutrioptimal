import os

# ===========================
# הגדרות בסיסיות
# ===========================

# Environment
ENV = os.getenv('FLASK_ENV', 'production')
DEBUG = ENV == 'development'

# Secret Key
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Port
PORT = int(os.getenv('PORT', 5001))

# ===========================
# הגדרות Database
# ===========================

# Railway provides DATABASE_URL automatically for PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Production - PostgreSQL
    DB_TYPE = 'postgresql'
    DB_URL = DATABASE_URL
else:
    # Development - SQLite
    DB_TYPE = 'sqlite'
    DB_URL = 'sqlite:///nutrioptimal.db'
    DB_NAME = 'nutrioptimal.db'

# ===========================
# הגדרות Selenium
# ===========================

# בסביבת פרודקשן (Railway) - headless mode
SELENIUM_HEADLESS = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'

# Chrome options for production
CHROME_OPTIONS = [
    '--headless',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-extensions',
]

# ===========================
# הגדרות App
# ===========================

# Admin email
ADMIN_EMAIL = 'meira199@gmail.com'

# Schedule for price updates (cron format)
# Default: every day at 2 AM
PRICE_UPDATE_SCHEDULE = os.getenv('PRICE_UPDATE_SCHEDULE', '0 2 * * *')