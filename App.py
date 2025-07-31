import streamlit as st
from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
import datetime

# Function to generate the invoice PDF
def generate_invoice_pdf(company_name, company_logo, invoice_number, invoice_date, items, total_amount):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- Company Name at the Top (Centered, Large Font) ---
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, 800, company_name.upper())

    # --- Company Logo on Top-Right (if uploaded) ---
    if company_logo:
        logo = ImageReader(company_logo)
        c.drawImage(logo, width - 150, 770, width=100, height=40)

    # --- Quotation Number and Date ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 730, f"Quotation Number: {invoice_number}")
    c.drawString(50, 710, f"Quotation Date: {invoice_date}")

    # --- Items Table ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 680, "Item")
    c.drawString(300, 680, "Description")
    c.drawString(500, 680, "Price")

    y = 660
    c.setFont("Helvetica", 12)
    for item in items:
        c.drawString(50, y, item["name"])
        c.drawString(300, y, item["description"])
        c.drawString(500, y, f"{item['price']}")
        y -= 20

    # --- Total Amount ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y - 20, f"Total Amount: {total_amount}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- Streamlit App ---
st.set_page_config(page_title="Quotation Generator", page_icon="🧾")

st.title("🧾 Quotation Generator")

company_name = st.text_input("Company Name")
company_logo = st.file_uploader("Upload Company Logo (Optional)", type=["png", "jpg", "jpeg"])

invoice_number = st.text_input("Quotation Number", "0001")
invoice_date = st.date_input("Quotation Date", datetime.date.today())

st.subheader("Add Items to the Quotation")
item_name = st.text_input("Item Name")
item_description = st.text_input("Item Description")
item_price = st.text_input("Item Price")

# Add Items
if "items" not in st.session_state:
    st.session_state.items = []

if st.button("Add Item"):
    if item_name and item_price:
        try:
            price = float(item_price)
            st.session_state.items.append({
                "name": item_name,
                "description": item_description,
                "price": price
            })
            st.success("Item added!")
        except ValueError:
            st.error("Invalid price format. Please enter a number.")
    else:
        st.error("Please enter item name and price.")

# Show Added Items
if st.session_state.items:
    st.subheader("Items Added:")
    for i, item in enumerate(st.session_state.items):
        st.write(f"{i+1}. **{item['name']}** - {item['description']} - Rs. {item['price']}")

# Generate PDF
if st.button("Generate Quotation PDF"):
    if company_name and invoice_number and invoice_date and st.session_state.items:
        total = sum(item['price'] for item in st.session_state.items)
        pdf = generate_invoice_pdf(company_name, company_logo, invoice_number, invoice_date, st.session_state.items, total)
        st.success("Quotation PDF generated successfully!")
        st.download_button(label="Download PDF", data=pdf, file_name=f"Quotation_{invoice_number}.pdf", mime="application/pdf")
    else:
        st.error("Please complete all required fields and add at least one item.")
