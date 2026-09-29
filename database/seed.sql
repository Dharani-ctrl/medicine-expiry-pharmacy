-- Default data only. Import schema.sql first to create the database tables.
CREATE DATABASE IF NOT EXISTS pharmacy_db
	CHARACTER SET utf8mb4
	COLLATE utf8mb4_unicode_ci;
USE pharmacy_db;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Default local login: username admin, password admin123
-- Re-importing this seed resets the admin password to the documented default.
INSERT INTO admins (id, username, password_hash, email) VALUES
(1, 'admin', 'scrypt:32768:8:1$6t9Cz98uYRpLd6Ov$e995fa63ca8ef6a7b72771254ef18ede264fcfd3375fa2364502492a88f43686de07ec512b1e02c05bc47c463f9256bdd31503696faf83488a6ccc59231ff2e0', 'admin@pharmacy.com')
ON DUPLICATE KEY UPDATE
	password_hash = VALUES(password_hash),
	email = VALUES(email);

-- Default Categories
INSERT IGNORE INTO categories (id, name, description, status) VALUES
(1, 'Tablets', 'Solid dosage form medicines', 'active'),
(2, 'Syrups & Liquids', 'Oral liquid solutions and suspensions', 'active'),
(3, 'Injections', 'Sterile injectable formulations', 'active'),
(4, 'Ointments & Creams', 'Topical semi-solid applications', 'active'),
(5, 'Capsules', 'Gelatin encapsulated medications', 'active');

-- Default Suppliers
INSERT IGNORE INTO suppliers
	(id, name, company_name, phone, email, address, registered_date, supplied_items, status)
VALUES
(1, 'Apex Pharma Distributors', 'Apex Pharmaceuticals Ltd.', '9876543210', 'sales@apexpharma.com', '123 Health Ave, Metro City', CURRENT_DATE, NULL, 'active'),
(2, 'MedLife Supplies', 'MedLife Healthcare Solutions', '9812345678', 'contact@medlifesupplies.com', '45 Science Park, Tech Hub', CURRENT_DATE, NULL, 'active'),
(3, 'BioCare Wholesale', 'BioCare Laboratories Inc.', '9711223344', 'info@biocare.com', '88 Industry Estate, North Zone', CURRENT_DATE, NULL, 'active');

-- Default Settings
INSERT IGNORE INTO settings (setting_key, setting_value) VALUES
('pharmacy_name', 'CurePlus Pharmacy & Healthcare'),
('address', '104 Main Street, Medical District, Cityville'),
('phone', '+1 (555) 019-2834'),
('email', 'info@curepluspharmacy.com'),
('tax_no', 'TAX-88942-PHARM'),
('currency_symbol', '₹'),
('receipt_footer', 'Thank you for choosing CurePlus Pharmacy! Get well soon.');

SET FOREIGN_KEY_CHECKS = 1;
