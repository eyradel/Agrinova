/**
 * AgriNova Customer Behavior Prediction API - TypeScript Interfaces
 * 
 * Import this file in your frontend project for type safety:
 * import { CustomerInput, CustomerPrediction, BatchPredictionRequest, BatchPredictionResponse } from './api-types';
 */

// Input schema for customer data
export interface CustomerInput {
  /** Unique customer identifier */
  Customer_ID: number;
  
  /** Days since last purchase (≥0) */
  Recency_Days: number;
  
  /** Number of purchases (≥1) */
  Frequency: number;
  
  /** Total monetary value (≥0) */
  Monetary: number;
  
  /** Average order value (≥0) */
  Avg_Order_Value: number;
  
  /** Total items sold (≥0) */
  Total_Items_Sold: number;
  
  /** Customer acquisition source */
  Attribution: AttributionType;
  
  /** Customer type */
  Customer_Type: CustomerType;
}

// Output schema for predictions
export interface CustomerPrediction {
  /** Original customer identifier */
  Customer_ID: number;
  
  /** Predicted days until next purchase */
  Pred_Next_Purchase_Days: number;
  
  /** Churn probability as percentage (0-100) */
  Churn_Probability: number;
}

// Batch prediction request
export interface BatchPredictionRequest {
  /** List of customers to predict */
  customers: CustomerInput[];
}

// Batch prediction response
export interface BatchPredictionResponse {
  /** List of predictions */
  predictions: CustomerPrediction[];
}

// Health check response
export interface HealthCheckResponse {
  /** API status */
  status: 'healthy' | 'unhealthy';
  
  /** Model loading status */
  models_loaded: 'loaded' | 'not loaded';
  
  /** Regression model type */
  regression_model: string | null;
  
  /** Classification model type */
  classification_model: string | null;
}

// API error response
export interface APIError {
  /** Error details */
  detail: string;
}

// Supported attribution types
export type AttributionType = 
  | 'Direct'
  | 'Unknown'
  | 'Organic: Google'
  | 'Source: Google'
  | 'Web admin'
  | 'Source: Category'
  | 'Source: Metorik'
  | 'Referral: Dashboard.tawk.to'
  | 'Referral: Dash.callbell.eu'
  | 'Source: Chatgpt.com'
  | 'Source: Home'
  | 'Referral: Diyagric.com'
  | 'Source: CategoryPage'
  | 'Referral: Yandex.com'
  | 'Referral: Com.slack'
  | 'Referral: Duckduckgo.com'
  | 'Referral: Com.google.android.googlequicksearchbox'
  | 'Referral: Com.google.android.gm'
  | 'Referral: Bing.com'
  | 'Referral: L.instagram.com'
  | 'Referral: L.wl.co'
  | 'Source: Equipment+Category';

// Supported customer types
export type CustomerType = 'new' | 'returning';

// Risk level based on churn probability
export type RiskLevel = 'Low Risk' | 'Medium Risk' | 'High Risk';

// Utility function to determine risk level
export function getRiskLevel(churnProbability: number): RiskLevel {
  if (churnProbability > 50) return 'High Risk';
  if (churnProbability > 25) return 'Medium Risk';
  return 'Low Risk';
}

// Utility function to get risk color
export function getRiskColor(churnProbability: number): string {
  if (churnProbability > 50) return '#e74c3c'; // Red
  if (churnProbability > 25) return '#f39c12'; // Orange
  return '#27ae60'; // Green
}

// API client configuration
export interface APIConfig {
  /** Base URL of the API */
  baseURL: string;
  
  /** Request timeout in milliseconds */
  timeout?: number;
  
  /** Default headers */
  headers?: Record<string, string>;
}

// API client class
export class AgriNovaAPI {
  private baseURL: string;
  private timeout: number;
  private headers: Record<string, string>;

  constructor(config: APIConfig) {
    this.baseURL = config.baseURL.replace(/\/$/, ''); // Remove trailing slash
    this.timeout = config.timeout || 10000;
    this.headers = {
      'Content-Type': 'application/json',
      ...config.headers
    };
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.request('/health');
    return response;
  }

  /**
   * Predict behavior for a single customer
   */
  async predictCustomer(customer: CustomerInput): Promise<CustomerPrediction> {
    const response = await this.request('/predict', {
      method: 'POST',
      body: JSON.stringify(customer)
    });
    return response;
  }

  /**
   * Predict behavior for multiple customers
   */
  async predictBatchCustomers(customers: CustomerInput[]): Promise<CustomerPrediction[]> {
    const response = await this.request('/predict/batch', {
      method: 'POST',
      body: JSON.stringify({ customers })
    });
    return response.predictions;
  }

  /**
   * Make a request to the API
   */
  private async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${this.baseURL}${endpoint}`;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.headers,
          ...options.headers
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      throw error;
    }
  }
}

// Example usage:
/*
const api = new AgriNovaAPI({
  baseURL: 'https://your-api-url',
  timeout: 10000
});

// Single prediction
const prediction = await api.predictCustomer({
  Customer_ID: 101,
  Recency_Days: 10,
  Frequency: 5,
  Monetary: 500.0,
  Avg_Order_Value: 100.0,
  Total_Items_Sold: 20,
  Attribution: 'Organic: Google',
  Customer_Type: 'new'
});

// Batch prediction
const predictions = await api.predictBatchCustomers([
  { /* customer 1 */ },
  { /* customer 2 */ }
]);
*/
