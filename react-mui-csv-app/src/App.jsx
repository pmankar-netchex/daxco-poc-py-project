import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, CssBaseline, createTheme, Box } from "@mui/material";
import UploadPage from "./UploadPage";
import ValidationPage from "./ValidationPage";
import Header from "./components/Header";

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <Box sx={{ flexGrow: 1, mt: 6, px: 2 }}>
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/validate" element={<ValidationPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
