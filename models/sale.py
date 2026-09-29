from models.db import fetch_all, fetch_one, execute_query

class SaleModel:
    @staticmethod
    def get_all():
        sql = """
            SELECT s.*, COUNT(i.id) AS total_items
            FROM sales s
            LEFT JOIN sale_items i ON i.sale_id = s.id
            GROUP BY s.id
            ORDER BY s.sale_date DESC, s.id DESC
        """
        return fetch_all(sql)

    @staticmethod
    def get_by_id(sale_id):
        return fetch_one("SELECT * FROM sales WHERE id = %s", (sale_id,))

    @staticmethod
    def get_items(sale_id):
        sql = """
            SELECT i.*, m.name AS medicine_name, m.generic_name, m.unit, b.batch_no, b.manufacturer, b.expiry_date
            FROM sale_items i
            JOIN medicines m ON i.medicine_id = m.id
            JOIN medicine_batches b ON i.batch_id = b.id
            WHERE i.sale_id = %s
        """
        return fetch_all(sql, (sale_id,))

    @staticmethod
    def create(invoice_no, customer_name, customer_phone, subtotal, tax_amount, discount_amount, grand_total, payment_method, doctor_name=None):
        return execute_query(
            """INSERT INTO sales (invoice_no, customer_name, customer_phone, doctor_name, subtotal, tax_amount, discount_amount, grand_total, payment_method)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (invoice_no, customer_name, customer_phone, doctor_name, subtotal, tax_amount, discount_amount, grand_total, payment_method)
        )

    @staticmethod
    def add_sale_item(sale_id, medicine_id, batch_id, quantity, unit_price, total_price):
        # 1. Add item
        item_id = execute_query(
            """INSERT INTO sale_items (sale_id, medicine_id, batch_id, quantity, unit_price, total_price)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (sale_id, medicine_id, batch_id, quantity, unit_price, total_price)
        )
        # 2. Deduct batch remaining quantity
        execute_query(
            "UPDATE medicine_batches SET remaining_quantity = remaining_quantity - %s WHERE id = %s",
            (quantity, batch_id)
        )
        return item_id

    @staticmethod
    def generate_invoice_no():
        last = fetch_one("SELECT MAX(id) as max_id FROM sales")
        next_id = (last['max_id'] or 0) + 1 if last else 1
        return f"INV-{next_id:06d}"

    @staticmethod
    def get_today_sales_summary():
        sql = """
            SELECT COALESCE(SUM(grand_total), 0) as total_amount, COUNT(id) as total_invoices
            FROM sales
            WHERE DATE(sale_date) = CURDATE()
        """
        # Note: SQLite date fallback helper in services/report_service or query compatibility
        return fetch_one(sql)
