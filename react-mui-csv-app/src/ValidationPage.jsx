import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  IconButton,
  TextField,
  Select,
  MenuItem,
  Snackbar,
  Alert
} from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import DeleteIcon from '@mui/icons-material/Delete';

/**
 * @typedef {Object} Output
 * @property {string} first_name
 * @property {string} last_name
 * @property {string} department
 * @property {any} adjustments
 * @property {any} time_clock_hours
 * @property {any} scheduled_hours
 * @property {any} scheduled_payroll
 * @property {any} total_hours
 * @property {any} details
 * @property {any} employee_code
 * @property {boolean=} employee_code_valid
 * @property {Array<any>=} possible_employee_codes
 * @property {boolean=} scheduled_payroll_valid
 */

const isValidationColumn = (col) => col.endsWith('_valid') || col.startsWith('possible_') || col.endsWith('_valid');

const getUserColumns = (columns) =>
  columns.filter(
    (col) =>
      !col.endsWith('_valid') &&
      !col.startsWith('possible_') &&
      col !== 'Details' &&
      col !== 'details' &&
      !col.endsWith('_codes') &&
      !col.endsWith('_valid')
  );

const hasInvalidCell = (row, columns) =>
  columns.some(
    (col) => row[`${col}_valid`] === false
  );

const COLUMN_LABELS = {
  first_name: "First Name",
  last_name: "Last Name",
  department: "Department",
  adjustments: "Adjustments",
  time_clock_hours: "Time Clock Hours",
  scheduled_hours: "Scheduled Hours",
  scheduled_payroll: "Scheduled Payroll",
  total_hours: "Total Hours",
  details: "Details",
  employee_code: "Employee Code",
  employee_code_valid: "Employee Code Valid",
  possible_employee_codes: "Possible Employee Codes",
  scheduled_payroll_valid: "Scheduled Payroll Valid"
};

const ValidationPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(location.state?.webhookResult || null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [successOpen, setSuccessOpen] = useState(false);

  useEffect(() => {
    if (data?.all_valid) {
      setSuccessOpen(true);
    }
  }, [data?.all_valid]);

  if (!data) {
    return (
      <Box mt={8} textAlign="center">
        <Typography color="error">No validation data found. Please upload a file first.</Typography>
      </Box>
    );
  }

  const { rows = [], all_valid = false } = data;
  const allColumns = rows.length > 0 ? Object.keys(rows[0]) : [];
  const columns = getUserColumns(allColumns);

  const handleRevalidate = async () => {
    setSaving(true);
    setError("");
    try {
      // Get values from localStorage
      const companyId = localStorage.getItem('companyId');
      const integrationType = localStorage.getItem('integration_type') || 'payroll';
      const integrationProvider = localStorage.getItem('integration_provider') || 'Daxco';
      const res = await axios.post(
        `/validate?companyId=${companyId}&integration_type=${integrationType}&integration_provider=${integrationProvider}`,
        { rows }
      );
      setData(res.data);
    } catch {
      setError("Revalidation failed.");
    }
    setSaving(false);
  };

  const handleDownload = async () => {
    setSaving(true);
    setError("");
    try {
      const res = await axios.post("/download", { rows }, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "validated.csv");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      setError("Download failed.");
    }
    setSaving(false);
  };

  const handleDeleteRow = (rowIdx) => {
    const newRows = rows.filter((_, idx) => idx !== rowIdx);
    setData({ ...data, rows: newRows });
  };

  return (
    <Box display="flex" flexDirection="column" alignItems="center" mt={6}>
      <Snackbar
        open={successOpen}
        autoHideDuration={3000}
        onClose={() => setSuccessOpen(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={() => setSuccessOpen(false)} severity="success" sx={{ width: '100%' }}>
          All rows are valid! You can now download the file.
        </Alert>
      </Snackbar>
      <Paper sx={{ p: 3, minWidth: 900 }}>
        <Typography variant="h5" mb={2}>Validation Results</Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                {columns.map((col) => (
                  <TableCell key={col}>{COLUMN_LABELS[col] || col}</TableCell>
                ))}
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row, rowIdx) => {
                const invalid = hasInvalidCell(row, columns);
                return (
                  <TableRow key={rowIdx}>
                    {columns.map((col) => {
                      const isInvalid = row[`${col}_valid`] === false;
                      if (
                        col === "employee_code" &&
                        isInvalid
                      ) {
                        if (!row.possible_employee_codes || row.possible_employee_codes.length === 0) {
                          return (
                            <TableCell key={col}>
                              <TextField
                                value={row[col] || ""}
                                size="small"
                                onChange={e => {
                                  let val = e.target.value;
                                  // Only allow integer or empty
                                  if (/^\d*$/.test(val)) {
                                    val = val === "" ? "" : parseInt(val, 10);
                                    const newRows = rows.map((r, i) =>
                                      i === rowIdx ? { ...r, [col]: val } : r
                                    );
                                    setData({ ...data, rows: newRows });
                                  }
                                }}
                                error={isInvalid}
                                helperText={isInvalid ? "Invalid employee" : ""}
                                sx={isInvalid ? { '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: '#b71c1c', borderWidth: 2 } } } : {}}
                              />
                            </TableCell>
                          );
                        } else {
                          return (
                            <TableCell key={col}>
                              <Select
                                value={row[col] || ""}
                                size="small"
                                displayEmpty
                                onChange={e => {
                                  let val = e.target.value;
                                  val = val === "" ? "" : parseInt(val, 10);
                                  const newRows = rows.map((r, i) =>
                                    i === rowIdx ? { ...r, [col]: val } : r
                                  );
                                  setData({ ...data, rows: newRows });
                                }}
                                error={isInvalid}
                                sx={isInvalid ? { '& .MuiOutlinedInput-notchedOutline': { borderColor: '#b71c1c', borderWidth: 2 } } : {}}
                                style={{ minWidth: 120 }}
                              >
                                <MenuItem value=""><em>None</em></MenuItem>
                                {row.possible_employee_codes.map(code => (
                                  <MenuItem key={code} value={code}>{code}</MenuItem>
                                ))}
                              </Select>
                            </TableCell>
                          );
                        }
                      }
                      // Scheduled Payroll: allow manual edit if invalid
                      if (
                        col === "scheduled_payroll" &&
                        isInvalid
                      ) {
                        return (
                          <TableCell key={col}>
                            <TextField
                              value={row[col] === null || row[col] === undefined ? "" : row[col]}
                              size="small"
                              onChange={e => {
                                let val = e.target.value;
                                // Only allow numbers or empty
                                if (/^\d*\.?\d*$/.test(val)) {
                                  val = val === "" ? "" : parseFloat(val);
                                  const newRows = rows.map((r, i) =>
                                    i === rowIdx ? { ...r, [col]: val } : r
                                  );
                                  setData({ ...data, rows: newRows });
                                }
                              }}
                              error={isInvalid}
                              helperText={isInvalid ? "Invalid scheduled payroll" : ""}
                              sx={isInvalid ? { '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: '#b71c1c', borderWidth: 2 } } } : {}}
                            />
                          </TableCell>
                        );
                      }
                      return (
                        <TableCell
                          key={col}
                        >
                          {(col === 'adjustments' || col === 'scheduled_payroll') && typeof row[col] === 'number'
                            ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(row[col])
                            : row[col]
                          }
                        </TableCell>
                      );
                    })}
                    <TableCell>
                      {invalid && (
                        <IconButton color="error" onClick={() => handleDeleteRow(rowIdx)}>
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
        <Box mt={2} display="flex" gap={2}>
          {!all_valid ? (
            <Button variant="contained" color="warning" onClick={handleRevalidate} disabled={saving}>
              {saving ? <CircularProgress size={20} /> : "Revalidate"}
            </Button>
          ) : (
            <Button variant="contained" color="success" onClick={handleDownload} disabled={saving}>
              {saving ? <CircularProgress size={20} /> : "Download"}
            </Button>
          )}
        </Box>
        {error && <Typography color="error" mt={2}>{error}</Typography>}
      </Paper>
    </Box>
  );
};

export default ValidationPage; 