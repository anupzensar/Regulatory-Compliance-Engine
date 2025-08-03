// filepath: electron/preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Existing utility methods
  sendMessage: (channel, data) => {
    ipcRenderer.send(channel, data);
  },
  onMessage: (channel, func) => {
    ipcRenderer.on(channel, (event, ...args) => func(...args));
  },
  checkBackendStatus: () => {
    return ipcRenderer.invoke('check-backend-status');
  },
  getBackendUrl: () => {
    return 'http://localhost:7000';
  },

  // ----------------- EDIT: new orchestrator primitives exposed -----------------
  openTestWindow: (url) => ipcRenderer.invoke('open-test-window', url),
  captureScreenshot: () => ipcRenderer.invoke('capture-screenshot'),
  performClick: (x, y) => ipcRenderer.invoke('perform-click', x, y),
  getTestWindowMetrics: () => ipcRenderer.invoke('get-test-window-metrics'),
  // ---------------------------------------------------------------------------  
});
