import pandas as pd
from AutoClean import AutoClean


def auto_clean_dataset(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    """
    Automatically clean and preprocess the dataset using py-AutoClean's automated cleaning pipeline.

    This function leverages py-AutoClean's capabilities to handle
    missing values, outliers, duplicates, and other common data issues
    suitable for machine learning.

    Parameters:
    - df (pd.DataFrame): The input dataset to clean.
    - target_col (str): The name of the target column (for reference, not used in cleaning).

    Returns:
    - pd.DataFrame: The cleaned and preprocessed dataset.

    Raises:
    - ValueError: If the target column is not found in the dataset.
    """
    if df is None or df.empty:
        return df.copy()

    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in the dataset.")

    # Determine task type: classification or regression
    target_series = df[target_col].dropna()
    unique_values = target_series.nunique()

    # Heuristic: if target has few unique values or is object/category, treat as classification
    is_classification = (
        df[target_col].dtype in ['object', 'category'] or
        unique_values <= 20  # Arbitrary threshold for classification
    )

    try:
        # Use py-AutoClean for automated data cleaning
        pipeline = AutoClean(df)
        cleaned_df = pipeline.output
        return cleaned_df.reset_index(drop=True)

    except Exception as e:
        # Fallback: return original dataframe if py-AutoClean fails
        print(f"py-AutoClean preprocessing failed: {e}. Returning original dataset.")
        return df.copy()
