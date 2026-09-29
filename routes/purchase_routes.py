from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes import login_required
from models.purchase import PurchaseModel
from models.supplier import SupplierModel
from models.medicine import MedicineModel

purchase_bp = Blueprint('purchase', __name__, url_prefix='/purchases')

@purchase_bp.route('/')
@login_required
def index():
    purchases = PurchaseModel.get_all()
    return render_template('purchases/index.html', purchases=purchases)

@purchase_bp.route('/view/<int:purchase_id>')
@login_required
def view(purchase_id):
    purchase = PurchaseModel.get_by_id(purchase_id)
    if not purchase:
        flash('Purchase record not found.', 'danger')
        return redirect(url_for('purchase.index'))
    items = PurchaseModel.get_items(purchase_id)
    return render_template('purchases/view.html', purchase=purchase, items=items)

@purchase_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id', type=int)
        purchase_date = request.form.get('purchase_date', date.today().strftime('%Y-%m-%d'))
        paid_amount = request.form.get('paid_amount', 0.0, type=float)
        payment_status = request.form.get('payment_status', 'Paid')
        notes = request.form.get('notes', '').strip()

        # Dynamic items arrays
        medicine_ids = request.form.getlist('medicine_id[]')
        batch_nos = request.form.getlist('batch_no[]')
        mfg_dates = request.form.getlist('mfg_date[]')
        expiry_dates = request.form.getlist('expiry_date[]')
        quantities = request.form.getlist('quantity[]')
        purchase_prices = request.form.getlist('purchase_price[]')
        selling_prices = request.form.getlist('selling_price[]')
        manufacturers = request.form.getlist('manufacturer[]')

        if not supplier_id or not medicine_ids:
            flash('Please select a supplier and add at least one medicine item.', 'danger')
            return redirect(url_for('purchase.new'))

        # Calculate total
        total_amount = 0.0
        parsed_items = []

        for i in range(len(medicine_ids)):
            med_id = int(medicine_ids[i])
            b_no = batch_nos[i].strip()
            exp_date = expiry_dates[i]
            qty = int(quantities[i])
            p_price = float(purchase_prices[i])
            s_price = float(selling_prices[i])
            m_date = mfg_dates[i] if mfg_dates[i] else None
            manufacturer = manufacturers[i].strip() if i < len(manufacturers) else ''

            item_total = qty * p_price
            total_amount += item_total

            parsed_items.append({
                'medicine_id': med_id,
                'batch_no': b_no,
                'mfg_date': m_date,
                'expiry_date': exp_date,
                'quantity': qty,
                'purchase_price': p_price,
                'selling_price': s_price,
                'manufacturer': manufacturer
            })

        purchase_no = PurchaseModel.generate_purchase_no()
        purchase_id = PurchaseModel.create(
            purchase_no=purchase_no,
            supplier_id=supplier_id,
            purchase_date=purchase_date,
            total_amount=round(total_amount, 2),
            paid_amount=round(paid_amount, 2),
            payment_status=payment_status,
            notes=notes
        )

        for item in parsed_items:
            PurchaseModel.add_batch(
                purchase_id=purchase_id,
                medicine_id=item['medicine_id'],
                batch_no=item['batch_no'],
                mfg_date=item['mfg_date'],
                expiry_date=item['expiry_date'],
                quantity=item['quantity'],
                purchase_price=item['purchase_price'],
                selling_price=item['selling_price'],
                manufacturer=item['manufacturer']
            )

        flash(f'Purchase #{purchase_no} recorded successfully with {len(parsed_items)} batch item(s).', 'success')
        return redirect(url_for('purchase.view', purchase_id=purchase_id))

    suppliers = SupplierModel.get_active()
    medicines = MedicineModel.get_all()
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template('purchases/new.html', suppliers=suppliers, medicines=medicines, today_date=today_date)
