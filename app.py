import io
import base64

import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# ReportLab – pure-Python PDF generation
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
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        alignment=1, fontSize=18, spaceAfter=6
    )
    normal = styles["BodyText"]
    normal.spaceAfter = 6

    story = []

    # HEADER: logo + title + intro
    logo_data = base64.b64decode(fields["logo_b64"])
    logo_buf = io.BytesIO(logo_data)
    story.append(RLImage(logo_buf, width=40*mm))
    story.append(Paragraph("SUPPLY AGREEMENT", title_style))
    story.append(Spacer(1, 4*mm))
    intro = (
        "This agreement is issued in conjunction with our Terms of Business. "
        "Please contact us on <b>0800 772 3959</b> or email "
        "<b>info@prlsitesolutions.co.uk</b> if you have any queries."
    )
    story.append(Paragraph(intro, normal))
    story.append(Spacer(1, 6*mm))

    # DETAILS TABLE
    details = [
        ["<b>Your Details</b>", "", "<b>Supply Details</b>", ""],
        ["Company Name:", fields["company_name"], "For the Supply of:", fields["supply_of"]],
        ["Address:", fields["address"].replace("\n", "<br/>"), "Site Location:", fields["site_location"]],
        ["Company Reg No:", fields["reg_no"], "Start Date:", fields["start_date"]],
    ]
    tbl = Table(details, colWidths=[40*mm, 70*mm, 40*mm, 40*mm])
    tbl.setStyle(TableStyle([
        ("SPAN", (0,0), (1,0)), ("SPAN", (2,0), (3,0)),
        ("BACKGROUND", (0,0), (3,0), colors.lightgrey),
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6*mm))

    # RATES TABLE
    rates_rows = [["Description", "Rate", "Basis"]] + [list(r) for r in fields["rates"]]
    rates_tbl = Table(rates_rows, colWidths=[60*mm, 30*mm, 30*mm])
    rates_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(Paragraph("<b>Our Charge Rates</b>", normal))
    story.append(rates_tbl)
    story.append(Spacer(1, 6*mm))

    # BREAKDOWN
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

    # ADDITIONAL INFO
    story.append(Paragraph("<b>Additional Information</b>", normal))
    story.append(Paragraph(fields["terms"].replace("\n", "<br/>"), normal))
    story.append(Spacer(1, 10*mm))

    # SIGNATURES
    kt_data = base64.b64decode(fields["kt_b64"])
    kt_buf = io.BytesIO(kt_data)
    prl_sig = RLImage(kt_buf, width=50*mm)

    arr = sig_data.astype("uint8")
    img = Image.fromarray(arr, "RGBA").convert("RGB")
    client_buf = io.BytesIO()
    img.save(client_buf, format="PNG")
    client_buf.seek(0)
    client_sig = RLImage(client_buf, width=50*mm)

    sig_table = Table([
        [
            [prl_sig,
             Paragraph(f"Signed by: {fields['signer_name']}", normal),
             Paragraph(f"Position: {fields['signer_position']}", normal),
             Paragraph(f"Date: {fields['signer_date']}", normal)],
            [client_sig,
             Paragraph(f"Signed by: {fields['client_name']}", normal),
             Paragraph(f"Position: {fields['client_position']}", normal),
             Paragraph(f"Date: {fields['client_date']}", normal)]
        ]
    ], colWidths=[80*mm, 80*mm])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(sig_table)

    doc.build(story)
    return buffer.getvalue()

def main():
    st.set_page_config(page_title="PRL Site Solutions – Supply Agreement", layout="wide")

    # GLOBAL CSS
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
        border-radius:6px!important; padding:.6em 1em!important;
        font-weight:600!important;
      }
      .stButton>button:hover { background:#008fcc!important; }
    </style>
    """, unsafe_allow_html=True)

    # HEADER
    with st.container():
        st.markdown("<div class='header-card'>", unsafe_allow_html=True)
        cols = st.columns([1, 4])
        with cols[0]:
            st.image(f"data:image/png;base64,{logo_b64}", width=80)
        with cols[1]:
            st.markdown("## SUPPLY AGREEMENT")
            st.write(
                "This agreement is issued in conjunction with our Terms of Business.\n"
                "Please contact us on **0800 772 3959** or email **info@prlsitesolutions.co.uk** if you have any queries."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # YOUR DETAILS
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Your Details")
        company_name = st.text_input("Company Name", "PRL Site Solutions")
        address      = st.text_area("Address", "18 Beryl Rd, Birkenhead, Prenton CH43 9RT", height=80)
        reg_no       = st.text_input("Company Reg No", "14358717")
        st.markdown("</div>", unsafe_allow_html=True)

    # SUPPLY DETAILS
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Supply Details")
        supply_of     = st.text_input("For the Supply of", "Bolting Technicians (Flange Techs)")
        site_location = st.text_input("Site Location", "UK Wide")
        start_date    = st.date_input("Start Date")
        st.markdown("</div>", unsafe_allow_html=True)

    # CHARGE RATES
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Our Charge Rates")
        default_rates = {
            "Description": ["Basic Rate (Day)","Basic Rate (Night)",
                            "Overtime Rate (1)","Overtime Rate (2)",
                            "Expenses","Lodge"],
            "Rate": ["£29.90","£38.87","£42.90","£50.96","£–","£60"],
            "Basis": ["Per Hour","Per Hour","Per Hour","Per Hour","Per Day",""]
        }
        df_rates = pd.DataFrame(default_rates)
        try:
            rates_df = st.data_editor(df_rates, num_rows="fixed", key="rates")
        except:
            rates_df = st.experimental_data_editor(df_rates, num_rows="fixed", key="rates")
        rates = list(rates_df.itertuples(index=False, name=None))
        st.markdown("</div>", unsafe_allow_html=True)

    # ADDITIONAL INFO
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Additional Information")
        terms = st.text_area("Notes (e.g., breaks)", "Breaks to be paid (15 min, 30 min, 15 min).", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    # CLIENT SIGNATURE
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Client Signature")
        client_name     = st.text_input("Printed Name", key="c_name")
        client_position = st.text_input("Position",     key="c_pos")
        client_date     = st.date_input("Date",         key="c_date")
        client_canvas   = st_canvas(stroke_width=2, stroke_color="#000",
                                    background_color="#fff",
                                    height=120, width=400,
                                    drawing_mode="freedraw", key="c_canvas")
        st.markdown("</div>", unsafe_allow_html=True)

    # GENERATE & DOWNLOAD & EMAIL
    if st.button("📄 Generate PDF"):
        if not client_name.strip() or client_canvas.image_data is None:
            st.error("⚠️ Please enter the client's name and draw their signature.")
        else:
            fields = {
                "logo_b64": logo_b64, "kt_b64": kt_b64,
                "company_name": company_name, "address": address,
                "reg_no": reg_no, "supply_of": supply_of,
                "site_location": site_location,
                "start_date": start_date.strftime("%B %Y"),
                "rates": rates, "terms": terms,
                "client_name": client_name,
                "client_position": client_position,
                "client_date": client_date.strftime("%d/%m/%Y"),
                "signer_name": "Keenan Thomas",
                "signer_position": "Managing Director",
                "signer_date": "13/06/2025",
            }
            st.session_state["pdf"] = generate_pdf_bytes(fields, client_canvas.image_data)
            st.session_state["company"] = company_name
            st.success("✅ PDF is ready!")

    if "pdf" in st.session_state:
        pdf_data = st.session_state["pdf"]
        cname    = st.session_state["company"]

        st.download_button(
            "⬇️ Download Supply Agreement PDF",
            data=pdf_data,
            file_name=f"supply_agreement_{cname}.pdf",
            mime="application/pdf"
        )

        subject = f"New Supply Agreement – {cname}".replace(" ", "%20")
        body    = (
            "Hello,%0A%0A"
            f"Please find attached the Supply Agreement for {cname}.%0A%0A"
            "Best regards,%0APRLSiteSolutions"
        )
        mailto = f"mailto:info@prlsitesolutions.co.uk?subject={subject}&body={body}"

        st.markdown(
            f'<a href="{mailto}" style="display:inline-block;margin-top:10px;'
            'padding:0.6em 1em;background:#00aaff;color:#fff;border-radius:6px;'
            'text-decoration:none;">✉️ Compose Email</a>',
            unsafe_allow_html=True
        )
        st.caption("👉 Remember to attach the downloaded PDF in your mail client before sending.")

if __name__ == "__main__":
    main()
