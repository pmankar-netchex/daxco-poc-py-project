import React from 'react';
import { Box, Typography, AppBar, Toolbar, IconButton } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AppsIcon from '@mui/icons-material/Apps';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.webp';

const Header = () => {
  return (
    <AppBar position="static" color="default" sx={{ background: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ height: '40px', width: '40px', mr: 2, display: 'flex', alignItems: 'center' }}>
            <img 
              src={logo}
              alt="Company Logo"
              style={{ width: '100%', height: '100%' }}
            />
          </Box>
          <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <Typography variant="subtitle1" sx={{ mr: 4, color: '#333', fontSize: '0.9rem', fontWeight: 'bold' }}>
              EWJ - QA (DEMO)
            </Typography>
          </Link>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ mr: 2 }}>
            <Typography 
              component={Link} 
              to="/" 
              sx={{ 
                mx: 1.5, 
                color: '#333', 
                textDecoration: 'none', 
                fontWeight: 'medium',
                fontSize: '0.85rem',
                '&:hover': { color: '#000' } 
              }}
            >
              DASHBOARD
            </Typography>
            
            <Typography 
              component="span" 
              sx={{ 
                mx: 1.5, 
                color: '#333', 
                fontWeight: 'medium',
                fontSize: '0.85rem',
                cursor: 'pointer', 
                '&:hover': { color: '#000' } 
              }}
            >
              PEOPLE
            </Typography>
            
            <Typography 
              component="span" 
              sx={{ 
                mx: 1.5, 
                color: '#333', 
                fontWeight: 'medium',
                fontSize: '0.85rem',
                cursor: 'pointer', 
                '&:hover': { color: '#000' } 
              }}
            >
              PAYROLL
            </Typography>
            
            <Typography 
              component="span" 
              sx={{ 
                mx: 1.5, 
                color: '#333', 
                fontWeight: 'medium',
                fontSize: '0.85rem', 
                cursor: 'pointer', 
                '&:hover': { color: '#000' } 
              }}
            >
              TIME & ATTENDANCE
            </Typography>
          </Box>
          
          <IconButton sx={{ mr: 1, color: '#666' }}>
            <AppsIcon />
          </IconButton>
          
          <IconButton sx={{ color: '#666' }}>
            <AccountCircleIcon />
          </IconButton>
        </Box>
      </Toolbar>
      
      {/* Green line below the header */}
      <Box sx={{ height: '4px', bgcolor: '#6ab04c', width: '100%' }} />
    </AppBar>
  );
};

export default Header;
