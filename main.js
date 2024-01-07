// main.js
const { app, BrowserWindow, ipcMain } = require("electron");
const { join } = require("path");
const { exec } = require("child_process");
const { spawn } = require('child_process');
const url = require('url');

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

  // Load the index.html file
  mainWindow.loadURL(url.format({
    pathname: join(__dirname, './index.html'),
    protocol: 'file:',
    slashes: true
  }));

  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  const pythonScriptPath = join(__dirname, 'jumping.py');
  const pythonProcess = spawn('python', [pythonScriptPath]);

  let buffer = '';

  pythonProcess.stdout.on('data', (data) => {
    const messages = data.toString().split('\n');
    messages.forEach((message) => {
      try {
        const framesData = JSON.parse(message);
        console.log('Received frames:', framesData);
        mainWindow.webContents.send('frames', framesData);
        console.log('Frames data sent successfully.');
      } catch (parseError) {
        if (parseError instanceof SyntaxError) {
          // Ignore non-JSON log messages
          console.log('Log:', message);
        } else {
          console.error(parseError.message);
        }
      }
    });
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error executing Python script: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python script finished with code ${code}`);
  });
}

app.on("ready", createWindow);

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", function () {
  if (mainWindow === null) createWindow();
});

let renderedFrames = [];

ipcMain.on('frames', (event, framesData) => {
  // Use framesData to update the display on your Electron.js app
  console.log(framesData);
  mainWindow.webContents.send('frames', framesData);

  // Add the rendered frame path to the list
  renderedFrames.push(framesData.frame_path);
});

ipcMain.handle('get-rendered-frames', (event) => {
  // Send the list of rendered frames to the renderer process
  return renderedFrames;
});

ipcMain.on('clear-rendered-frames', (event) => {
  // Clear the list of rendered frames
  renderedFrames = [];
});
