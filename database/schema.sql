CREATE DATABASE IF NOT EXISTS pharmacy_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE pharmacy_db;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Admin table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company_name VARCHAR(150),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    registered_date DATE,
    supplied_items VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Medicines table
CREATE TABLE IF NOT EXISTS medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    generic_name VARCHAR(150),
    category_id INT NOT NULL,
    supplier_id INT,
    unit VARCHAR(50) DEFAULT 'Tablet',
    min_stock_level INT DEFAULT 10,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Purchases table
CREATE TABLE IF NOT EXISTS purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_no VARCHAR(50) NOT NULL UNIQUE,
    supplier_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    payment_status VARCHAR(20) DEFAULT 'Paid',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Medicine Batches (Purchase Items) table
CREATE TABLE IF NOT EXISTS medicine_batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    medicine_id INT NOT NULL,
    batch_no VARCHAR(50) NOT NULL,
    mfg_date DATE,
    expiry_date DATE NOT NULL,
    manufacturer VARCHAR(150),
    quantity INT NOT NULL DEFAULT 0,
    remaining_quantity INT NOT NULL DEFAULT 0,
    purchase_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    selling_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sales / Invoices table
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_no VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(100) DEFAULT 'Walk-in Customer',
    customer_phone VARCHAR(20),
    doctor_name VARCHAR(100),
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    grand_total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_method VARCHAR(50) DEFAULT 'Cash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sale Items table
CREATE TABLE IF NOT EXISTS sale_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    medicine_id INT NOT NULL,
    batch_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id) REFERENCES medicine_batches(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Purchase Returns table
CREATE TABLE IF NOT EXISTS purchase_returns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    PRNo INT UNIQUE,
    return_no VARCHAR(50) NOT NULL UNIQUE,
    supplier_id INT NOT NULL,
    medicine_id INT NOT NULL,
    batch_id INT NOT NULL,
    return_quantity INT NOT NULL,
    refund_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    reason VARCHAR(255),
    return_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IVNO VARCHAR(5),
    SName VARCHAR(30),
    PNO INT,
    PName VARCHAR(30),
    PType VARCHAR(30),
    MFR VARCHAR(30),
    PPrice FLOAT,
    MRP FLOAT,
    AQTY INT,
    RQTY INT,
    Batch INT,
    EDate INT,
    Tot FLOAT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id) REFERENCES medicine_batches(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add legacy Purchase Return fields when this table already exists.
DROP PROCEDURE IF EXISTS migrate_purchase_returns;
DELIMITER //
CREATE PROCEDURE migrate_purchase_returns()
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'PRNo') THEN
        ALTER TABLE purchase_returns ADD COLUMN PRNo INT UNIQUE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'IVNO') THEN
        ALTER TABLE purchase_returns ADD COLUMN IVNO VARCHAR(5);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'SName') THEN
        ALTER TABLE purchase_returns ADD COLUMN SName VARCHAR(30);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'PNO') THEN
        ALTER TABLE purchase_returns ADD COLUMN PNO INT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'PName') THEN
        ALTER TABLE purchase_returns ADD COLUMN PName VARCHAR(30);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'PType') THEN
        ALTER TABLE purchase_returns ADD COLUMN PType VARCHAR(30);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'MFR') THEN
        ALTER TABLE purchase_returns ADD COLUMN MFR VARCHAR(30);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'PPrice') THEN
        ALTER TABLE purchase_returns ADD COLUMN PPrice FLOAT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'MRP') THEN
        ALTER TABLE purchase_returns ADD COLUMN MRP FLOAT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'AQTY') THEN
        ALTER TABLE purchase_returns ADD COLUMN AQTY INT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'RQTY') THEN
        ALTER TABLE purchase_returns ADD COLUMN RQTY INT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'Batch') THEN
        ALTER TABLE purchase_returns ADD COLUMN Batch INT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'EDate') THEN
        ALTER TABLE purchase_returns ADD COLUMN EDate INT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'purchase_returns' AND COLUMN_NAME = 'Tot') THEN
        ALTER TABLE purchase_returns ADD COLUMN Tot FLOAT;
    END IF;
END//
DELIMITER ;
CALL migrate_purchase_returns();
DROP PROCEDURE migrate_purchase_returns;
UPDATE purchase_returns SET PRNo = id WHERE PRNo IS NULL;

-- Legacy invoice details table
CREATE TABLE IF NOT EXISTS invoice_details (
    ENo INT AUTO_INCREMENT PRIMARY KEY,
    IVNO VARCHAR(5) NOT NULL,
    SName VARCHAR(30),
    PNO INT NOT NULL,
    PName VARCHAR(30),
    PType VARCHAR(30),
    MFR VARCHAR(30),
    PPrice FLOAT,
    MRP FLOAT,
    QTY INT,
    Batch INT,
    EDate INT,
    Tot FLOAT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Legacy inventory details table
CREATE TABLE IF NOT EXISTS inventory_details (
    PNO INT PRIMARY KEY,
    PName VARCHAR(30),
    PType VARCHAR(30),
    QTY INT,
    Batch INT,
    EDate INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Legacy billing details table
CREATE TABLE IF NOT EXISTS billing_details (
    BNo INT AUTO_INCREMENT PRIMARY KEY,
    DName VARCHAR(5),
    CName VARCHAR(30),
    CMno BIGINT,
    `Date` DATE,
    `Time` TIME,
    PNO INT NOT NULL,
    PName VARCHAR(30),
    MFR VARCHAR(30),
    QTY INT,
    MRP FLOAT,
    EDate INT,
    Tot FLOAT,
    GTot FLOAT,
    CONSTRAINT fk_billing_inventory_pno
        FOREIGN KEY (PNO) REFERENCES inventory_details(PNO)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Pharmacy Settings table
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- Default admin (password: admin123), categories, suppliers, and settings.
INSERT IGNORE INTO admins (id, username, password_hash, email) VALUES
(1, 'admin', 'scrypt:32768:8:1$7N26b7zL8Z78X8xT$ee3b6a9e88ff281a8b9e6ad7a048a1ef96faec481f3088b9015c7e148bd5d79679261aeead9df66f7f2b1d0eeed5a7114b0b144bcf55b55bf9ad6293eb64f699', 'admin@pharmacy.com');

INSERT IGNORE INTO categories (id, name, description, status) VALUES
(1, 'Tablets', 'Solid dosage form medicines', 'active'),
(2, 'Syrups & Liquids', 'Oral liquid solutions and suspensions', 'active'),
(3, 'Injections', 'Sterile injectable formulations', 'active'),
(4, 'Ointments & Creams', 'Topical semi-solid applications', 'active'),
(5, 'Capsules', 'Gelatin encapsulated medications', 'active');

INSERT IGNORE INTO suppliers
    (id, name, company_name, phone, email, address, registered_date, supplied_items, status)
VALUES
(1, 'Apex Pharma Distributors', 'Apex Pharmaceuticals Ltd.', '9876543210', 'sales@apexpharma.com', '123 Health Ave, Metro City', CURRENT_DATE, NULL, 'active'),
(2, 'MedLife Supplies', 'MedLife Healthcare Solutions', '9812345678', 'contact@medlifesupplies.com', '45 Science Park, Tech Hub', CURRENT_DATE, NULL, 'active'),
(3, 'BioCare Wholesale', 'BioCare Laboratories Inc.', '9711223344', 'info@biocare.com', '88 Industry Estate, North Zone', CURRENT_DATE, NULL, 'active');

INSERT IGNORE INTO settings (setting_key, setting_value) VALUES
('pharmacy_name', 'CurePlus Pharmacy & Healthcare'),
('address', '104 Main Street, Medical District, Cityville'),
('phone', '+1 (555) 019-2834'),
('email', 'info@curepluspharmacy.com'),
('tax_no', 'TAX-88942-PHARM'),
('currency_symbol', '₹'),
('receipt_footer', 'Thank you for choosing CurePlus Pharmacy! Get well soon.');
