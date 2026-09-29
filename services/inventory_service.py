from datetime import date
from models.db import fetch_all, fetch_one

class InventoryService:
    @staticmethod
    def get_current_stock():
        today_str = date.today().strftime('%Y-%m-%d')
        sql = """
            SELECT m.id as medicine_id, m.name as medicine_name, m.generic_name, m.unit, m.min_stock_level,
                   c.name as category_name, s.name as supplier_name,
                   COALESCE(SUM(b.remaining_quantity), 0) as total_quantity,
                   COUNT(CASE WHEN b.remaining_quantity > 0 AND b.expiry_date >= %s THEN b.id END) as active_batches
            FROM medicines m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            LEFT JOIN medicine_batches b ON b.medicine_id = m.id AND b.remaining_quantity > 0
            WHERE m.status = 'active'
            GROUP BY m.id
            ORDER BY m.name ASC
        """
        return fetch_all(sql, (today_str,))

    @staticmethod
    def get_batch_inventory():
        today_str = date.today().strftime('%Y-%m-%d')
        sql = """
            SELECT b.*, m.name as medicine_name, m.generic_name, m.unit, c.name as category_name, s.name as supplier_name,
                   CASE WHEN b.expiry_date < %s THEN 'Expired' ELSE 'Active' END as expiry_status
            FROM medicine_batches b
            JOIN medicines m ON b.medicine_id = m.id
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            WHERE b.remaining_quantity > 0
            ORDER BY b.expiry_date ASC
        """
        return fetch_all(sql, (today_str,))

    @staticmethod
    def get_low_stock_medicines():
        today_str = date.today().strftime('%Y-%m-%d')
        sql = """
            SELECT m.id, m.name, m.generic_name, m.unit, m.min_stock_level,
                   c.name as category_name, s.name as supplier_name,
                   COALESCE(SUM(CASE WHEN b.expiry_date >= %s THEN b.remaining_quantity ELSE 0 END), 0) as current_stock
            FROM medicines m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            LEFT JOIN medicine_batches b ON b.medicine_id = m.id AND b.remaining_quantity > 0
            WHERE m.status = 'active'
            GROUP BY m.id
            HAVING current_stock <= m.min_stock_level
            ORDER BY current_stock ASC
        """
        return fetch_all(sql, (today_str,))

    @staticmethod
    def get_out_of_stock_medicines():
        today_str = date.today().strftime('%Y-%m-%d')
        sql = """
            SELECT m.id, m.name, m.generic_name, m.unit, m.min_stock_level,
                   c.name as category_name, s.name as supplier_name,
                   COALESCE(SUM(CASE WHEN b.expiry_date >= %s THEN b.remaining_quantity ELSE 0 END), 0) as current_stock
            FROM medicines m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            LEFT JOIN medicine_batches b ON b.medicine_id = m.id AND b.remaining_quantity > 0
            WHERE m.status = 'active'
            GROUP BY m.id
            HAVING current_stock = 0
            ORDER BY m.name ASC
        """
        return fetch_all(sql, (today_str,))

    @staticmethod
    def get_inventory_valuation():
        today_str = date.today().strftime('%Y-%m-%d')
        sql = """
            SELECT 
                COALESCE(SUM(b.remaining_quantity * b.purchase_price), 0) as total_cost_value,
                COALESCE(SUM(b.remaining_quantity * b.selling_price), 0) as total_selling_value,
                COALESCE(SUM(b.remaining_quantity), 0) as total_items_count
            FROM medicine_batches b
            WHERE b.remaining_quantity > 0 AND b.expiry_date >= %s
        """
        return fetch_one(sql, (today_str,))
