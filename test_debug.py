#!/usr/bin/env python3
"""
Debug script to test the API locally and identify issues
"""

import requests
import json

def test_local_api():
    """Test the API running locally"""
    base_url = "http://localhost:8000"
    
    print("Testing AgriNova API Debug")
    print("=" * 50)
    
    try:
        # Test basic endpoint
        print("1. Testing basic endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test debug endpoint
        print("\n2. Testing debug endpoint...")
        response = requests.get(f"{base_url}/debug")
        print(f"Status: {response.status_code}")
        debug_data = response.json()
        print("Debug Info:")
        for key, value in debug_data.items():
            print(f"  {key}: {value}")
        
        # Test health endpoint
        print("\n3. Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        health_data = response.json()
        print("Health Info:")
        for key, value in health_data.items():
            print(f"  {key}: {value}")
        
        # Test prediction if models are loaded
        if health_data.get("models_loaded", False):
            print("\n4. Testing prediction...")
            test_data = {
                "Customer_ID": 101,
                "Recency_Days": 10,
                "Frequency": 5,
                "Monetary": 500.0,
                "Avg_Order_Value": 100.0,
                "Total_Items_Sold": 20,
                "Attribution": "Organic: Google",
                "Customer_Type": "new"
            }
            
            response = requests.post(f"{base_url}/predict", json=test_data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Prediction: {response.json()}")
            else:
                print(f"Error: {response.text}")
        else:
            print("\n4. Models not loaded - skipping prediction test")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Make sure it's running on localhost:8000")
        print("Start the API with: python main.py")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_local_api()
