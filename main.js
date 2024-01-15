const { app, BrowserWindow, ipcMain } = require("electron");
const { join } = require("path");
const { spawn } = require('child_process');
const net = require('net');

let mainWindow;
let pythonProcess = null;
let client = null;

const pythonPath = 'C:\\Users\\TEST-USER\\.pyenv\\pyenv-win\\versions\\3.8.10\\python.exe'; // Correct Python path
const pythonScriptPath = join(__dirname, 'jumping.py');
pythonProcess = spawn(pythonPath, [pythonScriptPath]);

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: join(__dirname, "preload.js"),
    },
  });

  mainWindow.loadFile(join(__dirname, "index.html"));
  mainWindow.webContents.openDevTools();

  // Setup TCP client
  const client = new net.Socket();
  client.connect(5002, '127.0.0.1', () => {
      console.log('Connected to Python server');
  });

  let buffer = '';

  client.on('data', function(dataBuffer) {
    buffer += dataBuffer.toString();
    let messages = buffer.split('\n'); // Split using the delimiter
    buffer = messages.pop();
    
    messages.forEach((message) => {
        if (message) {
            try {
                const frameData = JSON.parse(message);
                mainWindow.webContents.send('frame-data', frameData);
            } catch (err) {
                console.error('Error parsing data:', err.message);
            }
        }
    });
});

  client.on('close', () => {
    console.log('Connection closed');
  });

  // Setup Python process
  // const pythonPath = 'C:\\Users\\TEST-USER\\.pyenv\\pyenv-win\\versions\\3.8.10\\python.exe';
  // const pythonScriptPath = join(__dirname, 'jumping.py');
  // const pythonProcess = spawn(pythonPath, [pythonScriptPath]);

  // pythonProcess.stderr.on('data', (data) => {
  //   console.error(`Error from Python script: ${data}`);
  // });

  // pythonProcess.on('close', (code) => {
  //   console.log(`Python script exited with code ${code}`);
  // });

  mainWindow.on("closed", () => {
    client.destroy(); // Close the TCP connection
    pythonProcess.kill(); // Terminate Python process
    mainWindow = null;
  });
}

app.on("ready", createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (mainWindow === null) createWindow
});