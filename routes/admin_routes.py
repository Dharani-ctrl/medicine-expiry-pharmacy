from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes import login_required
from models.admin import AdminModel

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    admin_id = session.get('admin_id')
    admin = AdminModel.get_by_id(admin_id)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()

        if not username or not email:
            flash('Username and Email are required.', 'danger')
            return redirect(url_for('admin.profile'))

        try:
            AdminModel.update_profile(admin_id, username, email)
            session['admin_username'] = username
            session['admin_email'] = email
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('admin.profile'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('admin/profile.html', admin=admin)

@admin_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    admin_id = session.get('admin_id')
    admin = AdminModel.get_by_id(admin_id)

    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not AdminModel.verify_password(admin['password_hash'], current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('admin.change_password'))

        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'danger')
            return redirect(url_for('admin.change_password'))

        if new_password != confirm_password:
            flash('New password and Confirmation password do not match.', 'danger')
            return redirect(url_for('admin.change_password'))

        try:
            AdminModel.update_password(admin_id, new_password)
            flash('Password changed successfully.', 'success')
            return redirect(url_for('admin.change_password'))
        except Exception as e:
            flash(f'Error updating password: {str(e)}', 'danger')

    return render_template('admin/change_password.html')

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        pharmacy_name = request.form.get('pharmacy_name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        tax_no = request.form.get('tax_no', '').strip()
        currency_symbol = request.form.get('currency_symbol', '₹').strip()
        receipt_footer = request.form.get('receipt_footer', '').strip()

        AdminModel.update_setting('pharmacy_name', pharmacy_name)
        AdminModel.update_setting('address', address)
        AdminModel.update_setting('phone', phone)
        AdminModel.update_setting('email', email)
        AdminModel.update_setting('tax_no', tax_no)
        AdminModel.update_setting('currency_symbol', currency_symbol)
        AdminModel.update_setting('receipt_footer', receipt_footer)

        flash('Pharmacy settings updated successfully.', 'success')
        return redirect(url_for('admin.settings'))

    current_settings = AdminModel.get_all_settings()
    return render_template('admin/settings.html', settings=current_settings)
