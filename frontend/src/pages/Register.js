import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Alert,
  Paper,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await register(formData);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #080c14 0%, #0f1525 100%)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: '-20%',
          left: '-10%',
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%)',
          borderRadius: '50%',
        }}
      />

      <Container maxWidth="sm" sx={{ position: 'relative', zIndex: 1 }}>
        <Paper
          elevation={24}
          sx={{
            p: 4,
            background: 'rgba(15,21,37,0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 4,
            maxHeight: '90vh',
            overflowY: 'auto',
          }}
        >
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Box
              sx={{
                width: 60,
                height: 60,
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                borderRadius: 3,
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '28px',
                mb: 1.5,
              }}
            >
              ◈
            </Box>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 800,
                fontFamily: "'Playfair Display', serif",
                mb: 0.5,
                color: '#f1f5f9',
              }}
            >
              Create Account
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              Start tracking your job applications
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Full Name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              InputLabelProps={{
                shrink: true,
              }}
              sx={{ 
                mb: 2,
                '& .MuiInputLabel-root': { 
                  color: 'rgba(255,255,255,0.6)',
                  backgroundColor: 'rgba(15,21,37,0.9)',
                  padding: '0 8px',
                  marginLeft: '-4px',
                },
                '& .MuiInputLabel-root.Mui-focused': { color: '#6366f1' },
                '& .MuiOutlinedInput-root': {
                  color: '#f1f5f9',
                  '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
                  '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                  '&.Mui-focused fieldset': { borderColor: '#6366f1' },
                },
              }}
            />

            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              InputLabelProps={{
                shrink: true,
              }}
              sx={{ 
                mb: 2,
                '& .MuiInputLabel-root': { 
                  color: 'rgba(255,255,255,0.6)',
                  backgroundColor: 'rgba(15,21,37,0.9)',
                  padding: '0 8px',
                  marginLeft: '-4px',
                },
                '& .MuiInputLabel-root.Mui-focused': { color: '#6366f1' },
                '& .MuiOutlinedInput-root': {
                  color: '#f1f5f9',
                  '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
                  '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                  '&.Mui-focused fieldset': { borderColor: '#6366f1' },
                },
              }}
            />

            <TextField
              fullWidth
              label="Password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleChange}
              required
              InputLabelProps={{
                shrink: true,
              }}
              sx={{ 
                mb: 2,
                '& .MuiInputLabel-root': { 
                  color: 'rgba(255,255,255,0.6)',
                  backgroundColor: 'rgba(15,21,37,0.9)',
                  padding: '0 8px',
                  marginLeft: '-4px',
                },
                '& .MuiInputLabel-root.Mui-focused': { color: '#6366f1' },
                '& .MuiOutlinedInput-root': {
                  color: '#f1f5f9',
                  '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
                  '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                  '&.Mui-focused fieldset': { borderColor: '#6366f1' },
                },
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      sx={{ color: 'rgba(255,255,255,0.6)' }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{
                py: 1.5,
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                fontWeight: 700,
                fontSize: '16px',
                mb: 2,
              }}
            >
              {loading ? 'Creating account...' : 'Sign Up'}
            </Button>

            <Typography variant="body2" align="center" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              Already have an account?{' '}
              <Link
                to="/login"
                style={{
                  color: '#a5b4fc',
                  textDecoration: 'none',
                  fontWeight: 600,
                }}
              >
                Sign in
              </Link>
            </Typography>
          </form>
        </Paper>
      </Container>
    </Box>
  );
};

export default Register;
