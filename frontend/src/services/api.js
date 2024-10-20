// src/services/api.js

const API_URL = 'http://localhost:8000'; // Update to match backend port

export const getInsights = async (query) => {
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('Error fetching insights:', error);
    throw error;
  }
};

export const fetchDataset = async (datasetName) => {
  try {
    const response = await fetch(`${API_URL}/datasets/${datasetName}`);
    const data = await response.json();
    if (response.ok) {
      return data.data;
    } else {
      throw new Error(data.detail || 'Failed to fetch dataset');
    }
  } catch (error) {
    console.error('Error fetching dataset:', error);
    throw error;
  }
};