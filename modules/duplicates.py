import streamlit as st

def analyze_duplicates(df):

    duplicates = df.duplicated().sum()
    percent = round(duplicates / len(df) * 100, 2)

    st.subheader("Duplicate Detection")
    st.write(f"Duplicate Rows: {duplicates} ({round(percent,2)}%)")

    return {
        "duplicate_percent": percent
    }