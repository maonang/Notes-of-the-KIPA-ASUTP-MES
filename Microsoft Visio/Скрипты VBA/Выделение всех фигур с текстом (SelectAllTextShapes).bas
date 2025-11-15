Attribute VB_Name = "Module1"
Option Explicit

' =============================================================================
' Назначение:    Выделение всех фигур с текстом на активной странице
' =============================================================================

Public Sub SelectAllTextShapes()
    On Error Resume Next
    
    ActiveWindow.DeselectAll
    
    Dim shp As Visio.Shape
    Dim textShapesCount As Long
    
    For Each shp In ActivePage.Shapes
        ' Простая проверка: есть ли текст и не пустой ли он
        If shp.Text <> "" And Trim(shp.Text) <> "" Then
            ActiveWindow.Select shp, visSelect
            textShapesCount = textShapesCount + 1
        End If
    Next shp
    
    Select Case textShapesCount
        Case 0
            MsgBox "Фигуры с текстом не найдены.", vbInformation
        Case 1
            MsgBox "Выделена 1 фигура с текстом.", vbInformation
        Case Else
            MsgBox "Выделено фигур с текстом: " & textShapesCount, vbInformation
    End Select
    
    Exit Sub

ErrorHandler:
    MsgBox "Произошла ошибка: " & Err.Description & vbCrLf & _
           "Код ошибки: " & Err.Number, vbCritical, "Ошибка выполнения"
End Sub



