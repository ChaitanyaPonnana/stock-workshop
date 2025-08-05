import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --------- CONFIGURATION ---------
CSV_FILE = "registrations.csv"
WHATSAPP_LINK = "https://chat.whatsapp.com/KpkyyyevxqmFOnkaZUsTo2?mode=ac_t"
QR_CODE_IMAGE = "screenshots/QR-CODE.jpg"

EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Use app password if 2FA enabled

# --------- FUNCTIONS ---------
def send_confirmation_email(to_email, name):
    subject = "Workshop Registration Confirmation"
    body = f"""
    Hi {name},

    Thank you for registering for the Stock Market Workshop.

    We have received your registration successfully.

    Regards,
    Workshop Team
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

def save_registration(data: dict):
    df = pd.DataFrame([data])
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, mode='w', header=True, index=False)

def get_registration_count():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return len(df)
    return 0

# --------- STREAMLIT UI ---------
st.title("📈 Stock Market Workshop Registration")

st.markdown("Please fill the form below to register for the workshop.")

# Payment QR Code
st.image(QR_CODE_IMAGE, caption="Scan to Pay via PhonePe", width=250)

with st.form(key='registration_form'):
    name = st.text_input("Full Name", max_chars=50)
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")

    college = st.selectbox("College / Institution", [
        "ANIL NEERUKONDA INSTITUTE OF TECHNOLOGY AND SCIENCES",
        "OTHER"
    ])
    
    branch = st.selectbox("Branch", [
        "CSE", "CSD", "CSM", "ECE", "EEE", "MEC", "CIVIL", "CHEMICAL", "OTHER"
    ])
    
    year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Other"])
    payment_screenshot = st.file_uploader("Upload your payment screenshot here (PNG/JPG)", type=["png", "jpg", "jpeg"])
    submit = st.form_submit_button("Register")

if submit:
    if not (name and email and phone and college and branch and year and payment_screenshot):
        st.error("Please fill all fields and upload payment screenshot before submitting.")
    else:
        # Save Screenshot
        os.makedirs("screenshots", exist_ok=True)
        file_path = os.path.join("screenshots", payment_screenshot.name)
        with open(file_path, "wb") as f:
            f.write(payment_screenshot.getbuffer())

        # Save Registration
        registration_data = {
            "Name": name,
            "Email": email,
            "Phone": phone,
            "College": college,
            "Branch": branch,
            "Year": year,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Payment Screenshot": file_path
        }

        save_registration(registration_data)

        # Send email
        email_sent = send_confirmation_email(email, name)

        if email_sent:
            st.success("✅ Registration successful! Confirmation email sent.")
        else:
            st.warning("⚠️ Registration saved but failed to send confirmation email.")

        # WhatsApp group link after successful submission
        st.markdown(f"📱 *Join the WhatsApp group here:* [Click to Join]({WHATSAPP_LINK})")

st.markdown("---")
st.markdown(f"### 🧾 Total Registered Participants (Paid): **{get_registration_count()}**")
