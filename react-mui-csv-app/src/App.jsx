import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, CssBaseline, createTheme } from "@mui/material";
import UploadPage from "./UploadPage";
import ValidationPage from "./ValidationPage";

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/validate" element={<ValidationPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ThemeProvider>
  );
}

export default App;
