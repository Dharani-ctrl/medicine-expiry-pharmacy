from models.db import fetch_all, fetch_one, execute_query

class PurchaseModel:
    @staticmethod
    def get_all():
        sql = """
            SELECT p.*, s.name AS supplier_name, COUNT(b.id) AS item_count
            FROM purchases p
            JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN medicine_batches b ON b.purchase_id = p.id
            GROUP BY p.id
            ORDER BY p.purchase_date DESC, p.id DESC
        """
        return fetch_all(sql)

    @staticmethod
    def get_by_id(purchase_id):
        sql = """
            SELECT p.*, s.name AS supplier_name, s.company_name, s.phone AS supplier_phone, s.address AS supplier_address
            FROM purchases p
            JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.id = %s
        """
        return fetch_one(sql, (purchase_id,))

    @staticmethod
    def get_items(purchase_id):
        sql = """
            SELECT b.*, m.name AS medicine_name, m.generic_name, m.unit
            FROM medicine_batches b
            JOIN medicines m ON b.medicine_id = m.id
            WHERE b.purchase_id = %s
        """
        return fetch_all(sql, (purchase_id,))

    @staticmethod
    def create(purchase_no, supplier_id, purchase_date, total_amount, paid_amount, payment_status, notes):
        return execute_query(
            """INSERT INTO purchases (purchase_no, supplier_id, purchase_date, total_amount, paid_amount, payment_status, notes)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (purchase_no, supplier_id, purchase_date, total_amount, paid_amount, payment_status, notes)
        )

    @staticmethod
    def add_batch(purchase_id, medicine_id, batch_no, mfg_date, expiry_date, quantity, purchase_price, selling_price, manufacturer=None):
        return execute_query(
            """INSERT INTO medicine_batches (purchase_id, medicine_id, batch_no, mfg_date, expiry_date, manufacturer, quantity, remaining_quantity, purchase_price, selling_price)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (purchase_id, medicine_id, batch_no, mfg_date, expiry_date, manufacturer, quantity, quantity, purchase_price, selling_price)
        )

    @staticmethod
    def generate_purchase_no():
        last = fetch_one("SELECT MAX(id) as max_id FROM purchases")
        next_id = (last['max_id'] or 0) + 1 if last else 1
        return f"PUR-{next_id:05d}"
