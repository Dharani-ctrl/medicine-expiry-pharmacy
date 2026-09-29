from flask import Blueprint, render_template, request
from routes import login_required
from services.inventory_service import InventoryService
from services.expiry_service import ExpiryService

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
def index():
    tab = request.args.get('tab', 'medicine')
    current_stock = InventoryService.get_current_stock()
    batch_inventory = InventoryService.get_batch_inventory()
    valuation = InventoryService.get_inventory_valuation()

    return render_template('inventory/index.html',
                           current_stock=current_stock,
                           batch_inventory=batch_inventory,
                           valuation=valuation,
                           active_tab=tab)

@inventory_bp.route('/low-stock')
@login_required
def low_stock():
    low_stock_list = InventoryService.get_low_stock_medicines()
    out_of_stock_list = InventoryService.get_out_of_stock_medicines()
    return render_template('inventory/low_stock.html', low_stock=low_stock_list, out_of_stock=out_of_stock_list)

@inventory_bp.route('/expiry')
@login_required
def expiry():
    range_type = request.args.get('range', 'expired') # expired, 30, 60, 90

    counts = ExpiryService.get_expiry_summary_counts()

    if range_type == 'expired':
        items = ExpiryService.get_expired_medicines()
    elif range_type == '30':
        items = ExpiryService.get_expiring_in_days(0, 30)
    elif range_type == '60':
        items = ExpiryService.get_expiring_in_days(31, 60)
    elif range_type == '90':
        items = ExpiryService.get_expiring_in_days(61, 90)
    else:
        items = ExpiryService.get_expired_medicines()

    return render_template('inventory/expiry.html', items=items, counts=counts, selected_range=range_type)
