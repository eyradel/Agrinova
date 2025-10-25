import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Load models and encoders
try:
    import os
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    print(f"Python path: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    # Check if we're in a cloud environment
    is_cloud = os.environ.get('K_SERVICE') or os.environ.get('GAE_SERVICE') or os.environ.get('CLOUD_RUN_SERVICE')
    print(f"Cloud environment detected: {bool(is_cloud)}")
    
    print("Loading regression model...")
    if os.path.exists('next_purchase_stack_model.pkl'):
        print(f"Model file size: {os.path.getsize('next_purchase_stack_model.pkl')} bytes")
        reg_model = joblib.load('next_purchase_stack_model.pkl')
        print(f"Regression model loaded: {type(reg_model)}")
    else:
        print("next_purchase_stack_model.pkl not found!")
        reg_model = None
    
    print("Loading classification model...")
    if os.path.exists('churn_model.pkl'):
        print(f"Model file size: {os.path.getsize('churn_model.pkl')} bytes")
        clf_model = joblib.load('churn_model.pkl')
        print(f"Classification model loaded: {type(clf_model)}")
    else:
        print("churn_model.pkl not found!")
        clf_model = None
    
    if reg_model and clf_model:
        print("All models loaded successfully!")
    else:
        print("Some models failed to load!")
        
except Exception as e:
    print(f"Error loading models: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    print(f"Full traceback: {traceback.format_exc()}")
    print("Make sure you have installed all dependencies: pip install -r requirements.txt")
    reg_model = None
    clf_model = None

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
        # Try to reload models if they failed initially
        try:
            print("Attempting to reload models...")
            # Load models into local variables first
            new_reg_model = joblib.load('next_purchase_stack_model.pkl')
            new_clf_model = joblib.load('churn_model.pkl')
            
            # Update global variables
            globals()['reg_model'] = new_reg_model
            globals()['clf_model'] = new_clf_model
            print("Models reloaded successfully!")
        except Exception as e:
            print(f"Failed to reload models: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Models not loaded properly. Error: {str(e)}. Please check server logs and ensure all dependencies are installed."
            )
    
    # Create a copy to avoid modifying original data
    df = df.copy()
    
    # Encode categorical variables using single encoder (as shown in guide)
    df['Customer_Type'] = le.transform(df['Customer_Type'])
    df['Attribution'] = le.transform(df['Attribution'])
    
    # Features for regression model (next purchase prediction) - exact from guide
    reg_features = ['Frequency', 'Monetary', 'Avg_Order_Value', 'Total_Items_Sold', 'Customer_Type', 'Attribution']
    X_reg = df[reg_features].values  # Convert to numpy array to avoid feature name warnings
    df['Pred_Next_Purchase_Days'] = reg_model.predict(X_reg)
    
    # Features for classification model (churn prediction) - exact from guide
    clf_features = ['Recency_Days', 'Avg_Order_Value', 'Total_Items_Sold', 'Attribution']
    X_clf_new = df[clf_features].values  # Convert to numpy array to avoid feature name warnings
    df['Churn_Probability'] = clf_model.predict_proba(X_clf_new)[:, 1] * 100
    
    return df

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AgriNova Customer Behavior Prediction API", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    import os
    
    model_status = "loaded" if reg_model is not None and clf_model is not None else "not loaded"
    
    # Cloud-specific debugging information
    cloud_info = {
        "cloud_environment": bool(os.environ.get('K_SERVICE') or os.environ.get('GAE_SERVICE') or os.environ.get('CLOUD_RUN_SERVICE')),
        "working_directory": os.getcwd(),
        "model_files_exist": {
            "regression_model": os.path.exists('next_purchase_stack_model.pkl'),
            "classification_model": os.path.exists('churn_model.pkl')
        }
    }
    
    if os.path.exists('next_purchase_stack_model.pkl'):
        cloud_info["regression_model_size"] = os.path.getsize('next_purchase_stack_model.pkl')
    if os.path.exists('churn_model.pkl'):
        cloud_info["classification_model_size"] = os.path.getsize('churn_model.pkl')
    
    return {
        "status": "healthy",
        "models_loaded": model_status,
        "regression_model": type(reg_model).__name__ if reg_model else None,
        "classification_model": type(clf_model).__name__ if clf_model else None,
        "cloud_debug": cloud_info
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
