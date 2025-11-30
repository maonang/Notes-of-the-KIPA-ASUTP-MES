### Сохранение документа в формате docx с названием filename
```vba
ActiveDocument.SaveAs2 filename:=filename, _
FileFormat:=wdFormatXMLDocument, _
LockComments:=False, _
Password:="", _
AddToRecentFiles:=True, _
WritePassword:="", _
ReadOnlyRecommended:=False, _
EmbedTrueTypeFonts:=False, _
SaveNativePictureFormat:=False, _
SaveFormsData:=False, _
SaveAsAOCELetter:=False, _
CompatibilityMode:=15
```
