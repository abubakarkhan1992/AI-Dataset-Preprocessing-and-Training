import streamlit as st
import pandas as pd
import io
# Import the logic directly from your main.py file
from main import run_analysis_logic 

st.set_page_config(page_title="AI Dataset Preprocessor", layout="wide")

st.title("📊 AI Dataset Preprocessing & Training")
st.write("Upload your dataset to analyze and clean it instantly.")

uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Read the file into a DataFrame
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    if st.button("Run Full Analysis"):
        with st.spinner("Analyzing data..."):
            # CALL LOGIC DIRECTLY (No HTTP requests needed)
            results = run_analysis_logic(df, uploaded_file.name)
            
            # Display Results
            col1, col2, col3 = st.columns(3)
            col1.metric("Quality Score", f"{results['quality_score']}/10")
            col2.metric("Rows", results['rows'])
            col3.metric("Columns", results['columns'])

            st.write("### Missing Values")
            st.json(results['missing_metrics'])

            st.write("### Outliers Detected")
            st.json(results['outlier_metrics'])

    st.sidebar.header("Settings")
    target_col = st.sidebar.selectbox("Select Target Column", options=["None"] + list(df.columns))
    
    if st.sidebar.button("Auto-Clean Dataset"):
        if target_col == "None":
            st.error("Please select a target column first.")
        else:
            from main import auto_clean_dataset
            cleaned_df = auto_clean_dataset(df, target_col)
            st.success("Cleaning complete!")
            st.dataframe(cleaned_df.head())
            
            # Download button for the result
            csv = cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Cleaned CSV", data=csv, file_name="cleaned_data.csv", mime="text/csv")
