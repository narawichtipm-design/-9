import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "mobile_shop.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
conn.executescript('''
CREATE TABLE IF NOT EXISTS CUSTOMER (
    CUSTOMER_ID CHAR(5) PRIMARY KEY,
    CUS_NAME VARCHAR(50) NOT NULL,
    CUS_PHONE CHAR(10) NOT NULL
);
CREATE TABLE IF NOT EXISTS PRODUCT (
    PRODUCT_ID CHAR(5) PRIMARY KEY,
    PRODUCT_NAME VARCHAR(50) NOT NULL,
    BRAND VARCHAR(30) NOT NULL,
    MODEL VARCHAR(30),
    PRICE DECIMAL(10,2) NOT NULL DEFAULT 0,
    STOCK_QTY INT NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS EMPLOYEE (
    EMP_ID CHAR(5) PRIMARY KEY,
    EMP_NAME VARCHAR(50) NOT NULL,
    EMP_POSITION VARCHAR(30) NOT NULL
);
CREATE TABLE IF NOT EXISTS SUPPLIER (
    SUPPLIER_ID CHAR(5) PRIMARY KEY,
    SUPPLIER_NAME VARCHAR(50) NOT NULL,
    SUPPLIER_PHONE CHAR(10) NOT NULL
);
CREATE TABLE IF NOT EXISTS SALE (
    SALE_ID CHAR(6) PRIMARY KEY,
    CUSTOMER_ID CHAR(5) NOT NULL,
    EMP_ID CHAR(5) NOT NULL,
    SALE_DATE DATE NOT NULL,
    TOTAL_AMOUNT DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMER(CUSTOMER_ID),
    FOREIGN KEY (EMP_ID) REFERENCES EMPLOYEE(EMP_ID)
);
CREATE TABLE IF NOT EXISTS SALE_DETAIL (
    SALE_ID CHAR(6) NOT NULL,
    PRODUCT_ID CHAR(5) NOT NULL,
    QTY INT NOT NULL DEFAULT 1,
    UNIT_PRICE DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (SALE_ID, PRODUCT_ID),
    FOREIGN KEY (SALE_ID) REFERENCES SALE(SALE_ID),
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID)
);
CREATE TABLE IF NOT EXISTS SUPPLIER_PRODUCT (
    SUPPLIER_ID CHAR(5) NOT NULL,
    PRODUCT_ID CHAR(5) NOT NULL,
    PRIMARY KEY (SUPPLIER_ID, PRODUCT_ID),
    FOREIGN KEY (SUPPLIER_ID) REFERENCES SUPPLIER(SUPPLIER_ID),
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID)
);
''')

seed = conn.execute("SELECT COUNT(*) FROM CUSTOMER").fetchone()[0]
if seed == 0:
    conn.executemany("INSERT INTO CUSTOMER VALUES (?, ?, ?)", [
        ("C0001", "สมชาย ใจดี", "0811111111"),
        ("C0002", "สมหญิง รักดี", "0822222222"),
        ("C0003", "มานะ พากเพียร", "0833333333"),
        ("C0004", "วิภา สุขใจ", "0844444444"),
        ("C0005", "ประยุทธ์ ตั้งใจ", "0855555555"),
    ])
    conn.executemany("INSERT INTO PRODUCT VALUES (?, ?, ?, ?, ?, ?)", [
        ("P0001", "iPhone 15", "Apple", "15", 25900, 20),
        ("P0002", "Samsung S25", "Samsung", "S25", 28900, 15),
        ("P0003", "AirPods", "Apple", "AirPods", 5990, 30),
        ("P0004", "Xiaomi 14", "Xiaomi", "14", 19900, 18),
    ])
    conn.executemany("INSERT INTO EMPLOYEE VALUES (?, ?, ?)", [
        ("E0001", "สมศักดิ์ ขยัน", "พนักงานขาย"),
        ("E0002", "สายฝน ใจเย็น", "พนักงานขาย"),
        ("E0003", "อรุณรุ่ง เรือง", "พนักงานคลังสินค้า"),
    ])
    conn.executemany("INSERT INTO SUPPLIER VALUES (?, ?, ?)", [
        ("S0001", "บริษัท มือถือไทย จำกัด", "0899999991"),
        ("S0002", "ร้านอุปกรณ์เสริมรุ่งเรือง", "0899999992"),
    ])
    conn.executemany("INSERT INTO SALE VALUES (?, ?, ?, ?, ?)", [
        ("S00001", "C0001", "E0001", "2026-08-01", 31890),
        ("S00002", "C0002", "E0001", "2026-08-01", 28900),
        ("S00003", "C0003", "E0002", "2026-08-02", 45800),
    ])
    conn.executemany("INSERT INTO SALE_DETAIL VALUES (?, ?, ?, ?)", [
        ("S00001", "P0001", 1, 25900),
        ("S00001", "P0003", 1, 5990),
        ("S00002", "P0002", 1, 28900),
        ("S00003", "P0004", 1, 19900),
        ("S00003", "P0001", 1, 25900),
    ])
    conn.executemany("INSERT INTO SUPPLIER_PRODUCT VALUES (?, ?)", [
        ("S0001", "P0001"),
        ("S0001", "P0002"),
        ("S0001", "P0004"),
        ("S0002", "P0003"),
    ])

conn.commit()
print(f"สร้างฐานข้อมูลแล้ว: {DB_PATH}")
print("ตาราง:", [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")])
for table in ["CUSTOMER","PRODUCT","EMPLOYEE","SUPPLIER","SALE","SALE_DETAIL","SUPPLIER_PRODUCT"]:
    print(table, conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
conn.close()
