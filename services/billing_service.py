from datetime import date
from math import floor
from models.sale import SaleModel
from models.db import fetch_all, fetch_one

class BillingService:
    @staticmethod
    def search_medicines_for_pos(query=""):
        today_str = date.today().strftime('%Y-%m-%d')
        sql = """
            SELECT m.id, m.name, m.generic_name, m.unit, c.name as category_name,
                   COALESCE(SUM(b.remaining_quantity), 0) as total_available_stock
            FROM medicines m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN medicine_batches b ON b.medicine_id = m.id AND b.remaining_quantity > 0 AND b.expiry_date >= %s
            WHERE m.status = 'active'
        """
        params = [today_str]
        if query:
            sql += " AND (m.name LIKE %s OR m.generic_name LIKE %s)"
            params.extend([f"%{query}%", f"%{query}%"])

        sql += " GROUP BY m.id HAVING total_available_stock > 0 ORDER BY m.name ASC LIMIT 20"
        return fetch_all(sql, params)

    @staticmethod
    def get_available_batches(medicine_id):
        today_str = date.today().strftime('%Y-%m-%d')
        sql = """
            SELECT id, batch_no, expiry_date, remaining_quantity, selling_price, purchase_price
            FROM medicine_batches
            WHERE medicine_id = %s AND remaining_quantity > 0 AND expiry_date >= %s
            ORDER BY expiry_date ASC
        """
        return fetch_all(sql, (medicine_id, today_str))

    @staticmethod
    def process_sale(customer_name, customer_phone, items, tax_percent=0.0, discount_percent=0.0, payment_method="Cash", doctor_name=None):
        """
        items: list of dicts [{'medicine_id': int, 'batch_id': int, 'quantity': int, 'unit_price': float}]
        """
        if not items:
            raise ValueError("No items in bill.")

        tax_percent = float(tax_percent)
        discount_percent = float(discount_percent)
        if not 0 <= tax_percent <= 100 or not 0 <= discount_percent <= 100:
            raise ValueError("Tax and discount must be between 0% and 100%.")

        subtotal = 0.0
        validated_items = []

        for item in items:
            med_id = int(item['medicine_id'])
            batch_id = int(item['batch_id'])
            qty = int(item['quantity'])
            unit_price = float(item['unit_price'])

            # Verify batch stock
            batch = fetch_one("SELECT remaining_quantity, selling_price FROM medicine_batches WHERE id = %s", (batch_id,))
            if not batch:
                raise ValueError(f"Batch #{batch_id} not found.")
            if batch['remaining_quantity'] < qty:
                raise ValueError(f"Requested quantity ({qty}) exceeds available batch stock ({batch['remaining_quantity']}).")

            total_price = round(qty * unit_price, 2)
            subtotal += total_price
            validated_items.append({
                'medicine_id': med_id,
                'batch_id': batch_id,
                'quantity': qty,
                'unit_price': unit_price,
                'total_price': total_price
            })

        subtotal = round(subtotal, 2)
        tax_amount = round(subtotal * tax_percent / 100, 2)
        discount_amount = round(subtotal * discount_percent / 100, 2)
        unrounded_total = max(0, subtotal + tax_amount - discount_amount)
        grand_total = floor(unrounded_total + 0.5)

        invoice_no = SaleModel.generate_invoice_no()
        sale_id = SaleModel.create(
            invoice_no=invoice_no,
            customer_name=customer_name or 'Walk-in Customer',
            customer_phone=customer_phone or '',
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            grand_total=grand_total,
            payment_method=payment_method,
            doctor_name=doctor_name or ''
        )

        for v_item in validated_items:
            SaleModel.add_sale_item(
                sale_id=sale_id,
                medicine_id=v_item['medicine_id'],
                batch_id=v_item['batch_id'],
                quantity=v_item['quantity'],
                unit_price=v_item['unit_price'],
                total_price=v_item['total_price']
            )

        return sale_id, invoice_no
