import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import io
from pathlib import Path

from modules.load_and_preview import load_data, show_preview

FASTAPI_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Dataset Quality Auditor", layout="wide")
st.title("🔍 AI Dataset Quality Auditor")

# Initialize session state for persistent results
if "manual_results" not in st.session_state:
    st.session_state.manual_results = None
if "profile_results" not in st.session_state:
    st.session_state.profile_results = None
if "current_df" not in st.session_state:
    st.session_state.current_df = None

# Sidebar upload
uploaded_file = st.sidebar.file_uploader("Upload Dataset", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.session_state.current_df = df
        st.success("✅ Dataset Loaded Successfully")
        show_preview(df, uploaded_file)
        
        # ==================== Analysis Options ====================
        st.subheader("📊 Analysis Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Manual Quality Analysis", key="manual_btn"):
                with st.spinner("Analyzing dataset with manual quality checks..."):
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), 
                             "text/csv" if uploaded_file.name.endswith('.csv') else 
                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                    
                    try:
                        response = requests.post(f"{FASTAPI_URL}/analyze", files=files)
                        response.raise_for_status()
                        st.session_state.manual_results = response.json()
                        st.success("✅ Manual analysis complete!")
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Failed to connect to backend: {e}")
                        st.session_state.manual_results = None
        
        with col2:
            if st.button("📈 Automated Profiling (ydata)", key="profile_btn"):
                with st.spinner("Generating automated data profile..."):
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), 
                             "text/csv" if uploaded_file.name.endswith('.csv') else 
                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                    
                    try:
                        response = requests.post(f"{FASTAPI_URL}/profile", files=files)
                        response.raise_for_status()
                        st.session_state.profile_results = response.json()
                        st.success("✅ Automated profiling complete!")
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Failed to generate profile: {e}")
                        st.session_state.profile_results = None
        
        # ==================== Tab System ====================
        tab1, tab2 = st.tabs(["📋 Manual Analysis", "📊 Automated Profile"])
        
        # ==================== TAB 1: MANUAL ANALYSIS ====================
        with tab1:
            if st.session_state.manual_results:
                results = st.session_state.manual_results
                
                # Download button for manual report
                col_dl1, col_dl2, col_dl3 = st.columns([2, 2, 4])
                with col_dl1:
                    if st.button("⬇️ Download JSON Report", key="dl_manual"):
                        try:
                            uploaded_file.seek(0)
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), 
                                     "text/csv" if uploaded_file.name.endswith('.csv') else 
                                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                            response = requests.post(f"{FASTAPI_URL}/analyze/download", files=files)
                            response.raise_for_status()
                            st.download_button(
                                label="💾 Save JSON Report",
                                data=response.content,
                                file_name=f"manual_report_{Path(uploaded_file.name).stem}.json",
                                mime="application/json"
                            )
                        except requests.exceptions.RequestException as e:
                            st.error(f"❌ Failed to download report: {e}")
                
                with col_dl2:
                    if st.button("⬇️ Download PDF Report", key="dl_manual_pdf"):
                        try:
                            uploaded_file.seek(0)
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), 
                                     "text/csv" if uploaded_file.name.endswith('.csv') else 
                                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                            response = requests.post(f"{FASTAPI_URL}/analyze/download/pdf", files=files)
                            response.raise_for_status()
                            st.download_button(
                                label="💾 Save PDF Report",
                                data=response.content,
                                file_name=f"manual_report_{Path(uploaded_file.name).stem}.pdf",
                                mime="application/pdf"
                            )
                        except requests.exceptions.RequestException as e:
                            st.error(f"❌ Failed to download PDF report: {e}")
                
                st.header("📊 Data Quality Analysis Results")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Total Rows", results["rows"])
                with col2:
                    st.metric("📋 Total Columns", results["columns"])
                with col3:
                    st.metric("⚠️ Quality Score", f"{results['quality_score']}/10")
                with col4:
                    st.metric("🏆 Remarks", "Excellent" if results['quality_score'] >= 8 else 
                             "Good" if results['quality_score'] >= 7 else
                             "Average" if results['quality_score'] >= 6 else "Poor")
                
                st.divider()
                
                # Missing Values & Duplicates
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔍 Missing Values")
                    missing_df = pd.DataFrame({
                        "Count": results["missing_metrics"]["missing_count"],
                        "Percentage (%)": results["missing_metrics"]["missing_percent"]
                    })
                    missing_cols = missing_df[missing_df["Count"] > 0]
                    if len(missing_cols) > 0:
                        st.dataframe(missing_cols, use_container_width=True)
                    else:
                        st.success("✅ No missing values found!")
                
                with col2:
                    st.subheader("♻️ Duplicate Detection")
                    dupes = results["duplicate_metrics"]["duplicate_count"]
                    dupe_pct = results["duplicate_metrics"]["duplicate_percent"]
                    st.write(f"**Duplicate Rows:** {dupes} ({dupe_pct}%)")
                    
                    if dupes > 0 and st.session_state.current_df is not None:
                        if st.checkbox("Show duplicate rows", key="show_dupes"):
                            st.dataframe(st.session_state.current_df[st.session_state.current_df.duplicated(keep=False)]
                                       .sort_values(by=list(st.session_state.current_df.columns)).head(50),
                                       use_container_width=True)
                    elif dupes == 0:
                        st.success("✅ No duplicates found!")
                
                st.divider()
                
                # Outliers & Inconsistencies
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Outlier Detection")
                    outliers = results["outlier_metrics"]["outlier_counts"]
                    outlier_ratio = results["outlier_metrics"]["outlier_ratio"]
                    if outliers:
                        st.write(f"**Overall Outlier Ratio:** {round(outlier_ratio, 2)}%")
                        outlier_df = pd.DataFrame([outliers]).T.rename(columns={0: "Count"})
                        st.dataframe(outlier_df.sort_values("Count", ascending=False), use_container_width=True)
                    else:
                        st.info("ℹ️ No numerical outliers detected")
                
                with col2:
                    st.subheader("⚙️ Data Inconsistencies")
                    inconsistencies = results["inconsistencies"]
                    if inconsistencies:
                        inc_df = pd.DataFrame(inconsistencies)
                        st.dataframe(inc_df, use_container_width=True)
                    else:
                        st.success("✅ No inconsistencies detected!")
                
                st.divider()
                
                # Class Imbalance
                st.subheader("⚖️ Class Imbalance Detection")
                imbalances = results["imbalance_metrics"]
                if imbalances:
                    target_col = st.selectbox("Select Target Column", ["None"] + list(imbalances.keys()), key="imbalance_select")
                    
                    if target_col != "None":
                        data = imbalances[target_col]
                        st.write(f"**Max class percentage:** {data['imbalance_score']}%")
                        
                        count_df = pd.DataFrame({
                            "Class": list(data["counts"].keys()),
                            "Count": list(data["counts"].values()),
                            "Percentage (%)": list(data["percentages"].values())
                        })
                        col_chart, col_table = st.columns([1.5, 1])
                        with col_chart:
                            st.bar_chart(count_df.set_index("Class")["Count"])
                        with col_table:
                            st.dataframe(count_df, use_container_width=True)
                else:
                    st.info("ℹ️ No categorical columns found for imbalance analysis")
                
                st.divider()
                
                # Correlation Matrix
                st.subheader("🔗 Correlation Matrix")
                matrix = results["correlation"]["matrix"]
                if matrix:
                    corr_df = pd.DataFrame(matrix)
                    fig, ax = plt.subplots(figsize=(10, 8))
                    sns.heatmap(corr_df, cmap="coolwarm", annot=True, fmt=".2f", ax=ax, 
                               cbar_kws={"label": "Correlation"})
                    st.pyplot(fig)
                else:
                    st.info("ℹ️ Not enough numeric columns for correlation analysis")
            else:
                st.info("📌 Click 'Manual Quality Analysis' to run the analysis")
        
        # ==================== TAB 2: AUTOMATED PROFILING ====================
        with tab2:
            if st.session_state.profile_results:
                prof_results = st.session_state.profile_results
                
                # Download button for profile report
                st.subheader("📥 Download Automated Profile Report")
                
                col_dl1, col_dl2, col_dl3 = st.columns([2, 2, 2])
                
                with col_dl1:
                    if st.button("⬇️ Download Profile (HTML)", key="dl_profile"):
                        try:
                            uploaded_file.seek(0)
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), 
                                     "text/csv" if uploaded_file.name.endswith('.csv') else 
                                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                            response = requests.post(f"{FASTAPI_URL}/profile/download", files=files)
                            response.raise_for_status()
                            st.download_button(
                                label="💾 Save HTML Report",
                                data=response.content,
                                file_name=f"data_profile_{Path(uploaded_file.name).stem}.html",
                                mime="text/html"
                            )
                            st.success("✅ Report ready for download!")
                        except requests.exceptions.RequestException as e:
                            st.error(f"❌ Failed to download profile: {e}")
                
                st.divider()
                
                st.header("📊 Automated Data Profiling Summary")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Rows", prof_results["rows"])
                with col2:
                    st.metric("📋 Columns", prof_results["columns"])
                with col3:
                    st.metric("⚠️ Missing Cells", prof_results["missing_cells"])
                with col4:
                    st.metric("♻️ Duplicates", prof_results["duplicate_rows"])
                
                st.divider()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🔢 Numeric Columns", prof_results["numeric_columns"])
                with col2:
                    st.metric("🏷️ Categorical Columns", prof_results["categorical_columns"])
                
                st.divider()
                
                st.subheader("📈 Detailed Profile Preview")
                st.info("💡 Click 'Download Profile (HTML)' to view the complete interactive profile report with detailed statistics, distributions, correlations, and more!")
                
                # Display data preview
                if st.session_state.current_df is not None:
                    st.subheader("📋 Dataset Preview")
                    st.dataframe(st.session_state.current_df.head(20), use_container_width=True)
                    
                    st.subheader("📊 Basic Statistics")
                    st.dataframe(st.session_state.current_df.describe(), use_container_width=True)
            else:
                st.info("📌 Click 'Automated Profiling (ydata)' to generate an automated profile report")
else:
    # Clear session state if a new file isn't uploaded
    st.session_state.manual_results = None
    st.session_state.profile_results = None
    st.session_state.current_df = None
    st.info("📤 Upload a dataset to begin analysis!")
