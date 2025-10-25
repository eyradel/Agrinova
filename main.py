import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Initialize FastAPI app
app = FastAPI(
    title="AgriNova Customer Behavior Prediction API",
    description="API for predicting customer churn probability and next purchase days",
    version="1.0.0"
)

# Load models and encoders
def load_models():
    """Load and validate models with detailed error reporting"""
    global reg_model, clf_model
    
    try:
        print("Checking model files...")
        import os
        if not os.path.exists('next_purchase_stack_model.pkl'):
            raise FileNotFoundError("next_purchase_stack_model.pkl not found")
        if not os.path.exists('churn_model.pkl'):
            raise FileNotFoundError("churn_model.pkl not found")
        print("Model files found")
        
        print("Checking dependencies...")
        try:
            import joblib
            import pandas as pd
            import numpy as np
            import xgboost
            from sklearn.preprocessing import LabelEncoder
            print("All dependencies available")
        except ImportError as e:
            raise ImportError(f"Missing dependency: {e}")
        
        print("Loading regression model...")
        reg_model = joblib.load('next_purchase_stack_model.pkl')
        print(f"Regression model loaded: {type(reg_model)}")
        
        print("Loading classification model...")
        clf_model = joblib.load('churn_model.pkl')
        print(f"Classification model loaded: {type(clf_model)}")
        
        # Test model functionality
        print("Testing model functionality...")
        test_data = pd.DataFrame({
            'Frequency': [1], 'Monetary': [100.0], 'Avg_Order_Value': [100.0], 
            'Total_Items_Sold': [1], 'Customer_Type': ['new'], 'Attribution': ['Direct']
        })
        test_clf_data = pd.DataFrame({
            'Recency_Days': [10], 'Avg_Order_Value': [100.0], 
            'Total_Items_Sold': [1], 'Attribution': ['Direct']
        })
        
        # Test regression model
        reg_pred = reg_model.predict(test_data[['Frequency', 'Monetary', 'Avg_Order_Value', 'Total_Items_Sold', 'Customer_Type', 'Attribution']])
        print(f"Regression model test prediction: {reg_pred[0]}")
        
        # Test classification model
        clf_pred = clf_model.predict_proba(test_clf_data)[:, 1]
        print(f"Classification model test prediction: {clf_pred[0]}")
        
        print("All models loaded and tested successfully!")
        return True
        
    except Exception as e:
        print(f"Error loading models: {e}")
        print(f"Error type: {type(e).__name__}")
        print("Make sure you have installed all dependencies: pip install -r requirements.txt")
        print("Check that model files are present in the container")
        reg_model = None
        clf_model = None
        return False

# Initialize models
models_loaded = load_models()

# Initialize single label encoder (as shown in the guide)
le = LabelEncoder()

# Fit encoder with all known categories
all_categories = ['new', 'returning', 'Direct', 'Unknown', 'Organic: Google', 'Source: Google', 'Web admin',
    'Source: Category', 'Source: Metorik', 'Referral: Dashboard.tawk.to',
    'Referral: Dash.callbell.eu', 'Source: Chatgpt.com', 'Source: Home',
    'Referral: Diyagric.com', 'Source: CategoryPage', 'Referral: Yandex.com',
    'Referral: Com.slack', 'Referral: Duckduckgo.com',
    'Referral: Com.google.android.googlequicksearchbox',
    'Referral: Com.google.android.gm', 'Referral: Bing.com',
    'Referral: L.instagram.com', 'Referral: L.wl.co',
    'Source: Equipment+Category']

le.fit(all_categories)

# Pydantic models for input/output validation
class CustomerInput(BaseModel):
    Customer_ID: int = Field(..., description="Unique customer identifier")
    Recency_Days: int = Field(..., ge=0, description="Days since last purchase")
    Frequency: int = Field(..., ge=1, description="Number of purchases")
    Monetary: float = Field(..., ge=0, description="Total monetary value")
    Avg_Order_Value: float = Field(..., ge=0, description="Average order value")
    Total_Items_Sold: int = Field(..., ge=0, description="Total items sold")
    Attribution: str = Field(..., description="Customer acquisition source")
    Customer_Type: Literal['new', 'returning'] = Field(..., description="Customer type")

class CustomerPrediction(BaseModel):
    Customer_ID: int
    Pred_Next_Purchase_Days: float = Field(..., description="Predicted days until next purchase")
    Churn_Probability: float = Field(..., ge=0, le=100, description="Churn probability as percentage")

class BatchPredictionRequest(BaseModel):
    customers: List[CustomerInput] = Field(..., description="List of customers to predict")

class BatchPredictionResponse(BaseModel):
    predictions: List[CustomerPrediction] = Field(..., description="List of predictions")

def predict_customer_behavior(df: pd.DataFrame) -> pd.DataFrame:
    """
    Predict customer behavior using the loaded models.
    This function matches the exact implementation from the guide.
    
    Args:
        df: DataFrame with customer features
        
    Returns:
        DataFrame with predictions added
    """
    if reg_model is None or clf_model is None:
        raise HTTPException(
            status_code=500, 
            detail="Models not loaded properly. Please check server logs and ensure all dependencies are installed."
        )
    
    # Create a copy to avoid modifying original data
    df = df.copy()
    
    # Encode categorical variables using single encoder (as shown in guide)
    df['Customer_Type'] = le.fit_transform(df['Customer_Type'])
    df['Attribution'] = le.fit_transform(df['Attribution'])
    
    # Features for regression model (next purchase prediction) - exact from guide
    reg_features = ['Frequency', 'Monetary', 'Avg_Order_Value', 'Total_Items_Sold', 'Customer_Type', 'Attribution']
    df['Pred_Next_Purchase_Days'] = reg_model.predict(df[reg_features])
    
    # Features for classification model (churn prediction) - exact from guide
    clf_features = ['Recency_Days', 'Avg_Order_Value', 'Total_Items_Sold', 'Attribution']
    X_clf_new = df[clf_features]
    df['Churn_Probability'] = clf_model.predict_proba(X_clf_new)[:, 1] * 100
    
    return df

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AgriNova Customer Behavior Prediction API", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check with comprehensive status"""
    import os
    
    # Check model files
    model_files = {
        "next_purchase_stack_model.pkl": os.path.exists('next_purchase_stack_model.pkl'),
        "churn_model.pkl": os.path.exists('churn_model.pkl')
    }
    
    # Check model loading status
    models_loaded = reg_model is not None and clf_model is not None
    
    # Check dependencies
    dependencies = {}
    try:
        import joblib
        dependencies["joblib"] = True
    except ImportError:
        dependencies["joblib"] = False
    
    try:
        import xgboost
        dependencies["xgboost"] = True
    except ImportError:
        dependencies["xgboost"] = False
    
    try:
        import pandas
        dependencies["pandas"] = True
    except ImportError:
        dependencies["pandas"] = False
    
    try:
        import sklearn
        dependencies["sklearn"] = True
    except ImportError:
        dependencies["sklearn"] = False
    
    return {
        "status": "healthy" if models_loaded else "unhealthy",
        "models_loaded": models_loaded,
        "model_files": model_files,
        "dependencies": dependencies,
        "regression_model": type(reg_model).__name__ if reg_model else None,
        "classification_model": type(clf_model).__name__ if clf_model else None,
        "models_loaded_successfully": models_loaded
    }

@app.post("/predict", response_model=CustomerPrediction)
async def predict_single_customer(customer: CustomerInput):
    """
    Predict behavior for a single customer
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame([customer.dict()])
        
        # Get predictions
        result_df = predict_customer_behavior(df)
        
        # Extract prediction
        prediction = result_df.iloc[0]
        
        return CustomerPrediction(
            Customer_ID=prediction['Customer_ID'],
            Pred_Next_Purchase_Days=float(prediction['Pred_Next_Purchase_Days']),
            Churn_Probability=float(prediction['Churn_Probability'])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch_customers(request: BatchPredictionRequest):
    """
    Predict behavior for multiple customers
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame([customer.dict() for customer in request.customers])
        
        # Get predictions
        result_df = predict_customer_behavior(df)
        
        # Convert to response format
        predictions = []
        for _, row in result_df.iterrows():
            predictions.append(CustomerPrediction(
                Customer_ID=int(row['Customer_ID']),
                Pred_Next_Purchase_Days=float(row['Pred_Next_Purchase_Days']),
                Churn_Probability=float(row['Churn_Probability'])
            ))
        
        return BatchPredictionResponse(predictions=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
