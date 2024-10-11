import axios from 'axios';

const API_URL = 'http://localhost:5000'; // Replace with your backend URL

export const getInsights = async (query, { data1, data2 }) => {
  try {
    const response = await axios.post(`${API_URL}/get-insights`, {
      query,
      data1,
      data2
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching insights:', error);
    throw error;
  }
};