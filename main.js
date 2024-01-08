// main.js

const { app, BrowserWindow, ipcMain } = require("electron");
const { join } = require("path");
const { exec } = require("child_process");
const { spawn } = require('child_process');
const url = require('url');
const fs = require('fs')
const { promisify } = require('util');

const unlinkAsync = promisify(fs.unlink);
const readdirAsync = promisify(fs.readdir);  // Add this line

let mainWindow;
let lastRenderedFramePath = null;
let pythonProcess; // Declare pythonProcess globally
const outputImagesPath = join(__dirname, 'output_images');

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: join(__dirname, "./preload.js"),
    },
  });

  mainWindow.loadFile("index.html");

  mainWindow.on("closed", function () {
    mainWindow = null;
  });

  mainWindow.loadURL(url.format({
    pathname: join(__dirname, './index.html'),
    protocol: 'file:',
    slashes: true
  }));

  mainWindow.webContents.openDevTools();
}

app.on("ready", createWindow);

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", function () {
  if (mainWindow === null) createWindow();
});

async function stopPythonScript() {
  if (pythonProcess) {
    pythonProcess.kill();
    console.log("pythonProcess killed");

     // Delete all frames in the output_images directory
     try {
      const files = await readdirAsync(outputImagesPath);
      const unlinkPromises = files.map((file) => unlinkAsync(join(outputImagesPath, file)));
      await Promise.all(unlinkPromises);
      console.log('All frames deleted');
    } catch (err) {
      console.error(`Error deleting frames: ${err}`);
    }


  }
}

function startPythonScript() {
  const pythonScriptPath = join(__dirname, 'jumping.py');
  pythonProcess = spawn('python', [pythonScriptPath]);

  pythonProcess.stdout.on('data', (data) => {
    const messages = data.toString().split('\n');
    messages.forEach((message) => {
      try {
        const framesData = JSON.parse(message);
        console.log('Received frames:', framesData);
        mainWindow.webContents.send('frames', framesData);
        console.log('Frames data sent successfully.');

        // Update the last rendered frame path
        lastRenderedFramePath = framesData.frame_path;
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

    //Remove the last rendered frame from disk
    // if (lastRenderedFramePath) {
    //   fs.unlink(lastRenderedFramePath, (err) => {
    //     if (err) {
    //       console.error(`Error deleting frame: ${err}`);
    //     } else {
    //       console.log(`Frame deleted: ${lastRenderedFramePath}`);
    //     }
    //   });
    // }
  });
}

ipcMain.on('stop-python-script', () => {
  stopPythonScript();
});

ipcMain.on('start-python-script', () => {
  startPythonScript();
});