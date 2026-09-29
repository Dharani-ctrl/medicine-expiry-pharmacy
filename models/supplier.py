from models.db import fetch_all, fetch_one, execute_query

class SupplierModel:
    @staticmethod
    def get_all():
        sql = """
            SELECT s.*, COUNT(p.id) AS total_purchases
            FROM suppliers s
            LEFT JOIN purchases p ON p.supplier_id = s.id
            GROUP BY s.id
            ORDER BY s.name ASC
        """
        return fetch_all(sql)

    @staticmethod
    def get_active():
        return fetch_all("SELECT * FROM suppliers WHERE status = 'active' ORDER BY name ASC")

    @staticmethod
    def get_by_id(supplier_id):
        return fetch_one("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))

    @staticmethod
    def create(name, company_name, phone, email, address, status='active', registered_date=None, supplied_items=None):
        return execute_query(
            "INSERT INTO suppliers (name, company_name, phone, email, address, status, registered_date, supplied_items) VALUES (%s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_DATE), %s)",
            (name, company_name, phone, email, address, status, registered_date, supplied_items)
        )

    @staticmethod
    def update(supplier_id, name, company_name, phone, email, address, status, registered_date=None, supplied_items=None):
        return execute_query(
            "UPDATE suppliers SET name = %s, company_name = %s, phone = %s, email = %s, address = %s, status = %s, registered_date = COALESCE(%s, registered_date), supplied_items = %s WHERE id = %s",
            (name, company_name, phone, email, address, status, registered_date, supplied_items, supplier_id)
        )

    @staticmethod
    def delete(supplier_id):
        return execute_query("DELETE FROM suppliers WHERE id = %s", (supplier_id,))

    @staticmethod
    def get_purchases(supplier_id):
        sql = """
            SELECT p.*, s.name as supplier_name 
            FROM purchases p
            JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.supplier_id = %s
            ORDER BY p.purchase_date DESC
        """
        return fetch_all(sql, (supplier_id,))
