from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import io
import json
from pathlib import Path
from ydata_profiling import ProfileReport
from fpdf import FPDF

# Import your existing pure modules
from modules.missing_values import analyze_missing
from modules.duplicates import analyze_duplicates
from modules.outliers import analyze_outliers
from modules.inconsistency import detect_inconsistencies
from modules.imbalance import detect_imbalance
from modules.correlation import correlation_analysis
from modules.quality_score import compute_quality_score
from modules.cleaning_manual import manual_clean_dataset
from modules.cleaning_auto import auto_clean_dataset

app = FastAPI(title="Dataset Analyser API")

# Store report paths for download
stored_reports = {}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Dataset Analyser API! The server is running successfully. You can test endpoints at http://localhost:8000/docs"}

# ==================== MANUAL ANALYSIS ENDPOINTS ====================

@app.post("/analyze")
async def analyze_dataset(file: UploadFile = File(...)):
    """
    Manual data quality analysis endpoint.
    Returns comprehensive quality metrics.
    """
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
        
    # Run modular functions
    missing = analyze_missing(df)
    duplicates = analyze_duplicates(df)
    outliers = analyze_outliers(df)
    inconsistencies = detect_inconsistencies(df)
    imbalance = detect_imbalance(df)
    correlation = correlation_analysis(df)
    
    score = compute_quality_score(missing, duplicates, outliers, len(inconsistencies))
    
    return {
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_metrics": missing,
        "duplicate_metrics": duplicates,
        "outlier_metrics": outliers,
        "inconsistencies": inconsistencies,
        "imbalance_metrics": imbalance,
        "correlation": correlation,
        "quality_score": score
    }

@app.post("/analyze/download")
async def download_manual_report(file: UploadFile = File(...)):
    """
    Download manual analysis report as JSON.
    """
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
        
    # Run modular functions
    missing = analyze_missing(df)
    duplicates = analyze_duplicates(df)
    outliers = analyze_outliers(df)
    inconsistencies = detect_inconsistencies(df)
    imbalance = detect_imbalance(df)
    correlation = correlation_analysis(df)
    
    score = compute_quality_score(missing, duplicates, outliers, len(inconsistencies))
    
    report_data = {
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_metrics": missing,
        "duplicate_metrics": duplicates,
        "outlier_metrics": outliers,
        "inconsistencies": inconsistencies,
        "imbalance_metrics": imbalance,
        "correlation": correlation,
        "quality_score": score
    }
    
    # Create JSON file for download
    report_json = json.dumps(report_data, indent=2, default=str)
    report_filename = f"manual_report_{Path(file.filename).stem}.json"
    report_path = Path(f"temp_{report_filename}")
    
    with open(report_path, 'w') as f:
        f.write(report_json)
    
    return FileResponse(report_path, media_type='application/json', filename=report_filename)

@app.post("/analyze/download/pdf")
async def download_manual_report_pdf(file: UploadFile = File(...)):
    """
    Download manual analysis report as PDF.
    """
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
        
    # Run modular functions
    missing = analyze_missing(df)
    duplicates = analyze_duplicates(df)
    outliers = analyze_outliers(df)
    inconsistencies = detect_inconsistencies(df)
    
    score = compute_quality_score(missing, duplicates, outliers, len(inconsistencies))
    
    report_filename = f"manual_report_{Path(file.filename).stem}.pdf"
    report_path = Path(f"temp_{report_filename}")
    
    # Generate PDF using fpdf2
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Data Quality Analysis Report", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f"Dataset: {file.filename}", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Total Rows: {int(df.shape[0])}", ln=True)
    pdf.cell(0, 10, f"Total Columns: {int(df.shape[1])}", ln=True)
    pdf.cell(0, 10, f"Quality Score: {score}/10", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Missing Values", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Missing Count: {missing.get('missing_count', 0)}", ln=True)
    pdf.cell(0, 10, f"Missing Percent: {missing.get('missing_percent', 0.0)}%", ln=True)
    pdf.ln(5)

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Duplicates", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Duplicate Count: {duplicates.get('duplicate_count', 0)}", ln=True)
    pdf.cell(0, 10, f"Duplicate Percent: {duplicates.get('duplicate_percent', 0.0)}%", ln=True)
    pdf.ln(5)

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Outliers", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Overall Outlier Ratio: {outliers.get('outlier_ratio', 0.0)}%", ln=True)
    pdf.ln(5)

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Inconsistencies", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Detected Patterns: {len(inconsistencies)}", ln=True)
    
    pdf.output(str(report_path))
    
    return FileResponse(report_path, media_type='application/pdf', filename=report_filename)

# ==================== AUTOMATED PROFILING ENDPOINTS ====================

@app.post("/profile")
async def profile_dataset(file: UploadFile = File(...)):
    """
    Automated data profiling using ydata-profiling.
    Returns profile report as HTML report status.
    """
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
    
    try:
        # Generate profile report
        profile = ProfileReport(df, title=f"Data Profile Report - {file.filename}", minimal=False)
        
        # Store report for later download
        report_id = Path(file.filename).stem
        stored_reports[report_id] = profile
        
        # Get summary stats from profile
        summary = {
            "filename": file.filename,
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "missing_cells": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "numeric_columns": int(df.select_dtypes(include=['number']).shape[1]),
            "categorical_columns": int(df.select_dtypes(include=['object']).shape[1]),
            "report_id": report_id,
            "status": "Profile generated successfully"
        }
        
        return summary
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.get("/profile/download/{report_id}")
async def download_profile_report(report_id: str):
    """
    Download the profile report as HTML.
    """
    if report_id not in stored_reports:
        return JSONResponse(status_code=404, content={"error": "Report not found"})
    
    profile = stored_reports[report_id]
    
    # Generate HTML report
    report_filename = f"data_profile_{report_id}.html"
    report_path = Path(f"temp_{report_filename}")
    
    profile.to_file(str(report_path))
    
    return FileResponse(report_path, media_type='text/html', filename=report_filename)

@app.post("/profile/download")
async def download_profile_report_direct(file: UploadFile = File(...)):
    """
    Generate and download profile report directly as HTML.
    """
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
    
    try:
        # Generate profile report
        profile = ProfileReport(df, title=f"Data Profile Report - {file.filename}", minimal=False)
        
        # Generate HTML report
        report_filename = f"data_profile_{Path(file.filename).stem}.html"
        report_path = Path(f"temp_{report_filename}")
        
        profile.to_file(str(report_path))
        
        return FileResponse(report_path, media_type='text/html', filename=report_filename)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# ==================== DATA CLEANING ENDPOINTS ====================

@app.post("/clean/manual")
async def clean_manual(file: UploadFile = File(...), config: str = Form(...)):
    """
    Apply manual cleaning based on the config JSON string.
    """
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
        
    config_dict = json.loads(config)
    cleaned_df = manual_clean_dataset(df, config_dict)
    
    cleaned_filename = f"cleaned_{file.filename}"
    cleaned_path = Path(f"temp_{cleaned_filename}")
    
    if file.filename.endswith('.csv'):
        cleaned_df.to_csv(cleaned_path, index=False)
        media_type = 'text/csv'
    else:
        cleaned_df.to_excel(cleaned_path, index=False)
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return FileResponse(cleaned_path, media_type=media_type, filename=cleaned_filename)

@app.post("/clean/auto")
async def clean_auto(file: UploadFile = File(...), target_col: str = Form("None")):
    """
    Apply automated PyCaret cleaning.
    """
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
        
    cleaned_df = auto_clean_dataset(df, target_col)
    
    cleaned_filename = f"autocleaned_{file.filename}"
    cleaned_path = Path(f"temp_{cleaned_filename}")
    
    if file.filename.endswith('.csv'):
        cleaned_df.to_csv(cleaned_path, index=False)
        media_type = 'text/csv'
    else:
        cleaned_df.to_excel(cleaned_path, index=False)
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return FileResponse(cleaned_path, media_type=media_type, filename=cleaned_filename)
