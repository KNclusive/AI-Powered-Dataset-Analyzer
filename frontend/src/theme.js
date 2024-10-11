import { createTheme } from '@mui/material/styles';
import '@fontsource/orbitron'; // Import the sci-fi font (Install via npm)

// Create a custom theme
const theme = createTheme({
  palette: {
    mode: 'dark', // Set dark mode
    primary: {
      main: '#00e5ff', // Neon cyan
    },
    secondary: {
      main: '#ff4081', // Neon pink
    },
    background: {
      default: '#121212', // Dark background
      paper: 'rgba(18, 18, 18, 0.8)', // Semi-transparent background for Paper components
    },
    text: {
      primary: '#ffffff', // White text
      secondary: '#b0bec5', // Light gray text
    },
  },
  typography: {
    fontFamily: 'Orbitron, sans-serif', // Sci-fi font
  },
});

export default theme;
