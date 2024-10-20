// src/services/api.js
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const getInsights = async (query) => {
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      // Parse error message from response
      const errorData = await response.json();
      throw new Error(errorData.detail || 'An error occurred');
    }

    const data = await response.json();
    return data.response; // Access the 'response' field from the backend
  } catch (error) {
    console.error('Error in getInsights:', error);
    throw error;
  }
};

export const fetchDataset = async (datasetName) => {
  try {
    const response = await fetch(`${API_URL}/datasets/${datasetName}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch dataset: ${response.statusText}`);
    }
    const data = await response.json();
    return data.data; // Access the 'data' field in the response
  } catch (error) {
    console.error('Error fetching dataset:', error);
    throw error;
  }
};