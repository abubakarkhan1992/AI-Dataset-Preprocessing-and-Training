import streamlit as st
import pandas as pd

# Standard imports for your logic
try:
    from main import run_analysis_logic, auto_clean_dataset
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.info("Ensure main.py and the 'modules' folder are in the same directory as app.py")
    st.stop()

st.set_page_config(page_title="AI Dataset Preprocessor", layout="wide")

st.title("📊 AI Dataset Preprocessing")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    # Handle file reading
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.subheader("Data Preview")
    st.dataframe(df.head())

    # Example Analysis Call
    if st.button("Run Full Analysis"):
        with st.spinner("Processing..."):
            results = run_analysis_logic(df, uploaded_file.name)
            st.success("Analysis Complete!")
            st.write(results)
