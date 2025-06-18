import io
import base64

import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# ReportLab imports
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

# ─── Load & encode static images ────────────────────────
with open("logo.png", "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()
with open("kt.png", "rb") as f:
    kt_b64 = base64.b64encode(f.read()).decode()

def generate_pdf_bytes(fields, sig_data):
    """Build a PDF entirely with ReportLab and return bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"], alignment=1, fontSize=18, spaceAfter=6
    )
    normal = styles["BodyText"]
    normal.spaceAfter = 6

    story = []

    # ── HEADER ──
    # Logo
    logo_data = base64.b64decode(fields["logo_b64"])
    logo_buf = io.BytesIO(logo_data)
    logo = RLImage(logo_buf, width=40*mm, height=None)
    story.append(logo)

    # Title
    story.append(Paragraph("SUPPLY AGREEMENT", title_style))
    story.append(Spacer(1, 4*mm))

    # Intro
    intro = (
        "This agreement is issued in conjunction with our Terms of Business. "
        "Please contact us on <b>0800 772 3959</b> or email "
        "<b>info@prlsitesolutions.co.uk</b> if you have any queries."
    )
    story.append(Paragraph(intro, normal))
    story.append(Spacer(1, 6*mm))

    # ── DETAILS TABLE ──
    details_data = [
        ["<b>Your Details</b>", "", "<b>Supply Details</b>", ""],
        ["Company Name:", fields["company_name"], "For the Supply of:", fields["supply_of"]],
        ["Address:", fields["address"].replace("\n", "<br/>"), "Site Location:", fields["site_location"]],
        ["Company Reg No:", fields["reg_no"], "Start Date:", fields["start_date"]],
    ]
    tbl = Table(details_data, colWidths=[40*mm, 70*mm, 40*mm, 40*mm])
    tbl.setStyle(TableStyle([
        ("SPAN", (0,0), (1,0)), ("SPAN", (2,0), (3,0)),
        ("BACKGROUND", (0,0), (3,0), colors.lightgrey),
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6*mm))

    # ── RATES TABLE ──
    rates_header = ["Description", "Rate", "Basis"]
    rates_rows = [rates_header] + [list(r) for r in fields["rates"]]
    rates_tbl = Table(rates_rows, colWidths=[60*mm, 30*mm, 30*mm])
    rates_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(Paragraph("<b>Our Charge Rates</b>", normal))
    story.append(rates_tbl)
    story.append(Spacer(1, 6*mm))

    # ── BREAKDOWN TABLE ──
    breakdown = [
        ["<b>BREAKDOWN</b>"],
        ["First 40 hours Mon–Fri (including breaks)"],
        ["After 40 hours Mon–Fri and all hours Saturday"],
        ["All hours Sunday"],
    ]
    bd_tbl = Table(breakdown, colWidths=[120*mm])
    bd_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(bd_tbl)
    story.append(Spacer(1, 6*mm))

    # ── ADDITIONAL INFO ──
    story.append(Paragraph("<b>Additional Information</b>", normal))
    story.append(Paragraph(fields["terms"].replace("\n", "<br/>"), normal))
    story.append(Spacer(1, 10*mm))

    # ── SIGNATURES ──
    # PRL signature
    kt_data = base64.b64decode(fields["kt_b64"])
    kt_buf = io.BytesIO(kt_data)
    prl_sig = RLImage(kt_buf, width=50*mm, height=None)

    # Client signature from array
    arr = sig_data.astype("uint8")
    im = Image.fromarray(arr, "RGBA").convert("RGB")
    client_buf = io.BytesIO()
    im.save(client_buf, format="PNG")
    client_buf.seek(0)
    client_sig = RLImage(client_buf, width=50*mm, height=None)

    sig_table = Table([
        [
            [prl_sig,
             Paragraph(f"Signed by: {fields['signer_name']}", normal),
             Paragraph(f"Position: {fields['signer_position']}", normal),
             Paragraph(f"Date: {fields['signer_date']}", normal)],
            [client_sig,
             Paragraph(f"Signed by: {fields['client_name']}", normal),
             Paragraph(f"Position: {fields['client_position']}", normal),
             Paragraph(f"Date: {fields['client_date']}", normal)],
        ]
    ], colWidths=[80*mm, 80*mm])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(sig_table)

    # Build PDF
    doc.build(story)
    return buffer.getvalue()

def main():
    st.set_page_config(page_title="PRL Site Solutions – Supply Agreement", layout="wide")

    # ─── Global CSS Styling ───────────────────────────────
    st.markdown("""<style>
      @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
      * { font-family: 'Roboto', sans-serif !important; }
      .stApp .block-container {
        padding-top: 80px !important; max-width: 760px; margin: auto;
      }
      .header-card, .section-card {
        background: #1f1f1f; padding: 20px; margin-bottom: 30px;
        border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.5);
      }
      .header-card h2, .section-card h2 {
        color: #00d1ff; margin-top: 0;
      }
      .stTextInput>div>input, .stTextArea>div>textarea {
        background: #2a2a2a !important; border: 1px solid #444 !important;
        border-radius: 6px !important; color: #eee !important;
      }
      .stButton>button {
        background: #00aaff !important; color: #fff !important;
        border-radius: 6px !important; padding: 0.6em 1em !important;
        font-weight: 600 !important;
      }
      .stButton>button:hover { background: #008fcc !important; }
    </style>""", unsafe_allow_html=True)

    # … the rest of your UI code is identical to before …
    # [Collect company_name, address, rates_df, client_canvas, etc.]

    if st.button("📄 Generate PDF"):
        # … validation …
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

    # … download_button & mailto link as before …

if __name__ == "__main__":
    main()
