#!/usr/bin/env python3
"""
Debug script to test model loading and dependencies
Run this locally to verify everything works before deploying
"""

import os
import sys

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    dependencies = [
        'joblib', 'pandas', 'numpy', 'sklearn', 'xgboost', 
        'fastapi', 'uvicorn', 'pydantic'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            missing.append(dep)
    
    if missing:
        print(f"\n❌ Missing dependencies: {missing}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies available")
        return True

def check_model_files():
    """Check if model files exist"""
    print("\n🔍 Checking model files...")
    
    model_files = [
        'next_purchase_stack_model.pkl',
        'churn_model.pkl'
    ]
    
    missing = []
    for file in model_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size:,} bytes)")
        else:
            print(f"❌ {file} - MISSING")
            missing.append(file)
    
    if missing:
        print(f"\n❌ Missing model files: {missing}")
        return False
    else:
        print("✅ All model files found")
        return True

def test_model_loading():
    """Test loading the models"""
    print("\n🔄 Testing model loading...")
    
    try:
        import joblib
        import pandas as pd
        import numpy as np
        from sklearn.preprocessing import LabelEncoder
        
        print("Loading regression model...")
        reg_model = joblib.load('next_purchase_stack_model.pkl')
        print(f"✅ Regression model: {type(reg_model)}")
        
        print("Loading classification model...")
        clf_model = joblib.load('churn_model.pkl')
        print(f"✅ Classification model: {type(clf_model)}")
        
        # Test with sample data
        print("🧪 Testing predictions...")
        
        # Create test data
        test_data = pd.DataFrame({
            'Frequency': [5], 'Monetary': [500.0], 'Avg_Order_Value': [100.0], 
            'Total_Items_Sold': [20], 'Customer_Type': ['new'], 'Attribution': ['Direct']
        })
        
        test_clf_data = pd.DataFrame({
            'Recency_Days': [10], 'Avg_Order_Value': [100.0], 
            'Total_Items_Sold': [20], 'Attribution': ['Direct']
        })
        
        # Test regression
        reg_pred = reg_model.predict(test_data[['Frequency', 'Monetary', 'Avg_Order_Value', 'Total_Items_Sold', 'Customer_Type', 'Attribution']])
        print(f"✅ Regression prediction: {reg_pred[0]}")
        
        # Test classification
        clf_pred = clf_model.predict_proba(test_clf_data)[:, 1]
        print(f"✅ Classification prediction: {clf_pred[0]}")
        
        print("🎉 All models working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

def test_api_startup():
    """Test if the API can start"""
    print("\n🚀 Testing API startup...")
    
    try:
        # Import the main module
        import main
        print("✅ API module imported successfully")
        
        # Check if models are loaded
        if main.reg_model is not None and main.clf_model is not None:
            print("✅ Models loaded in API")
            return True
        else:
            print("❌ Models not loaded in API")
            return False
            
    except Exception as e:
        print(f"❌ API startup failed: {e}")
        return False

def main():
    """Run all debug checks"""
    print("🐛 AgriNova API Debug Script")
    print("=" * 50)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Model Files", check_model_files),
        ("Model Loading", test_model_loading),
        ("API Startup", test_api_startup)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'='*20} {name} {'='*20}")
        result = check_func()
        results.append((name, result))
    
    print(f"\n{'='*50}")
    print("📊 SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Ready for deployment.")
    else:
        print("\n⚠️  Some checks failed. Fix issues before deploying.")
        print("\n💡 Common fixes:")
        print("   - Install dependencies: pip install -r requirements.txt")
        print("   - Ensure model files are in the project directory")
        print("   - Check Python version compatibility")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
