const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

// Global variable to store backend process
let backendProcess = null;

// Function to start the Python backend server
function startBackendServer() {
    const backendPath = path.join(__dirname, '..', 'backend');
    const pythonScript = path.join(backendPath, 'app.py');
    const venvPath = path.join(backendPath, 'venv');

    console.log('Starting Python backend server...');
    console.log('Backend path:', backendPath);
    console.log('Python script:', pythonScript);

    let pythonCmd = 'python';
    let args = [pythonScript];

    // Check if virtual environment exists and use it
    if (fs.existsSync(venvPath)) {
        const venvPython = path.join(venvPath, 'Scripts', 'python.exe');
        if (fs.existsSync(venvPython)) {
            pythonCmd = venvPython;
            console.log('Using virtual environment Python:', venvPython);
        }
    }

    // Try different Python commands if venv doesn't work
    const pythonCommands = [pythonCmd, 'python', 'python3', 'py'];

    let started = false;
    for (const cmd of pythonCommands) {
        try {
            console.log(`Attempting to start backend with: ${cmd}`);
            backendProcess = spawn(cmd, args, {
                cwd: backendPath,
                stdio: ['pipe', 'pipe', 'pipe'],
                shell: process.platform === 'win32' // Use shell on Windows
            });

            backendProcess.stdout.on('data', (data) => {
                const output = data.toString();
                console.log(`Backend stdout: ${output}`);
                // Look for successful startup message
                if (output.includes('Uvicorn running on')) {
                    console.log('Backend server started successfully!');
                }
            });

            backendProcess.stderr.on('data', (data) => {
                const error = data.toString();
                console.error(`Backend stderr: ${error}`);
                // Only log actual errors, not info messages
                if (!error.includes('INFO') && !error.includes('WARNING')) {
                    console.error('Backend error:', error);
                }
            });

            backendProcess.stdout.on('data', (data) => {
                process.stdout.write(`[BACKEND] ${data}`);
            });
            backendProcess.stderr.on('data', (data) => {
                process.stderr.write(`[BACKEND ERROR] ${data}`);
            });

            backendProcess.on('close', (code) => {
                console.log(`Backend process exited with code ${code}`);
                backendProcess = null;
            });

            backendProcess.on('error', (err) => {
                console.error('Failed to start backend process:', err);
                backendProcess = null;
            });

            console.log(`Backend server starting with ${cmd}, PID: ${backendProcess.pid}`);
            started = true;
            break;
        } catch (error) {
            console.error(`Failed to start with ${cmd}:`, error);
            // Continue to next command
        }
    }

    if (!started) {
        console.error('Failed to start Python backend server with any Python command');
        console.error('Please ensure Python is installed and the backend dependencies are installed');
        console.error('Run: pip install -r backend/requirements.txt');
    }
}

// Function to stop the backend server
function stopBackendServer() {
    if (backendProcess) {
        console.log('Stopping Python backend server...');
        backendProcess.kill();
        backendProcess = null;
    }
}

// Function to create the main application window
function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1200,        // Set your desired width
        height: 800,        // Set your desired height
        minWidth: 800,      // Optional: minimum width
        minHeight: 600,     // Optional: minimum height
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            enableRemoteModule: false,
            nodeIntegration: false,
        },
    });

    // Check if built files exist, otherwise load from dev server
    const builtIndexPath = path.join(__dirname, '..', 'dist', 'index.html');

    if (fs.existsSync(builtIndexPath)) {
        // Load the built application (production)
        mainWindow.loadFile(builtIndexPath);
    } else {
        // Load from dev server (development)
        mainWindow.loadURL('http://localhost:5173');
    }

    // Open the DevTools for debugging
    // mainWindow.webContents.openDevTools();

    // Handle window closed event
    mainWindow.on('closed', () => {
        stopBackendServer();
    });
}

// Event when the application is ready
app.whenReady().then(() => {
    // Start the backend server first
    startBackendServer();

    // Wait a moment for the server to start, then create the window
    setTimeout(() => {
        createWindow();
    }, 2000);
});

// Quit the application when all windows are closed
app.on('window-all-closed', () => {
    stopBackendServer();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Re-create the window on macOS if the dock icon is clicked
app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Handle app quit event
app.on('before-quit', () => {
    stopBackendServer();
});

// IPC handlers
ipcMain.handle('check-backend-status', async () => {
    return backendProcess !== null && !backendProcess.killed;
});
