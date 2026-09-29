from werkzeug.security import generate_password_hash, check_password_hash
from models.db import fetch_one, execute_query, fetch_all

class AdminModel:
    @staticmethod
    def get_by_username(username):
        return fetch_one("SELECT * FROM admins WHERE username = %s", (username,))

    @staticmethod
    def get_by_id(admin_id):
        return fetch_one("SELECT * FROM admins WHERE id = %s", (admin_id,))

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

    @staticmethod
    def update_profile(admin_id, username, email):
        return execute_query("UPDATE admins SET username = %s, email = %s WHERE id = %s",
                             (username, email, admin_id))

    @staticmethod
    def update_password(admin_id, new_password):
        pass_hash = generate_password_hash(new_password)
        return execute_query("UPDATE admins SET password_hash = %s WHERE id = %s",
                             (pass_hash, admin_id))

    @staticmethod
    def get_all_settings():
        rows = fetch_all("SELECT setting_key, setting_value FROM settings")
        settings_dict = {}
        for r in rows:
            settings_dict[r['setting_key']] = r['setting_value']
        return settings_dict

    @staticmethod
    def update_setting(key, value):
        existing = fetch_one("SELECT id FROM settings WHERE setting_key = %s", (key,))
        if existing:
            return execute_query("UPDATE settings SET setting_value = %s WHERE setting_key = %s", (value, key))
        else:
            return execute_query("INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s)", (key, value))
