from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes import login_required
from models.medicine import MedicineModel
from models.category import CategoryModel
from models.supplier import SupplierModel

medicine_bp = Blueprint('medicine', __name__, url_prefix='/medicines')

@medicine_bp.route('/')
@login_required
def index():
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', '').strip()

    medicines = MedicineModel.search(query=q, category_id=category_id, status=status)
    categories = CategoryModel.get_active()

    return render_template('medicines/index.html', medicines=medicines, categories=categories, search_q=q, selected_cat=category_id, selected_status=status)

@medicine_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        generic_name = request.form.get('generic_name', '').strip()
        category_id = request.form.get('category_id', type=int)
        supplier_id = request.form.get('supplier_id', type=int)
        unit = request.form.get('unit', 'Tablet').strip()
        min_stock_level = request.form.get('min_stock_level', 10, type=int)
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'active')

        if not name or not category_id:
            flash('Medicine Name and Category are required.', 'danger')
            return redirect(url_for('medicine.add'))

        try:
            MedicineModel.create(name, generic_name, category_id, supplier_id, unit, min_stock_level, description, status)
            flash('Medicine added successfully.', 'success')
            return redirect(url_for('medicine.index'))
        except Exception as e:
            flash(f'Error adding medicine: {str(e)}', 'danger')

    categories = CategoryModel.get_active()
    suppliers = SupplierModel.get_active()
    return render_template('medicines/form.html', categories=categories, suppliers=suppliers, medicine=None)

@medicine_bp.route('/edit/<int:medicine_id>', methods=['GET', 'POST'])
@login_required
def edit(medicine_id):
    medicine = MedicineModel.get_by_id(medicine_id)
    if not medicine:
        flash('Medicine not found.', 'danger')
        return redirect(url_for('medicine.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        generic_name = request.form.get('generic_name', '').strip()
        category_id = request.form.get('category_id', type=int)
        supplier_id = request.form.get('supplier_id', type=int)
        unit = request.form.get('unit', 'Tablet').strip()
        min_stock_level = request.form.get('min_stock_level', 10, type=int)
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'active')

        if not name or not category_id:
            flash('Medicine Name and Category are required.', 'danger')
            return redirect(url_for('medicine.edit', medicine_id=medicine_id))

        try:
            MedicineModel.update(medicine_id, name, generic_name, category_id, supplier_id, unit, min_stock_level, description, status)
            flash('Medicine updated successfully.', 'success')
            return redirect(url_for('medicine.index'))
        except Exception as e:
            flash(f'Error updating medicine: {str(e)}', 'danger')

    categories = CategoryModel.get_active()
    suppliers = SupplierModel.get_active()
    return render_template('medicines/form.html', categories=categories, suppliers=suppliers, medicine=medicine)

@medicine_bp.route('/delete/<int:medicine_id>', methods=['POST'])
@login_required
def delete(medicine_id):
    try:
        MedicineModel.delete(medicine_id)
        flash('Medicine status set to inactive.', 'success')
    except Exception as e:
        flash(f'Error deleting medicine: {str(e)}', 'danger')
    return redirect(url_for('medicine.index'))
