# AgriNova API - Frontend Integration Guide

This guide provides everything your frontend team needs to integrate with the AgriNova Customer Behavior Prediction API.

## 🌐 Base URL

**Production**: `https://your-service-url` (replace with your actual Cloud Run URL)  
**Local Development**: `http://localhost:8000`

## 📋 API Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Basic health check |
| GET | `/health` | Detailed health check with model status |
| POST | `/predict` | Predict behavior for a single customer |
| POST | `/predict/batch` | Predict behavior for multiple customers |

## 🔍 Health Check Endpoints

### Basic Health Check
```javascript
// GET /
const response = await fetch('https://your-api-url/');
const data = await response.json();
console.log(data); // { "message": "AgriNova Customer Behavior Prediction API", "status": "healthy" }
```

### Detailed Health Check
```javascript
// GET /health
const response = await fetch('https://your-api-url/health');
const data = await response.json();
console.log(data);
// {
//   "status": "healthy",
//   "models_loaded": "loaded",
//   "regression_model": "StackingRegressor",
//   "classification_model": "XGBClassifier"
// }
```

## 🎯 Single Customer Prediction

### Endpoint: `POST /predict`

**Request Body:**
```typescript
interface CustomerInput {
  Customer_ID: number;
  Recency_Days: number;        // Days since last purchase (≥0)
  Frequency: number;           // Number of purchases (≥1)
  Monetary: number;            // Total monetary value (≥0)
  Avg_Order_Value: number;     // Average order value (≥0)
  Total_Items_Sold: number;    // Total items sold (≥0)
  Attribution: string;         // Customer acquisition source
  Customer_Type: 'new' | 'returning';
}
```

**Response:**
```typescript
interface CustomerPrediction {
  Customer_ID: number;
  Pred_Next_Purchase_Days: number;  // Predicted days until next purchase
  Churn_Probability: number;        // Churn probability as percentage (0-100)
}
```

### JavaScript/TypeScript Examples

#### Using Fetch API
```javascript
async function predictCustomer(customerData) {
  try {
    const response = await fetch('https://your-api-url/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(customerData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const prediction = await response.json();
    return prediction;
  } catch (error) {
    console.error('Prediction failed:', error);
    throw error;
  }
}

// Usage
const customerData = {
  Customer_ID: 101,
  Recency_Days: 10,
  Frequency: 5,
  Monetary: 500.0,
  Avg_Order_Value: 100.0,
  Total_Items_Sold: 20,
  Attribution: "Organic: Google",
  Customer_Type: "new"
};

predictCustomer(customerData)
  .then(prediction => {
    console.log('Prediction:', prediction);
    // {
    //   "Customer_ID": 101,
    //   "Pred_Next_Purchase_Days": 176.16,
    //   "Churn_Probability": 22.41
    // }
  })
  .catch(error => console.error('Error:', error));
```

#### Using Axios
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://your-api-url',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

async function predictCustomer(customerData) {
  try {
    const response = await api.post('/predict', customerData);
    return response.data;
  } catch (error) {
    console.error('Prediction failed:', error.response?.data || error.message);
    throw error;
  }
}
```

## 📊 Batch Customer Prediction

### Endpoint: `POST /predict/batch`

**Request Body:**
```typescript
interface BatchPredictionRequest {
  customers: CustomerInput[];
}
```

**Response:**
```typescript
interface BatchPredictionResponse {
  predictions: CustomerPrediction[];
}
```

### JavaScript/TypeScript Examples

```javascript
async function predictBatchCustomers(customersData) {
  try {
    const response = await fetch('https://your-api-url/predict/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ customers: customersData })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result.predictions;
  } catch (error) {
    console.error('Batch prediction failed:', error);
    throw error;
  }
}

// Usage
const customersData = [
  {
    Customer_ID: 101,
    Recency_Days: 10,
    Frequency: 5,
    Monetary: 500.0,
    Avg_Order_Value: 100.0,
    Total_Items_Sold: 20,
    Attribution: "Organic: Google",
    Customer_Type: "new"
  },
  {
    Customer_ID: 102,
    Recency_Days: 200,
    Frequency: 1,
    Monetary: 50.0,
    Avg_Order_Value: 50.0,
    Total_Items_Sold: 2,
    Attribution: "Direct",
    Customer_Type: "returning"
  }
];

predictBatchCustomers(customersData)
  .then(predictions => {
    console.log('Batch Predictions:', predictions);
    // [
    //   {
    //     "Customer_ID": 101,
    //     "Pred_Next_Purchase_Days": 176.16,
    //     "Churn_Probability": 22.41
    //   },
    //   {
    //     "Customer_ID": 102,
    //     "Pred_Next_Purchase_Days": 73.51,
    //     "Churn_Probability": 56.93
    //   }
    // ]
  })
  .catch(error => console.error('Error:', error));
```

## 🏷️ Supported Attribution Values

The `Attribution` field accepts these values:

```javascript
const SUPPORTED_ATTRIBUTIONS = [
  'Direct',
  'Unknown',
  'Organic: Google',
  'Source: Google',
  'Web admin',
  'Source: Category',
  'Source: Metorik',
  'Referral: Dashboard.tawk.to',
  'Referral: Dash.callbell.eu',
  'Source: Chatgpt.com',
  'Source: Home',
  'Referral: Diyagric.com',
  'Source: CategoryPage',
  'Referral: Yandex.com',
  'Referral: Com.slack',
  'Referral: Duckduckgo.com',
  'Referral: Com.google.android.googlequicksearchbox',
  'Referral: Com.google.android.gm',
  'Referral: Bing.com',
  'Referral: L.instagram.com',
  'Referral: L.wl.co',
  'Source: Equipment+Category'
];
```

## ⚠️ Error Handling

### Common Error Responses

```typescript
interface APIError {
  detail: string;
}
```

### Error Handling Example

```javascript
async function handleAPICall(apiFunction, ...args) {
  try {
    return await apiFunction(...args);
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      const errorData = error.response.data;
      console.error('API Error:', errorData.detail);
      
      // Handle specific error cases
      if (error.response.status === 422) {
        console.error('Validation Error:', errorData.detail);
      } else if (error.response.status === 500) {
        console.error('Server Error:', errorData.detail);
      }
    } else if (error.request) {
      // Network error
      console.error('Network Error:', 'Unable to reach the API');
    } else {
      // Other error
      console.error('Error:', error.message);
    }
    throw error;
  }
}
```

## 🔧 React Integration Example

```jsx
import React, { useState } from 'react';

const CustomerPredictionForm = () => {
  const [customerData, setCustomerData] = useState({
    Customer_ID: '',
    Recency_Days: '',
    Frequency: '',
    Monetary: '',
    Avg_Order_Value: '',
    Total_Items_Sold: '',
    Attribution: 'Direct',
    Customer_Type: 'new'
  });
  
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('https://your-api-url/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...customerData,
          Customer_ID: parseInt(customerData.Customer_ID),
          Recency_Days: parseInt(customerData.Recency_Days),
          Frequency: parseInt(customerData.Frequency),
          Monetary: parseFloat(customerData.Monetary),
          Avg_Order_Value: parseFloat(customerData.Avg_Order_Value),
          Total_Items_Sold: parseInt(customerData.Total_Items_Sold),
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setPrediction(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* Form fields for customer data */}
        <input
          type="number"
          placeholder="Customer ID"
          value={customerData.Customer_ID}
          onChange={(e) => setCustomerData({...customerData, Customer_ID: e.target.value})}
        />
        {/* Add other form fields */}
        
        <button type="submit" disabled={loading}>
          {loading ? 'Predicting...' : 'Get Prediction'}
        </button>
      </form>

      {error && <div className="error">Error: {error}</div>}
      
      {prediction && (
        <div className="prediction">
          <h3>Prediction Results</h3>
          <p>Next Purchase Days: {prediction.Pred_Next_Purchase_Days.toFixed(2)}</p>
          <p>Churn Probability: {prediction.Churn_Probability.toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
};

export default CustomerPredictionForm;
```

## 🚀 Vue.js Integration Example

```vue
<template>
  <div>
    <form @submit.prevent="predictCustomer">
      <input v-model.number="customerData.Customer_ID" type="number" placeholder="Customer ID" />
      <input v-model.number="customerData.Recency_Days" type="number" placeholder="Recency Days" />
      <!-- Add other form fields -->
      
      <button type="submit" :disabled="loading">
        {{ loading ? 'Predicting...' : 'Get Prediction' }}
      </button>
    </form>

    <div v-if="error" class="error">
      Error: {{ error }}
    </div>

    <div v-if="prediction" class="prediction">
      <h3>Prediction Results</h3>
      <p>Next Purchase Days: {{ prediction.Pred_Next_Purchase_Days.toFixed(2) }}</p>
      <p>Churn Probability: {{ prediction.Churn_Probability.toFixed(2) }}%</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      customerData: {
        Customer_ID: null,
        Recency_Days: null,
        Frequency: null,
        Monetary: null,
        Avg_Order_Value: null,
        Total_Items_Sold: null,
        Attribution: 'Direct',
        Customer_Type: 'new'
      },
      prediction: null,
      loading: false,
      error: null
    }
  },
  methods: {
    async predictCustomer() {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch('https://your-api-url/predict', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.customerData)
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        this.prediction = await response.json();
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
```

## 📱 Mobile App Integration (React Native)

```javascript
import { Alert } from 'react-native';

const predictCustomer = async (customerData) => {
  try {
    const response = await fetch('https://your-api-url/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(customerData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const prediction = await response.json();
    return prediction;
  } catch (error) {
    Alert.alert('Error', `Prediction failed: ${error.message}`);
    throw error;
  }
};
```

## 🔒 Security Considerations

1. **HTTPS Only**: Always use HTTPS in production
2. **Input Validation**: Validate all inputs on the frontend
3. **Rate Limiting**: Implement client-side rate limiting
4. **Error Handling**: Never expose sensitive error details to users

## 📊 Performance Tips

1. **Batch Requests**: Use batch endpoint for multiple predictions
2. **Caching**: Cache predictions for the same customer data
3. **Loading States**: Show loading indicators during API calls
4. **Error Boundaries**: Implement error boundaries in React

## 🧪 Testing

### Test API Connection
```javascript
// Test health endpoint
fetch('https://your-api-url/health')
  .then(response => response.json())
  .then(data => console.log('API Status:', data))
  .catch(error => console.error('API Error:', error));
```

### Test Prediction
```javascript
// Test single prediction
const testCustomer = {
  Customer_ID: 101,
  Recency_Days: 10,
  Frequency: 5,
  Monetary: 500.0,
  Avg_Order_Value: 100.0,
  Total_Items_Sold: 20,
  Attribution: "Organic: Google",
  Customer_Type: "new"
};

fetch('https://your-api-url/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(testCustomer)
})
.then(response => response.json())
.then(data => console.log('Prediction:', data))
.catch(error => console.error('Error:', error));
```

## 📚 Additional Resources

- **API Documentation**: Visit `https://your-api-url/docs` for interactive API docs
- **OpenAPI Spec**: Available at `https://your-api-url/openapi.json`
- **Health Check**: Monitor API status at `https://your-api-url/health`

## 🆘 Support

If you encounter any issues:

1. Check the API health endpoint
2. Verify your request format matches the examples
3. Check network connectivity
4. Review error messages for specific issues
5. Contact the backend team with specific error details
