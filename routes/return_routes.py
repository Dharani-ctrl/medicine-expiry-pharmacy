from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes import login_required
from models.return_model import PurchaseReturnModel
from models.supplier import SupplierModel
from models.medicine import MedicineModel
from models.db import fetch_all, fetch_one

return_bp = Blueprint('return', __name__, url_prefix='/returns')

@return_bp.route('/')
@login_required
def index():
    returns_list = PurchaseReturnModel.get_all()
    return render_template('returns/index.html', returns=returns_list)

@return_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id', type=int)
        medicine_id = request.form.get('medicine_id', type=int)
        batch_id = request.form.get('batch_id', type=int)
        return_quantity = request.form.get('return_quantity', type=int)
        refund_amount = request.form.get('refund_amount', 0.0, type=float)
        reason = request.form.get('reason', '').strip()
        return_date = request.form.get('return_date', date.today().strftime('%Y-%m-%d'))

        if not supplier_id or not medicine_id or not batch_id or not return_quantity or return_quantity <= 0:
            flash('Please complete all required fields with valid return quantities.', 'danger')
            return redirect(url_for('return.new'))

        # Check stock in batch
        batch = fetch_one("SELECT remaining_quantity FROM medicine_batches WHERE id = %s", (batch_id,))
        if not batch or batch['remaining_quantity'] < return_quantity:
            flash(f'Cannot return {return_quantity} units. Available batch stock is only {batch["remaining_quantity"] if batch else 0}.', 'danger')
            return redirect(url_for('return.new'))

        return_no = PurchaseReturnModel.generate_return_no()
        PurchaseReturnModel.create(
            return_no=return_no,
            supplier_id=supplier_id,
            medicine_id=medicine_id,
            batch_id=batch_id,
            return_quantity=return_quantity,
            refund_amount=refund_amount,
            reason=reason,
            return_date=return_date
        )

        flash(f'Purchase return #{return_no} logged successfully and stock updated.', 'success')
        return redirect(url_for('return.index'))

    suppliers = SupplierModel.get_active()
    medicines = MedicineModel.get_all()
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template('returns/new.html', suppliers=suppliers, medicines=medicines, today_date=today_date)
