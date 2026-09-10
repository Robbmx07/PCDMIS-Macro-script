# Reference: Hexagon Sample Automation Script 1 — Increment a PC-DMIS Variable

Source: Hexagon Metrology's official PC-DMIS automation documentation
("Sample Automation Script 1 - Increment a PC-DMIS Variable"), provided by
the user. This is vendor-documented syntax, not user-tested in real
PC-DMIS. Treat it as more reliable than an unverified guess, but still not
the same as a confirmed real test run.

## What it shows

A DMIS part program prompts an operator for an integer, stores it in
variable `V1`, then calls a `.bas` script that increments `V1` by 1 and
writes it back, and the program then displays the new value in a comment.

## DMIS side (part program)

```
C1             =COMMENT/INPUT,NO,FULL SCREEN=NO,
               Type an integer
               ASSIGN/V1=INT(C1.INPUT)
               COMMENT/OPER,NO,FULL SCREEN=NO,AUTO-CONTINUE=NO,
               "BEFORE SCRIPT - Variable is: " + V1

CS1            =SCRIPT/FILENAME= D:\MYAUTOMATIONSCRIPTS\TEST2.BAS
               FUNCTION/Main,SHOW=YES,,
               STARTSCRIPT/
               ENDSCRIPT/
```

```
COMMENT/OPER,NO,FULL SCREEN=NO,AUTO-CONTINUE=NO,
"AFTER SCRIPT - Variable is: " + V1
```

Confirms the block structure for calling an external `.bas` file from a
DMIS program: `=SCRIPT/FILENAME=<path>`, `FUNCTION/<SubName>,SHOW=YES,,`,
`STARTSCRIPT/`, `ENDSCRIPT/`.

## Basic side (Test2.bas)

```vb
Sub Main
  Dim App As Object
  Set App = CreateObject ("PCDLRN.Application")
  Dim Part As Object
  Set Part = App.ActivePartProgram
  Dim Var As Object
  Set Var = Part.GetVariableValue ("V1")
  Dim I As Object
  If Not Var Is Nothing Then
    MsgBox "Initial value of V1: " & Var.LongValue,0,"Script Message Box"
    Var.LongValue = Var.LongValue + 1
    Part.SetVariableValue "V1", Var
    MsgBox "V1 is now: " & Var.LongValue,0,"Script Message Box"
  Else
    MsgBox "Could not find a V1 variable",0,"Script Message Box"
  End If
End Sub
```

## Confirmed API points to reuse elsewhere in this library

- `CreateObject("PCDLRN.Application")` — correct way to get the
  Application object from within a `.bas` script.
- `App.ActivePartProgram` — correct property for the active part program
  (previously guessed as `ActivePartIObject` in
  `basic-scripts/AlignmentRepeatability.bas` — that was wrong, now fixed).
- `Part.GetVariableValue("VarName")` / `Part.SetVariableValue "VarName", Var`
  — read/write a DMIS program variable from Basic. `Var.LongValue` is the
  integer accessor; other Variable types likely have equivalents (not yet
  confirmed).
- Interactive-editor confirmation behavior is real and documented, at
  least for `COMMENT`: press Enter twice after typing comment text before
  PC-DMIS accepts a new command. Still unconfirmed whether the
  `TIP`/`T1A0B0` case from the original brief works the same way or is
  saved differently in the file - needs its own reference sample.

## Still unconfirmed / needed next

- How to read a *variable* into a numeric Basic value when it's not a
  simple integer (e.g. a double, or an alignment origin/rotation value).
- Whether alignment origin/orientation is exposed as a `CoordSys` object
  (as guessed in `AlignmentRepeatability.bas`) or only reachable by having
  the DMIS side `ASSIGN/` it into `V` variables first, then reading those
  variables via the now-confirmed `GetVariableValue` method. The latter is
  more likely to be correct given this sample's pattern, but needs its own
  reference sample or real test to confirm.
