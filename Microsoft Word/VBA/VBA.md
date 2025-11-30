### Обязательное объявление переменных
`Option Explicit`

### Переход к метке Err_label в случае возникновения ошибки
```vba
On Error GoTo Err_label
Err_label:
...
```

### Активировать окно MS Word с названием в переменной FileName
`Windows(FileName).Activate`

### Закрыть окно MS Word с названием в переменной FileName
`Windows(FileName).Close`

### Создать новый документ
`Documents.Add DocumentType:=wdNewBlankDocument`

### Передать название активного файла MS Word в переменную FileName
`FileName = ActiveDocument.Name`

### Открыть нижний колонтитул
`ActiveWindow.ActivePane.View.SeekView = wdSeekCurrentPageFooter`

### Закрытие нижнего колонтитула
`ActiveWindow.ActivePane.View.SeekView = wdSeekMainDocument`

### Копировать
`Selection.Copy`

### Вырезать
`Selection.Cut`

### Вставить
`Selection.Paste`

### Вставить с сохранением форматирования
`Selection.PasteAndFormat (wdFormatOriginalFormatting)`

### Обработка ошибки
```vba
On Error Resume Next
...
If Err.Number <> 0 Then
GoTo Err_label
End If
```

### Перейти к началу документа
`Selection.HomeKey Unit:=wdStory`

### Перейти в начало строки
`Selection.HomeKey Unit:=wdLine`

### Поиск разрыва страницы
```vba
With Selection.Find
.Text = "^b"
End With
Selection.Find.Execute
```

### Перейти на 1 строку выше
`Selection.MoveUp Unit:=wdLine, Count:=1`

### Выделить текст от текущей позиции до начала документа
`Selection.HomeKey Unit:=wdStory, Extend:=wdExtend`

### Удалить 1 символ справа
`Selection.Delete Unit:=wdCharacter, Count:=1`

### Определение номера документа для сохранения
```vba
i_cnt_row_all = ActiveDocument.Sentences.Count
i_cnt_row = 1
Do While i_cnt_row <= i_cnt_row_all
If InStr(ActiveDocument.Sentences(i_cnt_row), "КАРТА №") Then
s_Number_doc = Left(ActiveDocument.Sentences(i_cnt_row), Len(ActiveDocument.Sentences(i_cnt_row)))
Exit Do
End If
i_cnt_row = i_cnt_row + 1
Loop
```

### Название документа
`filename = "D:\00\" & s_Number_doc & ".docx"`

### Путь до активного документа
`filepath = ActiveDocument.Path`

