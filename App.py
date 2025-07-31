import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO

# Streamlit app title
st.title("Quotation Generator App")

# Input fields for invoice details
st.header("Quotation Details")
invoice_number = st.text_input("Quotation Number:")
invoice_date = st.text_input("Quotation Date:")
company_name = st.text_input("Company Name:")
company_logo = st.file_uploader("Upload Company Logo (optional)", type=["png", "jpg", "jpeg"])

# Input fields for "Invoice From"
st.header("Quotation From")
invoice_from_name = st.text_input("Name (Quotation From):")
invoice_from_email = st.text_input("Email (Quotation From):")
invoice_from_contact = st.text_input("Contact Number (Quotation From):")

# Input fields for "Invoice To"
st.header("Quotation To")
invoice_to_name = st.text_input("Name (Quotation To):")
invoice_to_email = st.text_input("Email (Quotation To):")
invoice_to_contact = st.text_input("Contact Number (Quotation To):")

# Input fields for items
st.header("Items")
items = []
num_items = st.number_input("Number of Items", min_value=1, value=1)

for i in range(num_items):
    st.subheader(f"Item {i+1}")
    serial_number = st.text_input(f"Serial Number {i+1}:")
    production_description = st.text_input(f"Production Description {i+1}:")
    quantity = st.number_input(f"Quantity {i+1}:", min_value=1, value=1)
    price = st.number_input(f"Price {i+1} (PKR):", min_value=0.0, value=0.0)
    total = quantity * price
    items.append({
        "serial_number": serial_number,
        "production_description": production_description,
        "quantity": quantity,
        "price": price,
        "total": total
    })

# Input fields for additional charges
st.header("Additional Charges")
shipping_charges = st.number_input("Shipping Charges (PKR):", min_value=0.0, value=0.0)
packaging_charges = st.number_input("Packaging Charges (PKR):", min_value=0.0, value=0.0)
tax_rate = st.number_input("Tax Rate (%):", min_value=0.0, value=0.0)

# Function to check for empty fields
def check_empty_fields():
    empty_fields = []
    
    # Invoice Details
    if not invoice_number:
        empty_fields.append("Quotation Number")
    if not invoice_date:
        empty_fields.append("Quotation Date")
    if not company_name:
        empty_fields.append("Company Name")
    
    # Invoice From
    if not invoice_from_name:
        empty_fields.append("Name (Quotation From)")
    if not invoice_from_email:
        empty_fields.append("Email (Quotation From)")
    if not invoice_from_contact:
        empty_fields.append("Contact Number (Quotation From)")
    
    # Invoice To
    if not invoice_to_name:
        empty_fields.append("Name (Quotation To)")
    if not invoice_to_email:
        empty_fields.append("Email (Quotation To)")
    if not invoice_to_contact:
        empty_fields.append("Contact Number (Quotation To)")
    
    # Items
    for i, item in enumerate(items):
        if not item["serial_number"]:
            empty_fields.append(f"Serial Number {i+1}")
        if not item["production_description"]:
            empty_fields.append(f"Production Description {i+1}")
        if item["quantity"] <= 0:
            empty_fields.append(f"Quantity {i+1}")
        if item["price"] <= 0:
            empty_fields.append(f"Price {i+1}")
    
    return empty_fields

# Function to generate PDF invoice
def generate_invoice_pdf(invoice_number, invoice_date, company_name, company_logo,
                         invoice_from_name, invoice_from_email, invoice_from_contact,
                         invoice_to_name, invoice_to_email, invoice_to_contact,
                         items, shipping_charges, packaging_charges, tax_rate):
    # Create a BytesIO buffer to store the PDF
    buffer = BytesIO()
    
    # Create a PDF canvas
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set font and size for the title
    c.setFont("Helvetica-Bold", 16)
    
    # Add invoice number, reference number, and date on the left
    c.drawString(50, 750, f"Invoice Number: {invoice_number}")
    c.drawString(50, 710, f"Invoice Date: {invoice_date}")
    
    # Add company name and logo on the right
    if company_logo:
        # Save the uploaded logo to a temporary file
        logo_path = "temp_logo.png"
        with open(logo_path, "wb") as f:
            f.write(company_logo.getbuffer())
        
        # Draw the logo on the PDF
        c.drawImage(logo_path, 400, 730, width=100, height=50)
    
    c.drawString(400, 710, company_name)
    
    # Add a line separator
    c.line(50, 700, 550, 700)
    
    # Add "Invoice From" and "Invoice To" sections
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 680, "Quotation From:")
    c.drawString(300, 680, "Quotation To:")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 660, invoice_from_name)
    c.drawString(50, 640, f"Email: {invoice_from_email}")
    c.drawString(50, 620, f"Contact: {invoice_from_contact}")
    
    c.drawString(300, 660, invoice_to_name)
    c.drawString(300, 640, f"Email: {invoice_to_email}")
    c.drawString(300, 620, f"Contact: {invoice_to_contact}")
    
    # Add a line separator
    c.line(50, 600, 550, 600)
    
    # Add itemized table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 580, "Itemized Bill")
    
    # Create a table for items
    data = [["S.No.", "Production Description", "Quantity", "Price (PKR)", "Total (PKR)"]]
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
    
    # Create a Table object
    table = Table(data, colWidths=[50, 200, 50, 80, 80])
    
    # Add style to the table
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
    
    # Draw the table on the PDF
    table.wrapOn(c, 400, 200)
    table.drawOn(c, 50, 400)
    
    # Add additional charges below the table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 350, "Additional Charges:")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 330, f"Subtotal: {total_amount:.2f} PKR")
    c.drawString(50, 310, f"Shipping Charges: {shipping_charges:.2f} PKR")
    c.drawString(50, 290, f"Packaging Charges: {packaging_charges:.2f} PKR")
    
    # Calculate tax and total
    tax = total_amount * (tax_rate / 100)
    total_incl_tax = total_amount + shipping_charges + packaging_charges + tax
    
    c.drawString(50, 270, f"Tax ({tax_rate}%): {tax:.2f} PKR")
    c.drawString(50, 250, f"Total (INCL Tax): {total_incl_tax:.2f} PKR")
    
    # Add footer message
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "All prices are in PKR.")
    
    # Save the PDF
    c.showPage()
    c.save()
    
    # Get the value of the BytesIO buffer and return it
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# Button to generate and download the PDF
if st.button("Generate Quotation PDF"):
    empty_fields = check_empty_fields()
    
    if not empty_fields:
        # Generate the PDF
        pdf_bytes = generate_invoice_pdf(
            invoice_number, invoice_date, company_name, company_logo,
            invoice_from_name, invoice_from_email, invoice_from_contact,
            invoice_to_name, invoice_to_email, invoice_to_contact,
            items, shipping_charges, packaging_charges, tax_rate
        )
        
        # Show success message
        st.success("Quotation PDF generated successfully!")
        
        # Provide a download link for the PDF
        st.download_button(
            label="Download Quotation PDF",
            data=pdf_bytes,
            file_name="Quotation.pdf",
            mime="application/pdf",
        )
    else:
        # Show error message with empty fields highlighted
        st.error(f"The following fields are empty: {', '.join(empty_fields)}. Please fill them out.")
