# Regulatory Compliance Engine - Electron Integration

## Overview
The frontend React application has been successfully integrated with the Electron framework to create a desktop application. The system now builds the React app using Vite and packages it within the Electron app.

## Architecture

### Frontend (React + Vite)
- **Location**: `frontend/` directory
- **Build Output**: `electron/renderer/dist/`
- **Configuration**: `frontend/vite.config.js`
- **Entry Point**: `frontend/src/main.jsx`

### Electron Application
- **Main Process**: `electron/main.cjs`
- **Preload Script**: `electron/preload.js`
- **Renderer Process**: Loads the built React app from `electron/renderer/dist/index.html`

### Backend API
- **Location**: `backend/` directory
- **Flask API**: `backend/app.py`
- **Default Port**: 7000

## Build Process

### 1. Frontend Build
```bash
cd frontend
npm run build
```
- Compiles React app using Vite
- Outputs to `../electron/renderer/dist/`
- Generates optimized bundles with code splitting

### 2. Electron Build
```bash
npm run build
```
- Uses electron-builder to package the desktop app
- Includes the built React app

## Development Workflow

### Quick Start Scripts
1. **Batch File**: `run-unified.bat`
2. **PowerShell**: `run-unified.ps1`
3. **NPM Scripts**: 
   - `npm run electron-build` - Build and start Electron
   - `npm run electron-dev` - Development mode with hot reload
   - `npm run dist` - Build for distribution

### Manual Process
1. Build the React frontend:
   ```bash
   cd frontend && npm run build
   ```
2. Start Electron:
   ```bash
   npm start
   ```

## Key Features Integrated

### React Application Features
- **Homepage Component**: Main interface for compliance testing
- **API Integration**: Axios-based API client for backend communication
- **UI Components**: Toast notifications, loading spinners
- **Test Options**: Multiple compliance test types
- **URL Handling**: Opens test URLs in external browser

### Electron Integration
- **Context Isolation**: Secure communication between processes
- **Preload Script**: Safe API exposure to renderer
- **File Protocol**: Loads built React app from local files
- **Window Management**: Proper window creation and lifecycle

## Configuration Details

### Vite Configuration (`frontend/vite.config.js`)
- **Base Path**: `./` for relative asset loading
- **Output Directory**: `../electron/renderer/dist`
- **Code Splitting**: Vendor and utility chunks
- **Build Target**: ES Next for modern features

### Electron Configuration (`package.json`)
- **Main Entry**: `electron/main.cjs`
- **Build Files**: Includes frontend source and build output
- **Icon**: Uses `frontend/public/icon.ico`

### API Configuration
- **Base URL**: `http://localhost:7000` (configurable via VITE_API_BASE_URL)
- **Timeout**: 10 seconds
- **Headers**: JSON content type
- **Error Handling**: Comprehensive error mapping

## File Structure
```
regulatory-compliance-engine/
├── electron/
│   ├── main.cjs                  # Electron main process
│   ├── preload.js                # Preload script
│   └── renderer/
│       └── dist/                 # Built React app (generated)
├── src/                          # React source code (moved to root)
├── public/                       # Static assets (moved to root)
├── backend/
│   ├── app.py                    # FastAPI server
│   └── requirements.txt          # Python dependencies
├── package.json                  # Unified configuration
├── run-unified.bat               # Windows batch script
└── run-unified.ps1               # PowerShell script
```

## Dependencies

### Main Project
- `electron` ^25.0.0
- `react` ^18.2.0
- `react-dom` ^18.2.0
- `axios` ^1.6.0
- `lucide-react` ^0.294.0

### Frontend Project
- `vite` ^5.0.0
- `@vitejs/plugin-react` ^4.1.1
- `tailwindcss` ^4.0.0-alpha.24

## Running the Application

### Development Mode
```bash
npm run dev
```
This will:
1. Build the React frontend
2. Start the Electron application
3. Open the desktop app window

### Production Build
```bash
npm run build-all
```
This will:
1. Build the React frontend
2. Package the Electron application for distribution

## Notes
- The React app opens external URLs in the system's default browser
- API calls are made to the Flask backend server
- Toast notifications provide user feedback
- Loading states are handled gracefully
- Error handling is comprehensive across all layers

## Next Steps
1. Test the backend API server connection
2. Verify all compliance test types work correctly
3. Test the URL opening functionality
4. Package for distribution across platforms
5. Add auto-updater functionality if needed
