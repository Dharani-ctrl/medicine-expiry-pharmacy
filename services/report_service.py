from datetime import date, datetime, timedelta
from models.db import fetch_all, fetch_one

class ReportService:
    @staticmethod
    def get_sales_report(start_date=None, end_date=None):
        sql = """
            SELECT s.*, COUNT(i.id) AS item_count
            FROM sales s
            LEFT JOIN sale_items i ON i.sale_id = s.id
            WHERE 1=1
        """
        params = []
        if start_date:
            sql += " AND DATE(s.sale_date) >= %s"
            params.append(start_date)
        if end_date:
            sql += " AND DATE(s.sale_date) <= %s"
            params.append(end_date)

        sql += " GROUP BY s.id ORDER BY s.sale_date DESC"
        sales = fetch_all(sql, params)

        # Summary calculations
        total_revenue = sum(float(s['grand_total']) for s in sales) if sales else 0.0
        total_invoices = len(sales)
        avg_invoice = round(total_revenue / total_invoices, 2) if total_invoices > 0 else 0.0

        return {
            'sales': sales,
            'total_revenue': total_revenue,
            'total_invoices': total_invoices,
            'avg_invoice': avg_invoice
        }

    @staticmethod
    def get_purchase_report(start_date=None, end_date=None, supplier_id=None):
        sql = """
            SELECT p.*, sup.name as supplier_name, COUNT(b.id) as item_types
            FROM purchases p
            JOIN suppliers sup ON p.supplier_id = sup.id
            LEFT JOIN medicine_batches b ON b.purchase_id = p.id
            WHERE 1=1
        """
        params = []
        if start_date:
            sql += " AND p.purchase_date >= %s"
            params.append(start_date)
        if end_date:
            sql += " AND p.purchase_date <= %s"
            params.append(end_date)
        if supplier_id:
            sql += " AND p.supplier_id = %s"
            params.append(supplier_id)

        sql += " GROUP BY p.id ORDER BY p.purchase_date DESC"
        purchases = fetch_all(sql, params)

        total_amount = sum(float(p['total_amount']) for p in purchases) if purchases else 0.0
        total_paid = sum(float(p['paid_amount']) for p in purchases) if purchases else 0.0
        balance_due = total_amount - total_paid

        return {
            'purchases': purchases,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'balance_due': balance_due
        }

    @staticmethod
    def get_return_report(start_date=None, end_date=None):
        sql = """
            SELECT r.*, sup.name as supplier_name, m.name as medicine_name, b.batch_no
            FROM purchase_returns r
            JOIN suppliers sup ON r.supplier_id = sup.id
            JOIN medicines m ON r.medicine_id = m.id
            JOIN medicine_batches b ON r.batch_id = b.id
            WHERE 1=1
        """
        params = []
        if start_date:
            sql += " AND r.return_date >= %s"
            params.append(start_date)
        if end_date:
            sql += " AND r.return_date <= %s"
            params.append(end_date)

        sql += " ORDER BY r.return_date DESC"
        returns_list = fetch_all(sql, params)
        total_refund = sum(float(r['refund_amount']) for r in returns_list) if returns_list else 0.0

        return {
            'returns': returns_list,
            'total_refund': total_refund,
            'total_count': len(returns_list)
        }

    @staticmethod
    def get_chart_sales_last_7_days():
        today = date.today()
        labels = []
        data = []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            labels.append(day.strftime('%b %d'))

            res = fetch_one(
                "SELECT COALESCE(SUM(grand_total), 0) as total FROM sales WHERE DATE(sale_date) = %s",
                (day_str,)
            )
            data.append(float(res['total']) if res else 0.0)

        return {'labels': labels, 'data': data}

    @staticmethod
    def get_dashboard_summary():
        today_str = date.today().strftime('%Y-%m-%d')
        first_of_month = date.today().replace(day=1).strftime('%Y-%m-%d')

        # Total medicines count
        total_meds = fetch_one("SELECT COUNT(*) as cnt FROM medicines WHERE status = 'active'")['cnt']

        # Total active suppliers count
        total_suppliers = fetch_one("SELECT COUNT(*) as cnt FROM suppliers WHERE status = 'active'")['cnt']

        # Today sales
        today_sales = fetch_one("SELECT COALESCE(SUM(grand_total), 0) as total FROM sales WHERE DATE(sale_date) = %s", (today_str,))['total']

        # Monthly sales
        monthly_sales = fetch_one("SELECT COALESCE(SUM(grand_total), 0) as total FROM sales WHERE DATE(sale_date) >= %s", (first_of_month,))['total']

        # Low stock count
        low_stock_sql = """
            SELECT COUNT(*) as cnt FROM (
                SELECT m.id, m.min_stock_level,
                       COALESCE(SUM(CASE WHEN b.expiry_date >= %s THEN b.remaining_quantity ELSE 0 END), 0) as stock
                FROM medicines m
                LEFT JOIN medicine_batches b ON b.medicine_id = m.id AND b.remaining_quantity > 0
                WHERE m.status = 'active'
                GROUP BY m.id
                HAVING stock <= m.min_stock_level
            ) as sub
        """
        low_stock_cnt = fetch_one(low_stock_sql, (today_str,))['cnt']

        # Expired count
        expired_cnt = fetch_one("SELECT COUNT(*) as cnt FROM medicine_batches WHERE expiry_date < %s AND remaining_quantity > 0", (today_str,))['cnt']

        # Expiring in 30 days count
        d30 = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        expiring_soon_cnt = fetch_one("SELECT COUNT(*) as cnt FROM medicine_batches WHERE expiry_date >= %s AND expiry_date <= %s AND remaining_quantity > 0", (today_str, d30))['cnt']

        # Recent 5 invoices
        recent_sales = fetch_all("SELECT * FROM sales ORDER BY sale_date DESC LIMIT 5")

        # Top 5 medicines
        top_medicines = fetch_all("""
            SELECT m.name, SUM(si.quantity) as total_sold, SUM(si.total_price) as total_revenue
            FROM sale_items si
            JOIN medicines m ON si.medicine_id = m.id
            GROUP BY m.id
            ORDER BY total_sold DESC
            LIMIT 5
        """)

        return {
            'total_medicines': total_meds,
            'total_suppliers': total_suppliers,
            'today_sales': float(today_sales),
            'monthly_sales': float(monthly_sales),
            'low_stock_count': low_stock_cnt,
            'expired_count': expired_cnt,
            'expiring_soon_count': expiring_soon_cnt,
            'recent_sales': recent_sales,
            'top_medicines': top_medicines
        }
