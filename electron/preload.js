// filepath: electron/preload.js
const { contextBridge, ipcRenderer } = require('electron');

// Expose APIs to the renderer process
contextBridge.exposeInMainWorld('api', {
  // Example API to send a message to the main process
  sendMessage: (channel, data) => {
    ipcRenderer.send(channel, data);
  },
  // Example API to receive a message from the main process
  onMessage: (channel, func) => {
    ipcRenderer.on(channel, (event, ...args) => func(...args));
  },
  // Backend status checking
  checkBackendStatus: () => {
    return ipcRenderer.invoke('check-backend-status');
  },
  // Get backend URL
  getBackendUrl: () => {
    return 'http://localhost:7000';
  }
});

contextBridge.exposeInMainWorld('electronAPI', {
  runComplianceFlow: (args) => ipcRenderer.invoke('run-compliance-flow', args),
});