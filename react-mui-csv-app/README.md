# React MUI CSV Validation App

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```

## Backend API Endpoints (expected)
- `POST /webhook` — Accepts CSV file upload (multipart/form-data)
- `GET /output-json` — Returns validation result JSON
- `POST /validate` — Accepts edited rows for revalidation
- `GET /download` — Returns validated CSV as a file

The frontend expects the backend to run on `localhost:5000` (see `proxy` in `package.json`).
