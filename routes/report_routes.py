import csv
import io
from flask import Blueprint, render_template, request, Response, make_response
from routes import login_required
from services.report_service import ReportService
from services.inventory_service import InventoryService
from services.expiry_service import ExpiryService
from models.supplier import SupplierModel

report_bp = Blueprint('report', __name__, url_prefix='/reports')

@report_bp.route('/sales')
@login_required
def sales():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    data = ReportService.get_sales_report(start_date or None, end_date or None)

    if request.args.get('export') == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Invoice No', 'Customer Name', 'Phone', 'Date', 'Subtotal', 'Tax', 'Discount', 'Grand Total', 'Payment Method'])
        for s in data['sales']:
            writer.writerow([s['invoice_no'], s['customer_name'], s['customer_phone'], s['sale_date'], s['subtotal'], s['tax_amount'], s['discount_amount'], s['grand_total'], s['payment_method']])

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=sales_report.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    return render_template('reports/sales_report.html', data=data, start_date=start_date, end_date=end_date)

@report_bp.route('/purchase')
@login_required
def purchase():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    supplier_id = request.args.get('supplier_id', type=int)

    data = ReportService.get_purchase_report(start_date or None, end_date or None, supplier_id)
    suppliers = SupplierModel.get_all()

    if request.args.get('export') == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Purchase No', 'Supplier', 'Date', 'Total Amount', 'Paid Amount', 'Payment Status', 'Notes'])
        for p in data['purchases']:
            writer.writerow([p['purchase_no'], p['supplier_name'], p['purchase_date'], p['total_amount'], p['paid_amount'], p['payment_status'], p['notes']])

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=purchase_report.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    return render_template('reports/purchase_report.html', data=data, suppliers=suppliers, start_date=start_date, end_date=end_date, selected_sup=supplier_id)

@report_bp.route('/inventory')
@login_required
def inventory():
    current_stock = InventoryService.get_current_stock()
    valuation = InventoryService.get_inventory_valuation()

    if request.args.get('export') == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Medicine Name', 'Generic Name', 'Category', 'Supplier', 'Unit', 'Min Stock Level', 'Current Stock'])
        for m in current_stock:
            writer.writerow([m['medicine_name'], m['generic_name'], m['category_name'], m['supplier_name'], m['unit'], m['min_stock_level'], m['total_quantity']])

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=inventory_report.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    return render_template('reports/inventory_report.html', current_stock=current_stock, valuation=valuation)

@report_bp.route('/expiry')
@login_required
def expiry():
    range_type = request.args.get('range', '30')
    if range_type == 'expired':
        items = ExpiryService.get_expired_medicines()
    elif range_type == '30':
        items = ExpiryService.get_expiring_in_days(0, 30)
    elif range_type == '60':
        items = ExpiryService.get_expiring_in_days(31, 60)
    else:
        items = ExpiryService.get_expiring_in_days(61, 90)

    if request.args.get('export') == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Batch No', 'Medicine Name', 'Category', 'Supplier', 'Expiry Date', 'Remaining Qty', 'Selling Price'])
        for b in items:
            writer.writerow([b['batch_no'], b['medicine_name'], b['category_name'], b['supplier_name'], b['expiry_date'], b['remaining_quantity'], b['selling_price']])

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=expiry_report_{range_type}.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    return render_template('reports/expiry_report.html', items=items, range_type=range_type)

@report_bp.route('/returns')
@login_required
def returns():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    data = ReportService.get_return_report(start_date or None, end_date or None)

    if request.args.get('export') == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Return No', 'Supplier', 'Medicine', 'Batch No', 'Qty Returned', 'Refund Amount', 'Reason', 'Return Date'])
        for r in data['returns']:
            writer.writerow([r['return_no'], r['supplier_name'], r['medicine_name'], r['batch_no'], r['return_quantity'], r['refund_amount'], r['reason'], r['return_date']])

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=purchase_returns_report.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    return render_template('reports/returns_report.html', data=data, start_date=start_date, end_date=end_date)
