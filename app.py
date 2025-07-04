import io
import base64
import pandas as pd
import streamlit as st
from PIL import Image
from jinja2 import Environment, FileSystemLoader
import pdfkit
from datetime import datetime

# ─── Load & encode static images ────────────────────────
with open("logo.png", "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()
with open("kt.png", "rb") as f:
    kt_b64 = base64.b64encode(f.read()).decode()

def generate_pdf_bytes(fields):
    """
    Render our Jinja2 template to PDF, embedding
    a blank white box for the client signature.
    """
    # Create blank white PNG (400×120px)
    blank = Image.new("RGB", (400, 120), "white")
    buf = io.BytesIO()
    blank.save(buf, format="PNG")
    fields["client_sig_b64"] = base64.b64encode(buf.getvalue()).decode()

    # Render HTML
    env  = Environment(loader=FileSystemLoader("."))
    tpl  = env.get_template("template.html")
    html = tpl.render(**fields)

    # Convert HTML → PDF
    config  = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
    options = {"enable-local-file-access": None}
    return pdfkit.from_string(html, False, configuration=config, options=options)


def main():
    st.set_page_config(page_title="Supply Agreement", layout="wide")

    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
      * { font-family: 'Roboto', sans-serif!important; }
      .stApp .block-container { max-width:800px; margin:auto; padding-top:60px; }
      .stButton>button { background:#005f8c;color:#fff;border-radius:5px;padding:0.5em 1em; }
      .stButton>button:hover{background:#004a6b;}
    </style>
    """, unsafe_allow_html=True)

    # Header
    cols = st.columns([1,4])
    with cols[0]:
        st.image(f"data:image/png;base64,{logo_b64}", width=80)
    with cols[1]:
        st.markdown("## SUPPLY AGREEMENT")
        st.write(
            "This agreement is issued in conjunction with our Terms of Business.\n"
            "Contact us on **0800 772 3959** or **info@prlsitesolutions.co.uk**."
        )

    # Your Details
    st.markdown("### Your Details")
    company_name = st.text_input("Company Name", "PRL Site Solutions")
    address      = st.text_area("Address", "18 Beryl Rd, Birkenhead, Prenton CH43 9RT", height=80)
    reg_no       = st.text_input("Company Reg No", "14358717")

    # Supply Details
    st.markdown("### Supply Details")
    supply_of     = st.text_input("For the Supply of",     "Bolting Technicians (Flange Techs)")
    site_location = st.text_input("Site Location",         "UK Wide")
    start_date    = st.date_input("Start Date")

    # Charge Rates
    st.markdown("### Our Charge Rates")
    default = {
      "Description": ["Basic Rate (Day)", "Basic Rate (Night)",
                      "Overtime Rate (1)", "Overtime Rate (2)",
                      "Expenses", "Lodge"],
      "Rate": ["£29.90","£38.87","£42.90","£50.96","£–","£60"],
      "Basis": ["Per Hour","Per Hour","Per Hour","Per Hour","Per Day",""]
    }
    df_rates  = pd.DataFrame(default)
    rates_df  = st.data_editor(df_rates, num_rows="fixed", key="rates")
    rates = list(rates_df.itertuples(index=False, name=None))

    # Breakdown (multi-line text area)
    st.markdown("### Breakdown")
    raw_bd = st.text_area("Enter one line per row:", 
        "First 40 hrs Mon–Fri (including breaks)\n"
        "After 40 hrs Mon–Fri & all hrs Saturday\n"
        "All hrs Sunday", height=100)
    breakdown = [row.strip() for row in raw_bd.split("\n") if row.strip()]

    # Additional Info
    terms = st.text_area("### Additional Information",
        "Breaks to be paid (15 min, 30 min, 15 min).", height=80)

    # PRL signature date
    prl_date = datetime.today().strftime("%d/%m/%Y")

    # Generate PDF
    if st.button("📄 Generate PDF"):
        fields = {
            "logo_b64":        logo_b64,
            "kt_b64":          kt_b64,
            "company_name":    company_name,
            "address":         address.replace("\n","<br/>"),
            "reg_no":          reg_no,
            "supply_of":       supply_of,
            "site_location":   site_location,
            "start_date":      start_date.strftime("%B %Y"),
            "rates":           rates,
            "breakdown":       breakdown,
            "terms":           terms.replace("\n","<br/>"),
            "signer_name":     "Keenan Thomas",
            "signer_position": "Managing Director",
            "signer_date":     prl_date
        }
        try:
            pdf = generate_pdf_bytes(fields)
            st.session_state["pdf"]     = pdf
            st.session_state["company"] = company_name
            st.success("✅ PDF ready!")
        except Exception as e:
            st.error(f"PDF generation failed: {e}")

    # Download & Email
    if "pdf" in st.session_state:
        st.download_button(
            "⬇️ Download PDF",
            st.session_state["pdf"],
            file_name=f"supply_agreement_{st.session_state['company']}.pdf",
            mime="application/pdf"
        )
        mailto = (
          "mailto:info@prlsitesolutions.co.uk"
          f"?subject=New%20Supply%20Agreement%20–%20{st.session_state['company']}"
          "&body=Please%20see%20attached%20agreement."
        )
        st.markdown(
          f'<a href="{mailto}" target="_blank" '
          'style="display:inline-block;margin-top:10px;'
          'padding:0.5em 1em;background:#005f8c;color:#fff;'
          'border-radius:5px;text-decoration:none;">✉️ Compose Email</a>',
          unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
