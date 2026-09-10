' =========================================================================
' PC-DMIS Cypress Enable BASIC Script
' Purpose : Validate the format of an operator-entered serial number
'           (expects "SN-" followed by exactly 4 digits, e.g. SN-0248).
'           Sets a V_SN_VALID flag (1/0) that the native routine checks
'           to decide whether to re-prompt the operator.
' Requires: PC-DMIS CAD or CAD++ (Basic scripting is not available in
'           PC-DMIS Pro).
' Requires: V_SN_INPUT and V_SN_VALID must already exist in the routine
'           before this script runs — see Validate_SerialNumber_Insert.txt
'           for the full native wrapper.
' Confidence: HIGH — variable object access pattern (.StringValue,
' .DoubleValue, GetVariableValue/SetVariableValue) confirmed against
' Hexagon's own documentation and multiple independent working examples.
' =========================================================================

Sub Main
    Dim App As Object
    Dim Part As Object
    Dim InputVar As Object
    Dim ValidVar As Object
    Dim SN As String
    Dim IsValid As Boolean

    On Error GoTo ErrorHandler

    Set App = CreateObject("PCDLRN.Application")
    Set Part = App.ActivePartProgram

    If Part Is Nothing Then
        MsgBox "No active PC-DMIS routine detected.", vbCritical, "Execution Halted"
        Exit Sub
    End If

    Set InputVar = Part.GetVariableValue("V_SN_INPUT")
    SN = InputVar.StringValue

    ' Format check: "SN-" prefix + exactly 4 numeric digits
    IsValid = False
    If Len(SN) = 7 Then
        If Left(SN, 3) = "SN-" Then
            If IsNumeric(Right(SN, 4)) Then
                IsValid = True
            End If
        End If
    End If

    Set ValidVar = Part.GetVariableValue("V_SN_VALID")
    If IsValid Then
        ValidVar.DoubleValue = 1
    Else
        ValidVar.DoubleValue = 0
    End If
    Part.SetVariableValue "V_SN_VALID", ValidVar

    Exit Sub

ErrorHandler:
    MsgBox "Script error: " & Err.Description, vbCritical, "Fatal Exception"
End Sub
