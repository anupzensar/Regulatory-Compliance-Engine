# Electron App with Backend Integration

This document explains how the Regulatory Compliance Engine Electron app integrates with the Python FastAPI backend.

## Overview

The Electron app now automatically starts and manages the Python backend server when the application launches. This provides a seamless user experience where both the frontend and backend run together in a single application.

## How it Works

1. **Automatic Backend Startup**: When the Electron app starts, it automatically launches the Python FastAPI server on `http://localhost:7000`
2. **Process Management**: The backend process is managed by Electron and will be automatically stopped when the app closes
3. **Virtual Environment Support**: The app will automatically detect and use a Python virtual environment if available in `backend/venv`
4. **Cross-Platform Python Detection**: The app tries different Python commands (`python`, `python3`, `py`) to find a working Python installation

## Running the Application

### Method 1: Using the Run Scripts (Recommended)

**PowerShell:**
```powershell
.\run-unified.ps1
```

**Command Prompt:**
```cmd
run-unified.bat
```

These scripts will:
- Check for Python installation
- Create a virtual environment if needed
- Install Python dependencies
- Build the React frontend
- Start the Electron app with integrated backend

### Method 2: Manual Steps

1. **Install Python Dependencies:**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   deactivate
   cd ..
   ```

2. **Build Frontend:**
   ```bash
   npm run build
   ```

3. **Start Electron App:**
   ```bash
   npm run electron
   ```

## Prerequisites

- **Node.js** (for the Electron app and React frontend)
- **Python** (3.8 or higher recommended)
- **pip** (Python package manager)

## Backend API

The backend provides the following endpoints:

- `GET /` - Health check endpoint
- `POST /run-test` - Submit compliance test requests

The API documentation is available when the server is running at `http://localhost:7000/docs`

## Configuration

### Backend Configuration

The backend can be configured through environment variables or by modifying `backend/config.py`:

- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 7000)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: allows all for Electron compatibility)
- `LOG_LEVEL`: Logging level (default: info)

### Frontend Configuration

The frontend automatically detects if it's running in Electron and uses the appropriate backend URL.

## Troubleshooting

### Python Not Found
If you see "Python not found" errors:
1. Install Python from https://python.org/downloads/
2. Make sure Python is added to your system PATH
3. Try using `python`, `python3`, or `py` command to verify installation

### Backend Dependencies Missing
If the backend fails to start:
1. Navigate to the `backend` directory
2. Install dependencies: `pip install -r requirements.txt`
3. If using virtual environment: activate it first

### Port Already in Use
If port 7000 is already in use:
1. Check what's using the port: `netstat -ano | findstr :7000`
2. Kill the process or change the port in `backend/config.py`

### CORS Issues
The backend is configured to allow all origins for Electron compatibility. If you need to restrict this:
1. Modify the `ALLOWED_ORIGINS` in `backend/config.py`
2. Add specific origins instead of using `["*"]`

## Development Mode

For development with hot reload:

1. **Start Backend Separately:**
   ```bash
   cd backend
   python app.py
   ```

2. **Start Frontend Dev Server:**
   ```bash
   npm run dev
   ```

3. **Start Electron in Dev Mode:**
   ```bash
   npm run electron-dev
   ```

This setup allows for hot reloading of both frontend and backend during development.

## Security Considerations

- The backend is configured to allow all origins (`*`) for Electron compatibility
- In production, consider restricting CORS origins to specific domains
- The backend runs locally and is not exposed to external networks by default
- Ensure Python dependencies are kept up to date for security
