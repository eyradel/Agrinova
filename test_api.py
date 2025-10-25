#!/usr/bin/env python3
"""
Test script for the AgriNova Customer Behavior Prediction API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
        return False

def test_single_prediction():
    """Test single customer prediction using exact data from the guide"""
    print("\nTesting single customer prediction...")
    
    # Sample customer data from the guide
    customer_data = {
        "Customer_ID": 101,
        "Recency_Days": 10,
        "Frequency": 5,
        "Monetary": 500.0,
        "Avg_Order_Value": 100.0,
        "Total_Items_Sold": 20,
        "Attribution": "Organic: Google",
        "Customer_Type": "new"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=customer_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Prediction Result:")
            print(f"  Customer ID: {result['Customer_ID']}")
            print(f"  Predicted Next Purchase Days: {result['Pred_Next_Purchase_Days']:.2f}")
            print(f"  Churn Probability: {result['Churn_Probability']:.2f}%")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
        return False

def test_batch_prediction():
    """Test batch customer prediction using exact data from the guide"""
    print("\nTesting batch customer prediction...")
    
    # Sample batch data from the guide
    batch_data = {
        "customers": [
            {
                "Customer_ID": 101,
                "Recency_Days": 10,
                "Frequency": 5,
                "Monetary": 500.0,
                "Avg_Order_Value": 100.0,
                "Total_Items_Sold": 20,
                "Attribution": "Organic: Google",
                "Customer_Type": "new"
            },
            {
                "Customer_ID": 102,
                "Recency_Days": 200,
                "Frequency": 1,
                "Monetary": 50.0,
                "Avg_Order_Value": 50.0,
                "Total_Items_Sold": 2,
                "Attribution": "Direct",
                "Customer_Type": "returning"
            },
            {
                "Customer_ID": 103,
                "Recency_Days": 45,
                "Frequency": 3,
                "Monetary": 200.0,
                "Avg_Order_Value": 66.7,
                "Total_Items_Sold": 10,
                "Attribution": "Unknown",
                "Customer_Type": "new"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict/batch", json=batch_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Batch Prediction Results:")
            for i, prediction in enumerate(result['predictions']):
                print(f"  Customer {i+1}:")
                print(f"    Customer ID: {prediction['Customer_ID']}")
                print(f"    Predicted Next Purchase Days: {prediction['Pred_Next_Purchase_Days']:.2f}")
                print(f"    Churn Probability: {prediction['Churn_Probability']:.2f}%")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
        return False

def main():
    """Run all tests"""
    print("🚀 AgriNova API Test Suite")
    print("=" * 50)
    
    # Test health check
    health_ok = test_health_check()
    
    if health_ok:
        # Test single prediction
        single_ok = test_single_prediction()
        
        # Test batch prediction
        batch_ok = test_batch_prediction()
        
        print("\n" + "=" * 50)
        print("📊 Test Results:")
        print(f"  Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"  Single Prediction: {'✅ PASS' if single_ok else '❌ FAIL'}")
        print(f"  Batch Prediction: {'✅ PASS' if batch_ok else '❌ FAIL'}")
        
        if all([health_ok, single_ok, batch_ok]):
            print("\n🎉 All tests passed!")
        else:
            print("\n⚠️  Some tests failed. Check the output above.")
    else:
        print("\n❌ Health check failed. Make sure the API server is running.")
        print("   Start the server with: python main.py")

if __name__ == "__main__":
    main()
