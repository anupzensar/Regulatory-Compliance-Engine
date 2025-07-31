const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runFlow(url, flow) {
    const win = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
        },
    });

    await win.loadURL(url);

    for (let i = 0; i < flow.length; i++) {
        await delay(5000);

        // Take screenshot
        const image = await win.capturePage();
        const screenshot = image.toPNG();

        // Call your API (update fields as needed)
        const apiResponse = await axios.post('http://localhost:7000/get-coordinates', {
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

// Register the handler BEFORE app.whenReady()
ipcMain.handle('run-compliance-flow', async (event, { url, flow }) => {
    await runFlow(url, flow);
    return { success: true };
});

app.whenReady().then(() => {
    // Create your main window here
    const mainWindow = new BrowserWindow({
        width: 1024,
        height: 768,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
        },
    });
    mainWindow.loadURL('http://localhost:3000'); // or your React build/dev server
});