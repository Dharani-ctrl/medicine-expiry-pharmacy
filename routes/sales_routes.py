import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes import login_required
from models.sale import SaleModel
from models.admin import AdminModel
from services.billing_service import BillingService

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/')
@sales_bp.route('/history')
@login_required
def history():
    sales = SaleModel.get_all()
    return render_template('sales/history.html', sales=sales)

@sales_bp.route('/pos')
@login_required
def pos():
    settings = AdminModel.get_all_settings()
    return render_template('sales/pos.html', settings=settings)

@sales_bp.route('/api/search-medicines')
@login_required
def search_medicines_api():
    q = request.args.get('q', '').strip()
    meds = BillingService.search_medicines_for_pos(q)
    return jsonify(meds)

@sales_bp.route('/api/get-batches/<int:medicine_id>')
@login_required
def get_batches_api(medicine_id):
    batches = BillingService.get_available_batches(medicine_id)
    return jsonify(batches)

@sales_bp.route('/create', methods=['POST'])
@login_required
def create():
    try:
        data = request.get_json()
        if not data:
            data = request.form

        customer_name = data.get('customer_name', 'Walk-in Customer')
        customer_phone = data.get('customer_phone', '')
        doctor_name = data.get('doctor_name', '')
        tax_percent = float(data.get('tax_percent', 0.0))
        discount_percent = float(data.get('discount_percent', 0.0))
        payment_method = data.get('payment_method', 'Cash')

        items = data.get('items', [])
        if isinstance(items, str):
            items = json.loads(items)

        if not items:
            return jsonify({'success': False, 'message': 'Cart is empty. Add medicines to complete bill.'}), 400

        sale_id, invoice_no = BillingService.process_sale(
            customer_name=customer_name,
            customer_phone=customer_phone,
            items=items,
            tax_percent=tax_percent,
            discount_percent=discount_percent,
            payment_method=payment_method,
            doctor_name=doctor_name
        )

        return jsonify({
            'success': True,
            'message': 'Bill generated successfully!',
            'sale_id': sale_id,
            'invoice_no': invoice_no,
            'redirect_url': url_for('sales.invoice', sale_id=sale_id)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@sales_bp.route('/invoice/<int:sale_id>')
@login_required
def invoice(sale_id):
    sale = SaleModel.get_by_id(sale_id)
    if not sale:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('sales.history'))

    items = SaleModel.get_items(sale_id)
    settings = AdminModel.get_all_settings()

    return render_template('sales/invoice.html', sale=sale, items=items, settings=settings)
