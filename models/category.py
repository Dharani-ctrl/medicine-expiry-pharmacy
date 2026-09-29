from models.db import fetch_all, fetch_one, execute_query

class CategoryModel:
    @staticmethod
    def get_all():
        sql = """
            SELECT c.*, COUNT(m.id) AS medicine_count
            FROM categories c
            LEFT JOIN medicines m ON m.category_id = c.id
            GROUP BY c.id
            ORDER BY c.name ASC
        """
        return fetch_all(sql)

    @staticmethod
    def get_active():
        return fetch_all("SELECT * FROM categories WHERE status = 'active' ORDER BY name ASC")

    @staticmethod
    def get_by_id(category_id):
        return fetch_one("SELECT * FROM categories WHERE id = %s", (category_id,))

    @staticmethod
    def create(name, description, status='active'):
        return execute_query("INSERT INTO categories (name, description, status) VALUES (%s, %s, %s)",
                             (name, description, status))

    @staticmethod
    def update(category_id, name, description, status):
        return execute_query("UPDATE categories SET name = %s, description = %s, status = %s WHERE id = %s",
                             (name, description, status, category_id))

    @staticmethod
    def delete(category_id):
        return execute_query("DELETE FROM categories WHERE id = %s", (category_id,))

    @staticmethod
    def count_medicines(category_id):
        row = fetch_one("SELECT COUNT(*) as count FROM medicines WHERE category_id = %s", (category_id,))
        return row['count'] if row else 0
