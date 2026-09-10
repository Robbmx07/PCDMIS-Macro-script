' =========================================================================
' PC-DMIS Cypress Enable BASIC Script
' Purpose : After a measurement routine executes, scan every dimension
'           command and log any out-of-tolerance result to a CSV file.
' Requires: PC-DMIS CAD or CAD++ (Basic scripting is not available in
'           PC-DMIS Pro).
' Verified against Hexagon's PC-DMIS Automation Objects documentation and
' multiple confirmed working examples from the PC-DMIS user community.
' Known caveat: this uses the legacy DimensionCommand object model. If your
' routine uses modern Geometric Tolerance / Feature Control Frame commands
' (common from PC-DMIS 2020.2 onward) instead of legacy DIM blocks, test
' against one of those routines before relying on this in production.
' =========================================================================

Sub Main
    Dim App As Object
    Dim Part As Object
    Dim Cmds As Object
    Dim Cmd As Object
    Dim Dim1 As Object
    Dim FilePath As String
    Dim FileNum As Integer
    Dim OutCount As Integer
    Dim i As Integer

    On Error GoTo ErrorHandler

    Set App = CreateObject("PCDLRN.Application")
    Set Part = App.ActivePartProgram

    If Part Is Nothing Then
        MsgBox "No active PC-DMIS routine detected.", vbCritical, "Execution Halted"
        Exit Sub
    End If

    Set Cmds = Part.Commands

    ' Make sure C:\CMM_Logs exists on this machine before running, or
    ' change this path to a folder you know exists and is writable.
    FilePath = "C:\CMM_Logs\Out_Of_Tolerance_Log.csv"
    FileNum = FreeFile

    Open FilePath For Append As #FileNum

    ' Write a header row only if the file is new/empty
    If LOF(FileNum) = 0 Then
        Print #FileNum, "Timestamp,Routine_Name,Feature_ID,Nominal,Measured,Deviation,OutTol"
    End If

    OutCount = 0
    For i = 1 To Cmds.Count
        Set Cmd = Cmds.Item(i)
        If Cmd.IsDimension Then
            ' Dimension data lives on the DimensionCommand sub-object,
            ' not directly on the Command object.
            Set Dim1 = Cmd.DimensionCommand
            If Dim1.OutTol <> 0 Then
                Print #FileNum, Format(Now, "yyyy-mm-dd hh:nn:ss") & "," & _
                    Part.Name & "," & _
                    Dim1.ID & "," & _
                    Dim1.Nominal & "," & _
                    Dim1.Measured & "," & _
                    Dim1.Deviation & "," & _
                    Dim1.OutTol
                OutCount = OutCount + 1
            End If
        End If
    Next i

    Close #FileNum

    MsgBox "Scan complete. " & OutCount & " out-of-tolerance feature(s) logged.", _
        vbInformation, "Automation Result"
    Exit Sub

ErrorHandler:
    MsgBox "Script error: " & Err.Description, vbCritical, "Fatal Exception"
    If FileNum > 0 Then Close #FileNum
End Sub
