Конвертер JSON-структуры в формат формулы для вставки в Excel

Пример.
Было:
{"filter":[{"value":"Repeatability","fieldid":"34e62f8a-dac1-435b-8848-6178c7e1af4d"}],"fieldid":"34e62f8a-dac1-435b-8848-6178c7e1af4d","directoryid":"fe80d44a-7d01-4187-8ee4-4a3107874e34"}

Стало:
="{""filter"": [{""value"": """ & "Repeatability" & """, ""fieldid"": """ & "34e62f8a-dac1-435b-8848-6178c7e1af4d" & """}], ""fieldid"": """ & "34e62f8a-dac1-435b-8848-6178c7e1af4d" & """, ""directoryid"": """ & "fe80d44a-7d01-4187-8ee4-4a3107874e34" & """}"
