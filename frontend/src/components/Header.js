import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { Link } from 'react-router-dom';

const Header = () => (
  <AppBar position="static">
    <Toolbar>
      <Typography variant="h6" sx={{ flexGrow: 1 }}>
        AI Dataset Analyzer
      </Typography>
      <Link to="/" style={{ color: '#fff', textDecoration: 'none', marginRight: 20 }}>
        Home
      </Link>
      <Link to="/dashboard" style={{ color: '#fff', textDecoration: 'none' }}>
        Dashboard
      </Link>
    </Toolbar>
  </AppBar>
);

export default Header;
