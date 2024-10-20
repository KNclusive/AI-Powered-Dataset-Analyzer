import React from 'react';
import DatasetTable from '../components/DatasetTable';
import Insights from '../components/Insights';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';

const Home = () => {
  return (
    <Box sx={{ padding: 3 }}>
      <Typography
        variant="h4"
        gutterBottom
        align="center"
        sx={{ mb: 4 }}
      >
        Explore and Analyze Datasets
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <DatasetTable datasetName="df1" />
        </Grid>
        <Grid item xs={12} md={6}>
          <DatasetTable datasetName="df2" />
        </Grid>
      </Grid>
      <Insights />
    </Box>
  );
};

export default Home;