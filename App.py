import streamlit as st
from docx import Document
from docx.shared import Inches
from io import BytesIO

st.set_page_config(page_title="Quotation Generator", layout="centered")
st.title("Quotation Generator App")

# --- Quotation Details ---
st.header("Quotation Details")
invoice_number = st.text_input("Quotation Number")
invoice_date = st.text_input("Quotation Date")
company_name = st.text_input("Company Name")
company_logo = st.file_uploader("Upload Company Logo (optional)", type=["png", "jpg", "jpeg"])

# --- Quotation From ---
st.header("Quotation From")
invoice_from_name = st.text_input("Name (Quotation From)")
invoice_from_email = st.text_input("Email (Quotation From)")
invoice_from_contact = st.text_input("Contact Number (Quotation From)")

# --- Quotation To ---
st.header("Quotation To")
invoice_to_name = st.text_input("Name (Quotation To)")
invoice_to_email = st.text_input("Email (Quotation To)")
invoice_to_contact = st.text_input("Contact Number (Quotation To)")

# --- Items ---
st.header("Items")
items = []
num_items = st.number_input("Number of Items", min_value=1, value=1)

for i in range(int(num_items)):
    st.subheader(f"Item {i+1}")
    serial_number = st.text_input(f"Serial Number {i+1}", key=f"serial_{i}")
    production_description = st.text_input(f"Production Description {i+1}", key=f"desc_{i}")
    quantity = st.number_input(f"Quantity {i+1}", min_value=1, value=1, key=f"qty_{i}")
    price = st.number_input(f"Price {i+1} (PKR)", min_value=0.0, value=0.0, key=f"price_{i}")
    total = quantity * price
    items.append({
        "serial_number": serial_number,
        "production_description": production_description,
        "quantity": quantity,
        "price": price,
        "total": total
    })

# --- Additional Charges ---
st.header("Additional Charges")
shipping_charges = st.number_input("Shipping Charges (PKR)", min_value=0.0, value=0.0)
packaging_charges = st.number_input("Packaging Charges (PKR)", min_value=0.0, value=0.0)
tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, value=0.0)

# --- Validation ---
def check_empty_fields():
    empty_fields = []
    if not invoice_number: empty_fields.append("Quotation Number")
    if not invoice_date: empty_fields.append("Quotation Date")
    if not company_name: empty_fields.append("Company Name")
    if not invoice_from_name: empty_fields.append("Name (Quotation From)")
    if not invoice_from_email: empty_fields.append("Email (Quotation From)")
    if not invoice_from_contact: empty_fields.append("Contact Number (Quotation From)")
    if not invoice_to_name: empty_fields.append("Name (Quotation To)")
    if not invoice_to_email: empty_fields.append("Email (Quotation To)")
    if not invoice_to_contact: empty_fields.append("Contact Number (Quotation To)")
    for i, item in enumerate(items):
        if not item["serial_number"]: empty_fields.append(f"Serial Number {i+1}")
        if not item["production_description"]: empty_fields.append(f"Production Description {i+1}")
        if item["quantity"] <= 0: empty_fields.append(f"Quantity {i+1}")
        if item["price"] <= 0: empty_fields.append(f"Price {i+1}")
    return empty_fields

# --- DOCX Generator ---
def generate_invoice_docx(invoice_number, invoice_date, company_name, company_logo,
                          invoice_from_name, invoice_from_email, invoice_from_contact,
                          invoice_to_name, invoice_to_email, invoice_to_contact,
                          items, shipping_charges, packaging_charges, tax_rate):
    doc = Document()

    if company_logo:
        doc.add_picture(company_logo, width=Inches(2.0))

    doc.add_heading(company_name, level=1)
    doc.add_paragraph(f"Quotation Number: {invoice_number}")
    doc.add_paragraph(f"Quotation Date: {invoice_date}")
    doc.add_paragraph(" ")

    # Quotation From and To
    doc.add_heading("Quotation From", level=2)
    doc.add_paragraph(f"{invoice_from_name}\nEmail: {invoice_from_email}\nContact: {invoice_from_contact}")
    doc.add_heading("Quotation To", level=2)
    doc.add_paragraph(f"{invoice_to_name}\nEmail: {invoice_to_email}\nContact: {invoice_to_contact}")
    doc.add_paragraph(" ")

    # Items Table
    table = doc.add_table(rows=1, cols=5)
    table.style = 'Light List Accent 1'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'S.No.'
    hdr_cells[1].text = 'Description'
    hdr_cells[2].text = 'Quantity'
    hdr_cells[3].text = 'Price (PKR)'
    hdr_cells[4].text = 'Total (PKR)'

    total_amount = 0
    for item in items:
        row_cells = table.add_row().cells
        row_cells[0].text = item["serial_number"]
        row_cells[1].text = item["production_description"]
        row_cells[2].text = str(item["quantity"])
        row_cells[3].text = f"{item['price']:.2f}"
        row_cells[4].text = f"{item['total']:.2f}"
        total_amount += item["total"]

    tax = total_amount * (tax_rate / 100)
    total_incl_tax = total_amount + shipping_charges + packaging_charges + tax

    # Charges
    doc.add_paragraph(" ")
    doc.add_heading("Additional Charges", level=2)
    doc.add_paragraph(f"Subtotal: {total_amount:.2f} PKR")
    doc.add_paragraph(f"Shipping Charges: {shipping_charges:.2f} PKR")
    doc.add_paragraph(f"Packaging Charges: {packaging_charges:.2f} PKR")
    doc.add_paragraph(f"Tax ({tax_rate}%): {tax:.2f} PKR")
    doc.add_paragraph(f"Total (Incl. Tax): {total_incl_tax:.2f} PKR")

    # Footer
    doc.add_paragraph("\nAll prices are in Pakistani Rupees_
