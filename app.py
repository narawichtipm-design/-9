from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "mobile_shop.db"

app = Flask(__name__)
app.secret_key = "mobile-shop-local-2026"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
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
        """
    )

    # Seed only when the tables are empty.
    if conn.execute("SELECT COUNT(*) FROM CUSTOMER").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO CUSTOMER VALUES (?, ?, ?)",
            [
                ("C0001", "สมชาย ใจดี", "0811111111"),
                ("C0002", "สมหญิง รักดี", "0822222222"),
                ("C0003", "มานะ พากเพียร", "0833333333"),
                ("C0004", "วิภา สุขใจ", "0844444444"),
                ("C0005", "ประยุทธ์ ตั้งใจ", "0855555555"),
            ],
        )

    if conn.execute("SELECT COUNT(*) FROM PRODUCT").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO PRODUCT VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("P0001", "iPhone 15", "Apple", "15", 25900, 20),
                ("P0002", "Samsung S25", "Samsung", "S25", 28900, 15),
                ("P0003", "AirPods", "Apple", "AirPods", 5990, 30),
                ("P0004", "Xiaomi 14", "Xiaomi", "14", 19900, 18),
            ],
        )

    if conn.execute("SELECT COUNT(*) FROM EMPLOYEE").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO EMPLOYEE VALUES (?, ?, ?)",
            [
                ("E0001", "สมศักดิ์ ขยัน", "พนักงานขาย"),
                ("E0002", "สายฝน ใจเย็น", "พนักงานขาย"),
                ("E0003", "อรุณรุ่ง เรือง", "พนักงานคลังสินค้า"),
            ],
        )

    if conn.execute("SELECT COUNT(*) FROM SUPPLIER").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO SUPPLIER VALUES (?, ?, ?)",
            [
                ("S0001", "บริษัท มือถือไทย จำกัด", "0899999991"),
                ("S0002", "ร้านอุปกรณ์เสริมรุ่งเรือง", "0899999992"),
            ],
        )

    if conn.execute("SELECT COUNT(*) FROM SUPPLIER_PRODUCT").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO SUPPLIER_PRODUCT VALUES (?, ?)",
            [
                ("S0001", "P0001"),
                ("S0001", "P0002"),
                ("S0001", "P0004"),
                ("S0002", "P0003"),
            ],
        )

    # Sample sales from the report. Insert only if SALE is empty.
    if conn.execute("SELECT COUNT(*) FROM SALE").fetchone()[0] == 0:
        sales = [
            ("S00001", "C0001", "E0001", "2026-08-01", 31890),
            ("S00002", "C0002", "E0001", "2026-08-01", 28900),
            ("S00003", "C0003", "E0002", "2026-08-02", 45800),
        ]
        details = [
            ("S00001", "P0001", 1, 25900),
            ("S00001", "P0003", 1, 5990),
            ("S00002", "P0002", 1, 28900),
            ("S00003", "P0004", 1, 19900),
            ("S00003", "P0001", 1, 25900),
        ]
        conn.executemany("INSERT INTO SALE VALUES (?, ?, ?, ?, ?)", sales)
        conn.executemany("INSERT INTO SALE_DETAIL VALUES (?, ?, ?, ?)", details)

    conn.commit()
    conn.close()


def next_sale_id(conn):
    row = conn.execute(
        "SELECT SALE_ID FROM SALE ORDER BY SALE_ID DESC LIMIT 1"
    ).fetchone()
    if not row:
        return "S00001"
    number = int(row["SALE_ID"][1:]) + 1
    return f"S{number:05d}"


@app.route("/")
def index():
    conn = get_db()
    stats = {
        "customers": conn.execute("SELECT COUNT(*) FROM CUSTOMER").fetchone()[0],
        "products": conn.execute("SELECT COUNT(*) FROM PRODUCT").fetchone()[0],
        "sales": conn.execute("SELECT COUNT(*) FROM SALE").fetchone()[0],
        "revenue": conn.execute("SELECT COALESCE(SUM(TOTAL_AMOUNT),0) FROM SALE").fetchone()[0],
    }
    recent_sales = conn.execute(
        """
        SELECT s.SALE_ID, s.SALE_DATE, c.CUS_NAME, e.EMP_NAME, s.TOTAL_AMOUNT
        FROM SALE s
        JOIN CUSTOMER c ON c.CUSTOMER_ID = s.CUSTOMER_ID
        JOIN EMPLOYEE e ON e.EMP_ID = s.EMP_ID
        ORDER BY s.SALE_DATE DESC, s.SALE_ID DESC
        LIMIT 5
        """
    ).fetchall()
    conn.close()
    return render_template("index.html", stats=stats, recent_sales=recent_sales)


@app.route("/customers")
def customers():
    conn = get_db()
    rows = conn.execute("SELECT * FROM CUSTOMER ORDER BY CUSTOMER_ID").fetchall()
    conn.close()
    return render_template("customers.html", customers=rows)


@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        customer_id = request.form["customer_id"].strip().upper()
        name = request.form["cus_name"].strip()
        phone = request.form["cus_phone"].strip()
        if not customer_id or not name or not phone:
            flash("กรุณากรอกข้อมูลให้ครบ", "error")
            return render_template("customer_form.html")
        if len(customer_id) != 5 or len(phone) != 10:
            flash("รหัสลูกค้าต้อง 5 ตัว และเบอร์โทรศัพท์ 10 ตัว", "error")
            return render_template("customer_form.html")
        try:
            conn = get_db()
            conn.execute("INSERT INTO CUSTOMER VALUES (?, ?, ?)", (customer_id, name, phone))
            conn.commit()
            conn.close()
            flash("เพิ่มข้อมูลลูกค้าเรียบร้อยแล้ว", "success")
            return redirect(url_for("customers"))
        except sqlite3.IntegrityError:
            flash("รหัสลูกค้านี้มีอยู่แล้ว", "error")
    return render_template("customer_form.html")


@app.route("/products")
def products():
    conn = get_db()
    rows = conn.execute("SELECT * FROM PRODUCT ORDER BY PRODUCT_ID").fetchall()
    conn.close()
    return render_template("products.html", products=rows)


@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        product_id = request.form["product_id"].strip().upper()
        name = request.form["product_name"].strip()
        brand = request.form["brand"].strip()
        model = request.form["model"].strip()
        try:
            price = float(request.form["price"])
            stock = int(request.form["stock_qty"])
        except ValueError:
            flash("ราคาและสต๊อกต้องเป็นตัวเลข", "error")
            return render_template("product_form.html")

        if not all([product_id, name, brand]) or price < 0 or stock < 0:
            flash("กรุณากรอกข้อมูลให้ถูกต้อง", "error")
            return render_template("product_form.html")

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO PRODUCT VALUES (?, ?, ?, ?, ?, ?)",
                (product_id, name, brand, model, price, stock),
            )
            conn.commit()
            conn.close()
            flash("เพิ่มข้อมูลสินค้าเรียบร้อยแล้ว", "success")
            return redirect(url_for("products"))
        except sqlite3.IntegrityError:
            flash("รหัสสินค้านี้มีอยู่แล้ว", "error")
    return render_template("product_form.html")


@app.route("/sales")
def sales():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT s.SALE_ID, s.SALE_DATE, c.CUS_NAME, e.EMP_NAME, s.TOTAL_AMOUNT
        FROM SALE s
        JOIN CUSTOMER c ON c.CUSTOMER_ID = s.CUSTOMER_ID
        JOIN EMPLOYEE e ON e.EMP_ID = s.EMP_ID
        ORDER BY s.SALE_DATE DESC, s.SALE_ID DESC
        """
    ).fetchall()
    conn.close()
    return render_template("sales.html", sales=rows)


@app.route("/sales/add", methods=["GET", "POST"])
def add_sale():
    conn = get_db()
    customers = conn.execute("SELECT * FROM CUSTOMER ORDER BY CUSTOMER_ID").fetchall()
    employees = conn.execute("SELECT * FROM EMPLOYEE WHERE EMP_POSITION = 'พนักงานขาย' ORDER BY EMP_ID").fetchall()
    products = conn.execute("SELECT * FROM PRODUCT WHERE STOCK_QTY > 0 ORDER BY PRODUCT_ID").fetchall()

    if request.method == "POST":
        customer_id = request.form["customer_id"]
        emp_id = request.form["emp_id"]
        product_id = request.form["product_id"]
        sale_date = request.form["sale_date"] or date.today().isoformat()

        try:
            qty = int(request.form["qty"])
        except ValueError:
            qty = 0

        product = conn.execute("SELECT * FROM PRODUCT WHERE PRODUCT_ID = ?", (product_id,)).fetchone()
        if not product or qty < 1:
            flash("กรุณาเลือกสินค้าและจำนวนให้ถูกต้อง", "error")
            conn.close()
            return render_template("sale_form.html", customers=customers, employees=employees, products=products)

        if qty > product["STOCK_QTY"]:
            flash("จำนวนสินค้ามากกว่าสต๊อกที่มี", "error")
            conn.close()
            return render_template("sale_form.html", customers=customers, employees=employees, products=products)

        sale_id = next_sale_id(conn)
        total = product["PRICE"] * qty

        try:
            conn.execute(
                "INSERT INTO SALE VALUES (?, ?, ?, ?, ?)",
                (sale_id, customer_id, emp_id, sale_date, total),
            )
            conn.execute(
                "INSERT INTO SALE_DETAIL VALUES (?, ?, ?, ?)",
                (sale_id, product_id, qty, product["PRICE"]),
            )
            conn.execute(
                "UPDATE PRODUCT SET STOCK_QTY = STOCK_QTY - ? WHERE PRODUCT_ID = ?",
                (qty, product_id),
            )
            conn.commit()
            flash(f"บันทึกการขาย {sale_id} จำนวนเงิน {total:,.2f} บาท เรียบร้อยแล้ว", "success")
            return redirect(url_for("sales"))
        except sqlite3.IntegrityError as exc:
            conn.rollback()
            flash(f"ไม่สามารถบันทึกการขายได้: {exc}", "error")

    conn.close()
    return render_template(
        "sale_form.html",
        customers=customers,
        employees=employees,
        products=products,
        today=date.today().isoformat(),
    )


@app.route("/sales/<sale_id>")
def sale_detail(sale_id):
    conn = get_db()
    sale = conn.execute(
        """
        SELECT s.*, c.CUS_NAME, c.CUS_PHONE, e.EMP_NAME
        FROM SALE s
        JOIN CUSTOMER c ON c.CUSTOMER_ID = s.CUSTOMER_ID
        JOIN EMPLOYEE e ON e.EMP_ID = s.EMP_ID
        WHERE s.SALE_ID = ?
        """,
        (sale_id,),
    ).fetchone()
    details = conn.execute(
        """
        SELECT sd.*, p.PRODUCT_NAME, p.BRAND, p.MODEL
        FROM SALE_DETAIL sd
        JOIN PRODUCT p ON p.PRODUCT_ID = sd.PRODUCT_ID
        WHERE sd.SALE_ID = ?
        """,
        (sale_id,),
    ).fetchall()
    conn.close()
    if not sale:
        flash("ไม่พบรายการขาย", "error")
        return redirect(url_for("sales"))
    return render_template("sale_detail.html", sale=sale, details=details)


@app.route("/suppliers")
def suppliers():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT sp.SUPPLIER_ID, s.SUPPLIER_NAME, s.SUPPLIER_PHONE,
               sp.PRODUCT_ID, p.PRODUCT_NAME
        FROM SUPPLIER_PRODUCT sp
        JOIN SUPPLIER s ON s.SUPPLIER_ID = sp.SUPPLIER_ID
        JOIN PRODUCT p ON p.PRODUCT_ID = sp.PRODUCT_ID
        ORDER BY sp.SUPPLIER_ID, sp.PRODUCT_ID
        """
    ).fetchall()
    conn.close()
    return render_template("suppliers.html", suppliers=rows)


init_db()

if __name__ == "__main__":
    app.run(debug=True)
