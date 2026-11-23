const {contextBridge,ipcRenderer}=require("electron");
contextBridge.exposeInMainWorld("komarovaDesktop",Object.freeze({chooseFolder:()=>ipcRenderer.invoke("folder:choose"),chooseArchive:()=>ipcRenderer.invoke("archive:choose"),scanFolder:p=>ipcRenderer.invoke("folder:scan",p),importFiles:p=>ipcRenderer.invoke("archive:import",p),openPath:p=>ipcRenderer.invoke("archive:open",p)}));
