const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

// Global variable to store backend process
let backendProcess = null;

// ----------------- EDIT: managed test window reference -----------------
let testWindow = null; // Controlled window used for screenshot / click orchestration
// ----------------------------------------------------------------------

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

    // mainWindow.webContents.openDevTools();

    mainWindow.on('closed', () => {
        // stopBackendServer(); // if you're re-enabling backend logic
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

    // testWindow.webContents.openDevTools();

    testWindow.on('closed', () => {
        testWindow = null;
    });

    // Give the app time to fully render including modals
    await new Promise(resolve => setTimeout(resolve, 20000));
    testWindow.focus();
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
    testWindow.focus();
    const image = await testWindow.webContents.capturePage();
    const pngBuffer = image.toPNG();
    return pngBuffer.toString('base64');
});

/**
 * Performs a synthetic low-level click at (x,y) in the test window.
 * Adds a 10-second delay after the click event.
 */
ipcMain.handle('perform-click', async (event, x, y) => {
    if (!testWindow || testWindow.isDestroyed()) {
        throw new Error('Test window is not available');
    }

    testWindow.focus();

    try {
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
    } catch (err) {
        console.error('Low-level perform-click failed:', err);
        throw err;
    }

    // Wait to allow UI transition (modal close / next screen)
    await new Promise(resolve => setTimeout(resolve, 10000));
    return { success: true };
});

/**
 * Attempts an in-DOM click by executing a page-level click dispatcher function.
 * Falls back to low-level sendInputEvent if the in-page function is absent or fails.
 *
 * Expected in-page function signature:
 *   // exposed globally (e.g., via preload) as window.clickAtXY
 *   // returns a result object { success: boolean, method: string, ... }
 *   clickAtXY(rawX, rawY, options)
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
                if (typeof window.clickAtXY === 'function') {
                    try {
                        return await window.clickAtXY(${rawX}, ${rawY}, ${serializedOptions});
                    } catch (e) {
                        return { success: false, error: 'clickAtXY threw: ' + e.toString() };
                    }
                } else if (typeof window.api?.clickAt === 'function') {
                    // If you exposed via api.clickAt instead
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
            await new Promise(resolve => setTimeout(resolve, 500)); // shorter because in-page click is immediate
            return { success: true, via: 'in-dom', detail: result };
        } else {
            console.warn('In-DOM click failed or not available, falling back to low-level. Detail:', result);
            // Fallback to low-level click using same coords
            testWindow.webContents.sendInputEvent({ type: 'mouseMove', x: rawX, y: rawY });
            testWindow.webContents.sendInputEvent({
                type: 'mouseDown',
                x: rawX,
                y: rawY,
                button: 'left',
                clickCount: 1,
            });
            testWindow.webContents.sendInputEvent({
                type: 'mouseUp',
                x: rawX,
                y: rawY,
                button: 'left',
                clickCount: 1,
            });
            await new Promise(resolve => setTimeout(resolve, 10000));
            return { success: true, via: 'fallback-low-level', detail: result };
        }
    } catch (err) {
        console.error('click-in-dom handler error:', err);
        // As last resort, do low-level click
        try {
            testWindow.webContents.sendInputEvent({ type: 'mouseMove', x: rawX, y: rawY });
            testWindow.webContents.sendInputEvent({
                type: 'mouseDown',
                x: rawX,
                y: rawY,
                button: 'left',
                clickCount: 1,
            });
            testWindow.webContents.sendInputEvent({
                type: 'mouseUp',
                x: rawX,
                y: rawY,
                button: 'left',
                clickCount: 1,
            });
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

    // Attempt to get devicePixelRatio from the page context
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

// ------------------------------------------------------------------------------------------------------------------

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
