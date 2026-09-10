'=====================================================================
' AlignmentRepeatability.bas
'
' PURPOSE
'   Re-runs the active part's alignment routine N times in a row and
'   checks how much the resulting coordinate system moves between
'   runs. This is a repeatability check for the alignment itself
'   (not a full GR&R on measured features) - it answers "if I redo
'   this alignment from scratch, does the origin/orientation come
'   back to the same place every time, within tolerance?"
'
'   For each trial it records:
'     - Alignment origin:      OriginX, OriginY, OriginZ
'     - Alignment orientation: the active coordinate system's Z-axis
'                               vector (ZAxisI, ZAxisJ, ZAxisK)
'   Origin + Z-axis vector is used instead of Euler angles because
'   it's what PC-DMIS reports directly and avoids extra angle-
'   conversion math that would just be another thing to verify.
'
'   After all trials it computes the range (max-min) of each value
'   across trials, compares that range to the tolerances below, and
'   writes a PASS/FAIL summary to a CSV log file plus a message box.
'
' VERIFICATION STATUS
'   Connecting to PC-DMIS (CreateObject("PCDLRN.Application") and
'   App.ActivePartProgram) is confirmed against Hexagon's own
'   documented sample - see
'   library/reference/hexagon-sample-01-increment-variable/. Everything
'   else still tagged 'VERIFY: below is a best-guess at the correct
'   PC-DMIS Basic object/property/method name and has not been tested.
'   Everything else (loop, math, file I/O, dialogs) is plain Basic and
'   should run as written in any Basic host.
'
'   To validate the remaining VERIFY lines: open this in PC-DMIS's Basic
'   editor with a part program loaded that has its alignment commands
'   wrapped in LABEL/ALIGN_START ... LABEL/ALIGN_END (see "SETUP
'   REQUIRED" below), run it, and send back the exact error text + line
'   number for anything that fails. That will let me fix the specific
'   VERIFY line instead of re-guessing the whole script.
'
'   Also note: this script must currently be run standalone from PC-
'   DMIS's Basic editor. To call it from inside a part program instead
'   (the documented pattern), wrap it in the part program like:
'       CS1  =SCRIPT/FILENAME= <path>\AlignmentRepeatability.bas
'            FUNCTION/Main,SHOW=YES,,
'            STARTSCRIPT/
'            ENDSCRIPT/
'
' SETUP REQUIRED IN THE PART PROGRAM
'   Wrap the alignment command block in the loaded part program with
'   two label commands so this script knows what range to re-run:
'
'       LABEL/ALIGN_START
'       ... (leveling / origin / rotation alignment commands) ...
'       LABEL/ALIGN_END
'
'=====================================================================

Option Explicit

' ---- Configuration -------------------------------------------------
Const NUM_TRIALS_DEFAULT   As Integer = 10
Const TOL_LINEAR_MM        As Double  = 0.010   ' max allowed origin spread (mm)
Const TOL_VECTOR           As Double  = 0.0005  ' max allowed Z-axis vector spread (unitless direction cosine)
Const ALIGN_START_LABEL    As String  = "ALIGN_START"
Const ALIGN_END_LABEL      As String  = "ALIGN_END"
Const LOG_FILE_PATH        As String  = "C:\PCDMIS_Logs\AlignmentRepeatability.csv"

' ---- Globals used across Subs/Functions -----------------------------
Dim App As Object              'CONFIRMED: CreateObject("PCDLRN.Application") - see
                                '           library/reference/hexagon-sample-01-increment-variable/
Dim Part1 As Object            'CONFIRMED: App.ActivePartProgram (the currently active/loaded part)

Sub Main()

    Dim numTrials As Integer
    Dim i As Integer
    Dim inputStr As String

    inputStr = InputBox("Number of alignment trials to run:", _
                         "Alignment Repeatability Check", CStr(NUM_TRIALS_DEFAULT))
    If inputStr = "" Then
        Exit Sub   ' user cancelled
    End If
    numTrials = CInt(inputStr)
    If numTrials < 2 Then
        MsgBox "Need at least 2 trials to measure repeatability.", vbExclamation
        Exit Sub
    End If

    Dim originX(1 To numTrials) As Double
    Dim originY(1 To numTrials) As Double
    Dim originZ(1 To numTrials) As Double
    Dim zAxisI(1 To numTrials)  As Double
    Dim zAxisJ(1 To numTrials)  As Double
    Dim zAxisK(1 To numTrials)  As Double

    Set App = CreateObject("PCDLRN.Application")
    Set Part1 = App.ActivePartProgram

    For i = 1 To numTrials
        RunAlignmentBlock
        GetCurrentAlignment originX(i), originY(i), originZ(i), _
                             zAxisI(i), zAxisJ(i), zAxisK(i)
    Next i

    Dim rangeX As Double, rangeY As Double, rangeZ As Double
    Dim rangeI As Double, rangeJ As Double, rangeK As Double

    rangeX = RangeOf(originX, numTrials)
    rangeY = RangeOf(originY, numTrials)
    rangeZ = RangeOf(originZ, numTrials)
    rangeI = RangeOf(zAxisI, numTrials)
    rangeJ = RangeOf(zAxisJ, numTrials)
    rangeK = RangeOf(zAxisK, numTrials)

    Dim originPass As Boolean
    Dim vectorPass As Boolean
    originPass = (rangeX <= TOL_LINEAR_MM) And (rangeY <= TOL_LINEAR_MM) And (rangeZ <= TOL_LINEAR_MM)
    vectorPass = (rangeI <= TOL_VECTOR) And (rangeJ <= TOL_VECTOR) And (rangeK <= TOL_VECTOR)

    WriteLog numTrials, originX, originY, originZ, zAxisI, zAxisJ, zAxisK, _
             rangeX, rangeY, rangeZ, rangeI, rangeJ, rangeK, originPass, vectorPass

    Dim resultMsg As String
    resultMsg = "Trials: " & numTrials & vbCrLf & _
                "Origin spread (mm)  X=" & Format(rangeX, "0.0000") & _
                "  Y=" & Format(rangeY, "0.0000") & _
                "  Z=" & Format(rangeZ, "0.0000") & vbCrLf & _
                "Z-axis vector spread  I=" & Format(rangeI, "0.000000") & _
                "  J=" & Format(rangeJ, "0.000000") & _
                "  K=" & Format(rangeK, "0.000000") & vbCrLf & vbCrLf & _
                "Origin tolerance (" & TOL_LINEAR_MM & " mm): " & PassFailText(originPass) & vbCrLf & _
                "Orientation tolerance (" & TOL_VECTOR & "): " & PassFailText(vectorPass) & vbCrLf & vbCrLf & _
                "Log written to " & LOG_FILE_PATH

    If originPass And vectorPass Then
        MsgBox resultMsg, vbInformation, "Alignment Repeatability - PASS"
    Else
        MsgBox resultMsg, vbCritical, "Alignment Repeatability - FAIL"
    End If

End Sub

' ---------------------------------------------------------------------
' Re-runs only the alignment command block, located between the
' LABEL/ALIGN_START and LABEL/ALIGN_END commands in the loaded part
' program.
'VERIFY: CommandMgr access and the run-by-range/run-by-label call.
'        This function assumes Part1.CommandMgr exposes the command
'        list and something equivalent to "run from label X to label
'        Y". If PC-DMIS's object model instead wants command indices,
'        find the two LABEL commands' indices first and pass those in.
' ---------------------------------------------------------------------
Sub RunAlignmentBlock()
    Dim cmdMgr As Object
    Set cmdMgr = Part1.CommandMgr        'VERIFY: property name

    cmdMgr.RunFromLabelToLabel ALIGN_START_LABEL, ALIGN_END_LABEL
    'VERIFY: method name/signature above. If it doesn't exist, the
    ' fallback pattern is to look up each label's command index via
    ' cmdMgr.Item(...)/.Find(...) and call a run-by-index-range method
    ' such as cmdMgr.RunCommandsByRange(startIndex, endIndex).
End Sub

' ---------------------------------------------------------------------
' Reads back the currently active coordinate system's origin and
' Z-axis direction vector after an alignment has just been run.
'VERIFY: property path down to CoordSys/origin/axis-vector values. This
'        is the least-confirmed part of the whole script. An
'        alternative that leans on the now-confirmed
'        GetVariableValue/SetVariableValue pattern (see
'        library/reference/hexagon-sample-01-increment-variable/) would
'        have the DMIS-side alignment block itself ASSIGN/ the origin
'        and rotation into V variables, then this function would just
'        call Part1.GetVariableValue on each of those instead of trying
'        to reach a CoordSys object directly. Switch to that approach
'        if CoordSys below doesn't exist.
' ---------------------------------------------------------------------
Sub GetCurrentAlignment(ByRef oX As Double, ByRef oY As Double, ByRef oZ As Double, _
                         ByRef zI As Double, ByRef zJ As Double, ByRef zK As Double)
    Dim cs As Object
    Set cs = Part1.CoordSys.CurrentCoordSys   'VERIFY: property path

    oX = cs.Origin.X   'VERIFY
    oY = cs.Origin.Y   'VERIFY
    oZ = cs.Origin.Z   'VERIFY

    zI = cs.ZAxis.I    'VERIFY
    zJ = cs.ZAxis.J    'VERIFY
    zK = cs.ZAxis.K    'VERIFY
End Sub

' ---------------------------------------------------------------------
' Generic helpers - plain Basic, no PC-DMIS-specific calls below here.
' ---------------------------------------------------------------------
Function RangeOf(values() As Double, n As Integer) As Double
    Dim i As Integer
    Dim vMin As Double, vMax As Double
    vMin = values(1)
    vMax = values(1)
    For i = 2 To n
        If values(i) < vMin Then vMin = values(i)
        If values(i) > vMax Then vMax = values(i)
    Next i
    RangeOf = vMax - vMin
End Function

Function PassFailText(isPass As Boolean) As String
    If isPass Then
        PassFailText = "PASS"
    Else
        PassFailText = "FAIL"
    End If
End Function

Sub WriteLog(numTrials As Integer, _
             originX() As Double, originY() As Double, originZ() As Double, _
             zAxisI() As Double, zAxisJ() As Double, zAxisK() As Double, _
             rangeX As Double, rangeY As Double, rangeZ As Double, _
             rangeI As Double, rangeJ As Double, rangeK As Double, _
             originPass As Boolean, vectorPass As Boolean)

    Dim fileNum As Integer
    Dim i As Integer
    Dim fileExists As Boolean

    fileNum = FreeFile
    fileExists = (Dir(LOG_FILE_PATH) <> "")

    Open LOG_FILE_PATH For Append As #fileNum

    If Not fileExists Then
        Print #fileNum, "Timestamp,Trial,OriginX,OriginY,OriginZ,ZAxisI,ZAxisJ,ZAxisK"
    End If

    For i = 1 To numTrials
        Print #fileNum, Format(Now, "yyyy-mm-dd hh:nn:ss") & "," & i & "," & _
                         originX(i) & "," & originY(i) & "," & originZ(i) & "," & _
                         zAxisI(i) & "," & zAxisJ(i) & "," & zAxisK(i)
    Next i

    Print #fileNum, Format(Now, "yyyy-mm-dd hh:nn:ss") & ",SUMMARY," & _
                     "RangeX=" & rangeX & ",RangeY=" & rangeY & ",RangeZ=" & rangeZ & "," & _
                     "RangeI=" & rangeI & ",RangeJ=" & rangeJ & ",RangeK=" & rangeK & "," & _
                     "OriginResult=" & PassFailText(originPass) & "," & _
                     "OrientationResult=" & PassFailText(vectorPass)

    Close #fileNum

End Sub
