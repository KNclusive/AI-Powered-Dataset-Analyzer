import React, { useEffect, useState } from 'react';
import { fetchDataset } from '../services/api';
import KeyMetrics from '../components/KeyMetrics';
import PreviousInsights from '../components/PreviousInsights';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';

const Dashboard = () => {
  const [data1, setData1] = useState([]);
  const [data2, setData2] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [dataset1, dataset2] = await Promise.all([
          fetchDataset('df1'),
          fetchDataset('df2'),
        ]);
        setData1(dataset1);
        setData2(dataset2);
      } catch (error) {
        console.error('Failed to load datasets:', error);
      }
    };
    loadData();
  }, []);

  const insights = [
    {
      query: 'What is the average age?',
      insight: 'The average age is 30.',
      date: '2023-10-01',
    },
    {
      query: 'Show me the total sales.',
      insight: 'The total sales are 450.',
      date: '2023-10-02',
    },
  ];


  const numericKeys1 =
  data1.length > 0
    ? Object.keys(data1[0]).filter((key) => typeof data1[0][key] === 'number')
    : [];
  const numericKeys2 =
    data2.length > 0
      ? Object.keys(data2[0]).filter((key) => typeof data2[0][key] === 'number')
      : [];


  return (
    <Box sx={{ padding: 3 }}>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>
      
      <PreviousInsights insights={insights} />
      
      {/* Other dashboard components can go here */}
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>Key Metrics</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <KeyMetrics data={data1} numericKeys={numericKeys1} title="Dataset 1" />
          </Grid>
          <Grid item xs={12} md={6}>
            <KeyMetrics data={data2} numericKeys={numericKeys2} title="Dataset 2" />
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Dashboard;