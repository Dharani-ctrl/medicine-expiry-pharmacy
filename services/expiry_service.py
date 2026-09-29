from datetime import date, datetime, timedelta
from models.db import fetch_all, fetch_one

class ExpiryService:
    @staticmethod
    def get_expired_medicines():
        today = date.today().strftime('%Y-%m-%d')
        sql = """
            SELECT b.*, m.name AS medicine_name, m.generic_name, m.unit, c.name AS category_name, s.name AS supplier_name
            FROM medicine_batches b
            JOIN medicines m ON b.medicine_id = m.id
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            WHERE b.expiry_date < %s AND b.remaining_quantity > 0
            ORDER BY b.expiry_date ASC
        """
        return fetch_all(sql, (today,))

    @staticmethod
    def get_expiring_in_days(min_days, max_days):
        today = date.today()
        start_date = (today + timedelta(days=min_days)).strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=max_days)).strftime('%Y-%m-%d')

        sql = """
            SELECT b.*, m.name AS medicine_name, m.generic_name, m.unit, c.name AS category_name, s.name AS supplier_name
            FROM medicine_batches b
            JOIN medicines m ON b.medicine_id = m.id
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            WHERE b.expiry_date >= %s AND b.expiry_date <= %s AND b.remaining_quantity > 0
            ORDER BY b.expiry_date ASC
        """
        items = fetch_all(sql, (start_date, end_date))
        today_date = date.today()
        for item in items:
            try:
                exp_date = datetime.strptime(str(item['expiry_date']), '%Y-%m-%d').date()
                item['days_remaining'] = (exp_date - today_date).days
            except Exception:
                item['days_remaining'] = 0
        return items

    @staticmethod
    def get_expiry_summary_counts():
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        d30 = (today + timedelta(days=30)).strftime('%Y-%m-%d')
        d60 = (today + timedelta(days=60)).strftime('%Y-%m-%d')
        d90 = (today + timedelta(days=90)).strftime('%Y-%m-%d')

        expired = fetch_one(
            "SELECT COUNT(*) as cnt FROM medicine_batches WHERE expiry_date < %s AND remaining_quantity > 0",
            (today_str,)
        )
        exp_30 = fetch_one(
            "SELECT COUNT(*) as cnt FROM medicine_batches WHERE expiry_date >= %s AND expiry_date <= %s AND remaining_quantity > 0",
            (today_str, d30)
        )
        exp_60 = fetch_one(
            "SELECT COUNT(*) as cnt FROM medicine_batches WHERE expiry_date > %s AND expiry_date <= %s AND remaining_quantity > 0",
            (d30, d60)
        )
        exp_90 = fetch_one(
            "SELECT COUNT(*) as cnt FROM medicine_batches WHERE expiry_date > %s AND expiry_date <= %s AND remaining_quantity > 0",
            (d60, d90)
        )

        return {
            'expired': expired['cnt'] if expired else 0,
            'days_30': exp_30['cnt'] if exp_30 else 0,
            'days_60': exp_60['cnt'] if exp_60 else 0,
            'days_90': exp_90['cnt'] if exp_90 else 0,
        }
