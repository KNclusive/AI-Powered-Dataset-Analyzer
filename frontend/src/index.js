import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import theme from './theme'; // Import the custom theme
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline'; // To apply base CSS resets

ReactDOM.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Apply baseline CSS resets and background styles */}
      <App />
    </ThemeProvider>
  </React.StrictMode>,
  document.getElementById('root')
);
