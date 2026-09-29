from models.db import fetch_all, fetch_one, execute_query

class MedicineModel:
    @staticmethod
    def get_all():
        sql = """
            SELECT m.*, c.name AS category_name, s.name AS supplier_name,
                   COALESCE(SUM(b.remaining_quantity), 0) AS total_stock
            FROM medicines m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            LEFT JOIN medicine_batches b ON b.medicine_id = m.id AND b.remaining_quantity > 0
            GROUP BY m.id
            ORDER BY m.name ASC
        """
        return fetch_all(sql)

    @staticmethod
    def get_by_id(medicine_id):
        sql = """
            SELECT m.*, c.name AS category_name, s.name AS supplier_name,
                   COALESCE(SUM(b.remaining_quantity), 0) AS total_stock
            FROM medicines m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            LEFT JOIN medicine_batches b ON b.medicine_id = m.id AND b.remaining_quantity > 0
            WHERE m.id = %s
            GROUP BY m.id
        """
        return fetch_one(sql, (medicine_id,))

    @staticmethod
    def search(query, category_id=None, status=None):
        sql = """
            SELECT m.*, c.name AS category_name, s.name AS supplier_name,
                   COALESCE(SUM(b.remaining_quantity), 0) AS total_stock
            FROM medicines m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            LEFT JOIN medicine_batches b ON b.medicine_id = m.id AND b.remaining_quantity > 0
            WHERE 1=1
        """
        params = []
        if query:
            sql += " AND (m.name LIKE %s OR m.generic_name LIKE %s)"
            params.extend([f"%{query}%", f"%{query}%"])
        if category_id:
            sql += " AND m.category_id = %s"
            params.append(category_id)
        if status:
            sql += " AND m.status = %s"
            params.append(status)

        sql += " GROUP BY m.id ORDER BY m.name ASC"
        return fetch_all(sql, params)

    @staticmethod
    def create(name, generic_name, category_id, supplier_id, unit, min_stock_level, description, status='active'):
        return execute_query(
            """INSERT INTO medicines (name, generic_name, category_id, supplier_id, unit, min_stock_level, description, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, generic_name, category_id, supplier_id, unit, min_stock_level, description, status)
        )

    @staticmethod
    def update(medicine_id, name, generic_name, category_id, supplier_id, unit, min_stock_level, description, status):
        return execute_query(
            """UPDATE medicines 
               SET name = %s, generic_name = %s, category_id = %s, supplier_id = %s, unit = %s, 
                   min_stock_level = %s, description = %s, status = %s 
               WHERE id = %s""",
            (name, generic_name, category_id, supplier_id, unit, min_stock_level, description, status, medicine_id)
        )

    @staticmethod
    def delete(medicine_id):
        # Soft delete or hard delete if no dependencies
        return execute_query("UPDATE medicines SET status = 'inactive' WHERE id = %s", (medicine_id,))

    @staticmethod
    def get_batches(medicine_id):
        sql = """
            SELECT b.*, m.name as medicine_name
            FROM medicine_batches b
            JOIN medicines m ON b.medicine_id = m.id
            WHERE b.medicine_id = %s AND b.remaining_quantity > 0
            ORDER BY b.expiry_date ASC
        """
        return fetch_all(sql, (medicine_id,))
