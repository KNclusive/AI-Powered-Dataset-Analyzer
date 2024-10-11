import React from 'react';
import DatasetTable from '../components/DatasetTable';
import Insights from '../components/Insights';
import dataset1 from '../data/dataset1.json';
import dataset2 from '../data/dataset2.json';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';

const Home = () => {
  return (
    <Box sx={{ padding: 3 }}>
      <Typography variant="h4" gutterBottom align="center" sx={{ mb: 4 }}>
        Explore and Analyze Datasets
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <DatasetTable datasetName="Dataset 1" dataset={dataset1} />
        </Grid>
        <Grid item xs={12} md={6}>
          <DatasetTable datasetName="Dataset 2" dataset={dataset2} />
        </Grid>
      </Grid>
      <Insights data1={dataset1} data2={dataset2} />
    </Box>
  );
};

export default Home;