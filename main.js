// main.js
const { app, BrowserWindow, ipcMain   } = require("electron");
const { PythonShell } = require('python-shell');

const { join } = require("path");
const { exec } = require("child_process");
const {spawn} = require('child_process');
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

  pythonProcess.stdout.on('data', (data) => {
    try {
      const framesData = JSON.parse(data);
      console.log('Received frames:', framesData);
      mainWindow.webContents.send('frames', framesData);
      console.log('Frames data sent successfully.');
  } catch (parseError) {
      console.error(parseError.message);
  }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error executing Python script: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python script finished with code ${code}`);
  });



   // Run Python script using PythonShell
   //const pythonScriptPath = join(__dirname, 'jumping.py');

  //  exec(`python ${pythonScriptPath}`, (error, stdout, stderr) => {
  //   if (error) {
  //     console.error(`Error executing Python script: ${error.message}`);
  //   } else {
  //     console.log('Python script finished');
  //   }
  // });



  // PythonShell.run('jumping.py', options, function (err) {
  //   if (err) throw err;
  //   console.log('Python script finished');
  // });

  // // Run Python script
  // PythonShell.run('real_sense_capture.py', null, function (err) {
  //   if (err) throw err;
  //   console.log('Python script finished');
  // });


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
    exec(`python ${scriptPath}`, (error, stdout, stderr) => {
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

// IPC to receive frames from Python
ipcMain.on('frames', (event, framesData) => {
  // Use framesData to update the display on your Electron.js app
  console.log(framesData);
});
