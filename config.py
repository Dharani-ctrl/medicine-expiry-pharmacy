import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_pharmacy_secret_key_12345')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'pharmacy_db')
    DB_ENGINE = os.getenv('DB_ENGINE', 'mysql').lower()
    SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'pharmacy.db')
    SQLITE_SEED_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'seed.db')
