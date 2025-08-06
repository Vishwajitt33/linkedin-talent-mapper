
import streamlit as st
from linkedin_talent_mapper import run_tool

st.set_page_config(page_title="LinkedIn Talent Mapper", layout="centered")

st.title("🔎 LinkedIn Talent Mapper")
st.markdown("Map engineering talent from any company on LinkedIn (India-based only).")

with st.form("talent_form"):
    company = st.text_input("Enter Company Name (e.g. Google)")
    username = st.text_input("LinkedIn Email", type="default")
    password = st.text_input("LinkedIn Password", type="password")
    submit = st.form_submit_button("Run Talent Mapper")

if submit:
    with st.spinner("Scraping LinkedIn... please wait 30–60 seconds."):
        try:
            run_tool(company, username, password)
            st.success("Talent map generated!")
            with open("Talent_Map.xlsx", "rb") as f:
                st.download_button("📥 Download Excel", f, file_name="Talent_Map.xlsx")
        except Exception as e:
            st.error(f"Error: {str(e)}")
