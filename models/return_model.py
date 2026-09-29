from models.db import fetch_all, fetch_one, execute_query

class PurchaseReturnModel:
    @staticmethod
    def get_all():
        sql = """
            SELECT r.*, s.name AS supplier_name, m.name AS medicine_name, b.batch_no, b.expiry_date
            FROM purchase_returns r
            JOIN suppliers s ON r.supplier_id = s.id
            JOIN medicines m ON r.medicine_id = m.id
            JOIN medicine_batches b ON r.batch_id = b.id
            ORDER BY r.return_date DESC, r.id DESC
        """
        return fetch_all(sql)

    @staticmethod
    def get_by_id(return_id):
        sql = """
            SELECT r.*, s.name AS supplier_name, m.name AS medicine_name, b.batch_no, b.expiry_date
            FROM purchase_returns r
            JOIN suppliers s ON r.supplier_id = s.id
            JOIN medicines m ON r.medicine_id = m.id
            JOIN medicine_batches b ON r.batch_id = b.id
            WHERE r.id = %s
        """
        return fetch_one(sql, (return_id,))

    @staticmethod
    def create(return_no, supplier_id, medicine_id, batch_id, return_quantity, refund_amount, reason, return_date):
        # 1. Create return record
        return_id = execute_query(
            """INSERT INTO purchase_returns (return_no, supplier_id, medicine_id, batch_id, return_quantity, refund_amount, reason, return_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (return_no, supplier_id, medicine_id, batch_id, return_quantity, refund_amount, reason, return_date)
        )
        # 2. Reduce stock from batch
        execute_query(
            "UPDATE medicine_batches SET remaining_quantity = remaining_quantity - %s WHERE id = %s",
            (return_quantity, batch_id)
        )
        return return_id

    @staticmethod
    def generate_return_no():
        last = fetch_one("SELECT MAX(id) as max_id FROM purchase_returns")
        next_id = (last['max_id'] or 0) + 1 if last else 1
        return f"RET-{next_id:05d}"
