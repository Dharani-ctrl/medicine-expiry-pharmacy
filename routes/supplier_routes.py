from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes import login_required
from models.supplier import SupplierModel

supplier_bp = Blueprint('supplier', __name__, url_prefix='/suppliers')

@supplier_bp.route('/')
@login_required
def index():
    suppliers = SupplierModel.get_all()
    return render_template('suppliers/index.html', suppliers=suppliers)

@supplier_bp.route('/view/<int:supplier_id>')
@login_required
def view(supplier_id):
    supplier = SupplierModel.get_by_id(supplier_id)
    if not supplier:
        flash('Supplier not found.', 'danger')
        return redirect(url_for('supplier.index'))

    purchases = SupplierModel.get_purchases(supplier_id)
    return render_template('suppliers/view.html', supplier=supplier, purchases=purchases)

@supplier_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name', '').strip()
    company_name = request.form.get('company_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    registered_date = request.form.get('registered_date') or None
    supplied_items = request.form.get('supplied_items', '').strip()
    status = request.form.get('status', 'active')

    if not name:
        flash('Supplier contact name is required.', 'danger')
        return redirect(url_for('supplier.index'))

    try:
        SupplierModel.create(name, company_name, phone, email, address, status, registered_date, supplied_items)
        flash('Supplier added successfully.', 'success')
    except Exception as e:
        flash(f'Error adding supplier: {str(e)}', 'danger')

    return redirect(url_for('supplier.index'))

@supplier_bp.route('/edit/<int:supplier_id>', methods=['POST'])
@login_required
def edit(supplier_id):
    name = request.form.get('name', '').strip()
    company_name = request.form.get('company_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    registered_date = request.form.get('registered_date') or None
    supplied_items = request.form.get('supplied_items', '').strip()
    status = request.form.get('status', 'active')

    if not name:
        flash('Supplier contact name is required.', 'danger')
        return redirect(url_for('supplier.index'))

    try:
        SupplierModel.update(supplier_id, name, company_name, phone, email, address, status, registered_date, supplied_items)
        flash('Supplier updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating supplier: {str(e)}', 'danger')

    return redirect(url_for('supplier.index'))

@supplier_bp.route('/delete/<int:supplier_id>', methods=['POST'])
@login_required
def delete(supplier_id):
    try:
        SupplierModel.delete(supplier_id)
        flash('Supplier deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting supplier (it may have active purchases): {str(e)}', 'danger')

    return redirect(url_for('supplier.index'))
