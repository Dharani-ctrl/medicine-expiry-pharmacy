import os
import shutil
import sqlite3
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash
from config import Config

def get_connection():
    engine = Config.DB_ENGINE
    if engine == 'mysql':
        try:
            connection = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return connection, 'mysql'
        except Exception as e:
            print(f"[DB Warning] Could not connect to MySQL ({e}). Falling back to SQLite local database.")
    
    # SQLite Fallback / Default
    os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)
    if not os.path.exists(Config.SQLITE_DB_PATH):
        if not os.path.isfile(Config.SQLITE_SEED_DB_PATH):
            raise FileNotFoundError(f'SQLite seed database not found: {Config.SQLITE_SEED_DB_PATH}')
        shutil.copy2(Config.SQLITE_SEED_DB_PATH, Config.SQLITE_DB_PATH)
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def _format_query(query, engine):
    if engine == 'sqlite':
        # Replace %s with ? for sqlite compatibility
        return query.replace('%s', '?')
    return query

def fetch_all(query, params=()):
    conn, engine = get_connection()
    formatted_query = _format_query(query, engine)
    try:
        if engine == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(formatted_query, params)
                result = cursor.fetchall()
            conn.close()
            return result
        else:
            cursor = conn.cursor()
            cursor.execute(formatted_query, params)
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            conn.close()
            return result
    except Exception as e:
        print(f"[DB Error in fetch_all]: {e}")
        try:
            conn.close()
        except:
            pass
        return []

def fetch_one(query, params=()):
    conn, engine = get_connection()
    formatted_query = _format_query(query, engine)
    try:
        if engine == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(formatted_query, params)
                result = cursor.fetchone()
            conn.close()
            return result
        else:
            cursor = conn.cursor()
            cursor.execute(formatted_query, params)
            row = cursor.fetchone()
            result = dict(row) if row else None
            conn.close()
            return result
    except Exception as e:
        print(f"[DB Error in fetch_one]: {e}")
        try:
            conn.close()
        except:
            pass
        return None

def execute_query(query, params=()):
    conn, engine = get_connection()
    formatted_query = _format_query(query, engine)
    last_id = None
    try:
        if engine == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(formatted_query, params)
                last_id = cursor.lastrowid
            conn.close()
            return last_id
        else:
            cursor = conn.cursor()
            cursor.execute(formatted_query, params)
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
    except Exception as e:
        print(f"[DB Error in execute_query]: {e}")
        try:
            conn.rollback() if engine == 'sqlite' else None
            conn.close()
        except:
            pass
        raise e

def init_db():
    """Initializes tables and seeds default data if not already present."""
    conn, engine = get_connection()
    try:
        if engine == 'sqlite':
            cursor = conn.cursor()
            # SQLite Table definitions
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company_name TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                registered_date DATE,
                supplied_items TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                generic_name TEXT,
                category_id INTEGER NOT NULL,
                supplier_id INTEGER,
                unit TEXT DEFAULT 'Tablet',
                min_stock_level INTEGER DEFAULT 10,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_no TEXT UNIQUE NOT NULL,
                supplier_id INTEGER NOT NULL,
                purchase_date DATE NOT NULL,
                total_amount REAL DEFAULT 0.00,
                paid_amount REAL DEFAULT 0.00,
                payment_status TEXT DEFAULT 'Paid',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicine_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                batch_no TEXT NOT NULL,
                mfg_date DATE,
                expiry_date DATE NOT NULL,
                manufacturer TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                remaining_quantity INTEGER NOT NULL DEFAULT 0,
                purchase_price REAL NOT NULL DEFAULT 0.00,
                selling_price REAL NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (purchase_id) REFERENCES purchases(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                customer_name TEXT DEFAULT 'Walk-in Customer',
                customer_phone TEXT,
                doctor_name TEXT,
                sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                subtotal REAL NOT NULL DEFAULT 0.00,
                tax_amount REAL DEFAULT 0.00,
                discount_amount REAL DEFAULT 0.00,
                grand_total REAL NOT NULL DEFAULT 0.00,
                payment_method TEXT DEFAULT 'Cash',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                batch_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id),
                FOREIGN KEY (batch_id) REFERENCES medicine_batches(id)
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_no TEXT UNIQUE NOT NULL,
                supplier_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                batch_id INTEGER NOT NULL,
                return_quantity INTEGER NOT NULL,
                refund_amount REAL NOT NULL DEFAULT 0.00,
                reason TEXT,
                return_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id),
                FOREIGN KEY (batch_id) REFERENCES medicine_batches(id)
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            conn.commit()

            # Add fields introduced after the initial SQLite schema was created.
            migrations = {
                'suppliers': {
                    'registered_date': 'DATE',
                    'supplied_items': 'TEXT'
                },
                'medicine_batches': {'manufacturer': 'TEXT'},
                'sales': {'doctor_name': 'TEXT'}
            }
            for table_name, columns in migrations.items():
                existing_columns = {
                    row['name'] for row in cursor.execute(
                        f'PRAGMA table_info({table_name})'
                    ).fetchall()
                }
                for column_name, definition in columns.items():
                    if column_name not in existing_columns:
                        cursor.execute(
                            f'ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}'
                        )
            cursor.execute(
                "UPDATE suppliers SET registered_date = DATE('now') "
                "WHERE registered_date IS NULL"
            )
            conn.commit()
            conn.close()
        elif engine == 'mysql':
            # Seed default admin if missing in MySQL
            admin_check = fetch_one("SELECT * FROM admins WHERE username = 'admin'")
            if not admin_check:
                pass_hash = generate_password_hash('admin123')
                execute_query("INSERT IGNORE INTO admins (username, password_hash, email) VALUES (%s, %s, %s)",
                              ('admin', pass_hash, 'admin@pharmacy.com'))

            settings_check = fetch_one("SELECT COUNT(*) as count FROM settings")
            if not settings_check or settings_check['count'] == 0:
                default_settings = [
                    ('pharmacy_name', 'CurePlus Pharmacy & Healthcare'),
                    ('address', '104 Main Street, Medical District, Cityville'),
                    ('phone', '+1 (555) 019-2834'),
                    ('email', 'info@curepluspharmacy.com'),
                    ('tax_no', 'TAX-88942-PHARM'),
                    ('currency_symbol', '₹'),
                    ('receipt_footer', 'Thank you for choosing CurePlus Pharmacy! Get well soon.')
                ]
                for k, v in default_settings:
                    execute_query("INSERT IGNORE INTO settings (setting_key, setting_value) VALUES (%s, %s)", (k, v))
            conn.close()
    except Exception as e:
        print(f"[DB Init Exception]: {e}")
