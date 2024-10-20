// Loader.js
import React from 'react';
import CircularProgress from '@mui/material/CircularProgress'; 
import { LinearProgress } from '@mui/material';
import Box from '@mui/material/Box';

// const Loader = () => (
//   <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
//     <CircularProgress />
//   </Box>
// );

const Loader = () => (
  <Box sx={{ width: '100%' }}>
    <LinearProgress />
  </Box>
);

export default Loader;