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
with open("kt.jpg", "rb") as f:
    kt_b64 = base64.b64encode(f.read()).decode()

def generate_pdf_bytes(fields):
    """Render the Jinja2 HTML template to PDF bytes, with a blank signature box."""
    # Generate a blank white PNG for the client signature
    blank = Image.new("RGB", (400, 120), "white")
    buf = io.BytesIO()
    blank.save(buf, format="PNG")
    client_sig_b64 = base64.b64encode(buf.getvalue()).decode()

    # Render HTML
    env = Environment(loader=FileSystemLoader("."))
    tpl = env.get_template("template.html")
    html = tpl.render(**fields, client_sig_b64=client_sig_b64)

    # HTML → PDF: point at the Linux wkhtmltopdf binary
    config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
    options = {"enable-local-file-access": None}
    return pdfkit.from_string(html, False, configuration=config, options=options)

def main():
    st.set_page_config(page_title="PRL Site Solutions – Supply Agreement", layout="wide")

    # ─── Global CSS: Roboto + Card Styling ─────────────────
    st.markdown("""<style>
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
    </style>""", unsafe_allow_html=True)

    # ─── HEADER ─────────────────────────────────────────────
    with st.container():
        st.markdown("<div class='header-card'>", unsafe_allow_html=True)
        cols = st.columns([1, 4])
        with cols[0]:
            st.image(f"data:image/png;base64,{logo_b64}", width=80)
        with cols[1]:
            st.markdown("## SUPPLY AGREEMENT")
            st.write(
                "This agreement is issued in conjunction with our Terms of Business.  \n"
                "Please contact us on **0800 772 3959** or email **info@prlsitesolutions.co.uk** if you have any queries."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── YOUR DETAILS ───────────────────────────────────────
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Your Details")
        company_name = st.text_input("Company Name", "PRL Site Solutions")
        address      = st.text_area("Address", "18 Beryl Rd, Birkenhead, Prenton CH43 9RT", height=80)
        reg_no       = st.text_input("Company Reg No", "14358717")
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── SUPPLY DETAILS ─────────────────────────────────────
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Supply Details")
        supply_of     = st.text_input("For the Supply of", "Bolting Technicians (Flange Techs)")
        site_location = st.text_input("Site Location", "UK Wide")
        start_date    = st.date_input("Start Date")
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── CHARGE RATES ───────────────────────────────────────
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Our Charge Rates")
        default_rates = {
            "Description": [
                "Basic Rate (Day)", "Basic Rate (Night)",
                "Overtime Rate (1)", "Overtime Rate (2)",
                "Expenses", "Lodge"
            ],
            "Rate": ["£29.90", "£38.87", "£42.90", "£50.96", "£–", "£60"],
            "Basis": ["Per Hour", "Per Hour", "Per Hour", "Per Hour", "Per Day", ""]
        }
        df_rates = pd.DataFrame(default_rates)
        try:
            rates_df = st.data_editor(df_rates, num_rows="fixed", key="rates")
        except:
            rates_df = st.experimental_data_editor(df_rates, num_rows="fixed", key="rates")
        rates = list(rates_df.itertuples(index=False, name=None))
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── ADDITIONAL INFO ────────────────────────────────────
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## Additional Information")
        terms = st.text_area("Notes (e.g., breaks)", "Breaks to be paid (15 min, 30 min, 15 min).", height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── PRL SIGNATURE ───────────────────────────────────────
    prl_date = datetime.today().strftime("%d/%m/%Y")
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("## PRL Signature")
        st.write(f"Date: {prl_date}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── GENERATE & DOWNLOAD & EMAIL LINK ──────────────────
    if st.button("📄 Generate PDF"):
        fields = {
            "logo_b64":       logo_b64,
            "kt_b64":         kt_b64,
            "company_name":   company_name,
            "address":        address.replace("\n", "<br/>"),
            "reg_no":         reg_no,
            "supply_of":      supply_of,
            "site_location":  site_location,
            "start_date":     start_date.strftime("%B %Y"),
            "rates":          rates,
            "terms":          terms.replace("\n", "<br/>"),
            "signer_name":    "Keenan Thomas",
            "signer_position":"Managing Director",
            "signer_date":    prl_date
        }

        try:
            pdf_bytes = generate_pdf_bytes(fields)
        except Exception as err:
            st.error("❌ PDF generation failed:")
            st.error(f"  • {type(err).__name__}: {err}")
            return

        st.session_state["pdf"]     = pdf_bytes
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
