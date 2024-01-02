// main.js
const { app, BrowserWindow, ipcMain } = require("electron");
const { join } = require("path");
const { exec } = require("child_process");

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false, // Add this line
      preload: join(__dirname, "./preload.js"), // Add this line
    },
  });

  mainWindow.loadFile("index.html");

  mainWindow.on("closed", function () {
    mainWindow = null;
  });
}

app.on("ready", createWindow);

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", function () {
  if (mainWindow === null) createWindow();
});

// Add the following IPC handler
ipcMain.handle("run-python-script", async (event, scriptPath) => {
  return new Promise((resolve, reject) => {
    exec(`python3 ${scriptPath}`, (error, stdout, stderr) => {
      if (error) {
        reject(error.message);
      } else {
        try {
          const parsedData = JSON.parse(stdout);
          resolve(parsedData);
        } catch (parseError) {
          reject(parseError.message);
        }
      }
    });
  });
});
