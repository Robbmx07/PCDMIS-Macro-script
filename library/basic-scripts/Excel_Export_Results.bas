' =========================================================================
' PC-DMIS Cypress Enable BASIC Script
' Purpose : Export all dimension results (legacy DIM commands) from the
'           active routine to a new Excel workbook.
' Requires: PC-DMIS CAD or CAD++, Microsoft Excel installed on the CMM PC.
' Confidence: MODERATE — the PC-DMIS object access pattern (IsDimension /
' DimensionCommand) is verified against real working examples; the Excel
' COM automation calls follow standard, well-established conventions but
' this exact combined script has not been tested against a live PC-DMIS
' session. Same GeoTol/FCF caveat as OOT_CSV_Export.bas applies — legacy
' DIM commands only.
' =========================================================================

Sub Main
    Dim App As Object
    Dim Part As Object
    Dim Cmds As Object
    Dim Cmd As Object
    Dim Dim1 As Object
    Dim xlApp As Object
    Dim xlBook As Object
    Dim xlSheet As Object
    Dim i As Integer
    Dim Row As Integer

    On Error GoTo ErrorHandler

    Set App = CreateObject("PCDLRN.Application")
    Set Part = App.ActivePartProgram

    If Part Is Nothing Then
        MsgBox "No active PC-DMIS routine detected.", vbCritical, "Execution Halted"
        Exit Sub
    End If

    Set Cmds = Part.Commands

    Set xlApp = CreateObject("Excel.Application")
    xlApp.Visible = False
    Set xlBook = xlApp.Workbooks.Add
    Set xlSheet = xlBook.Worksheets(1)

    xlSheet.Range("A1").Value = "Feature_ID"
    xlSheet.Range("B1").Value = "Nominal"
    xlSheet.Range("C1").Value = "Measured"
    xlSheet.Range("D1").Value = "Deviation"
    xlSheet.Range("E1").Value = "OutTol"

    Row = 2
    For i = 1 To Cmds.Count
        Set Cmd = Cmds.Item(i)
        If Cmd.IsDimension Then
            Set Dim1 = Cmd.DimensionCommand
            xlSheet.Range("A" & Row).Value = Dim1.ID
            xlSheet.Range("B" & Row).Value = Dim1.Nominal
            xlSheet.Range("C" & Row).Value = Dim1.Measured
            xlSheet.Range("D" & Row).Value = Dim1.Deviation
            xlSheet.Range("E" & Row).Value = Dim1.OutTol
            Row = Row + 1
        End If
    Next i

    xlBook.SaveAs "C:\CMM_Logs\" & Part.Name & "_Results.xlsx"
    xlBook.Close False
    xlApp.Quit

    Set xlSheet = Nothing
    Set xlBook = Nothing
    Set xlApp = Nothing

    MsgBox "Export complete. " & (Row - 2) & " dimension(s) written.", vbInformation, "Excel Export"
    Exit Sub

ErrorHandler:
    MsgBox "Script error: " & Err.Description, vbCritical, "Fatal Exception"
    If Not xlApp Is Nothing Then xlApp.Quit
End Sub
