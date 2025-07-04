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
    Render the Jinja2 HTML template to PDF bytes,
    embedding both the PRL signature and the blank client box.
    """
    # Create a blank white image for client signature
    blank_img = Image.new("RGB", (400, 120), "white")
    buf = io.BytesIO()
    blank_img.save(buf, format="PNG")
    client_sig_b64 = base64.b64encode(buf.getvalue()).decode()

    # Add it into our template context
    fields["client_sig_b64"] = client_sig_b64

    # Render HTML
    env  = Environment(loader=FileSystemLoader("."))
    tpl  = env.get_template("template.html")
    html = tpl.render(**fields)

    # Convert to PDF via wkhtmltopdf
    config  = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
    options = {"enable-local-file-access": None}
    return pdfkit.from_string(html, False, configuration=config, options=options)


def main():
    st.set_page_config(page_title="Supply Agreement", layout="wide")

    # --- global styling + Roboto font omitted for brevity (keep your existing CSS) ---

    # HEADER
    with st.container():
        cols = st.columns([1,4])
        with cols[0]:
            st.image(f"data:image/png;base64,{logo_b64}", width=80)
        with cols[1]:
            st.markdown("## SUPPLY AGREEMENT")
            st.write(
                "This agreement is issued in conjunction with our Terms of Business.\n"
                "Contact us on **0800 772 3959** or email **info@prlsitesolutions.co.uk**."
            )

    # YOUR DETAILS
    with st.container():
        st.markdown("### Your Details")
        company_name = st.text_input("Company Name", "PRL Site Solutions")
        address      = st.text_area ("Address",      "18 Beryl Rd, Birkenhead, Prenton CH43 9RT", height=80)
        reg_no       = st.text_input("Company Reg No", "14358717")

    # SUPPLY DETAILS
    with st.container():
        st.markdown("### Supply Details")
        supply_of     = st.text_input("For the Supply of",    "Bolting Technicians (Flange Techs)")
        site_location = st.text_input("Site Location",        "UK Wide")
        start_date    = st.date_input("Start Date")

    # CHARGE RATES
    df_rates = pd.DataFrame({
        "Description": [
            "Basic Rate (Day)", "Basic Rate (Night)",
            "Overtime Rate (1)", "Overtime Rate (2)",
            "Expenses", "Lodge"
        ],
        "Rate": ["£29.90","£38.87","£42.90","£50.96","£–","£60"],
        "Basis": ["Per Hour"]*4 + ["Per Day",""]
    })
    st.markdown("### Our Charge Rates")
    try:
        rates_df = st.data_editor(df_rates, num_rows="fixed", key="rates")
    except:
        rates_df = st.experimental_data_editor(df_rates, num_rows="fixed", key="rates")
    rates = list(rates_df.itertuples(index=False, name=None))

    # BREAKDOWN
    df_bd = pd.DataFrame({
        "Breakdown": [
            "First 40 hrs Mon–Fri (including breaks)",
            "After 40 hrs Mon–Fri & all hrs Saturday",
            "All hrs Sunday"
        ]
    })
    st.markdown("### Breakdown")
    try:
        bd_df = st.data_editor(df_bd, num_rows="fixed", key="breakdown")
    except:
        bd_df = st.experimental_data_editor(df_bd, num_rows="fixed", key="breakdown")
    breakdown = bd_df["Breakdown"].tolist()

    # ADDITIONAL INFO
    terms = st.text_area("### Additional Information",
                         "Breaks to be paid (15 min, 30 min, 15 min).", height=80)

    # PRL SIGNATURE DATE
    prl_date = datetime.today().strftime("%d/%m/%Y")

    # GENERATE
    if st.button("📄 Generate PDF"):
        fields = {
            "logo_b64":       logo_b64,
            "kt_b64":         kt_b64,
            "company_name":   company_name,
            "address":        address.replace("\n","<br/>"),
            "reg_no":         reg_no,
            "supply_of":      supply_of,
            "site_location":  site_location,
            "start_date":     start_date.strftime("%B %Y"),
            "rates":          rates,
            "breakdown":      breakdown,
            "terms":          terms.replace("\n","<br/>"),
            "signer_name":    "Keenan Thomas",
            "signer_position":"Managing Director",
            "signer_date":    prl_date
        }
        try:
            pdf_bytes = generate_pdf_bytes(fields)
        except Exception as e:
            st.error("❌ PDF generation failed:")
            st.error(f"• {type(e).__name__}: {e}")
            return

        st.session_state["pdf"]     = pdf_bytes
        st.session_state["company"] = company_name
        st.success("✅ PDF is ready!")

    # DOWNLOAD / EMAIL
    if "pdf" in st.session_state:
        st.download_button(
            "⬇️ Download PDF",
            data=st.session_state["pdf"],
            file_name=f"supply_agreement_{st.session_state['company']}.pdf",
            mime="application/pdf"
        )
        mailto = (
            "mailto:info@prlsitesolutions.co.uk"
            f"?subject=New%20Supply%20Agreement%20–%20{st.session_state['company']}"
            "&body=Please%20see%20attached%20agreement."
        )
        st.markdown(f'[✉️ Compose Email]({mailto})', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
