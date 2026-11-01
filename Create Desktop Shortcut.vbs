Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
strDir = WshShell.CurrentDirectory
Set oShortcut = WshShell.CreateShortcut(strDesktop & "\PET.EXE.lnk")
oShortcut.TargetPath = strDir & "\Start Pet.vbs"
oShortcut.WorkingDirectory = strDir
oShortcut.Description = "Launch PET.EXE Desktop Companion"
oShortcut.Save
MsgBox "Desktop Shortcut 'PET.EXE' created successfully!", vbInformation, "PET.EXE"

