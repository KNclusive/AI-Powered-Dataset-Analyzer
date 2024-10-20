import React, { useState } from 'react';
import { getInsights } from '../services/api';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';

const Insights = () => {
  const [query, setQuery] = useState('');
  const [insight, setInsight] = useState(null);

  const handleSubmit = async () => {
    try {
      const response = await getInsights(query);
      setInsight(response);
    } catch (error) {
      console.error('Failed to get insights:', error);
      setInsight('Failed to get insights. Please try again.');
    }
  };

  return (
    <Paper elevation={3} sx={{ padding: 3, marginTop: 3 }}>
      <Typography variant="h5" gutterBottom>
        Get Insights
      </Typography>
      <TextField
        label="Enter your query"
        variant="outlined"
        fullWidth
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        sx={{ marginBottom: 2 }}
      />
      <Button variant="contained" onClick={handleSubmit} disabled={!query.trim()}>
        Get Insights
      </Button>
      {insight && (
        <Typography variant="body1" sx={{ marginTop: 2 }}>
          Insight: {insight}
        </Typography>
      )}
    </Paper>
  );
};

export default Insights;
