from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.admin import AdminModel

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return render_template('auth/login.html')

        admin = AdminModel.get_by_username(username)

        if admin and AdminModel.verify_password(admin['password_hash'], password):
            session.clear()
            session['admin_logged_in'] = True
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            session['admin_email'] = admin['email']

            flash(f'Welcome back, Admin ({admin["username"]})!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
