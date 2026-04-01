# AutoML Training Feature Implementation

## Overview
This document summarizes the implementation of the AutoML training feature for the Automated Dataset Analyser and Trainer project.

## Components Implemented

### 1. AutoML Training Module (`modules/automl_training.py`)
A pure Python module that handles all machine learning operations:

#### Key Functions:
- **`detect_problem_type(df, target_column)`**
  - Automatically detects if the problem is Classification or Regression
  - Uses heuristics: data type, cardinality ratio, unique value counts
  - Returns: 'classification' or 'regression'

- **`train_automl_model(df, target_column, problem_type=None, test_size=0.2, verbose=False)`**
  - Trains an AutoML model using PyCaret
  - Automatically detects problem type if not provided
  - Uses PyCaret's `compare_models()` to find the best model
  - Returns: (results_dict, problem_type)

- **`save_model_pickle(model, model_name, filepath)`**
  - Saves the trained model to pickle format
  - Location: Can be used to serialize models for distribution

- **`load_model_pickle(filepath)`**
  - Loads a previously saved pickle model

- **`get_model_summary(results)`**
  - Extracts key metrics for display in the UI
  - Provides human-readable summary of training results

### 2. FastAPI Backend Endpoints (`backend/main.py`)
Three new endpoints for model training and download:

#### POST `/train`
```
Parameters:
  - file: Dataset file (CSV/XLSX)
  - target_col: Name of the target column

Returns:
  {
    "status": "success",
    "model_id": "dataset_name",
    "training_results": {
        "problem_type": "classification|regression",
        "target_column": "...",
        "n_samples": 1000,
        "n_features": 20,
        "best_model": "GradientBoostingClassifier",
        "status": "Success"
    },
    "message": "Model trained successfully! Problem type detected: classification"
  }
```

#### GET `/train/download/{model_id}`
- Downloads the trained model as a pickle file
- Returns: Binary pickle file with appropriate MIME type

#### POST `/train/download/direct`
- One-request endpoint: trains and downloads model in a single call
- Returns: Binary pickle file

### 3. Streamlit Frontend UI (`app.py`)
A complete 5-step training workflow:

#### Step 1: Select Target Column
- Dropdown selector for target variable
- Displays: unique values, data type, missing value count

#### Step 2: Data Quality Check
- Validates target column has no missing values
- Validates minimum dataset size (≥10 rows)
- Shows status for each validation

#### Step 3: Train AutoML Model
- One-click training button
- Shows progress spinner during training
- Displays success message with balloons animation

#### Step 4: Display Training Results
- Shows problem type (Classification/Regression)
- Displays selected best model
- Shows dataset statistics and feature count

#### Step 5: Download Trained Model
- Download button for pickle file
- Model ready for use in production or analysis

## Features

✅ **Automatic Problem Detection**
- Analyzes the target column to detect classification vs regression

✅ **AutoML Model Selection**
- Leverages PyCaret to automatically select the best model
- No manual hyperparameter tuning required

✅ **Pickle Format Export**
- Models saved in Python pickle format
- Compatible with scikit-learn, XGBoost, CatBoost, etc.

✅ **User-Friendly Interface**
- Step-by-step workflow
- Clear validation messages
- Status indicators and metrics

✅ **Error Handling**
- Validates input data before training
- Provides clear error messages for failures
- Graceful handling of missing values

## Dependencies
The following packages are already in your requirements.txt:
- `pycaret==3.3.0` - AutoML framework
- `streamlit==1.32.0` - Frontend
- `fastapi==0.110.0` - Backend API
- `pandas==2.1.4` - Data handling
- `scikit-learn==1.4.2` - ML algorithms
- `numpy==1.26.4` - Numerical computing

No additional dependencies required!

## Usage Workflow

### For Users:
1. Upload a cleaned dataset via Streamlit
2. Select "Training" from the Module Options
3. Choose your target column
4. Click "Train Model"
5. Wait for training to complete (depends on dataset size)
6. Click "Download Model as Pickle" to get the trained model
7. Use the pickle model for making predictions

### For Developers:
The pickle file can be loaded using:
```python
import pickle

with open('model_filename.pkl', 'rb') as f:
    model = pickle.load(f)

# Make predictions
predictions = model.predict(new_data)
```

## Example Datasets

The system works best with:
- **Classification**: Datasets with categorical target (e.g., "Yes/No", "Class A/B/C")
- **Regression**: Datasets with continuous numeric targets (e.g., prices, quantities)
- **Size**: 50+ rows recommended for reliable models

## Technical Notes

1. **Problem Detection Logic**:
   - Object dtype → Classification
   - Float values with decimals → Regression
   - Cardinality < 5% or <20 unique values → Classification
   - Otherwise → Regression

2. **Model Training**:
   - PyCaret uses 80-20 train-test split (configurable)
   - Session ID set to 42 for reproducibility
   - Silent mode enabled to avoid verbose output

3. **Storage**:
   - Trained models stored in memory during session
   - For production: Consider saving to database/file system

## Future Enhancements

Potential additions:
- Model performance metrics display (accuracy, RMSE, etc.)
- Feature importance visualization
- Cross-validation results
- Hyperparameter tuning options
- Model comparison (train multiple models)
- Batch predictions API
- Model versioning and history
