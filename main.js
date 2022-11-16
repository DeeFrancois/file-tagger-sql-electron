// Modules to control application life and create native browser window
const electron = require("electron");
const {app, protocol, dialog,BrowserWindow} = electron;
const path = require('path')
const url = require('url')


// app.disableHardwareAcceleration()
// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.

app.on("ready", () => {
    const mainWindow = new BrowserWindow({
      width: 1050,
      height: 690,
      // minHeight: 690,
      // minWidth: 542,
      autoHideMenuBar:false,
      frame:true,
      transparent:false,
      useContentSize:false,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false,
        enableRemoteModule: true,
        webSecurity:true, //This is apparently bad but for my offline, non-deployed project it seems fine?
        nodeIntegrationInWorker:true,
      },
    });
    
    
    mainWindow.loadURL(`http://localhost:8000/main.html`);
    // opened(mainWindow.id);
  });

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') app.quit()
});

app.on('activate', function () {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) createWindow()
});

app.whenReady().then(() => {
  protocol.registerFileProtocol('atom', (request, callback) => {
    const filePath = url.fileURLToPath('file://' + request.url.slice('atom://'.length))
    callback(filePath)
  });
  
})

// export function clack(){
//   console.log("YAYYY");
// }
// exports.clack = () => console.log("yayy");
// https://stackoverflow.com/questions/50781741/select-and-display-an-image-from-the-filesystem-with-electron