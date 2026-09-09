const { app, BrowserWindow } = require("electron");
const path = require("path");

const ICON = path.join(__dirname, "icon.ico");

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 800,
    title: "Making Death Count – Vanuatu",
    icon: ICON,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  win.loadFile(path.join(__dirname, "..", "index.html"));
}

app.whenReady().then(() => {
  if (process.platform === "win32") {
    app.setAppUserModelId("gov.vanuatu.making-death-count");
  }
  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
