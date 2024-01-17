const { app, BrowserWindow, ipcMain } = require("electron");
const { join } = require("path");
const { spawn } = require('child_process');
const net = require('net');


let mainWindow;
let pythonProcess = null;
let client = null;

function createPythonProcess() {
const pythonPath = 'C:\\Users\\TEST-USER\\.pyenv\\pyenv-win\\versions\\3.8.10\\python.exe'; // Correct Python path
const pythonScriptPath = join(__dirname, 'jumping.py');
pythonProcess = spawn(pythonPath, [pythonScriptPath]);

let retryInterval = 1000; // Retry every 2 seconds
let maxRetries = 5;
let retries = 0;

  // Setup TCP client connection
  function connectClient() {

  client = new net.Socket();
  client.connect(5002, '127.0.0.1', () => {
    console.log('Connected to Python server');
    mainWindow.webContents.send('server-status', 'connected');
    retries = 0; // Reset retry count on successful connection
  });

  client.on('error', (err) => {
    console.error('Socket error:', err);
    if (retries < maxRetries) {
      setTimeout(connectClient, retryInterval);
      retries++;
    } else {
      mainWindow.webContents.send('server-status', 'failed');
    }
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
    mainWindow.webContents.send('server-status', 'disconnected');
  });
}


connectClient(); // Initial attempt to connect

  // Handle pythonProcess stdout, stderr, etc.
}

function killPythonProcess() {
  if (client) {
    client.destroy(); // Close the TCP connection
    client = null;
  }

  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}


function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 1200,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: join(__dirname, "preload.js"),
    },
  });

  mainWindow.loadFile(join(__dirname, "index.html"));
  mainWindow.webContents.openDevTools();


  mainWindow.on("closed", () => {
    //client.destroy(); // Close the TCP connection
    pythonProcess.kill(); // Terminate Python process
    mainWindow = null;
  });
}



app.on("ready", createWindow);

ipcMain.on('start-server', (event) => {
createPythonProcess();
});

ipcMain.on('stop-server', (event) => {
killPythonProcess();
});

ipcMain.on('save-command', (event, command) => {
  if (client) {
    client.write(command);
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (mainWindow === null) createWindow
});