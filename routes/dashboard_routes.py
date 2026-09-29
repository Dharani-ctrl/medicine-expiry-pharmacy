from flask import Blueprint, render_template, jsonify
from routes import login_required
from services.report_service import ReportService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    summary = ReportService.get_dashboard_summary()
    return render_template('dashboard/index.html', summary=summary)

@dashboard_bp.route('/api/dashboard/sales-chart')
@login_required
def sales_chart_api():
    chart_data = ReportService.get_chart_sales_last_7_days()
    return jsonify(chart_data)
