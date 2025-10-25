# AgriNova Customer Behavior Prediction API

A FastAPI-based machine learning service for predicting customer churn probability and next purchase timing.

## Features

- **Churn Prediction**: Predicts the probability that a customer will churn (0-100%)
- **Next Purchase Prediction**: Predicts the number of days until a customer's next purchase
- **Batch Processing**: Support for single customer and batch customer predictions
- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check with model status

### Predictions
- `POST /predict` - Predict behavior for a single customer
- `POST /predict/batch` - Predict behavior for multiple customers

## Input Schema

```json
{
  "Customer_ID": 101,
  "Recency_Days": 10,
  "Frequency": 5,
  "Monetary": 500.0,
  "Avg_Order_Value": 100.0,
  "Total_Items_Sold": 20,
  "Attribution": "Direct",
  "Customer_Type": "new"
}
```

### Field Descriptions

- `Customer_ID` (int): Unique customer identifier
- `Recency_Days` (int): Days since last purchase (≥0)
- `Frequency` (int): Number of purchases (≥1)
- `Monetary` (float): Total monetary value (≥0)
- `Avg_Order_Value` (float): Average order value (≥0)
- `Total_Items_Sold` (int): Total items sold (≥0)
- `Attribution` (string): Customer acquisition source
- `Customer_Type` (string): Either "new" or "returning"

### Supported Attribution Values

- Direct
- Unknown
- Organic: Google
- Source: Google
- Web admin
- Source: Category
- Source: Metorik
- Referral: Dashboard.tawk.to
- Referral: Dash.callbell.eu
- Source: Chatgpt.com
- Source: Home
- Referral: Diyagric.com
- Source: CategoryPage
- Referral: Yandex.com
- Referral: Com.slack
- Referral: Duckduckgo.com
- Referral: Com.google.android.googlequicksearchbox
- Referral: Com.google.android.gm
- Referral: Bing.com
- Referral: L.instagram.com
- Referral: L.wl.co
- Source: Equipment+Category

## Output Schema

```json
{
  "Customer_ID": 101,
  "Pred_Next_Purchase_Days": 176.16,
  "Churn_Probability": 22.41
}
```

### Output Descriptions

- `Customer_ID` (int): Original customer identifier
- `Pred_Next_Purchase_Days` (float): Predicted days until next purchase
- `Churn_Probability` (float): Churn probability as percentage (0-100)

## Installation

1. Install dependencies:
```bash
pip install -e .
```

2. Ensure model files are present:
   - `churn_model.pkl`
   - `next_purchase_stack_model.pkl`

## Usage

### Start the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Example Usage

#### Single Customer Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Customer_ID": 101,
    "Recency_Days": 10,
    "Frequency": 5,
    "Monetary": 500.0,
    "Avg_Order_Value": 100.0,
    "Total_Items_Sold": 20,
    "Attribution": "Direct",
    "Customer_Type": "new"
  }'
```

#### Batch Customer Prediction

```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {
        "Customer_ID": 101,
        "Recency_Days": 10,
        "Frequency": 5,
        "Monetary": 500.0,
        "Avg_Order_Value": 100.0,
        "Total_Items_Sold": 20,
        "Attribution": "Direct",
        "Customer_Type": "new"
      },
      {
        "Customer_ID": 102,
        "Recency_Days": 200,
        "Frequency": 1,
        "Monetary": 50.0,
        "Avg_Order_Value": 50.0,
        "Total_Items_Sold": 2,
        "Attribution": "Unknown",
        "Customer_Type": "returning"
      }
    ]
  }'
```

### Testing

Run the test script to verify the API:

```bash
python test_api.py
```

## Model Information

The API uses two pre-trained machine learning models:

1. **Churn Model** (`churn_model.pkl`): Classification model for predicting churn probability
2. **Next Purchase Model** (`next_purchase_stack_model.pkl`): Regression model for predicting next purchase timing

Both models are loaded using `joblib` and expect specific feature sets as defined in the input schema.

## Error Handling

The API includes comprehensive error handling for:
- Invalid input data
- Model loading failures
- Prediction errors
- Missing required fields

All errors return appropriate HTTP status codes and descriptive error messages.
