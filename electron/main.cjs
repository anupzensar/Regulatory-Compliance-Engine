const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');


// Global variable to store backend process
let backendProcess = null;

// Global reference to the managed test window
let testWindow = null;

/**
 * Helper function to poll the renderer process for a canvas element.
 * Resolves when the canvas is found, rejects on timeout or if the window is closed.
 * @param {BrowserWindow} browserWindow The window to check.
 * @param {number} timeout The maximum time to wait in milliseconds.
 * @returns {Promise<void>}
 */
async function waitForCanvasInWindow(browserWindow, timeout = 20000) {
    const checkInterval = 500; // ms
    const startTime = Date.now();

    return new Promise((resolve, reject) => {
        const intervalId = setInterval(async () => {
            if (Date.now() - startTime > timeout) {
                clearInterval(intervalId);
                reject(new Error(`Canvas not found within ${timeout}ms timeout.`));
                return;
            }

            if (!browserWindow || browserWindow.isDestroyed()) {
                clearInterval(intervalId);
                reject(new Error('The window was closed while waiting for the canvas.'));
                return;
            }

            try {
                // Execute JS in the renderer to check for the canvas
                const canvasExists = await browserWindow.webContents.executeJavaScript(
                    "!!document.querySelector('canvas')",
                    true // userGesture
                );

                if (canvasExists) {
                    console.log('✅ Canvas detected in testWindow.');
                    clearInterval(intervalId);
                    resolve();
                } else {
                    console.log('⏳ Waiting for canvas in testWindow...');
                }
            } catch (error) {
                // This can happen if the page is navigating or not yet ready
                console.warn('Could not execute script to check for canvas, will retry:', error.message);
            }
        }, checkInterval);
    });
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

    const builtIndexPath = path.join(__dirname, '..', 'dist', 'index.html');

    if (fs.existsSync(builtIndexPath)) {
        mainWindow.loadFile(builtIndexPath);
    } else {
        mainWindow.loadURL('http://localhost:5173');
    }

    mainWindow.webContents.openDevTools();


    mainWindow.on('closed', () => {
        // stopBackendServer(); // if you're re-enabling backend logic
    });
}

// ----------------- IPC handlers for orchestrated test window control -----------------

/**
 * Opens or reuses a controlled test window.
 * Instead of a fixed delay, it now polls the window until a <canvas> element is detected.
 */
ipcMain.handle('open-test-window', async (event, url) => {
    const isReused = testWindow && !testWindow.isDestroyed();

    if (!isReused) {
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

        // testWindow.webContents.openDevTools();

        testWindow.on('closed', () => {
            testWindow = null;
        });
    }

    try {
        testWindow.focus();
        // Wait for the page's main frame to finish loading
        await testWindow.loadURL(url);

        // Revert to fixed delay to allow the game to fully launch
        // await waitForCanvasInWindow(testWindow, 20000); // (disabled)
        await new Promise(resolve => setTimeout(resolve, 20000)); // 20 seconds

        testWindow.focus(); // Focus again after load is complete
        return { success: true, reused: isReused };
    } catch (error) {
        console.error(`Failed to open/load test window (reused: ${isReused}):`, error.message);
        if (testWindow && !testWindow.isDestroyed()) {
            testWindow.close();
            testWindow = null;
        }
        return { success: false, error: error.message, reused: isReused };
    }
});


/**
 * Captures a screenshot of the current test window.
 * Returns base64-encoded PNG string.
 */
ipcMain.handle('capture-screenshot', async () => {
    if (!testWindow || testWindow.isDestroyed()) {
        throw new Error('Test window is not available');
    }
    testWindow.focus();
    const image = await testWindow.webContents.capturePage();
    const pngBuffer = image.toPNG();
    return pngBuffer.toString('base64');
});

/**
 * Performs a synthetic click at (x,y) in the test window.
 * If classId is 0, uses canvas pointer event simulation.
 * Otherwise, uses low-level sendInputEvent.
 * Adds a 10-second delay after the click event.
 */
ipcMain.handle('perform-click', async (event, classId, x, y) => {
    if (!testWindow || testWindow.isDestroyed()) {
        throw new Error('Test window is not available');
    }

    testWindow.focus();

    if (classId === 0) {
        // --- Simulate pointer events on canvas at (x, y) ---
        console.log(`Simulating canvas pointer events at (${x}, ${y})`);
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
        // --- Low-level click ---
        console.log(`Performing low-level click at (${x}, ${y}) with classId ${classId}`);

        try {
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
        } catch (err) {
            console.error('Low-level perform-click failed:', err);
            throw err;
        }
    }

    // Wait to allow UI transition (modal close / next screen)
    await new Promise(resolve => setTimeout(resolve, 10000));
    return { success: true };
});

/**
 * Attempts an in-DOM click by executing a page-level click dispatcher function.
 * Falls back to low-level sendInputEvent if the in-page function is absent or fails.
 */
ipcMain.handle('click-in-dom', async (event, rawX, rawY, options = {}) => {
    if (!testWindow || testWindow.isDestroyed()) {
        throw new Error('Test window is not available');
    }
    testWindow.focus();

    try {
        // Try the in-page dispatcher first
        const serializedOptions = JSON.stringify(options);
        const js = `
            (async () => {
                if (typeof window.api?.clickAt === 'function') {
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
            // Give UI time to respond
            await new Promise(resolve => setTimeout(resolve, 500));
            return { success: true, via: 'in-dom', detail: result };
        } else {
            console.warn('In-DOM click failed, falling back to low-level. Detail:', result);
            // Fallback to low-level click
            testWindow.webContents.sendInputEvent({ type: 'mouseMove', x: rawX, y: rawY });
            testWindow.webContents.sendInputEvent({ type: 'mouseDown', x: rawX, y: rawY, button: 'left', clickCount: 1 });
            testWindow.webContents.sendInputEvent({ type: 'mouseUp', x: rawX, y: rawY, button: 'left', clickCount: 1 });
            await new Promise(resolve => setTimeout(resolve, 10000));
            return { success: true, via: 'fallback-low-level', detail: result };
        }
    } catch (err) {
        console.error('click-in-dom handler error:', err);
        // As last resort, do low-level click
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


/**
 * Returns metrics about the test window including size, approximate zoom, and devicePixelRatio.
 */
ipcMain.handle('get-test-window-metrics', async () => {
    if (!testWindow || testWindow.isDestroyed()) {
        return null;
    }

    const [width, height] = testWindow.getSize();
    const zoomFactor = testWindow.webContents.getZoomFactor();
    let devicePixelRatio = 1;

    try {
        const dpr = await testWindow.webContents.executeJavaScript('window.devicePixelRatio', true);
        if (typeof dpr === 'number' && !isNaN(dpr)) {
            devicePixelRatio = dpr;
        }
    } catch (e) {
        console.warn('Failed to get devicePixelRatio from renderer, defaulting to 1:', e);
    }

    return { width, height, zoomFactor, devicePixelRatio };
});


ipcMain.handle('save-screenshot', async (event, base64Image, filename = 'screenshot') => {
    try {
        const buffer = Buffer.from(base64Image, 'base64');
        const fullPath = path.join(__dirname, `${filename}.png`);
        fs.writeFileSync(fullPath, buffer);
        console.log(`📸 Screenshot saved at: ${fullPath}`);
        return { success: true, path: fullPath };
    } catch (err) {
        console.error('❌ Failed to save screenshot:', err);
        return { success: false, error: err.message };
    }
});

// -------------------------------------------------------------------------------------

// Event when the application is ready
app.whenReady().then(() => {
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

// IPC handlers (example placeholder for backend status if needed)
ipcMain.handle('check-backend-status', async () => {
    return backendProcess !== null && !backendProcess.killed;
});