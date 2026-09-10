' =========================================================================
' PC-DMIS Cypress Enable BASIC Script
' Purpose : Increment a part counter variable by 1 each time this script
'           runs (e.g. once per loop iteration in a batch-run routine).
' Requires: PC-DMIS CAD or CAD++ (Basic scripting is not available in
'           PC-DMIS Pro).
' Requires: the routine must already have a V_PART_COUNT variable
'           declared before this script runs, e.g.:
'               ASSIGN/V_PART_COUNT = 0
'           placed once, before the loop, near the top of the routine.
' Note: SetVariableValue only holds the new value for the rest of THIS
' execution run. If you need the count to persist permanently across
' separate executions/saves, use the PutText method instead (confirmed
' from Hexagon's own Automation Objects documentation).
' =========================================================================

Sub Main
    Dim App As Object
    Dim Part As Object
    Dim CounterVar As Object
    Dim NewCount As Double

    On Error GoTo ErrorHandler

    Set App = CreateObject("PCDLRN.Application")
    Set Part = App.ActivePartProgram

    If Part Is Nothing Then
        MsgBox "No active PC-DMIS routine detected.", vbCritical, "Execution Halted"
        Exit Sub
    End If

    ' Read the current count
    Set CounterVar = Part.GetVariableValue("V_PART_COUNT")
    NewCount = CounterVar.DoubleValue + 1

    ' Write the incremented value back into the same variable object
    CounterVar.DoubleValue = NewCount
    Part.SetVariableValue "V_PART_COUNT", CounterVar

    MsgBox "Part count is now: " & NewCount, vbInformation, "Counter Updated"
    Exit Sub

ErrorHandler:
    MsgBox "Script error: " & Err.Description, vbCritical, "Fatal Exception"
End Sub
