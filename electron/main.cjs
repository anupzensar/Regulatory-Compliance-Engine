const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

// Global variable to store backend process
let backendProcess = null;

// ----------------- EDIT: managed test window reference -----------------
let testWindow = null; // Controlled window used for screenshot / click orchestration
// ----------------------------------------------------------------------

// Function to start the Python backend server
// function startBackendServer() {
//     const backendPath = path.join(__dirname, '..', 'backend');
//     const pythonScript = path.join(backendPath, 'app.py');
//     const venvPath = path.join(backendPath, 'venv');

//     console.log('Starting Python backend server...');
//     console.log('Backend path:', backendPath);
//     console.log('Python script:', pythonScript);

//     let pythonCmd = 'python';
//     let args = [pythonScript];

//     // Check if virtual environment exists and use it
//     if (fs.existsSync(venvPath)) {
//         const venvPython = path.join(venvPath, 'Scripts', 'python.exe');
//         if (fs.existsSync(venvPython)) {
//             pythonCmd = venvPython;
//             console.log('Using virtual environment Python:', venvPython);
//         }
//     }

//     // Try different Python commands if venv doesn't work
//     const pythonCommands = [pythonCmd, 'python', 'python3', 'py'];

//     let started = false;
//     for (const cmd of pythonCommands) {
//         try {
//             console.log(`Attempting to start backend with: ${cmd}`);
//             backendProcess = spawn(cmd, args, {
//                 cwd: backendPath,
//                 stdio: ['pipe', 'pipe', 'pipe'],
//                 shell: process.platform === 'win32' // Use shell on Windows
//             });

//             backendProcess.stdout.on('data', (data) => {
//                 const output = data.toString();
//                 console.log(`Backend stdout: ${output}`);
//                 // Look for successful startup message
//                 if (output.includes('Uvicorn running on')) {
//                     console.log('Backend server started successfully!');
//                 }
//             });

//             backendProcess.stderr.on('data', (data) => {
//                 const error = data.toString();
//                 console.error(`Backend stderr: ${error}`);
//                 // Only log actual errors, not info messages
//                 if (!error.includes('INFO') && !error.includes('WARNING')) {
//                     console.error('Backend error:', error);
//                 }
//             });

//             backendProcess.on('close', (code) => {
//                 console.log(`Backend process exited with code ${code}`);
//                 backendProcess = null;
//             });

//             backendProcess.on('error', (err) => {
//                 console.error('Failed to start backend process:', err);
//                 backendProcess = null;
//             });

//             console.log(`Backend server starting with ${cmd}, PID: ${backendProcess.pid}`);
//             started = true;
//             break;
//         } catch (error) {
//             console.error(`Failed to start with ${cmd}:`, error);
//             // Continue to next command
//         }
//     }

//     if (!started) {
//         console.error('Failed to start Python backend server with any Python command');
//         console.error('Please ensure Python is installed and the backend dependencies are installed');
//         console.error('Run: pip install -r backend/requirements.txt');
//     }
// }

// Function to stop the backend server
// function stopBackendServer() {
//     if (backendProcess) {
//         console.log('Stopping Python backend server...');
//         backendProcess.kill();
//         backendProcess = null;
//     }
// }

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

// ----------------- EDIT: IPC handlers for orchestrated test window control -----------------

/**
 * Opens or reuses a controlled test window for regression flow.
 * Adds a 20-second delay after launching the game window.
 */
ipcMain.handle('open-test-window', async (event, url) => {
    if (testWindow && !testWindow.isDestroyed()) {
        testWindow.loadURL(url);
        testWindow.focus();
        // Wait 20 seconds to ensure game loads completely
        await new Promise(resolve => setTimeout(resolve, 20000));
        return { success: true, reused: true };
    }

    testWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            enableRemoteModule: false,
            nodeIntegration: false,
        },
    });

    testWindow.loadURL(url);

    // Optional: open devtools for the test window for debugging if needed
    // testWindow.webContents.openDevTools();

    testWindow.on('closed', () => {
        testWindow = null;
    });

    // Wait 20 seconds to ensure game loads completely
    await new Promise(resolve => setTimeout(resolve, 20000));
    return { success: true, reused: false };
});

/**
 * Captures a screenshot of the current test window.
 * Returns base64-encoded PNG string.
 */
ipcMain.handle('capture-screenshot', async () => {
    if (!testWindow || testWindow.isDestroyed()) {
        throw new Error('Test window is not available');
    }
    // Optionally wait for the content to finish loading if caller desires
    const image = await testWindow.webContents.capturePage();
    const pngBuffer = image.toPNG();
    return pngBuffer.toString('base64');
});

/**
 * Performs a synthetic click at (x,y) in the test window.
 * Adds a 10-second delay after the click event.
 */
ipcMain.handle('perform-click', async (event, x, y) => {
    if (!testWindow || testWindow.isDestroyed()) {
        throw new Error('Test window is not available');
    }
    // Move + mouse down + mouse up to simulate click
    testWindow.webContents.sendInputEvent({ type: 'mouseMove', x, y });
    testWindow.webContents.sendInputEvent({
        type: 'mouseDown',
        x,
        y,
        button: 'left',
        clickCount: 1,
    });
    testWindow.webContents.sendInputEvent({
        type: 'mouseUp',
        x,
        y,
        button: 'left',
        clickCount: 1,
    });
    // Wait 10 seconds to allow next screen to appear
    await new Promise(resolve => setTimeout(resolve, 10000));
    return { success: true };
});

/**
 * (Optional enhancement) Expose test window info like size / DPR if needed by renderer.
 */
ipcMain.handle('get-test-window-metrics', () => {
    if (!testWindow || testWindow.isDestroyed()) {
        return null;
    }
    const [width, height] = testWindow.getSize();
    const scaleFactor = testWindow.webContents.getZoomFactor(); // approximate zoom
    return { width, height, scaleFactor };
});
// ------------------------------------------------------------------------------------------------------------------

// Event when the application is ready
app.whenReady().then(() => {
    // Start the backend server first
    // startBackendServer();

    // Wait a moment for the server to start, then create the window
    // setTimeout(() => {
    //     createWindow();
    // }, 2000);

    // Replace with just creating the window:
    createWindow();
});

// Quit the application when all windows are closed
app.on('window-all-closed', () => {
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

// IPC handlers
ipcMain.handle('check-backend-status', async () => {
    return backendProcess !== null && !backendProcess.killed;
});
