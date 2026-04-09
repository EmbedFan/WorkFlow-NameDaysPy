' Run application hidden
Dim objShell, objFSO, scriptPath, batPath, mainPyPath, pythonPath, cmd

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
batPath = objFSO.BuildPath(scriptPath, "run_hidden.bat")
mainPyPath = objFSO.BuildPath(scriptPath, "main.py")
pythonPath = objFSO.BuildPath(scriptPath, ".venv\Scripts\python.exe")

' Check if batch file exists, if not try to run main.py directly
If objFSO.FileExists(batPath) Then
    ' Run the batch file hidden (show = 0)
    objShell.Run batPath, 0, false
ElseIf objFSO.FileExists(pythonPath) And objFSO.FileExists(mainPyPath) Then
    ' If batch file not found, run Python directly with venv
    objShell.Run pythonPath & " " & mainPyPath, 0, false
Else
    ' Error: cannot find required files
    MsgBox "Error: Cannot find required files in " & scriptPath, vbCritical, "NameDaysApp Startup Error"
End If

' Clean up
Set objFSO = Nothing
Set objShell = Nothing
