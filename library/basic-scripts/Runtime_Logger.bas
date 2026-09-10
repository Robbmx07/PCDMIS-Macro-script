' =========================================================================
' PC-DMIS Cypress Enable BASIC Script
' Purpose : Record routine start and end time and log total elapsed
'           runtime to a text file. Requires TWO insertion points in
'           the routine — see Runtime_Logger_Insert.txt.
' Requires: PC-DMIS CAD or CAD++.
' Requires: V_START_TIME variable declared before the first insertion
'           point, e.g.  ASSIGN/V_START_TIME = ""
' Confidence: MODERATE — variable read/write pattern is verified; file
' logging is standard VB file I/O. This exact two-Sub, two-insertion-point
' script has not been tested against a live PC-DMIS session.
' =========================================================================

Sub StartTimer
    Dim App As Object
    Dim Part As Object
    Dim StartVar As Object

    On Error GoTo ErrorHandler

    Set App = CreateObject("PCDLRN.Application")
    Set Part = App.ActivePartProgram
    If Part Is Nothing Then Exit Sub

    Set StartVar = Part.GetVariableValue("V_START_TIME")
    StartVar.StringValue = CStr(Now)
    Part.SetVariableValue "V_START_TIME", StartVar
    Exit Sub

ErrorHandler:
    MsgBox "StartTimer error: " & Err.Description, vbCritical, "Fatal Exception"
End Sub

Sub StopTimer
    Dim App As Object
    Dim Part As Object
    Dim StartVar As Object
    Dim StartTime As Date
    Dim ElapsedSeconds As Double
    Dim FilePath As String
    Dim FileNum As Integer

    On Error GoTo ErrorHandler

    Set App = CreateObject("PCDLRN.Application")
    Set Part = App.ActivePartProgram
    If Part Is Nothing Then Exit Sub

    Set StartVar = Part.GetVariableValue("V_START_TIME")
    StartTime = CDate(StartVar.StringValue)
    ElapsedSeconds = DateDiff("s", StartTime, Now)

    FilePath = "C:\CMM_Logs\Runtime_Log.csv"
    FileNum = FreeFile
    Open FilePath For Append As #FileNum
    If LOF(FileNum) = 0 Then
        Print #FileNum, "Timestamp,Routine_Name,Elapsed_Seconds"
    End If
    Print #FileNum, Format(Now, "yyyy-mm-dd hh:nn:ss") & "," & Part.Name & "," & ElapsedSeconds
    Close #FileNum

    MsgBox "Runtime logged: " & ElapsedSeconds & " seconds.", vbInformation, "Runtime Logger"
    Exit Sub

ErrorHandler:
    MsgBox "StopTimer error: " & Err.Description, vbCritical, "Fatal Exception"
    If FileNum > 0 Then Close #FileNum
End Sub
