const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

let backendProcess = null;
let testWindow = null;
let canvasReadyResolver = null;
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


// ------------------- IPC: Canvas readiness -------------------
ipcMain.on('canvas-ready', () => {
    if (canvasReadyResolver) {
        canvasReadyResolver();
        canvasReadyResolver = null;
    }
});

// ------------------- App: Create main window -------------------
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

    const builtIndexPath = path.join(__dirname, '..', 'dist', 'index.html');

    if (fs.existsSync(builtIndexPath)) {
        mainWindow.loadFile(builtIndexPath);
    } else {
        mainWindow.loadURL('http://localhost:5173');
    }

    // mainWindow.webContents.openDevTools();

    mainWindow.on('closed', () => {
        // stopBackendServer(); // if you're re-enabling backend logic
    });
}

// ------------------- IPC: Test window orchestration -------------------

ipcMain.handle('open-test-window', async (event, url) => {
    const waitForCanvasReady = () => {
        return new Promise(resolve => {
            canvasReadyResolver = resolve;

            setTimeout(() => {
                if (canvasReadyResolver) {
                    console.warn('⚠️ Timed out waiting for canvas. Proceeding anyway.');
                    canvasReadyResolver();
                    canvasReadyResolver = null;
                }
            }, 30000); // 30s fallback
        });
    };

    if (testWindow && !testWindow.isDestroyed()) {
        testWindow.loadURL(url);
        testWindow.focus();
        await waitForCanvasReady();
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

    // testWindow.webContents.openDevTools();

    testWindow.on('closed', () => {
        testWindow = null;
    });

    await waitForCanvasReady();
    testWindow.focus();
    return { success: true, reused: false };
});

ipcMain.handle('capture-screenshot', async () => {
    if (!testWindow || testWindow.isDestroyed()) {
        throw new Error('Test window is not available');
    }
    testWindow.focus();
    const image = await testWindow.webContents.capturePage();
    const pngBuffer = image.toPNG();
    return pngBuffer.toString('base64');
});

ipcMain.handle('perform-click', async (event, classId, x, y) => {
    if (!testWindow || testWindow.isDestroyed()) {
        throw new Error('Test window is not available');
    }

    testWindow.focus();

    if (classId === 0) {
        try {
            const js = `
                (function() {
                    const canvas = document.querySelector('canvas');
                    if (!canvas) return { success: false, error: 'No canvas found' };
                    const rect = canvas.getBoundingClientRect();
                    const clientX = rect.left + ${x};
                    const clientY = rect.top + ${y};
                    ['pointerdown', 'pointerup', 'click'].forEach(type => {
                        canvas.dispatchEvent(new PointerEvent(type, {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            clientX,
                            clientY,
                            pointerType: 'mouse',
                            isPrimary: true
                        }));
                    });
                    return { success: true };
                })();
            `;
            const result = await testWindow.webContents.executeJavaScript(js, true);
            if (!result?.success) {
                console.warn('Canvas pointer event simulation failed:', result?.error);
            }
        } catch (err) {
            console.error('Canvas pointer event simulation error:', err);
        }
    } else {
        try {
            testWindow.webContents.sendInputEvent({ type: 'mouseMove', x, y });
            testWindow.webContents.sendInputEvent({ type: 'mouseDown', x, y, button: 'left', clickCount: 1 });
            testWindow.webContents.sendInputEvent({ type: 'mouseUp', x, y, button: 'left', clickCount: 1 });
        } catch (err) {
            console.error('Low-level perform-click failed:', err);
            throw err;
        }
    }

    await new Promise(resolve => setTimeout(resolve, 10000));
    return { success: true };
});

ipcMain.handle('click-in-dom', async (event, rawX, rawY, options = {}) => {
    if (!testWindow || testWindow.isDestroyed()) {
        throw new Error('Test window is not available');
    }

    testWindow.focus();

    try {
        const serializedOptions = JSON.stringify(options);
        const js = `
            (async () => {
                if (typeof window.clickAtXY === 'function') {
                    try {
                        return await window.clickAtXY(${rawX}, ${rawY}, ${serializedOptions});
                    } catch (e) {
                        return { success: false, error: 'clickAtXY threw: ' + e.toString() };
                    }
                } else if (typeof window.api?.clickAt === 'function') {
                    try {
                        return await window.api.clickAt(${rawX}, ${rawY}, ${serializedOptions});
                    } catch (e) {
                        return { success: false, error: 'api.clickAt threw: ' + e.toString() };
                    }
                } else {
                    return { success: false, error: 'No in-page click dispatcher found' };
                }
            })();
        `;

        const result = await testWindow.webContents.executeJavaScript(js, true);

        if (result && result.success) {
            await new Promise(resolve => setTimeout(resolve, 500));
            return { success: true, via: 'in-dom', detail: result };
        } else {
            console.warn('In-DOM click failed, falling back:', result);
            testWindow.webContents.sendInputEvent({ type: 'mouseMove', x: rawX, y: rawY });
            testWindow.webContents.sendInputEvent({ type: 'mouseDown', x: rawX, y: rawY, button: 'left', clickCount: 1 });
            testWindow.webContents.sendInputEvent({ type: 'mouseUp', x: rawX, y: rawY, button: 'left', clickCount: 1 });
            await new Promise(resolve => setTimeout(resolve, 10000));
            return { success: true, via: 'fallback-low-level', detail: result };
        }
    } catch (err) {
        console.error('click-in-dom handler error:', err);
        try {
            testWindow.webContents.sendInputEvent({ type: 'mouseMove', x: rawX, y: rawY });
            testWindow.webContents.sendInputEvent({ type: 'mouseDown', x: rawX, y: rawY, button: 'left', clickCount: 1 });
            testWindow.webContents.sendInputEvent({ type: 'mouseUp', x: rawX, y: rawY, button: 'left', clickCount: 1 });
            await new Promise(resolve => setTimeout(resolve, 10000));
            return { success: true, via: 'fallback-on-error', error: err.toString() };
        } catch (fallbackErr) {
            console.error('Fallback low-level click also failed:', fallbackErr);
            throw fallbackErr;
        }
    }
});

ipcMain.handle('get-test-window-metrics', async () => {
    if (!testWindow || testWindow.isDestroyed()) return null;

    const [width, height] = testWindow.getSize();
    const zoomFactor = testWindow.webContents.getZoomFactor();

    let devicePixelRatio = 1;
    try {
        const dpr = await testWindow.webContents.executeJavaScript('window.devicePixelRatio', true);
        if (typeof dpr === 'number' && !isNaN(dpr)) {
            devicePixelRatio = dpr;
        }
    } catch (e) {
        console.warn('Failed to get devicePixelRatio:', e);
    }

    return { width, height, zoomFactor, devicePixelRatio };
});

ipcMain.handle('check-backend-status', async () => {
    return backendProcess !== null && !backendProcess.killed;
});

// ------------------- App lifecycle -------------------

app.whenReady().then(() => {
    createWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});