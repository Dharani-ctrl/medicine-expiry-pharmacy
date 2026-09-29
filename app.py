import os
from flask import Flask
from config import Config
from models.db import init_db

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.medicine_routes import medicine_bp
from routes.category_routes import category_bp
from routes.supplier_routes import supplier_bp
from routes.purchase_routes import purchase_bp
from routes.inventory_routes import inventory_bp
from routes.sales_routes import sales_bp
from routes.return_routes import return_bp
from routes.report_routes import report_bp
from routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(medicine_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(return_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)

    # Initialize Database tables & seeds
    with app.app_context():
        init_db()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Pharmacy Management System on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
