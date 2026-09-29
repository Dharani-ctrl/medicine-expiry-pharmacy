from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes import login_required
from models.category import CategoryModel

category_bp = Blueprint('category', __name__, url_prefix='/categories')

@category_bp.route('/')
@login_required
def index():
    categories = CategoryModel.get_all()
    return render_template('categories/index.html', categories=categories)

@category_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'active')

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('category.index'))

    try:
        CategoryModel.create(name, description, status)
        flash('Category created successfully.', 'success')
    except Exception as e:
        flash(f'Error creating category: {str(e)}', 'danger')

    return redirect(url_for('category.index'))

@category_bp.route('/edit/<int:category_id>', methods=['POST'])
@login_required
def edit(category_id):
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'active')

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('category.index'))

    try:
        CategoryModel.update(category_id, name, description, status)
        flash('Category updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating category: {str(e)}', 'danger')

    return redirect(url_for('category.index'))

@category_bp.route('/delete/<int:category_id>', methods=['POST'])
@login_required
def delete(category_id):
    count = CategoryModel.count_medicines(category_id)
    if count > 0:
        flash(f'Cannot delete category because it has {count} associated medicines. Deactivate it instead.', 'warning')
        return redirect(url_for('category.index'))

    try:
        CategoryModel.delete(category_id)
        flash('Category deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('category.index'))
