import React from 'react';
import { Typography, Grid, Paper } from '@mui/material';

const KeyMetrics = ({ data, numericKeys, title }) => {
  if (!data || data.length === 0) return null;

  const calculateMetrics = (key) => {
    const values = data.map((item) => parseFloat(item[key])).filter((val) => !isNaN(val));
    const total = values.reduce((sum, val) => sum + val, 0);
    const mean = (total / values.length).toFixed(2);
    const sortedValues = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sortedValues.length / 2);
    const median = sortedValues.length % 2 !== 0 ? sortedValues[mid] : ((sortedValues[mid - 1] + sortedValues[mid]) / 2).toFixed(2);
    const min = Math.min(...values);
    const max = Math.max(...values);
    return { mean, median, min, max };
  };

  return (
    <Paper sx={{ p: 2, backgroundColor: 'background.paper' }}>
      <Typography variant="subtitle1" sx={{ mb: 1 }}>{title} Key Metrics</Typography>
      <Grid container spacing={1}>
        {numericKeys.map((key) => {
          const { mean, median, min, max } = calculateMetrics(key);
          return (
            <Grid item xs={6} sm={3} key={key}>
              <Typography variant="body2" fontWeight="bold">{key}</Typography>
              <Typography variant="caption" display="block">Mean: {mean}</Typography>
              <Typography variant="caption" display="block">Median: {median}</Typography>
              <Typography variant="caption" display="block">Min: {min}</Typography>
              <Typography variant="caption" display="block">Max: {max}</Typography>
            </Grid>
          );
        })}
      </Grid>
    </Paper>
  );
};

export default KeyMetrics;