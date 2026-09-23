# ระบบจัดการร้านขายโทรศัพท์มือถือ

Local Web Application สำหรับ Bonus Project วิชาการออกแบบและจัดการฐานข้อมูล

## เทคโนโลยี
- Python
- Flask
- SQLite
- HTML/CSS/Jinja2

## โครงสร้างฐานข้อมูล
ใช้ 7 ตารางตามใบงานโครงงานเดิมเท่านั้น

- CUSTOMER
- PRODUCT
- EMPLOYEE
- SUPPLIER
- SALE
- SALE_DETAIL
- SUPPLIER_PRODUCT

## ฟังก์ชันที่มี
- หน้า Dashboard แสดงข้อมูลสรุป
- ดูข้อมูล CUSTOMER
- เพิ่ม CUSTOMER (INSERT)
- ดูข้อมูล PRODUCT
- เพิ่ม PRODUCT (INSERT)
- ดูข้อมูล SALE
- เพิ่ม SALE และ SALE_DETAIL (INSERT)
- ตัดจำนวน STOCK_QTY เมื่อบันทึกการขาย
- ดูข้อมูล SUPPLIER_PRODUCT

## วิธีติดตั้งและรัน

### 1) เปิด Terminal ในโฟลเดอร์โปรเจกต์
```bash
cd mobile_shop_web
```

### 2) ติดตั้ง Flask
```bash
pip install -r requirements.txt
```

### 3) รันโปรแกรม
```bash
python app.py
```

### 4) เปิดเว็บ
เข้าเบราว์เซอร์ที่
```text
http://127.0.0.1:5000
```

ไฟล์ `mobile_shop.db` จะถูกสร้างอัตโนมัติในโฟลเดอร์โปรเจกต์ และข้อมูลจะไม่หายเมื่อปิดแล้วเปิดโปรแกรมใหม่ เพราะใช้ SQLite เป็นไฟล์ฐานข้อมูล

## โครงสร้างโฟลเดอร์
```text
mobile_shop_web/
├── app.py
├── mobile_shop.db
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── customers.html
│   ├── customer_form.html
│   ├── products.html
│   ├── product_form.html
│   ├── sales.html
│   ├── sale_form.html
│   ├── sale_detail.html
│   └── suppliers.html
└── static/
    └── style.css
```
