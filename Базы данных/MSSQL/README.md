### Поиск первого недостающего (удаленного) ID в таблице  
``` sql  
USE [db_DEK]
GO
SELECT MIN(t1.id) + 1 AS 'missed_id'
ㅤㅤFROM [dbo].[db_t_route_1] t1
ㅤㅤLEFT JOIN [dbo].[db_t_route_1] t2 ON t1.id + 1 = t2.id
ㅤㅤWHERE t2.id IS NULL
```  
Применение: добавить другим запросом запись под номером ранее удаленного.  

### Хранимые процедуры  
  
- Во время создания вначале строки с названием процедуры находится ключевое слово "CREATE", а во время изменения - "ALTER".  
- Пример вызова хранимой процедуры: EXEC [dbo].[prog_1_SELECT_route_1] {$ch_OUT_x}, {$ch_OUT_Search} (фото 1)  
- В случае использования "SELECT ... FROM ... WHERE ... LIKE N'...' " необходимо формировать строку с текстом из поля для ввода через программу на языке ST: p_TextEdit_1_change := CONCAT('N','$'','%', p_TextEdit_1, '%','$'');  
где p_TextEdit_1_change - параметр типа STRING, связанный в выходом базового канала ch_OUT_Search;  
$' - символ одинарной кавычки;  
p_TextEdit_1 - параметр типа STRING, связанный с параметром "Текст" текстового поля на мнемосхеме.  
  
- Пример хранимой процедуры из рабочего проекта  
- 1 - (фото 2)  
Содержимое задействованных объектов: Таблица данных, поле для ввода, кнопка для поиска, 2 радиокнопки для фильтрации.  
Описание: В период работы с таблицей данных посредством программы на языке ST осуществляется определение статуса отображения записей.

![1mssql](https://github.com/user-attachments/assets/b00b01f7-9751-425e-aa4e-3ff3d9835181)

![2mssql](https://github.com/user-attachments/assets/27970440-0e8b-499c-a414-eb4e1b892fd1)

### Выборка записей из таблицы 1 по фильтру из набора записей в таблице 2. (В записях таблицы 1 должны совпасть все элементы из таблицы 2)
``` sql
SELECT [p1],[p2],[p6] INTO #t_buf
ㅤㅤFROM [db_t_route_1] r
ㅤㅤWHERE EXISTS(
ㅤㅤSELECT 1
ㅤㅤFROM [db_t_obj_filter] d
ㅤㅤWHERE
ㅤㅤㅤㅤr.[p10] = d.[obj_kks] OR
ㅤㅤㅤㅤ...
ㅤㅤㅤㅤr.[p206] = d.[obj_kks]
ㅤㅤHAVING COUNT(*) = (SELECT COUNT(*) FROM [db_t_obj_filter]))
```

### Проверка: число @ch_OUT_x начинается с цифры 2
``` sql
IF LEFT(CAST(@ch_OUT_x AS varchar(3)),1) = '2'
BEGIN
...
END
```

### Передача записей из поля [obj_kks] таблицы [db_t_obj_filter] в переменные от @p1 до @p50  
Сокращенный участок SQL-запроса из хранимой процедуры:  
``` sql
@p1 varchar(255) ='%%', ... @p50 varchar(255) ='%%',
SELECT @p1 = COALESCE((SELECT [obj_kks] FROM [db_t_obj_filter] WHERE [id] = 1), '%%'),
...
@p50 = COALESCE((SELECT [obj_kks] FROM [db_t_obj_filter] WHERE [id] = 50), '%%')
FROM [db_t_obj_filter]
...
```

### Количество записей в таблице БД
``` sql
SELECT COUNT(*) FROM [dbo].[table_name]
```
### Количество записей в таблице БД передать в переменную
``` sql
SELECT @cnt_row = COUNT(*) FROM [dbo].[table_name]
```

### Формирование SQL-запроса для удаления ограничений внешнего ключа
``` sql
SELECT 'ALTER TABLE ' + OBJECT_SCHEMA_NAME(k.parent_object_id) +
'.[' + OBJECT_NAME(k.parent_object_id) + '] DROP CONSTRAINT ' + k.name
FROM sys.foreign_keys k WHERE referenced_object_id = object_id('НАЗВАНИЕ ТАБЛИЦЫ')
```
### Сформированный текст SQL-запроса нужно скопировать в поле SQLQuery и выполнить  
#### Пример: 
``` sql
ALTER TABLE dbo.[db_t_cmd_rule] DROP CONSTRAINT FK_db_t_cmd_rule_db_t_cmd
```
### Отобразить все ограничения внешнего ключа
``` sql
SELECT * FROM sys.foreign_keys
```
### Хранимая процедура пересоздания таблицы
``` sql
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE db_t_obj_filter_CLEAR
AS
BEGIN
ㅤㅤSET NOCOUNT ON;
ㅤㅤDROP TABLE IF EXISTS [dbo].[db_t_obj_filter];
ㅤㅤDECLARE @s_Query AS nvarchar(MAX) = '
ㅤㅤㅤㅤSET ANSI_NULLS ON
ㅤㅤㅤㅤSET QUOTED_IDENTIFIER ON
ㅤㅤㅤㅤCREATE TABLE [dbo].[db_t_obj_filter](
ㅤㅤㅤㅤㅤㅤ[id] [bigint] IDENTITY(1,1) NOT NULL,
ㅤㅤㅤㅤㅤㅤ[obj_kks] [varchar](255) NOT NULL,
ㅤㅤㅤㅤㅤㅤ[obj_cat_main] [varchar](255) NOT NULL,
ㅤㅤㅤㅤCONSTRAINT [PK_db_t_obj_filter] PRIMARY KEY CLUSTERED
ㅤㅤㅤㅤ([id] ASC) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]) ON [PRIMARY]
ㅤㅤㅤㅤEXEC sys.sp_addextendedproperty @name=N''MS_Description'', @value=N''Список выбранных устройств'' , @level0type=N''SCHEMA'',@level0name=N''dbo'', @level1type=N''TABLE'',@level1name=N''db_t_obj_filter'''

ㅤㅤEXEC sp_executesql @s_Query
END
GO
```

### Ошибки (SQL Server Management Studio)
***"A fatal scripting error occurred.
Incorrect syntax was encountered while parsing GO."***  
Возможная причина: лишний символ закрытия комментария (*/) на строке GO.  

***"Msg 0, Level ..., State 0, Line 0***  
***The connection is broken and recovery is not possible. The client driver attempted to recover the connection one or more times and all attempts failed. Increase the value of ConnectRetryCount to increase the number of recovery attempts."***  
Если возникает во время запуска сложного SQL-запроса, то необходимо переподключиться к серверу и сразу выполнить запрос.  

### Шаблон SQL-запросов
В SQL Server Management Studio есть удобный инструмент для создания шаблонов SQL-запросов. С его помощью можно быстро создавать SQL-запросы для запросов протокола MSSQL.
Используя шаблон INSERT, можно изменить значения полей вида "<obj, varchar(255),>" на названия базовых выходных каналов, например, {ch_obj}. Затем сформированный запрос можно вставить в параметр "Команда" нужного запроса в протоколе MSSQL.  
![3mssql](https://github.com/user-attachments/assets/e90a3474-6ec6-4a28-91b6-640ad3fc0020)

### Кодировка БД
Отобразить текущую кодировку
```sql
SELECT name, collation_name FROM sys.databases WHERE name = '<Название БД>'
GO
```
Изменить кодировку на Cyrillic_General_CI_AS
```sql
ALTER DATABASE [<Название БД>] COLLATE Cyrillic_General_CI_AS
GO
```

 ### Ветвление
 ```sql
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER PROCEDURE CFG_prog_8_combobox2_cmd
@KKS_to_combobox2 AS NVARCHAR(255) = N''
AS
BEGIN
SET NOCOUNT ON;
DECLARE @combobox2 AS NVARCHAR(255) = N''
SELECT @combobox2 = [obj_type] FROM [db_DEK].[dbo].[db_t_obj] WHERE [obj_kks] = @KKS_to_combobox2
SELECT
CASE
WHEN @combobox2 IN (N'БИС', N'Вибромотор', N'Конвейер скребковый', N'Конвейер ленточный', N'Механизм выгрузки', N'Нория', N'Роторный питатель', N'Роторный питатель аспирации', N'Скальператор') THEN N' ~Пуск'
WHEN @combobox2 IN (N'Конвейер реверсивный', N'Конвейер ленточный реверсивный') THEN N' ~Пуск вперед~Пуск реверс'
WHEN @combobox2 IN (N'Перекидной клапан') THEN N' ~Положение 1~Положение 2'
WHEN @combobox2 IN (N'Шибер') THEN N' ~Открыть~Закрыть'
WHEN @combobox2 IN (N'Шибер трехпозиционный') THEN N' ~Положение 1~Положение 2~Положение 3 (Открыт)~Закрыть'
END AS Result
END
GO
```

###  Вернуть пустое поле Result
```sql
SELECT '' AS Result
```

### Создание резервной копии БД  
К теме: https://ironskills.by/tpost/x0pzcaln31-kak-nastroit-avtomaticheskoe-rezervnoe-k  
Содержимое SQL-запроса:  
```sql
DECLARE @path varchar(max)=N'C:\BackupDB\db_DEK_'+convert(varchar(max),getdate(),112) + N'.bak'
BACKUP DATABASE [db_DEK] TO DISK = @path WITH NOFORMAT, NOINIT, NAME = N'db_DEK-Full Database Backup', SKIP, NOREWIND, NOUNLOAD, STATS = 10
GO
DECLARE @backupSetId AS int
SELECT @backupSetId = position
FROM msdb..backupset
WHERE database_name=N'db_DEK' and backup_set_id=(SELECT max(backup_set_id) FROM msdb..backupset WHERE database_name=N'db_DEK' )
IF @backupSetId IS NULL
BEGIN
RAISERROR(N'Verify failed. Backup information for database ''db_DEK'' not found.', 16, 1)
END
DECLARE @path varchar(max)=N'C:\BackupDB\db_DEK_'+convert(varchar(max),getdate(),112) + N'.bak'
RESTORE VERIFYONLY
FROM DISK = @path WITH FILE = @backupSetId, NOUNLOAD, NOREWIND
GO
```
### Восстановление из резервной копии БД
```sql
USE [master]
RESTORE DATABASE [db_DEK] FROM DISK = N'D:\БД\db_DEK_20231127.bak' WITH FILE = 1, NOUNLOAD, STATS = 5
GO
```
