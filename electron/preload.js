// electron/preload.js
const { contextBridge, ipcRenderer } = require('electron');

/**
 * In-page dispatcher: synthesizes a click at given raw (pixel) coordinates,
 * accounting for devicePixelRatio and scrolling, targeting the topmost element.
 * Retries if the element isn’t immediately present. Optional fallback selector.
 */
async function clickAtXY(rawX, rawY, options = {}) {
    const {
        maxRetries = 5,
        retryDelay = 100, // ms
        fallbackSelector = null, // e.g. '.modal .close-btn'
    } = options;

    const scale = window.devicePixelRatio || 1;
    const clientX = rawX / scale;
    const clientY = rawY / scale;

    function dispatchClickOnElement(el) {
        if (!el) return false;
        ['mousedown', 'mouseup', 'click'].forEach(type => {
            const evt = new MouseEvent(type, {
                bubbles: true,
                cancelable: true,
                clientX,
                clientY,
                view: window,
                button: 0,
            });
            el.dispatchEvent(evt);
        });
        return true;
    }

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        const el = document.elementFromPoint(clientX, clientY);
        if (el) {
            const success = dispatchClickOnElement(el);
            if (success) {
                return { success: true, method: 'direct', tag: el.tagName, attempt };
            }
        }

        const stack = document.elementsFromPoint(clientX, clientY);
        for (const candidate of stack) {
            const success = dispatchClickOnElement(candidate);
            if (success) {
                return { success: true, method: 'stack', tag: candidate.tagName, attempt };
            }
        }

        await new Promise(r => setTimeout(r, retryDelay));
    }

    if (fallbackSelector) {
        const fb = document.querySelector(fallbackSelector);
        if (fb) {
            try {
                fb.click();
                return { success: true, method: 'fallback-selector', selector: fallbackSelector };
            } catch (e) {
                return { success: false, error: `fallback-selector click threw: ${e}` };
            }
        }
    }

    return { success: false, reason: 'no clickable target found after retries' };
}

// ---- Context Bridge Exports ----
contextBridge.exposeInMainWorld('api', {
    // Backend & messaging utilities
    sendMessage: (channel, data) => ipcRenderer.send(channel, data),
    onMessage: (channel, func) => ipcRenderer.on(channel, (event, ...args) => func(...args)),
    checkBackendStatus: () => ipcRenderer.invoke('check-backend-status'),
    getBackendUrl: () => 'http://127.0.0.1:7000',

    openTestWindow: (url) => ipcRenderer.invoke('open-test-window', url),
    captureScreenshot: () => ipcRenderer.invoke('capture-screenshot'),
    performClick: (classId, x, y) => ipcRenderer.invoke('perform-click', classId, x, y),
    clickInDOM: (rawX, rawY, options) => ipcRenderer.invoke('click-in-dom', rawX, rawY, options),
    getTestWindowMetrics: () => ipcRenderer.invoke('get-test-window-metrics'),

    // In-page click simulation
    clickAt: (x, y, options) => clickAtXY(x, y, options),

    // DOM inspection utilities
    isElementPresent: (selector) => {
        try {
            return !!document.querySelector(selector);
        } catch (e) {
            return false;
        }
    },

    querySelectorText: (selector) => {
        try {
            const el = document.querySelector(selector);
            return el ? el.innerText : null;
        } catch (e) {
            return null;
        }
    },

    elementAtPoint: (rawX, rawY) => {
        const scale = window.devicePixelRatio || 1;
        const clientX = rawX / scale;
        const clientY = rawY / scale;
        const el = document.elementFromPoint(clientX, clientY);
        if (!el) return null;
        return {
            tag: el.tagName,
            className: el.className,
            id: el.id,
            boundingClientRect: el.getBoundingClientRect?.(),
        };
    },
});