Set WshShell = CreateObject("WScript.Shell")
strDir = WshShell.CurrentDirectory
WshShell.Run "pythonw.exe """ & strDir & "\pet.py""", 0, False

