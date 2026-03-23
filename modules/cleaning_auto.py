import pandas as pd
from modules.cleaning_manual import smart_type_conversion

def auto_clean_dataset(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    # Clean messy numeric strings and handle "nan" strings first
    df = smart_type_conversion(df)
    
    try:
        from pycaret.classification import setup as cls_setup, get_config as cls_get_config
        from pycaret.regression import setup as reg_setup, get_config as reg_get_config
        
        # Heuristic to determine if Classification or Regression
        is_classification = False
        if target_col in df.columns:
            if df[target_col].dtype == 'object' or df[target_col].dtype.name == 'category':
                is_classification = True
            elif df[target_col].nunique() < 20:
                is_classification = True
                
            if is_classification:
                cls_setup(data=df, target=target_col, verbose=False, preprocess=True)
                cleaned_df = cls_get_config('dataset_transformed')
                return cleaned_df
            else:
                reg_setup(data=df, target=target_col, verbose=False, preprocess=True)
                cleaned_df = reg_get_config('dataset_transformed')
                return cleaned_df
    except Exception as e:
        print(f"PyCaret auto-cleaning failed: {e}")
        
    # Fallback to robust scikit-learn heuristic cleaning
    # 1. Fill NaNs using SimpleImputer
    cleaned_df = df.copy()
    import numpy as np
    from sklearn.impute import SimpleImputer
    
    numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = cleaned_df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    if len(numeric_cols) > 0:
        cleaned_df[numeric_cols] = SimpleImputer(strategy='median').fit_transform(cleaned_df[numeric_cols])
    if len(categorical_cols) > 0:
        cleaned_df[categorical_cols] = SimpleImputer(strategy='most_frequent').fit_transform(cleaned_df[categorical_cols])
            
    # 2. Drop duplicates
    cleaned_df.drop_duplicates(inplace=True)
    
    return cleaned_df
