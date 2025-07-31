import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
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

# --- PDF Generator ---
def generate_invoice_pdf(invoice_number, invoice_date, company_name, company_logo,
                         invoice_from_name, invoice_from_email, invoice_from_contact,
                         invoice_to_name, invoice_to_email, invoice_to_contact,
                         items, shipping_charges, packaging_charges, tax_rate):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"Quotation Number: {invoice_number}")
    c.drawString(50, 730, f"Quotation Date: {invoice_date}")

    if company_logo:
        logo = ImageReader(company_logo)
        c.drawImage(logo, 400, 730, width=120, height=50)
    c.setFont("Helvetica", 12)
    c.drawString(400, 710, company_name)

    c.line(50, 700, 550, 700)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 680, "Quotation From:")
    c.drawString(300, 680, "Quotation To:")
    c.setFont("Helvetica", 11)
    c.drawString(50, 660, invoice_from_name)
    c.drawString(50, 645, f"Email: {invoice_from_email}")
    c.drawString(50, 630, f"Contact: {invoice_from_contact}")
    c.drawString(300, 660, invoice_to_name)
    c.drawString(300, 645, f"Email: {invoice_to_email}")
    c.drawString(300, 630, f"Contact: {invoice_to_contact}")
    c.line(50, 615, 550, 615)

    # Table data
    data = [["S.No.", "Description", "Qty", "Price (PKR)", "Total (PKR)"]]
    total_amount = 0
    for i, item in enumerate(items):
        data.append([
            item["serial_number"],
            item["production_description"],
            str(item["quantity"]),
            f"{item['price']:.2f}",
            f"{item['total']:.2f}"
        ])
        total_amount += item["total"]

    table = Table(data, colWidths=[50, 200, 50, 80, 80])
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    y_position = 580 - (len(items) * 20)
    table.wrapOn(c, 500, 300)
    table.drawOn(c, 50, y_position)

    charges_y = y_position - 60
    tax = total_amount * (tax_rate / 100)
    total_incl_tax = total_amount + shipping_charges + packaging_charges + tax

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, charges_y, "Additional Charges:")
    c.setFont("Helvetica", 11)
    c.drawString(50, charges_y - 20, f"Subtotal: {total_amount:.2f} PKR")
    c.drawString(50, charges_y - 40, f"Shipping: {shipping_charges:.2f} PKR")
    c.drawString(50, charges_y - 60, f"Packaging: {packaging_charges:.2f} PKR")
    c.drawString(50, charges_y - 80, f"Tax ({tax_rate}%): {tax:.2f} PKR")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, charges_y - 100, f"Total (Incl. Tax): {total_incl_tax:.2f} PKR")
    c.setFont("Helvetica", 10)
    c.drawString(50, 40, "All prices are in Pakistani Rupees (PKR).")
    c.showPage()
    c.save()
    return buffer.getvalue()

# --- Generate PDF Button ---
if st.button("Generate Quotation PDF"):
    empty_fields = check_empty_fields()
    if not empty_fields:
        pdf_bytes = generate_invoice_pdf(
            invoice_number, invoice_date, company_name, company_logo,
            invoice_from_name, invoice_from_email, invoice_from_contact,
            invoice_to_name, invoice_to_email, invoice_to_contact,
            items, shipping_charges, packaging_charges, tax_rate
        )
        st.success("Quotation PDF generated successfully!")
        st.download_button(
            label="📄 Download PDF",
            data=pdf_bytes,
            file_name="Quotation.pdf",
            mime="application/pdf"
        )
    else:
        st.error(f"Please fill out the following fields: {', '.join(empty_fields)}")
