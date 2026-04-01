from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import io
import json
from pathlib import Path
from ydata_profiling import ProfileReport
from fpdf import FPDF

# Import your existing modules
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

# --- CORE LOGIC FUNCTIONS (Importable by Streamlit) ---

def run_analysis_logic(df, filename):
    missing = analyze_missing(df)
    duplicates = analyze_duplicates(df)
    outliers = analyze_outliers(df)
    inconsistencies = detect_inconsistencies(df)
    imbalance = detect_imbalance(df)
    correlation = correlation_analysis(df)
    score = compute_quality_score(missing, duplicates, outliers, len(inconsistencies))
    
    return {
        "filename": filename,
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

# --- API ENDPOINTS (For local use or external hosting) ---

@app.get("/")
def read_root():
    return {"message": "API is running. Use /docs for testing."}

@app.post("/analyze")
async def analyze_dataset(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents)) if file.filename.endswith('.csv') else pd.read_excel(io.BytesIO(contents))
    return run_analysis_logic(df, file.filename)

@app.post("/clean/auto")
async def clean_auto(file: UploadFile = File(...), target_col: str = Form("None")):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents)) if file.filename.endswith('.csv') else pd.read_excel(io.BytesIO(contents))
    
    if target_col == "None" or target_col not in df.columns:
        return JSONResponse(status_code=400, content={"error": "Invalid target column"})

    cleaned_df = auto_clean_dataset(df, target_col)
    cleaned_path = Path(f"temp_autocleaned_{file.filename}")
    cleaned_df.to_csv(cleaned_path, index=False)
    return FileResponse(cleaned_path, filename=cleaned_path.name)
