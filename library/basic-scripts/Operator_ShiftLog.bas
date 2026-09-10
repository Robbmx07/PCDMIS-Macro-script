' =========================================================================
' PC-DMIS Cypress Enable BASIC Script
' Purpose : Log operator/employee ID with a timestamp and routine name
'           to a shift log CSV, for run traceability.
' Requires: PC-DMIS CAD or CAD++.
' Requires: V_EMP_ID variable populated via COMMENT/INPUT before this
'           script runs — see Operator_ShiftLog_Insert.txt.
' Confidence: HIGH — reuses the same verified variable-read and
' file-logging pattern as OOT_CSV_Export.bas and Validate_SerialNumber.bas.
' =========================================================================

Sub Main
    Dim App As Object
    Dim Part As Object
    Dim EmpVar As Object
    Dim EmpID As String
    Dim FilePath As String
    Dim FileNum As Integer

    On Error GoTo ErrorHandler

    Set App = CreateObject("PCDLRN.Application")
    Set Part = App.ActivePartProgram

    If Part Is Nothing Then
        MsgBox "No active PC-DMIS routine detected.", vbCritical, "Execution Halted"
        Exit Sub
    End If

    Set EmpVar = Part.GetVariableValue("V_EMP_ID")
    EmpID = EmpVar.StringValue

    FilePath = "C:\CMM_Logs\Shift_Log.csv"
    FileNum = FreeFile
    Open FilePath For Append As #FileNum
    If LOF(FileNum) = 0 Then
        Print #FileNum, "Timestamp,Routine_Name,Employee_ID"
    End If
    Print #FileNum, Format(Now, "yyyy-mm-dd hh:nn:ss") & "," & Part.Name & "," & EmpID
    Close #FileNum

    Exit Sub

ErrorHandler:
    MsgBox "Script error: " & Err.Description, vbCritical, "Fatal Exception"
    If FileNum > 0 Then Close #FileNum
End Sub
