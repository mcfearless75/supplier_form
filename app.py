import io
import base64

import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

def generate_pdf_bytes(fields, sig_data):
    """
    Manual PDF builder using reportlab.pdfgen.canvas.
    Draws text, tables, and images at fixed positions.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 20 * mm

    # — Logo —
    logo_img = ImageReader(io.BytesIO(base64.b64decode(fields["logo_b64"])))
    c.drawImage(logo_img,
                x=margin,
                y=height - margin - 30*mm,
                width=40*mm,
                preserveAspectRatio=True,
                mask='auto')

    # — Title —
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin + 45*mm,
                 height - margin - 15*mm,
                 "SUPPLY AGREEMENT")

    # — Intro —
    c.setFont("Helvetica", 10)
    intro = (
        "This agreement is issued in conjunction with our Terms of Business. "
        "Contact us on 0800 772 3959 or email info@prlsitesolutions.co.uk with any queries."
    )
    text = c.beginText(margin, height - margin - 40*mm)
    text.textLines(intro)
    c.drawText(text)

    # — Your Details —
    y = height - margin - 60*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Your Details:")
    c.setFont("Helvetica", 10)
    y -= 6*mm
    c.drawString(margin, y, f"Company Name: {fields['company_name']}")
    y -= 5*mm
    c.drawString(margin, y, f"Address: {fields['address'].replace(chr(10), ' ')}")
    y -= 5*mm
    c.drawString(margin, y, f"Company Reg No: {fields['reg_no']}")

    # — Supply Details —
    x2 = margin + 90*mm
    y = height - margin - 60*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x2, y, "Supply Details:")
    c.setFont("Helvetica", 10)
    y -= 6*mm
    c.drawString(x2, y, f"For the Supply of: {fields['supply_of']}")
    y -= 5*mm
    c.drawString(x2, y, f"Site Location: {fields['site_location']}")
    y -= 5*mm
    c.drawString(x2, y, f"Start Date: {fields['start_date']}")

    # — Rates Table —
    y = height - margin - 90*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Our Charge Rates:")
    y -= 6*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Description")
    c.drawString(margin + 60*mm, y, "Rate")
    c.drawString(margin + 90*mm, y, "Basis")
    c.setFont("Helvetica", 10)
    for desc, rate, basis in fields["rates"]:
        y -= 5*mm
        c.drawString(margin, y, desc)
        c.drawString(margin + 60*mm, y, rate)
        c.drawString(margin + 90*mm, y, basis)

    # — Breakdown —
    y -= 10*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "BREAKDOWN:")
    c.setFont("Helvetica", 10)
    for line in [
        "First 40 hrs Mon–Fri (including breaks)",
        "After 40 hrs Mon–Fri & all hrs Saturday",
        "All hrs Sunday"
    ]:
        y -= 5*mm
        c.drawString(margin, y, f"• {line}")

    # — Additional Info —
    y -= 10*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Additional Information:")
    c.setFont("Helvetica", 10)
    y -= 6*mm
    for ln in fields["terms"].split("\n"):
        c.drawString(margin, y, ln)
        y -= 5*mm

    # — PRL Signature —
    y -= 10*mm
    prl_sig_buf = io.BytesIO(base64.b64decode(fields["kt_b64"]))
    prl_img = ImageReader(prl_sig_buf)
    c.drawImage(prl_img,
                x=margin,
                y=y - 25*mm,
                width=50*mm,
                preserveAspectRatio=True,
                mask='auto')
    c.setFont("Helvetica", 10)
    c.drawString(margin, y - 27*mm, "Signed on behalf of PRL Site Solutions")
    c.drawString(margin, y - 32*mm, f"Signed by: {fields['signer_name']}")
    c.drawString(margin, y - 37*mm, f"Position: {fields['signer_position']}")
    c.drawString(margin, y - 42*mm, f"Date: {fields['signer_date']}")

    # — Client Signature —
    arr = sig_data.astype("uint8")
    client_im = Image.fromarray(arr, "RGBA").convert("RGB")
    client_buf = io.BytesIO()
    client_im.save(client_buf, format="PNG")
    client_buf.seek(0)
    client_reader = ImageReader(client_buf)
    x_sig = margin + 90*mm
    c.drawImage(client_reader,
                x=x_sig,
                y=y - 25*mm,
                width=50*mm,
                preserveAspectRatio=True,
                mask='auto')
    c.drawString(x_sig, y - 27*mm, "Signed on behalf of the Client")
    c.drawString(x_sig, y - 32*mm, f"Signed by: {fields['client_name']}")
    c.drawString(x_sig, y - 37*mm, f"Position: {fields['client_position']}")
    c.drawString(x_sig, y - 42*mm, f"Date: {fields['client_date']}")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()

def main():
    st.set_page_config(page_title="PRL Site Solutions – Supply Agreement", layout="wide")

    # ─── Global CSS Styling ───────────────────────────────
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
      * { font-family: 'Roboto', sans-serif !important; }
      .stApp .block-container { padding-top:80px!important; max-width:760px; margin:auto; }
      .header-card, .section-card {
        background:#1f1f1f; padding:20px; margin-bottom:30px;
        border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.5);
      }
      .header-card h2, .section-card h2 { color:#00d1ff; margin-top:0; }
      .stTextInput>div>input, .stTextArea>div>textarea {
        background:#2a2a2a!important; border:1px solid #444!important;
        border-radius:6px!important; color:#eee!important;
      }
      .stButton>button {
        background:#00aaff!important; color:#fff!important;
        border-radius:6px!important; padding:.6em 1em!important; font-weight:600!important;
      }
      .stButton>button:hover { background:#008fcc!important; }
    </style>
    """, unsafe_allow_html=True)

    # ─── HEADER ───────────────────────────────────────────
    with st.container():
        st.markdown("<div class='header-card'>", unsafe_allow_html=True)
        cols = st.columns([1,4])
        with cols[0]:
            st.image("logo.png", width=80)
        with cols[1]:
            st.markdown("## SUPPLY AGREEMENT")
            st.write(
                "This agreement is issued in conjunction with our Terms of Business.\n"
                "Please contact us on **0800 772 3959** or email **info@prlsitesolutions.co.uk** if you have any queries."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── YOUR DETAILS ─────────────────────────────────────
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Your Details")
        company_name = st.text_input("Company Name", "PRL Site Solutions")
        address      = st.text_area("Address", "18 Beryl Rd, Birkenhead, Prenton CH43 9RT", height=80)
        reg_no       = st.text_input("Company Reg No", "14358717")
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── SUPPLY DETAILS ───────────────────────────────────
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Supply Details")
        supply_of     = st.text_input("For the Supply of", "Bolting Technicians (Flange Techs)")
        site_location = st.text_input("Site Location", "UK Wide")
        start_date    = st.date_input("Start Date")
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── CHARGE RATES ────────────────────────────────────
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Our Charge Rates")
        df_rates = pd.DataFrame({
            "Description": [
                "Basic Rate (Day)", "Basic Rate (Night)",
                "Overtime Rate (1)", "Overtime Rate (2)",
                "Expenses", "Lodge"
            ],
            "Rate": ["£29.90","£38.87","£42.90","£50.96","£–","£60"],
            "Basis": ["Per Hour"]*4 + ["Per Day",""]
        })
        try:
            rates_df = st.data_editor(df_rates, num_rows="fixed", key="rates")
        except:
            rates_df = st.experimental_data_editor(df_rates, num_rows="fixed", key="rates")
        rates = list(rates_df.itertuples(index=False, name=None))
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── ADDITIONAL INFO ──────────────────────────────────
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Additional Information")
        terms = st.text_area("Notes (e.g., breaks)", "Breaks to be paid (15 min, 30 min, 15 min).", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── CLIENT SIGNATURE ────────────────────────────────
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Client Signature")
        client_name     = st.text_input("Printed Name", key="c_name")
        client_position = st.text_input("Position",     key="c_pos")
        client_date     = st.date_input("Date",         key="c_date")
        client_canvas   = st_canvas(
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=120, width=400,
            drawing_mode="freedraw",
            key="c_canvas"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── GENERATE & DOWNLOAD & EMAIL ─────────────────────
    if st.button("📄 Generate PDF"):
        if not client_name.strip() or client_canvas.image_data is None:
            st.error("⚠️ Please enter the client's name and draw their signature.")
        else:
            # load & encode images
            with open("logo.png","rb") as f: logo_b64 = base64.b64encode(f.read()).decode()
            with open("kt.png","rb")  as f: kt_b64   = base64.b64encode(f.read()).decode()
            fields = {
                "logo_b64": logo_b64,
                "kt_b64": kt_b64,
                "company_name": company_name,
                "address": address,
                "reg_no": reg_no,
                "supply_of": supply_of,
                "site_location": site_location,
                "start_date": start_date.strftime("%B %Y"),
                "rates": rates,
                "terms": terms,
                "client_name": client_name,
                "client_position": client_position,
                "client_date": client_date.strftime("%d/%m/%Y"),
                "signer_name": "Keenan Thomas",
                "signer_position": "Managing Director",
                "signer_date": "13/06/2025",
            }
            pdf_bytes = generate_pdf_bytes(fields, client_canvas.image_data)
            st.session_state["pdf"] = pdf_bytes
            st.session_state["company"] = company_name
            st.success("✅ PDF is ready!")

    if "pdf" in st.session_state:
        st.download_button(
            "⬇️ Download Supply Agreement PDF",
            data=st.session_state["pdf"],
            file_name=f"supply_agreement_{st.session_state['company']}.pdf",
            mime="application/pdf"
        )
        subject = f"New Supply Agreement – {st.session_state['company']}".replace(" ", "%20")
        body = (
            "Hello,%0A%0A"
            f"Please find attached the Supply Agreement for {st.session_state['company']}.%0A%0A"
            "Best regards,%0APRLSiteSolutions"
        )
        mailto = f"mailto:info@prlsitesolutions.co.uk?subject={subject}&body={body}"
        st.markdown(
            f'<a href="{mailto}" style="display:inline-block; margin-top:10px; '
            'padding:0.6em 1em; background:#00aaff; color:#fff; border-radius:6px; '
            'text-decoration:none;">✉️ Compose Email</a>',
            unsafe_allow_html=True
        )
        st.caption("👉 Remember to attach the downloaded PDF in your mail client before sending.")

if __name__ == "__main__":
    main()
