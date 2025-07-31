const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const axios = require('axios');

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
        width: 1280,
        height: 800,
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

// Utility delay function
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Function to run the compliance flow
async function runFlow(url, flow) {
    const win = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
    });

    await win.loadURL(url);

    for (let i = 0; i < flow.length; i++) {
        await delay(5000);

        // Take screenshot
        const image = await win.capturePage();
        const screenshot = image.toPNG();

        // Call your API (POST, not GET)
        const apiResponse = await axios.get('http://localhost:7000/get-coordinates', {
            game_url: url,
            test_type: "UI Element Detection",
            additional_params: { classIds: [flow[i]] },
            image_data: screenshot.toString('base64'),
        });

        console.log(`Coordinates for step ${i + 1}:`, apiResponse.data);

        // Simulate click at (x, y) if needed
        // const { x, y } = apiResponse.data;
        // await win.webContents.sendInputEvent({ type: 'mouseDown', x, y, button: 'left', clickCount: 1 });
        // await win.webContents.sendInputEvent({ type: 'mouseUp', x, y, button: 'left', clickCount: 1 });
    }
}

// Register IPC handlers at the top level
ipcMain.handle('check-backend-status', async () => {
    return backendProcess !== null && !backendProcess.killed;
});

ipcMain.handle('run-compliance-flow', async (event, { url, flow }) => {
    await runFlow(url, flow);
    return { success: true };
});

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
