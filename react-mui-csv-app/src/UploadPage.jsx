import React, { useState, useRef } from "react";
import { Box, Button, Typography, Paper, CircularProgress, TextField, Grid, InputLabel } from "@mui/material";
import Papa from "papaparse";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const UploadPage = () => {
  const [csvFile, setCsvFile] = useState(null);
  const [csvData, setCsvData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [companyId, setCompanyId] = useState("123");
  const [integrationType, setIntegrationType] = useState("payroll");
  const [integrationProvider, setIntegrationProvider] = useState("Daxco");
  const [webhookResult, setWebhookResult] = useState(null);
  const navigate = useNavigate();
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const handleFileChange = (e) => {
    setError("");
    const file = e.target.files[0];
    setCsvFile(file);
    if (file) {
      Papa.parse(file, {
        complete: (result) => setCsvData(result.data),
        header: true,
      });
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setCsvFile(e.dataTransfer.files[0]);
      Papa.parse(e.dataTransfer.files[0], {
        complete: (result) => setCsvData(result.data),
        header: true,
      });
    }
  };

  const handleFileClick = () => {
    inputRef.current.click();
  };

  const handleUpload = async () => {
    if (!csvFile) return;
    setLoading(true);
    setError("");
    setWebhookResult(null);
    localStorage.setItem('companyId', companyId);
    localStorage.setItem('integration_type', integrationType);
    localStorage.setItem('integration_provider', integrationProvider);
    const formData = new FormData();
    formData.append("file", csvFile);
    try {
      const response = await axios.post(`/webhook?companyId=${companyId}&integration_type=${integrationType}&integration_provider=${integrationProvider}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setLoading(false);
      navigate("/validate", { state: { webhookResult: response.data } });
    } catch (err) {
      setLoading(false);
      setError("Upload failed. Please try again.");
    }
  };

  return (
    <Box display="flex" flexDirection="column" alignItems="center" mt={8}>
      <Paper sx={{ p: 4, width: 400 }} elevation={3}>
        <Typography variant="h5" mb={2}>Upload CSV</Typography>
        <Box mb={2}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <InputLabel shrink htmlFor="company-id-field">Company ID</InputLabel>
              <TextField
                id="company-id-field"
                type="number"
                value={companyId}
                onChange={e => setCompanyId(e.target.value)}
                fullWidth
                variant="outlined"
                size="small"
                sx={{ mb: 1 }}
              />
            </Grid>
            <Grid item xs={12}>
              <InputLabel shrink htmlFor="integration-type-field">Integration Type</InputLabel>
              <TextField
                id="integration-type-field"
                type="text"
                value={integrationType}
                onChange={e => setIntegrationType(e.target.value)}
                fullWidth
                variant="outlined"
                size="small"
                sx={{ mb: 1 }}
              />
            </Grid>
            <Grid item xs={12}>
              <InputLabel shrink htmlFor="integration-provider-field">Integration Provider</InputLabel>
              <TextField
                id="integration-provider-field"
                type="text"
                value={integrationProvider}
                onChange={e => setIntegrationProvider(e.target.value)}
                fullWidth
                variant="outlined"
                size="small"
                sx={{ mb: 2 }}
              />
            </Grid>
          </Grid>
        </Box>
        <Box
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={handleFileClick}
          sx={{
            border: dragActive ? '2px solid #1976d2' : '2px dashed #ccc',
            borderRadius: 2,
            p: 2,
            mb: 2,
            textAlign: 'center',
            background: dragActive ? '#e3f2fd' : '#fafbfc',
            cursor: 'pointer',
            transition: 'border 0.2s, background 0.2s',
          }}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <Typography variant="body1" color="textSecondary">
            {csvFile ? csvFile.name : 'Drag & drop your CSV file here, or click to select'}
          </Typography>
        </Box>
        {csvData && csvData.length > 0 && (
          <Box mb={2}>
            <Typography variant="subtitle1">Preview:</Typography>
            <Box sx={{ maxHeight: 200, overflow: "auto", fontSize: 12 }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    {Object.keys(csvData[0]).map((header) => (
                      <th key={header} style={{ border: '1px solid #ccc', padding: '4px', background: '#f5f5f5' }}>{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {csvData.slice(0, 10).map((row, idx) => (
                    <tr key={idx}>
                      {Object.keys(csvData[0]).map((header) => (
                        <td key={header} style={{ border: '1px solid #ccc', padding: '4px' }}>{row[header]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </Box>
          </Box>
        )}
        {error && <Typography color="error">{error}</Typography>}
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={!csvFile || loading}
          fullWidth
        >
          {loading ? <CircularProgress size={24} /> : "Validate"}
        </Button>
        {webhookResult && (
          <Box mt={3}>
            <Typography variant="subtitle1">Webhook Output:</Typography>
            <Box sx={{ maxHeight: 200, overflow: "auto", fontSize: 12 }}>
              <pre>{JSON.stringify(webhookResult, null, 2)}</pre>
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default UploadPage; 