/* Содержание:
		 Добавление БД 
				 Database [db_DEK] 

		 Изменение кодировки БД на Cyrillic_General_CI_AS

		 Добавление таблиц 
				 Table [dbo].[db_t_filters] 
				 Table [dbo].[db_t_route_1] 
				 Table [dbo].[db_t_route_2] 
				 Table [dbo].[db_t_route_active] 
				 Table [dbo].[db_t_obj]
				 Table [dbo].[db_t_obj_filter]
				 Table [dbo].[db_t_cfg_obj]
				 Table [dbo].[db_t_new]
				 Table [dbo].[Motor_WorkTime]								// Таблица часовой наработки двигателей

		 Добавление пользователя db_DEK_adm 

		 Заполнение таблиц 
				 Table [dbo].[db_t_route_active] 		 Статус: + 50 пустых строк 
				 Table [dbo].[db_t_obj] 				 Статус: + 
				 Table [dbo].[Motor_WorkTime]			 Статус: + 71 записей с 0 ч

		Создание типа данных [dbo].[Motor_WorkTime_run_type]

		Создание хранимой процедуры [dbo].[prog_0_SELECT_statistic]			// Очередь маршрутов - Статистика по маршрутам
		Создание хранимой процедуры [dbo].[prog_1_SELECT_route_1]			// Маршруты - Перечень маршрутов с учетом поиска и выборки устройств
		Создание хранимой процедуры [dbo].[prog_2_SELECT_obj]				// Маршруты - Перечень устройств
		Создание хранимой процедуры [dbo].[prog_3_SELECT_add_obj]			// Маршруты - Перечень обязательных устройств
		Создание хранимой процедуры [dbo].[prog_4_SELECT_missed_id]			// Конфигуратор маршрутов - поиск ближайшего меньшего свободного ID маршрута
		Создание хранимой процедуры [dbo].[prog_5_DELETE_route]				// Маршруты - Удаление выбранного маршрута
		Создание хранимой процедуры [dbo].[prog_6_db_t_obj_filter_CLEAR]	// Маршруты - Очистка перечня обязательных устройств
		Создание хранимой процедуры [dbo].[prog_7_union_table_route]		// Результат объединения двух таблиц для отображения устройств в маршруте
		Создание хранимой процедуры [dbo].[prog_7_union_table_route_ID]		// Результат объединения двух таблиц для добавления данных маршрута в ПЛК
		Создание хранимой процедуры [dbo].[prog_8_union_table_cfg]		    // Результат объединения двух таблиц для изменения устройств в маршруте
		Создание хранимой процедуры [dbo].[prog_9_inc_cnt_execute]			// Увеличение количества добавлений маршршута в очередь
		Создание хранимой процедуры [dbo].[prog_10_Motor_WorkTime]			***** В процессе доработки!

	-	Создание хранимой процедуры [dbo].[CFG_prog_1_SELECT_obj]			// Конфигуратор маршрутов - Перечень выбранных устройств с параметрами времени и действия
		Создание хранимой процедуры [dbo].[CFG_prog_2_SELECT_obj]			// Конфигуратор маршрутов - Перечень всех устройств для выбора
		Создание хранимой процедуры [dbo].[CFG_prog_2_SELECT_obj_one]		// Конфигуратор маршрутов - Получение параметров выбранного устройства для автозаполнения
	-	Создание хранимой процедуры [dbo].[CFG_prog_3_DropAndCreate_obj_add]    // Конфигуратор маршрутов - Пересоздание таблицы перечня устройств в маршруте
		Создание хранимой процедуры [dbo].[CFG_prog_4_DeleteRowOrDropAndCreate_obj_add]    // Конфигуратор маршрутов - Удаление записей. Если записей не осталось - пересоздание таблицы для обнуления ключевого поля [id]
		Создание хранимой процедуры [dbo].[CFG_prog_5_replace]				// Конфигуратор маршрутов - Действие замены в зависимости от параметра
		Создание хранимой процедуры [dbo].[CFG_prog_6_moving]				// Конфигуратор маршрутов - Перемещение строки вверх/вниз по таблице
		Создание хранимой процедуры [dbo].[CFG_prog_7_ChangeOrCreateRoute]	// Конфигуратор маршрутов - Сохранение изменений в маршруте или его создание. Тип действия зависит от параметра
		Создание хранимой процедуры [dbo].[CFG_prog_8_combobox2_cmd]		// Конфигуратор маршрутов - Данные для выпадающего списка
	
Справка
	Сообщение после выполнения запроса:
		(1 row affected)
		(50 rows affected)
		(142 rows affected)
		(71 rows affected)

	Время выполнения: 1 секунды

	!!!	Глобальную переменную @s_Dir_MSSQL изменить на путь до своего SQL-сервера !!!
*/

USE [master]
GO
/* Закрытие всех подключений к БД */
DECLARE @CmdKill NVARCHAR(MAX) = N'';
SELECT @CmdKill += N'KILL ' + CAST(session_id AS NVARCHAR) + N';'
FROM sys.dm_exec_sessions
WHERE DB_NAME(database_id) = 'db_DEK';
EXEC(@CmdKill);
/* Удаление БД для пересоздания */
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'db_DEK')
BEGIN
	DROP DATABASE db_DEK;
END
DROP TABLE IF EXISTS [dbo].[t_global_var];
CREATE TABLE [dbo].[t_global_var] (
	var_name varchar(255), 
	var_type varchar(50),  
	var_value varchar(MAX))
/* Глобальные переменные */
/* ИЗМЕНИТЬ НА ПУТЬ ДО СВОЕГО SQL-сервера */
-- INSERT INTO [dbo].[t_global_var] (var_name, var_type, var_value) VALUES ('@s_Dir_MSSQL', 'nvarchar(MAX)', 'C:\Program Files\Microsoft SQL Server\MSSQL15.SQLEXPRESS\MSSQL\DATA\')
 INSERT INTO [dbo].[t_global_var] (var_name, var_type, var_value) VALUES ('@s_Dir_MSSQL', 'nvarchar(MAX)', 'C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\DATA\')
/* --------------------- */
USE [master]
GO
/****** Создание БД ******/
/****** Database [db_DEK] ******/
DECLARE @s_Folder1 AS nvarchar(MAX) = CONCAT(CAST((SELECT var_value FROM [dbo].[t_global_var] WHERE var_name = '@s_Dir_MSSQL') AS nvarchar(MAX)) , 'db_DEK.mdf')
DECLARE @s_Folder2 AS nvarchar(MAX) = CONCAT(CAST((SELECT var_value FROM [dbo].[t_global_var] WHERE var_name = '@s_Dir_MSSQL') AS nvarchar(MAX)) , 'db_DEK_log.ldf')
DECLARE @s_Query AS nvarchar(MAX) = '
CREATE DATABASE [db_DEK]
	CONTAINMENT = NONE
	ON PRIMARY
		( NAME = N''db_DEK'', FILENAME = N''' + @s_Folder1 + ''', SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
	LOG ON
		( NAME = N''db_DEK_log'', FILENAME = ''' + @s_Folder2 + ''', SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
	WITH CATALOG_COLLATION = DATABASE_DEFAULT'
EXEC sp_executesql @s_Query
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
	EXEC [db_DEK].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [db_DEK] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [db_DEK] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [db_DEK] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [db_DEK] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [db_DEK] SET ARITHABORT OFF 
GO
ALTER DATABASE [db_DEK] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [db_DEK] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [db_DEK] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [db_DEK] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [db_DEK] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [db_DEK] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [db_DEK] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [db_DEK] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [db_DEK] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [db_DEK] SET  DISABLE_BROKER 
GO
ALTER DATABASE [db_DEK] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [db_DEK] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [db_DEK] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [db_DEK] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [db_DEK] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [db_DEK] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [db_DEK] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [db_DEK] SET RECOVERY SIMPLE 
GO
ALTER DATABASE [db_DEK] SET  MULTI_USER 
GO
ALTER DATABASE [db_DEK] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [db_DEK] SET DB_CHAINING OFF 
GO
ALTER DATABASE [db_DEK] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [db_DEK] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [db_DEK] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [db_DEK] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
ALTER DATABASE [db_DEK] SET QUERY_STORE = OFF
GO
ALTER DATABASE [db_DEK] SET  READ_WRITE 
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
USE [db_DEK]
GO
/****** Изменение кодировки ******/
ALTER DATABASE [db_DEK] COLLATE Cyrillic_General_CI_AS
/****** Создание таблиц ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Table [dbo].[db_t_filters] ******/
/****** Список устройств для отбора, находящиеся между Источником и Приемником ******/
CREATE TABLE [dbo].[db_t_filters](
	[id] [bigint] IDENTITY(1,1) NOT NULL,				/* ID записи */
	[obj_cat_main] [varchar](255) NOT NULL,				/* Категория устройства */
	[id_obj] [bigint] NOT NULL,							/* Код устройства */
	[obj_kks] [varchar](255) NOT NULL,					/* Тег АСУТП */
	CONSTRAINT [PK_db_t_filters] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Список устройств для фильтра' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'db_t_filters'
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Table [dbo].[db_t_route_1] ******/
/****** Список всех маршрутов с служебной информацией ******/
CREATE TABLE [dbo].[db_t_route_1](
	[id] [bigint] IDENTITY(1,1) NOT NULL, 	/* ID записи */
	[p1] [bigint]  NOT NULL, 				/* Код маршрута */
	[p2] [varchar](255) NOT NULL, 			/* Описание маршрута */
	[p3] [varchar](255) NOT NULL, 			/* Дата и время добавления маршрута */
	[p4] [varchar](255), 					/* Дата и время изменения маршрута */
	[p5] [varchar](255), 					/* Описание причины изменения */
	[p6] [bigint] NOT NULL, 				/* Общее количество использований маршрута для аналитики */
	[p7] [tinyint] NOT NULL, 				/* Количество устройств в маршруте */
	[p8] [varchar](255) NOT NULL, 			/* Статус маршрута для изменения или удаления */
/* ИСТОЧНИК */						
	[p9] [int] NOT NULL,					/* Код устройства */
	[p10] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p11] [int] NOT NULL,					/* Код команды */
	[p12] [varchar](255) NOT NULL, 			/* Команда */		
/* ПРИЕМНИК */						
	[p13] [int] NOT NULL,					/* Код устройства */
	[p14] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p15] [int] NOT NULL,					/* Код команды */
	[p16] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 2 */						
	[p17] [int] NOT NULL,					/* Код устройства */
	[p18] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p19] [int] NOT NULL,					/* Код команды */
	[p20] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 3 */						
	[p21] [int] NOT NULL,					/* Код устройства */
	[p22] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p23] [int] NOT NULL,					/* Код команды */
	[p24] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 4 */						
	[p25] [int] NOT NULL,					/* Код устройства */
	[p26] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p27] [int] NOT NULL,					/* Код команды */
	[p28] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 5 */						
	[p29] [int] NOT NULL,					/* Код устройства */
	[p30] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p31] [int] NOT NULL,					/* Код команды */
	[p32] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 6 */						
	[p33] [int] NOT NULL,					/* Код устройства */
	[p34] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p35] [int] NOT NULL,					/* Код команды */
	[p36] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 7 */						
	[p37] [int] NOT NULL,					/* Код устройства */
	[p38] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p39] [int] NOT NULL,					/* Код команды */
	[p40] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 8 */						
	[p41] [int] NOT NULL,					/* Код устройства */
	[p42] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p43] [int] NOT NULL,					/* Код команды */
	[p44] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 9 */						
	[p45] [int] NOT NULL,					/* Код устройства */
	[p46] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p47] [int] NOT NULL,					/* Код команды */
	[p48] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 10 */						
	[p49] [int] NOT NULL,					/* Код устройства */
	[p50] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p51] [int] NOT NULL,					/* Код команды */
	[p52] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 11 */						
	[p53] [int] NOT NULL,					/* Код устройства */
	[p54] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p55] [int] NOT NULL,					/* Код команды */
	[p56] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 12 */						
	[p57] [int] NOT NULL,					/* Код устройства */
	[p58] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p59] [int] NOT NULL,					/* Код команды */
	[p60] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 13 */						
	[p61] [int] NOT NULL,					/* Код устройства */
	[p62] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p63] [int] NOT NULL,					/* Код команды */
	[p64] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 14 */						
	[p65] [int] NOT NULL,					/* Код устройства */
	[p66] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p67] [int] NOT NULL,					/* Код команды */
	[p68] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 15 */						
	[p69] [int] NOT NULL,					/* Код устройства */
	[p70] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p71] [int] NOT NULL,					/* Код команды */
	[p72] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 16 */						
	[p73] [int] NOT NULL,					/* Код устройства */
	[p74] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p75] [int] NOT NULL,					/* Код команды */
	[p76] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 17 */						
	[p77] [int] NOT NULL,					/* Код устройства */
	[p78] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p79] [int] NOT NULL,					/* Код команды */
	[p80] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 18 */						
	[p81] [int] NOT NULL,					/* Код устройства */
	[p82] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p83] [int] NOT NULL,					/* Код команды */
	[p84] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 19 */						
	[p85] [int] NOT NULL,					/* Код устройства */
	[p86] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p87] [int] NOT NULL,					/* Код команды */
	[p88] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 20 */						
	[p89] [int] NOT NULL,					/* Код устройства */
	[p90] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p91] [int] NOT NULL,					/* Код команды */
	[p92] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 21 */						
	[p93] [int] NOT NULL,					/* Код устройства */
	[p94] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p95] [int] NOT NULL,					/* Код команды */
	[p96] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 22 */						
	[p97] [int] NOT NULL,					/* Код устройства */
	[p98] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p99] [int] NOT NULL,					/* Код команды */
	[p100] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 23 */						
	[p101] [int] NOT NULL,					/* Код устройства */
	[p102] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p103] [int] NOT NULL,					/* Код команды */
	[p104] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 24 */						
	[p105] [int] NOT NULL,					/* Код устройства */
	[p106] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p107] [int] NOT NULL,					/* Код команды */
	[p108] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 25 */						
	[p109] [int] NOT NULL,					/* Код устройства */
	[p110] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p111] [int] NOT NULL,					/* Код команды */
	[p112] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 26 */						
	[p113] [int] NOT NULL,					/* Код устройства */
	[p114] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p115] [int] NOT NULL,					/* Код команды */
	[p116] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 27 */						
	[p117] [int] NOT NULL,					/* Код устройства */
	[p118] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p119] [int] NOT NULL,					/* Код команды */
	[p120] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 28 */						
	[p121] [int] NOT NULL,					/* Код устройства */
	[p122] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p123] [int] NOT NULL,					/* Код команды */
	[p124] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 29 */						
	[p125] [int] NOT NULL,					/* Код устройства */
	[p126] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p127] [int] NOT NULL,					/* Код команды */
	[p128] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 30 */						
	[p129] [int] NOT NULL,					/* Код устройства */
	[p130] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p131] [int] NOT NULL,					/* Код команды */
	[p132] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 31 */						
	[p133] [int] NOT NULL,					/* Код устройства */
	[p134] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p135] [int] NOT NULL,					/* Код команды */
	[p136] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 32 */						
	[p137] [int] NOT NULL,					/* Код устройства */
	[p138] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p139] [int] NOT NULL,					/* Код команды */
	[p140] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 33 */						
	[p141] [int] NOT NULL,					/* Код устройства */
	[p142] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p143] [int] NOT NULL,					/* Код команды */
	[p144] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 34 */						
	[p145] [int] NOT NULL,					/* Код устройства */
	[p146] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p147] [int] NOT NULL,					/* Код команды */
	[p148] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 35 */						
	[p149] [int] NOT NULL,					/* Код устройства */
	[p150] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p151] [int] NOT NULL,					/* Код команды */
	[p152] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 36 */						
	[p153] [int] NOT NULL,					/* Код устройства */
	[p154] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p155] [int] NOT NULL,					/* Код команды */
	[p156] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 37 */						
	[p157] [int] NOT NULL,					/* Код устройства */
	[p158] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p159] [int] NOT NULL,					/* Код команды */
	[p160] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 38 */						
	[p161] [int] NOT NULL,					/* Код устройства */
	[p162] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p163] [int] NOT NULL,					/* Код команды */
	[p164] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 39 */						
	[p165] [int] NOT NULL,					/* Код устройства */
	[p166] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p167] [int] NOT NULL,					/* Код команды */
	[p168] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 40 */						
	[p169] [int] NOT NULL,					/* Код устройства */
	[p170] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p171] [int] NOT NULL,					/* Код команды */
	[p172] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 41 */						
	[p173] [int] NOT NULL,					/* Код устройства */
	[p174] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p175] [int] NOT NULL,					/* Код команды */
	[p176] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 42 */						
	[p177] [int] NOT NULL,					/* Код устройства */
	[p178] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p179] [int] NOT NULL,					/* Код команды */
	[p180] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 43 */						
	[p181] [int] NOT NULL,					/* Код устройства */
	[p182] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p183] [int] NOT NULL,					/* Код команды */
	[p184] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 44 */						
	[p185] [int] NOT NULL,					/* Код устройства */
	[p186] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p187] [int] NOT NULL,					/* Код команды */
	[p188] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 45 */						
	[p189] [int] NOT NULL,					/* Код устройства */
	[p190] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p191] [int] NOT NULL,					/* Код команды */
	[p192] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 46 */						
	[p193] [int] NOT NULL,					/* Код устройства */
	[p194] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p195] [int] NOT NULL,					/* Код команды */
	[p196] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 47 */						
	[p197] [int] NOT NULL,					/* Код устройства */
	[p198] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p199] [int] NOT NULL,					/* Код команды */
	[p200] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 48 */						
	[p201] [int] NOT NULL,					/* Код устройства */
	[p202] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p203] [int] NOT NULL,					/* Код команды */
	[p204] [varchar](255) NOT NULL, 			/* Команда */		
/* Устройство 49 */						
	[p205] [int] NOT NULL,					/* Код устройства */
	[p206] [varchar](255) NOT NULL, 			/* Тег АСУТП */		
	[p207] [int] NOT NULL,					/* Код команды */
	[p208] [varchar](255) NOT NULL, 			/* Команда */		
	CONSTRAINT [PK_db_t_route_1] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Список маршрутов. Часть 1' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'db_t_route_1'
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Table [dbo].[db_t_route_2] ******/
/****** Список всех маршрутов с служебной информацией ******/
CREATE TABLE [dbo].[db_t_route_2](
	[id] [bigint] IDENTITY(1,1) NOT NULL, 	/* ID записи */
	[p1] [bigint]  NOT NULL, 				/* Код маршрута */
	[p2] [tinyint] NOT NULL, 				/* Количество устройств в маршруте */
/* ИСТОЧНИК */
	[p3] [int] NOT NULL, 			/* Время задержки выполнения команды для маршрута включения */
	[p4] [int] NOT NULL, 			/* Время задержки выполнения команды для маршрута выключения */
/* ПРИЕМНИК */						
	[p5] [int] NOT NULL, 			/* Время задержки выполнения команды для маршрута включения */
	[p6] [int] NOT NULL, 			/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 2 */						
	[p7] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p8] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 3 */						
	[p9] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p10] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 4 */						
	[p11] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p12] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 5 */						
	[p13] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p14] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 6 */						
	[p15] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p16] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 7 */						
	[p17] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p18] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 8 */						
	[p19] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p20] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 9 */						
	[p21] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p22] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 10 */						
	[p23] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p24] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 11 */						
	[p25] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p26] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 12 */						
	[p27] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p28] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 13 */						
	[p29] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p30] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 14 */						
	[p31] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p32] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 15 */						
	[p33] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p34] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 16 */						
	[p35] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p36] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 17 */						
	[p37] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p38] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 18 */						
	[p39] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p40] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 19 */						
	[p41] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p42] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 20 */						
	[p43] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p44] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 21 */						
	[p45] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p46] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 22 */						
	[p47] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p48] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 23 */						
	[p49] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p50] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 24 */						
	[p51] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p52] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 25 */						
	[p53] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p54] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 26 */						
	[p55] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p56] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 27 */						
	[p57] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p58] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 28 */						
	[p59] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p60] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 29 */						
	[p61] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p62] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 30 */						
	[p63] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p64] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 31 */						
	[p65] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p66] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 32 */						
	[p67] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p68] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 33 */						
	[p69] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p70] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 34 */						
	[p71] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p72] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 35 */						
	[p73] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p74] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 36 */						
	[p75] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p76] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 37 */						
	[p77] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p78] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 38 */						
	[p79] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p80] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 39 */						
	[p81] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p82] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 40 */						
	[p83] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p84] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 41 */						
	[p85] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p86] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 42 */						
	[p87] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p88] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 43 */						
	[p89] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p90] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 44 */						
	[p91] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p92] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 45 */						
	[p93] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p94] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 46 */						
	[p95] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p96] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 47 */						
	[p97] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p98] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 48 */						
	[p99] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p100] [int], 					/* Время задержки выполнения команды для маршрута выключения */
/* Устройство 49 */						
	[p101] [int] , 					/* Время задержки выполнения команды для маршрута включения */
	[p102] [int], 					/* Время задержки выполнения команды для маршрута выключения */
	CONSTRAINT [PK_db_t_route_2] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Список маршрутов. Часть 2' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'db_t_route_2'
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Table [dbo].[db_t_route_active] ******/
/****** Список активных маршрутов (на период тестирования без ПЛК) ******/
CREATE TABLE [dbo].[db_t_route_active](
	[id] [bigint] IDENTITY(1,1) NOT NULL,	/* ID записи */
	[id_vis] [varchar](255) NOT NULL,		/* Номер по порядку */
	[date_add] [varchar](255) ,				/* Дата и время добавления маршрута в очередь */
	[id_route] [varchar](255) ,				/* Код маршрута из справочника */
	[route_desc] [varchar](255) ,			/* Описание маршрута */
	[route_status] [varchar](255) ,			/* Текущий статус выбранного маршрута: В работе / Остановлен */
CONSTRAINT [PK_db_t_route_active] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Список активных маршрутов' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'db_t_route_active'
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Table [dbo].[db_t_obj] ******/
/****** Список всех устройств, которые разрешено использовать и добавлять в маршрут ******/
CREATE TABLE [dbo].[db_t_obj](
	[id] [bigint] IDENTITY(1,1) NOT NULL,			/* ID записи */
	[bi_index_row] [bigint] NOT NULL,			/* Номер записи для сортировки */
	[id_obj] [bigint] NOT NULL,						/* Код устройства */
	[obj_kks] [varchar](255) NOT NULL,				/* Тег АСУТП */
	[obj_desc] [varchar](255) NOT NULL,				/* Описание */
	[obj_type] [varchar](255) NOT NULL,				/* Тип устройства */
	[obj_cat1] [bit] NOT NULL,						/* Категория устройства: Источник */
	[obj_cat2] [bit] NOT NULL,						/* Категория устройства: Приемник */
	[obj_cat3] [bit] NOT NULL,						/* Категория устройства: Промежуточное */
	[obj_cat_main] [varchar](255) NOT NULL,			/* Название основной категории  */
	CONSTRAINT [PK_db_t_obj] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Список устройств' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'db_t_obj'
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Table [dbo].[db_t_obj_filter] ******/
/****** Список всех устройств, которые разрешено использовать и добавлять в маршрут ******/
CREATE TABLE [dbo].[db_t_obj_filter](
	[id] [bigint] IDENTITY(1,1) NOT NULL,			/* ID записи */
	[obj_kks] [varchar](255) NOT NULL,				/* Тег АСУТП */
	[obj_cat_main] [varchar](255) NOT NULL,			/* Название основной категории  */
	CONSTRAINT [PK_db_t_obj_filter] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Список выбранных устройств' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'db_t_obj_filter'
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Table [dbo].[db_t_cfg_obj] ******/
/****** Список выбранных устройств в конфигураторе маршрутов ******/
CREATE TABLE [dbo].[db_t_cfg_obj](
	[id] [bigint] IDENTITY(1,1) NOT NULL,
	[id_vis] [varchar](255) NOT NULL,
	[obj_kks] [varchar](255) NOT NULL,
	[id_cmd] [bigint] NOT NULL,
	[cmd_desc] [varchar](255) NOT NULL,
	[t_on] [int] NOT NULL,
	[t_off] [int] NOT NULL,
 CONSTRAINT [PK_db_t_cfg_obj] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Список выбранных устройств в конфигураторе маршрутов' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'db_t_cfg_obj'
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Table [dbo].[db_t_new] ******/
/****** Конфигуратор маршрутов - Перечень устройств с параметрами для изменения и создания нового маршрута ******/
CREATE TABLE db_t_new (
	i_id			bigint,			-- Номер п/п
	i_id_obj		bigint,			-- ID устройства
	s_obj			NVARCHAR(255),	-- KKS устройства (тег)
	i_cmd			int,			-- ID команды
	s_cmd_desc		NVARCHAR(255),	-- Описание команды
	i_time_start	bigint,			-- Время пуска
	i_time_stop		bigint			-- Время остановки
)
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Table [dbo].[Motor_WorkTime] ******/
/****** Конфигуратор маршрутов - Перечень устройств с параметрами для изменения и создания нового маршрута ******/
CREATE TABLE [dbo].[Motor_WorkTime](
	[id] [bigint] IDENTITY(1,1) NOT NULL,	-- Номер п/п
	[kks] [nchar](255) NULL,				-- KKS устройства (тег)
	[hour] [bigint] NULL,					-- Часовая наработка двигателя, ч
	[folder] [nchar](255) NULL,				-- Папка, в которой хранится параметр (OPC UA)
 CONSTRAINT [PK_Motor_WorkTime] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/* ---------------------------------------------------------------------------------------------------------------------- */
/* ---------------------------------------------------------------------------------------------------------------------- */
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Добавление пользователя db_DEK_adm ******/
IF NOT EXISTS (SELECT * FROM sys.syslogins WHERE name = 'db_DEK_adm')
BEGIN
	CREATE LOGIN db_DEK_adm WITH PASSWORD = '123'
END
CREATE USER db_DEK_adm FOR LOGIN db_DEK_adm
GO
EXEC sp_addrolemember 'db_owner', 'db_DEK_adm';
GO
/* ---------------------------------------------------------------------------------------------------------------------- */
/* ---------------------------------------------------------------------------------------------------------------------- */
/* ---------------------------------------------------------------------------------------------------------------------- */
/* ---------------------------------------------------------------------------------------------------------------------- */
/****** Заполнение таблиц ******/
/****** Table [dbo].[db_t_route_active] ******/
/* EXCEL:  ="('','','','','')," */
INSERT INTO [dbo].[db_t_route_active]([id_vis],[date_add],[id_route],[route_desc],[route_status])
     VALUES        
		('01','','','',''),
		('02','','','',''),
		('03','','','',''),
		('04','','','',''),
		('05','','','',''),
		('06','','','',''),
		('07','','','',''),
		('08','','','',''),
		('09','','','',''),
		('10','','','',''),
		('11','','','',''),
		('12','','','',''),
		('13','','','',''),
		('14','','','',''),
		('15','','','',''),
		('16','','','',''),
		('17','','','',''),
		('18','','','',''),
		('19','','','',''),
		('20','','','',''),
		('21','','','',''),
		('22','','','',''),
		('23','','','',''),
		('24','','','',''),
		('25','','','',''),
		('26','','','',''),
		('27','','','',''),
		('28','','','',''),
		('29','','','',''),
		('30','','','',''),
		('31','','','',''),
		('32','','','',''),
		('33','','','',''),
		('34','','','',''),
		('35','','','',''),
		('36','','','',''),
		('37','','','',''),
		('38','','','',''),
		('39','','','',''),
		('40','','','',''),
		('41','','','',''),
		('42','','','',''),
		('43','','','',''),
		('44','','','',''),
		('45','','','',''),
		('46','','','',''),
		('47','','','',''),
		('48','','','',''),
		('49','','','',''),
		('50','','','','')
GO
/****** Table [dbo].[db_t_obj] ******/
/* EXCEL: ="(" & "'" & B4 & "'" & "," & "'" & C4 & "'" & "," & "'" & D4 & "'" & "," & E4 & "," & F4 & "," & G4 & "," & "'" & H4 & "'" & ")," */
INSERT INTO [dbo].[db_t_obj]([bi_index_row],[id_obj],[obj_kks],[obj_desc],[obj_type],[obj_cat1],[obj_cat2],[obj_cat3],[obj_cat_main])
     VALUES
			(1001,'1','K1R','Перекидной клапан 1Р','Перекидной клапан',0,0,0,'0'),
			(1002,'2','K2R','Перекидной клапан 2Р','Перекидной клапан',0,0,0,'0'),
			(1003,'3','K45','Перекидной клапан 45','Перекидной клапан',0,0,0,'0'),
			(1004,'4','K45A','Перекидной клапан 45A','Перекидной клапан',0,0,0,'0'),
			(1005,'5','K46','Перекидной клапан 46','Перекидной клапан',0,0,0,'0'),
			(1006,'6','K47','Перекидной клапан 47','Перекидной клапан',0,0,0,'0'),
			(1007,'7','K124','Перекидной клапан 124','Перекидной клапан',0,0,0,'0'),
			(1008,'8','K124A','Перекидной клапан 124A','Перекидной клапан',0,0,0,'0'),
			(1009,'9','K125','Перекидной клапан 125','Перекидной клапан',0,0,0,'0'),
			(1010,'10','K125A','Перекидной клапан 125A','Перекидной клапан',0,0,0,'0'),
			(1011,'11','K126','Перекидной клапан 126','Перекидной клапан',0,0,0,'0'),
			(1012,'12','K127','Перекидной клапан 127','Перекидной клапан',0,0,0,'0'),
			(1013,'13','K128','Перекидной клапан 128','Перекидной клапан',0,0,0,'0'),
			(1014,'14','K129','Перекидной клапан 129','Перекидной клапан',0,0,0,'0'),
			(1015,'15','K130','Перекидной клапан 130','Перекидной клапан',0,0,0,'0'),
			(1016,'16','K130A','Перекидной клапан 130A','Перекидной клапан',0,0,0,'0'),
			(1017,'17','K131','Перекидной клапан 131','Перекидной клапан',0,0,0,'0'),
			(1018,'18','K132','Перекидной клапан 132','Перекидной клапан',0,0,0,'0'),
			(1019,'19','K133','Перекидной клапан 133','Перекидной клапан',0,0,0,'0'),
			(1020,'20','K134','Перекидной клапан 134','Перекидной клапан',0,0,0,'0'),
			(1021,'21','K135','Перекидной клапан 135','Перекидной клапан',0,0,0,'0'),
			(1022,'22','K136','Перекидной клапан 136','Перекидной клапан',0,0,0,'0'),
			(1023,'23','K137','Перекидной клапан 137','Перекидной клапан',0,0,0,'0'),
			(1024,'24','K138','Перекидной клапан 138','Перекидной клапан',0,0,0,'0'),
			(1025,'25','K139','Перекидной клапан 139','Перекидной клапан',0,0,0,'0'),
			(1026,'26','K139A','Перекидной клапан 139A','Перекидной клапан',0,0,0,'0'),
			(1027,'27','K140','Перекидной клапан 140','Перекидной клапан',0,0,0,'0'),
			(1028,'28','K140A','Перекидной клапан 140A','Перекидной клапан',0,0,0,'0'),
			(1029,'29','K141','Перекидной клапан 141','Перекидной клапан',0,0,0,'0'),
			(1030,'30','K142','Перекидной клапан 142','Перекидной клапан',0,0,0,'0'),
			(1031,'31','K143','Перекидной клапан 143','Перекидной клапан',0,0,0,'0'),
			(1032,'32','K144','Перекидной клапан 144','Перекидной клапан',0,0,0,'0'),
			(1033,'33','K145','Перекидной клапан 145','Перекидной клапан',0,0,0,'0'),
			(1034,'34','K168','Перекидной клапан 168','Перекидной клапан',0,0,0,'0'),
			(1035,'35','K169','Перекидной клапан 169','Перекидной клапан',0,0,0,'0'),
			(1036,'68','M1','Нория 01','Нория',0,0,0,'0'),
			(1037,'69','M2','Нория 02','Нория',0,0,0,'0'),
			(1038,'70','M3','Нория 03','Нория',0,0,0,'0'),
			(1039,'71','M4','Нория 04','Нория',0,0,0,'0'),
			(1040,'72','M5','Нория 05','Нория',0,0,0,'0'),
			(1041,'73','M6','Нория 06','Нория',0,0,0,'0'),
			(1042,'74','M7','Нория 07','Нория',0,0,0,'0'),
			(1043,'75','M8','Нория 08','Нория',0,0,0,'0'),
			(1044,'76','M9','Нория 09','Нория',0,0,0,'0'),
			(1045,'77','M10','Конвейер ленточный 10','Конвейер ленточный',0,0,0,'0'),
			(1046,'78','M11','Конвейер ленточный 11','Конвейер ленточный',0,0,0,'0'),
			(1047,'79','M12','Конвейер ленточный 12','Конвейер ленточный',0,0,0,'0'),
			(1048,'80','M13','Конвейер ленточный 13','Конвейер ленточный',0,0,0,'0'),
			(1049,'81','M14','Конвейер ленточный 14','Конвейер ленточный',0,0,0,'0'),
			(1050,'62','M15','Конвейер ленточный 15','Конвейер реверсивный',0,0,0,'0'),
			(1051,'87','M16','Конвейер скребковый 16','Конвейер скребковый',0,0,0,'0'),
			(1052,'88','M17','Конвейер скребковый 17','Конвейер скребковый',0,0,0,'0'),
			(1053,'89','M29','Конвейер скребковый 29','Конвейер скребковый',0,0,0,'0'),
			(1054,'90','M30','Конвейер скребковый 30','Конвейер скребковый',0,0,0,'0'),
			(1055,'91','M31','Конвейер скребковый 31','Конвейер скребковый',0,0,0,'0'),
			(1056,'92','M32','Конвейер скребковый 32','Конвейер скребковый',0,0,0,'0'),
			(1057,'93','M33','Конвейер скребковый 33','Конвейер скребковый',0,0,0,'0'),
			(1058,'94','M34','Конвейер скребковый 34','Конвейер скребковый',0,0,0,'0'),
			(1059,'95','M35','Конвейер скребковый 35','Конвейер скребковый',0,0,0,'0'),
			(1060,'96','M36','Конвейер скребковый 36','Конвейер скребковый',0,0,0,'0'),
			(1061,'97','M37','Конвейер скребковый 37','Конвейер скребковый',0,0,0,'0'),
			(1062,'98','M38','Конвейер скребковый 38','Конвейер скребковый',0,0,0,'0'),
			(1063,'99','M39','Конвейер скребковый 39','Конвейер скребковый',0,0,0,'0'),
			(1064,'100','M40','Конвейер скребковый 40','Конвейер скребковый',0,0,0,'0'),
			(1065,'82','M41','Конвейер ленточный 41','Конвейер ленточный',0,0,0,'0'),
			(1066,'83','M42','Конвейер ленточный 42','Конвейер ленточный',0,0,0,'0'),
			(1067,'84','M43','Конвейер ленточный 43','Конвейер ленточный',0,0,0,'0'),
			(1068,'85','M44','Конвейер ленточный 44','Конвейер ленточный',0,0,0,'0'),
			(1069,'86','M45','Конвейер ленточный 45','Конвейер ленточный',0,0,0,'0'),
			(1070,'125','M48','Скальператор48','Скальператор',0,0,0,'0'),
			(1071,'126','M49','Скальператор49','Скальператор',0,0,0,'0'),
			(1072,'101','M50','Конвейер скребковый 50','Конвейер скребковый',0,0,0,'0'),
			(1073,'102','M51','Конвейер скребковый 51','Конвейер скребковый',0,0,0,'0'),
			(1074,'103','M52','Конвейер скребковый 52','Конвейер скребковый',0,0,0,'0'),
			(1075,'104','M53','Конвейер скребковый 53','Конвейер скребковый',0,0,0,'0'),
			(1076,'105','M54','Конвейер скребковый 54','Конвейер скребковый',0,0,0,'0'),
			(1077,'106','M55','Конвейер скребковый 55','Конвейер скребковый',0,0,0,'0'),
			(1078,'107','M56','Конвейер скребковый 56','Конвейер скребковый',0,0,0,'0'),
			(1079,'108','M57','Конвейер скребковый 57','Конвейер скребковый',0,0,0,'0'),
			(1080,'109','M58','Конвейер скребковый 58','Конвейер скребковый',0,0,0,'0'),
			(1081,'110','M59','Конвейер скребковый 59','Конвейер скребковый',0,0,0,'0'),
			(1082,'111','M60','Конвейер скребковый 60','Конвейер скребковый',0,0,0,'0'),
			(1083,'112','M61','Конвейер скребковый 61','Конвейер скребковый',0,0,0,'0'),
			(1084,'113','M62','Конвейер скребковый 62','Конвейер скребковый',0,0,0,'0'),
			(1085,'114','M63','Конвейер скребковый 63','Конвейер скребковый',0,0,0,'0'),
			(1086,'115','M64','Конвейер скребковый 64','Конвейер скребковый',0,0,0,'0'),
			(1087,'123','M65','БИС65','БИС',0,0,0,'0'),
			(1088,'64','M66','Вибромотор 66','Вибромотор',0,0,0,'0'),
			(1089,'65','M67','Вибромотор 67','Вибромотор',0,0,0,'0'),
			(1090,'124','M68','БИС68','БИС',0,0,0,'0'),
			(1091,'66','M69','Вибромотор 69','Вибромотор',0,0,0,'0'),
			(1092,'67','M70','Вибромотор 70','Вибромотор',0,0,0,'0'),
			(1093,'131','M96','Роторный питатель асперации 96','Роторный питатель',0,0,0,'0'),
			(1094,'132','M97','Роторный питатель асперации 97','Роторный питатель',0,0,0,'0'),
			(1095,'133','M98','Роторный питатель асперации 98','Роторный питатель',0,0,0,'0'),
			(1096,'134','M99','Роторный питатель асперации 99','Роторный питатель',0,0,0,'0'),
			(1097,'136','M100','Роторный питатель асперации 100','Роторный питатель',0,0,0,'0'),
			(1098,'137','M101','Роторный питатель асперации 101','Роторный питатель',0,0,0,'0'),
			(1099,'139','M102','Роторный питатель асперации 102','Роторный питатель',0,0,0,'0'),
			(1100,'138','M103','Роторный питатель асперации 103','Роторный питатель',0,0,0,'0'),
			(1101,'135','M104','Роторный питатель асперации 104','Роторный питатель',0,0,0,'0'),
			(1102,'140','M105','Роторный питатель асперации 105','Роторный питатель',0,0,0,'0'),
			(1103,'36','M106','Шибер 106','Шибер',0,0,0,'0'),
			(1104,'37','M107','Шибер 107','Шибер',0,0,0,'0'),
			(1105,'38','M108','Шибер 108','Шибер',0,0,0,'0'),
			(1106,'39','M109','Шибер 109','Шибер',0,0,0,'0'),
			(1107,'40','M110','Шибер 110','Шибер',0,0,0,'0'),
			(1108,'41','M112','Шибер 112','Шибер',0,0,0,'0'),
			(1109,'42','M113','Шибер 113','Шибер',0,0,0,'0'),
			(1110,'43','M115','Шибер 115','Шибер',0,0,0,'0'),
			(1111,'55','M116','Шибер 116','Шибер трехпозиционный',0,0,0,'0'),
			(1112,'56','M117','Шибер 117','Шибер трехпозиционный',0,0,0,'0'),
			(1113,'57','M118','Шибер 118','Шибер трехпозиционный',0,0,0,'0'),
			(1114,'44','M123','Шибер 123','Шибер',0,0,0,'0'),
			(1115,'58','M146','Шибер 146','Шибер трехпозиционный',0,0,0,'0'),
			(1116,'45','M147','Шибер 147','Шибер',0,0,0,'0'),
			(1117,'46','M148','Шибер 148','Шибер',0,0,0,'0'),
			(1118,'47','M149','Шибер 149','Шибер',0,0,0,'0'),
			(1119,'48','M150','Шибер 150','Шибер',0,0,0,'0'),
			(1120,'49','M151','Шибер 151','Шибер',0,0,0,'0'),
			(1121,'50','M152','Шибер 152','Шибер',0,0,0,'0'),
			(1122,'51','M153','Шибер 153','Шибер',0,0,0,'0'),
			(1123,'52','M154','Шибер 154','Шибер',0,0,0,'0'),
			(1124,'116','M160','Конвейер скребковый 160','Конвейер скребковый',0,0,0,'0'),
			(1125,'117','M161','Конвейер скребковый 161','Конвейер скребковый',0,0,0,'0'),
			(1126,'118','M162','Конвейер скребковый 162','Конвейер скребковый',0,0,0,'0'),
			(1127,'119','M163','Конвейер скребковый 163','Конвейер скребковый',0,0,0,'0'),
			(1128,'63','M164','Конвейер скребковый 164','Конвейер реверсивный',0,0,0,'0'),
			(1129,'59','M165','Шибер 165','Шибер трехпозиционный',0,0,0,'0'),
			(1130,'60','M166','Шибер 166','Шибер трехпозиционный',0,0,0,'0'),
			(1131,'61','M167','Шибер 167','Шибер трехпозиционный',0,0,0,'0'),
			(1132,'120','M170','Конвейер скребковый 170','Конвейер скребковый',0,0,0,'0'),
			(1133,'121','M171','Конвейер скребковый 171','Конвейер скребковый',0,0,0,'0'),
			(1134,'122','M172','Конвейер скребковый 172','Конвейер скребковый',0,0,0,'0'),
			(1135,'53','M173','Шибер 173','Шибер',0,0,0,'0'),
			(1136,'54','M174','Шибер 174','Шибер',0,0,0,'0'),
			(1137,'127','M300','Роторный питатель асперации 300','Роторный питатель',0,0,0,'0'),
			(1138,'128','M301','Роторный питатель асперации 301','Роторный питатель',0,0,0,'0'),
			(1139,'129','M302','Роторный питатель асперации 302','Роторный питатель',0,0,0,'0'),
			(1140,'130','M303','Роторный питатель асперации 303','Роторный питатель',0,0,0,'0'),
			(1141,'141','M311','Механизм выгрузки 311','Механизм выгрузки',0,0,0,'0'),
			(1142,'142','M312','Механизм выгрузки 312','Механизм выгрузки',0,0,0,'0')
GO
/****** Table [dbo].[[Motor_WorkTime]] ******/
INSERT INTO [dbo].[Motor_WorkTime]
           ([kks]
           ,[hour]
           ,[folder])
     VALUES
           ('M1', 0, 'NOR'),
			('M2', 0, 'NOR'),
			('M3', 0, 'NOR'),
			('M4', 0, 'NOR'),
			('M5', 0, 'NOR'),
			('M6', 0, 'NOR'),
			('M7', 0, 'NOR'),
			('M8', 0, 'NOR'),
			('M9', 0, 'NOR'),
			('M10', 0, 'CONV'),
			('M11', 0, 'CONV'),
			('M12', 0, 'CONV'),
			('M13', 0, 'CONV'),
			('M14', 0, 'CONV'),
			('M15', 0, 'CONV'),
			('M16', 0, 'CONV'),
			('M17', 0, 'CONV'),
			('M29', 0, 'CONV'),
			('M30', 0, 'CONV'),
			('M31', 0, 'CONV'),
			('M32', 0, 'CONV'),
			('M33', 0, 'CONV'),
			('M34', 0, 'CONV'),
			('M35', 0, 'CONV'),
			('M36', 0, 'CONV'),
			('M37', 0, 'CONV'),
			('M38', 0, 'CONV'),
			('M39', 0, 'CONV'),
			('M40', 0, 'CONV'),
			('M41', 0, 'CONV'),
			('M42', 0, 'CONV'),
			('M43', 0, 'CONV'),
			('M44', 0, 'CONV'),
			('M45', 0, 'CONV'),
			('M48', 0, 'EQV'),
			('M49', 0, 'EQV'),
			('M50', 0, 'CONV'),
			('M51', 0, 'CONV'),
			('M52', 0, 'CONV'),
			('M53', 0, 'CONV'),
			('M54', 0, 'CONV'),
			('M55', 0, 'CONV'),
			('M56', 0, 'CONV'),
			('M57', 0, 'CONV'),
			('M58', 0, 'CONV'),
			('M59', 0, 'CONV'),
			('M60', 0, 'CONV'),
			('M61', 0, 'CONV'),
			('M62', 0, 'CONV'),
			('M63', 0, 'CONV'),
			('M64', 0, 'CONV'),
			('M65', 0, 'EQV'),
			('M68', 0, 'EQV'),
			('M96', 0, 'EQV'),
			('M97', 0, 'EQV'),
			('M98', 0, 'EQV'),
			('M99', 0, 'EQV'),
			('M100', 0, 'EQV'),
			('M101', 0, 'EQV'),
			('M102', 0, 'EQV'),
			('M103', 0, 'EQV'),
			('M104', 0, 'EQV'),
			('M105', 0, 'EQV'),
			('M160', 0, 'CONV'),
			('M161', 0, 'CONV'),
			('M162', 0, 'CONV'),
			('M163', 0, 'CONV'),
			('M164', 0, 'CONV'),
			('M170', 0, 'CONV'),
			('M171', 0, 'CONV'),
			('M172', 0, 'CONV')
GO
-- Создание типа данных [dbo].[Motor_WorkTime_run_type]
CREATE TYPE [dbo].[Motor_WorkTime_run_type] AS TABLE
(
    id bigint,
    kks VARCHAR(255),
    hour bigint,
    folder VARCHAR(255)
)	
/* Создание хранимой процедуры [dbo].[prog_0_SELECT_statistic] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[prog_0_SELECT_statistic]
AS
BEGIN
	SET NOCOUNT ON;
	SELECT [route_status], COUNT(*) AS count
	FROM [db_DEK].[dbo].[db_t_route_active]
	GROUP BY [route_status]
END
GO
/* Создание хранимой процедуры [dbo].[prog_1_SELECT_route_1] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[prog_1_SELECT_route_1]
	@ch_OUT_x tinyint = 0,
	@ch_OUT_Search varchar(255) = ''
AS
BEGIN
	SET NOCOUNT ON;
	/* С выборкой по устройствам */
	IF LEFT(CAST(@ch_OUT_x AS varchar(3)),1) = '2'
	BEGIN
		/* Поиск совпадений */	
		IF @ch_OUT_x = 20 /* Без поиска, с сортировкой по номеру маршрута */
			SELECT [p1],[p2] 
			FROM [db_t_route_1] r
			WHERE EXISTS(
				SELECT 1
				FROM [db_t_obj_filter] d
				WHERE 
					r.[p10] = d.[obj_kks] OR r.[p14] = d.[obj_kks] OR r.[p18] = d.[obj_kks] OR r.[p22] = d.[obj_kks] OR r.[p26] = d.[obj_kks] OR r.[p30] = d.[obj_kks] OR 
					r.[p34] = d.[obj_kks] OR r.[p38] = d.[obj_kks] OR r.[p42] = d.[obj_kks] OR r.[p46] = d.[obj_kks] OR r.[p50] = d.[obj_kks] OR r.[p54] = d.[obj_kks] OR 
					r.[p58] = d.[obj_kks] OR r.[p62] = d.[obj_kks] OR r.[p66] = d.[obj_kks] OR r.[p70] = d.[obj_kks] OR r.[p74] = d.[obj_kks] OR r.[p78] = d.[obj_kks] OR 
					r.[p82] = d.[obj_kks] OR r.[p86] = d.[obj_kks] OR r.[p90] = d.[obj_kks] OR r.[p94] = d.[obj_kks] OR r.[p98] = d.[obj_kks] OR r.[p102] = d.[obj_kks] OR 
					r.[p106] = d.[obj_kks] OR r.[p110] = d.[obj_kks] OR r.[p114] = d.[obj_kks] OR r.[p118] = d.[obj_kks] OR r.[p122] = d.[obj_kks] OR r.[p126] = d.[obj_kks] OR 
					r.[p130] = d.[obj_kks] OR r.[p134] = d.[obj_kks] OR r.[p138] = d.[obj_kks] OR r.[p142] = d.[obj_kks] OR r.[p146] = d.[obj_kks] OR r.[p150] = d.[obj_kks] OR 
					r.[p154] = d.[obj_kks] OR r.[p158] = d.[obj_kks] OR r.[p162] = d.[obj_kks] OR r.[p166] = d.[obj_kks] OR r.[p170] = d.[obj_kks] OR r.[p174] = d.[obj_kks] OR 
					r.[p178] = d.[obj_kks] OR r.[p182] = d.[obj_kks] OR r.[p186] = d.[obj_kks] OR r.[p190] = d.[obj_kks] OR r.[p194] = d.[obj_kks] OR r.[p198] = d.[obj_kks] OR 
					r.[p202] = d.[obj_kks] OR r.[p206] = d.[obj_kks]
				HAVING COUNT(*) = (SELECT COUNT(*) FROM [db_t_obj_filter])) ORDER BY [p1] ASC
		IF @ch_OUT_x = 21 /* Без поиска, с сортировкой по популярности */
			SELECT [p1],[p2] 
			FROM [db_t_route_1] r
			WHERE EXISTS(
				SELECT 1
				FROM [db_t_obj_filter] d
				WHERE 
					r.[p10] = d.[obj_kks] OR r.[p14] = d.[obj_kks] OR r.[p18] = d.[obj_kks] OR r.[p22] = d.[obj_kks] OR r.[p26] = d.[obj_kks] OR r.[p30] = d.[obj_kks] OR 
					r.[p34] = d.[obj_kks] OR r.[p38] = d.[obj_kks] OR r.[p42] = d.[obj_kks] OR r.[p46] = d.[obj_kks] OR r.[p50] = d.[obj_kks] OR r.[p54] = d.[obj_kks] OR 
					r.[p58] = d.[obj_kks] OR r.[p62] = d.[obj_kks] OR r.[p66] = d.[obj_kks] OR r.[p70] = d.[obj_kks] OR r.[p74] = d.[obj_kks] OR r.[p78] = d.[obj_kks] OR 
					r.[p82] = d.[obj_kks] OR r.[p86] = d.[obj_kks] OR r.[p90] = d.[obj_kks] OR r.[p94] = d.[obj_kks] OR r.[p98] = d.[obj_kks] OR r.[p102] = d.[obj_kks] OR 
					r.[p106] = d.[obj_kks] OR r.[p110] = d.[obj_kks] OR r.[p114] = d.[obj_kks] OR r.[p118] = d.[obj_kks] OR r.[p122] = d.[obj_kks] OR r.[p126] = d.[obj_kks] OR 
					r.[p130] = d.[obj_kks] OR r.[p134] = d.[obj_kks] OR r.[p138] = d.[obj_kks] OR r.[p142] = d.[obj_kks] OR r.[p146] = d.[obj_kks] OR r.[p150] = d.[obj_kks] OR 
					r.[p154] = d.[obj_kks] OR r.[p158] = d.[obj_kks] OR r.[p162] = d.[obj_kks] OR r.[p166] = d.[obj_kks] OR r.[p170] = d.[obj_kks] OR r.[p174] = d.[obj_kks] OR 
					r.[p178] = d.[obj_kks] OR r.[p182] = d.[obj_kks] OR r.[p186] = d.[obj_kks] OR r.[p190] = d.[obj_kks] OR r.[p194] = d.[obj_kks] OR r.[p198] = d.[obj_kks] OR 
					r.[p202] = d.[obj_kks] OR r.[p206] = d.[obj_kks]
				HAVING COUNT(*) = (SELECT COUNT(*) FROM [db_t_obj_filter])) ORDER BY [p6] DESC
		IF @ch_OUT_x = 210 /* С поиском, с сортировкой по номеру маршрута */ 
		BEGIN
			DECLARE @s_Query1 AS nvarchar(MAX) = '
				SELECT [p1],[p2] 
				FROM [db_t_route_1] r
				WHERE EXISTS(
					SELECT 1
					FROM [db_t_obj_filter] d
					WHERE 
						(r.[p10] = d.[obj_kks] OR r.[p14] = d.[obj_kks] OR r.[p18] = d.[obj_kks] OR r.[p22] = d.[obj_kks] OR r.[p26] = d.[obj_kks] OR r.[p30] = d.[obj_kks] OR 
						r.[p34] = d.[obj_kks] OR r.[p38] = d.[obj_kks] OR r.[p42] = d.[obj_kks] OR r.[p46] = d.[obj_kks] OR r.[p50] = d.[obj_kks] OR r.[p54] = d.[obj_kks] OR 
						r.[p58] = d.[obj_kks] OR r.[p62] = d.[obj_kks] OR r.[p66] = d.[obj_kks] OR r.[p70] = d.[obj_kks] OR r.[p74] = d.[obj_kks] OR r.[p78] = d.[obj_kks] OR 
						r.[p82] = d.[obj_kks] OR r.[p86] = d.[obj_kks] OR r.[p90] = d.[obj_kks] OR r.[p94] = d.[obj_kks] OR r.[p98] = d.[obj_kks] OR r.[p102] = d.[obj_kks] OR 
						r.[p106] = d.[obj_kks] OR r.[p110] = d.[obj_kks] OR r.[p114] = d.[obj_kks] OR r.[p118] = d.[obj_kks] OR r.[p122] = d.[obj_kks] OR r.[p126] = d.[obj_kks] OR 
						r.[p130] = d.[obj_kks] OR r.[p134] = d.[obj_kks] OR r.[p138] = d.[obj_kks] OR r.[p142] = d.[obj_kks] OR r.[p146] = d.[obj_kks] OR r.[p150] = d.[obj_kks] OR 
						r.[p154] = d.[obj_kks] OR r.[p158] = d.[obj_kks] OR r.[p162] = d.[obj_kks] OR r.[p166] = d.[obj_kks] OR r.[p170] = d.[obj_kks] OR r.[p174] = d.[obj_kks] OR 
						r.[p178] = d.[obj_kks] OR r.[p182] = d.[obj_kks] OR r.[p186] = d.[obj_kks] OR r.[p190] = d.[obj_kks] OR r.[p194] = d.[obj_kks] OR r.[p198] = d.[obj_kks] OR 
						r.[p202] = d.[obj_kks] OR r.[p206] = d.[obj_kks])
				HAVING COUNT(*) = (SELECT COUNT(*) FROM [db_t_obj_filter])) AND ((r.[p1] LIKE N''%' + @ch_OUT_Search + '%'') OR (r.[p2] LIKE N''%' + @ch_OUT_Search + '%'')) ORDER BY r.[p1] ASC'
			EXEC sp_executesql @s_Query1
		END
		IF @ch_OUT_x = 211 /* С поиском, с сортировкой по популярности */
		BEGIN
			DECLARE @s_Query2 AS nvarchar(MAX) = '
				SELECT [p1],[p2] 
				FROM [db_t_route_1] r
				WHERE EXISTS(
					SELECT 1
					FROM [db_t_obj_filter] d
					WHERE 
						(r.[p10] = d.[obj_kks] OR r.[p14] = d.[obj_kks] OR r.[p18] = d.[obj_kks] OR r.[p22] = d.[obj_kks] OR r.[p26] = d.[obj_kks] OR r.[p30] = d.[obj_kks] OR 
						r.[p34] = d.[obj_kks] OR r.[p38] = d.[obj_kks] OR r.[p42] = d.[obj_kks] OR r.[p46] = d.[obj_kks] OR r.[p50] = d.[obj_kks] OR r.[p54] = d.[obj_kks] OR 
						r.[p58] = d.[obj_kks] OR r.[p62] = d.[obj_kks] OR r.[p66] = d.[obj_kks] OR r.[p70] = d.[obj_kks] OR r.[p74] = d.[obj_kks] OR r.[p78] = d.[obj_kks] OR 
						r.[p82] = d.[obj_kks] OR r.[p86] = d.[obj_kks] OR r.[p90] = d.[obj_kks] OR r.[p94] = d.[obj_kks] OR r.[p98] = d.[obj_kks] OR r.[p102] = d.[obj_kks] OR 
						r.[p106] = d.[obj_kks] OR r.[p110] = d.[obj_kks] OR r.[p114] = d.[obj_kks] OR r.[p118] = d.[obj_kks] OR r.[p122] = d.[obj_kks] OR r.[p126] = d.[obj_kks] OR 
						r.[p130] = d.[obj_kks] OR r.[p134] = d.[obj_kks] OR r.[p138] = d.[obj_kks] OR r.[p142] = d.[obj_kks] OR r.[p146] = d.[obj_kks] OR r.[p150] = d.[obj_kks] OR 
						r.[p154] = d.[obj_kks] OR r.[p158] = d.[obj_kks] OR r.[p162] = d.[obj_kks] OR r.[p166] = d.[obj_kks] OR r.[p170] = d.[obj_kks] OR r.[p174] = d.[obj_kks] OR 
						r.[p178] = d.[obj_kks] OR r.[p182] = d.[obj_kks] OR r.[p186] = d.[obj_kks] OR r.[p190] = d.[obj_kks] OR r.[p194] = d.[obj_kks] OR r.[p198] = d.[obj_kks] OR 
						r.[p202] = d.[obj_kks] OR r.[p206] = d.[obj_kks])
				HAVING COUNT(*) = (SELECT COUNT(*) FROM [db_t_obj_filter])) AND ((r.[p1] LIKE N''%' + @ch_OUT_Search + '%'') OR (r.[p2] LIKE N''%' + @ch_OUT_Search + '%'')) ORDER BY r.[[p6]] DESC'
			EXEC sp_executesql @s_Query2
		END
	END
	ELSE
	BEGIN 
		IF @ch_OUT_x = 0 /* Без поиска, с сортировкой по номеру маршрута */
			SELECT [p1],[p2] FROM [dbo].[db_t_route_1] ORDER BY [p1] ASC
		IF @ch_OUT_x = 1 /* Без поиска, с сортировкой по популярности */
			SELECT [p1],[p2] FROM [dbo].[db_t_route_1] ORDER BY [p6] DESC, [p1]
		IF @ch_OUT_x = 10 /* С поиском, с сортировкой по номеру маршрута */
		BEGIN
			DECLARE @s_Query3 AS nvarchar(MAX) = '
				SELECT [p1],[p2] FROM [dbo].[db_t_route_1] WHERE (([p1] LIKE N''%' + @ch_OUT_Search + '%'') OR ([p2] LIKE N''%' + @ch_OUT_Search + '%'')) ORDER BY [p1] ASC'
			EXEC sp_executesql @s_Query3
		END
		IF @ch_OUT_x = 11 /* С поиском, с сортировкой по популярности */
		BEGIN
			DECLARE @s_Query4 AS nvarchar(MAX) = '
				SELECT [p1],[p2] FROM [dbo].[db_t_route_1] WHERE (([p1] LIKE N''%' + @ch_OUT_Search + '%'') OR ([p2] LIKE N''%' + @ch_OUT_Search + '%'')) ORDER BY [p6] DESC'
			EXEC sp_executesql @s_Query4
		END 
	END
END
/* Создание хранимой процедуры [dbo].[prog_2_SELECT_obj] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[prog_2_SELECT_obj]
	@ch_OUT_x tinyint = 0,
	@ch_OUT_Search varchar(255) = ''
AS
BEGIN
	SET NOCOUNT ON;
	IF @ch_OUT_x = 0
		SELECT * FROM [dbo].[db_t_obj]
	IF @ch_OUT_x = 1
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat1]=1)
	IF @ch_OUT_x = 2
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat2]=1)
	IF @ch_OUT_x = 3
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat3]=1)
	IF @ch_OUT_x = 10
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_kks] LIKE @ch_OUT_Search)
	IF @ch_OUT_x = 11
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat1]=1) AND ([obj_kks] LIKE @ch_OUT_Search)
	IF @ch_OUT_x = 12
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat2]=1) AND ([obj_kks] LIKE @ch_OUT_Search)
	IF @ch_OUT_x = 13
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat3]=1) AND ([obj_kks] LIKE @ch_OUT_Search)
END
/* Создание хранимой процедуры [dbo].[prog_3_SELECT_add_obj] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[prog_3_SELECT_add_obj]
	@ch_OUT_x tinyint = 0,
	@ch_OUT_Search varchar(255) = ''
AS
BEGIN
	SET NOCOUNT ON;
	IF @ch_OUT_x = 0
		SELECT [obj_kks],[obj_cat_main] FROM [dbo].[db_t_obj_filter]
	IF @ch_OUT_x = 1
		SELECT [obj_kks],[obj_cat_main] FROM [dbo].[db_t_obj_filter] WHERE ([obj_kks] LIKE @ch_OUT_Search)
END
/* Создание хранимой процедуры [dbo].[prog_4_SELECT_missed_id] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[prog_4_SELECT_missed_id]
AS
BEGIN
	SET NOCOUNT ON;
	SELECT MIN(t1.p1) + 1 AS 'missed_id'
	FROM [dbo].[db_t_route_1] t1
	LEFT JOIN [dbo].[db_t_route_1] t2 ON t1.p1 + 1 = t2.p1
	WHERE t2.p1 IS NULL
END
/* Создание хранимой процедуры [dbo].[prog_5_DELETE_route] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[prog_5_DELETE_route]
	@ch_OUT_x bigint = 0
AS
BEGIN
	SET NOCOUNT ON;
DELETE FROM [dbo].[db_t_route_1] WHERE [p1] = @ch_OUT_x
DELETE FROM [dbo].[db_t_route_2] WHERE [p1] = @ch_OUT_x
END
/* Создание хранимой процедуры [dbo].[prog_6_db_t_obj_filter_CLEAR] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO 
CREATE PROCEDURE prog_6_db_t_obj_filter_CLEAR 
AS
BEGIN
	SET NOCOUNT ON;
	DROP TABLE IF EXISTS [dbo].[db_t_obj_filter];
	DECLARE @s_Query AS nvarchar(MAX) = '
	SET ANSI_NULLS ON
	SET QUOTED_IDENTIFIER ON
	CREATE TABLE [dbo].[db_t_obj_filter](
		[id] [bigint] IDENTITY(1,1) NOT NULL,
		[obj_kks] [varchar](255) NOT NULL,
		[obj_cat_main] [varchar](255) NOT NULL,
	 CONSTRAINT [PK_db_t_obj_filter] PRIMARY KEY CLUSTERED 
	([id] ASC) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]) ON [PRIMARY]
	EXEC sys.sp_addextendedproperty @name=N''MS_Description'', @value=N''Список выбранных устройств'' , @level0type=N''SCHEMA'',@level0name=N''dbo'', @level1type=N''TABLE'',@level1name=N''db_t_obj_filter'''
	EXEC sp_executesql @s_Query
END
GO
/* Создание хранимой процедуры [dbo].[prog_7_union_table_route] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE prog_7_union_table_route 
	@i_num BIGINT = 1
AS
BEGIN
	SET NOCOUNT ON;
SELECT 1 AS id, p.p10 AS obj, p.p12 AS cmd, y.p3 AS t1, y.p4 AS t2 
								   FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 1 UNION ALL
SELECT 2, p.p18, p.p20, y.p7, y.p8 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 3 UNION ALL
SELECT 3, p.p22, p.p24, y.p9, y.p10 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 4 UNION ALL
SELECT 4, p.p26, p.p28, y.p11, y.p12 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 5 UNION ALL
SELECT 5, p.p30, p.p32, y.p13, y.p14 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 6 UNION ALL
SELECT 6, p.p34, p.p36, y.p15, y.p16 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 7 UNION ALL
SELECT 7, p.p38, p.p40, y.p17, y.p18 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 8 UNION ALL
SELECT 8, p.p42, p.p44, y.p19, y.p20 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 9 UNION ALL
SELECT 9, p.p46, p.p48, y.p21, y.p22 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 10 UNION ALL
SELECT 10, p.p50, p.p52, y.p23, y.p24 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 11 UNION ALL
SELECT 11, p.p54, p.p56, y.p25, y.p26 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 12 UNION ALL
SELECT 12, p.p58, p.p60, y.p27, y.p28 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 13 UNION ALL
SELECT 13, p.p62, p.p64, y.p29, y.p30 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 14 UNION ALL
SELECT 14, p.p66, p.p68, y.p31, y.p32 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 15 UNION ALL
SELECT 15, p.p70, p.p72, y.p33, y.p34 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 16 UNION ALL
SELECT 16, p.p74, p.p76, y.p35, y.p36 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 17 UNION ALL
SELECT 17, p.p78, p.p80, y.p37, y.p38 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 18 UNION ALL
SELECT 18, p.p82, p.p84, y.p39, y.p40 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 19 UNION ALL
SELECT 19, p.p86, p.p88, y.p41, y.p42 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 20 UNION ALL
SELECT 20, p.p90, p.p92, y.p43, y.p44 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 21 UNION ALL
SELECT 21, p.p94, p.p96, y.p45, y.p46 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 22 UNION ALL
SELECT 22, p.p98, p.p100, y.p47, y.p48 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 23 UNION ALL
SELECT 23, p.p102, p.p104, y.p49, y.p50 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 24 UNION ALL
SELECT 24, p.p106, p.p108, y.p51, y.p52 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 25 UNION ALL
SELECT 25, p.p110, p.p112, y.p53, y.p54 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 26 UNION ALL
SELECT 26, p.p114, p.p116, y.p55, y.p56 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 27 UNION ALL
SELECT 27, p.p118, p.p120, y.p57, y.p58 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 28 UNION ALL
SELECT 28, p.p122, p.p124, y.p59, y.p60 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 29 UNION ALL
SELECT 29, p.p126, p.p128, y.p61, y.p62 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 30 UNION ALL
SELECT 30, p.p130, p.p132, y.p63, y.p64 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 31 UNION ALL
SELECT 31, p.p134, p.p136, y.p65, y.p66 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 32 UNION ALL
SELECT 32, p.p138, p.p140, y.p67, y.p68 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 33 UNION ALL
SELECT 33, p.p142, p.p144, y.p69, y.p70 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 34 UNION ALL
SELECT 34, p.p146, p.p148, y.p71, y.p72 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 35 UNION ALL
SELECT 35, p.p150, p.p152, y.p73, y.p74 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 36 UNION ALL
SELECT 36, p.p154, p.p156, y.p75, y.p76 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 37 UNION ALL
SELECT 37, p.p158, p.p160, y.p77, y.p78 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 38 UNION ALL
SELECT 38, p.p162, p.p164, y.p79, y.p80 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 39 UNION ALL
SELECT 39, p.p166, p.p168, y.p81, y.p82 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 40 UNION ALL
SELECT 40, p.p170, p.p172, y.p83, y.p84 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 41 UNION ALL
SELECT 41, p.p174, p.p176, y.p85, y.p86 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 42 UNION ALL
SELECT 42, p.p178, p.p180, y.p87, y.p88 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 43 UNION ALL
SELECT 43, p.p182, p.p184, y.p89, y.p90 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 44 UNION ALL
SELECT 44, p.p186, p.p188, y.p91, y.p92 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 45 UNION ALL
SELECT 45, p.p190, p.p192, y.p93, y.p94 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 46 UNION ALL
SELECT 46, p.p194, p.p196, y.p95, y.p96 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 47 UNION ALL
SELECT 47, p.p198, p.p200, y.p97, y.p98 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 48 UNION ALL
SELECT 48, p.p202, p.p204, y.p99, y.p100 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 49 UNION ALL
SELECT 49, p.p206, p.p208, y.p101, y.p102 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 50 UNION ALL
SELECT p.p7, p.p14, p.p16, y.p5, y.p6 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 2
END
GO
/* Создание хранимой процедуры [dbo].[prog_7_union_table_route_ID] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE prog_7_union_table_route_ID 
	@i_num BIGINT = 1
AS
BEGIN
	SET NOCOUNT ON;
SELECT 1 AS i_id, p.p9 AS i_id_obj, p.p11 AS i_cmd, y.p3 AS i_time_start, y.p4 AS i_time_stop 
								   FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 1 UNION ALL
SELECT 2, p.p17, p.p19, y.p7, y.p8 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 3 UNION ALL
SELECT 3, p.p21, p.p23, y.p9, y.p10 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 4 UNION ALL
SELECT 4, p.p25, p.p27, y.p11, y.p12 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 5 UNION ALL
SELECT 5, p.p29, p.p31, y.p13, y.p14 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 6 UNION ALL
SELECT 6, p.p33, p.p35, y.p15, y.p16 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 7 UNION ALL
SELECT 7, p.p37, p.p39, y.p17, y.p18 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 8 UNION ALL
SELECT 8, p.p41, p.p43, y.p19, y.p20 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 9 UNION ALL
SELECT 9, p.p45, p.p47, y.p21, y.p22 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 10 UNION ALL
SELECT 10, p.p49, p.p51, y.p23, y.p24 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 11 UNION ALL
SELECT 11, p.p53, p.p55, y.p25, y.p26 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 12 UNION ALL
SELECT 12, p.p57, p.p59, y.p27, y.p28 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 13 UNION ALL
SELECT 13, p.p61, p.p63, y.p29, y.p30 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 14 UNION ALL
SELECT 14, p.p65, p.p67, y.p31, y.p32 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 15 UNION ALL
SELECT 15, p.p69, p.p71, y.p33, y.p34 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 16 UNION ALL
SELECT 16, p.p73, p.p75, y.p35, y.p36 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 17 UNION ALL
SELECT 17, p.p77, p.p79, y.p37, y.p38 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 18 UNION ALL
SELECT 18, p.p81, p.p83, y.p39, y.p40 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 19 UNION ALL
SELECT 19, p.p85, p.p87, y.p41, y.p42 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 20 UNION ALL
SELECT 20, p.p89, p.p91, y.p43, y.p44 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 21 UNION ALL
SELECT 21, p.p93, p.p95, y.p45, y.p46 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 22 UNION ALL
SELECT 22, p.p97, p.p99, y.p47, y.p48 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 23 UNION ALL
SELECT 23, p.p101, p.p103, y.p49, y.p50 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 24 UNION ALL
SELECT 24, p.p105, p.p107, y.p51, y.p52 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 25 UNION ALL
SELECT 25, p.p109, p.p111, y.p53, y.p54 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 26 UNION ALL
SELECT 26, p.p113, p.p115, y.p55, y.p56 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 27 UNION ALL
SELECT 27, p.p117, p.p119, y.p57, y.p58 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 28 UNION ALL
SELECT 28, p.p121, p.p123, y.p59, y.p60 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 29 UNION ALL
SELECT 29, p.p125, p.p127, y.p61, y.p62 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 30 UNION ALL
SELECT 30, p.p129, p.p131, y.p63, y.p64 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 31 UNION ALL
SELECT 31, p.p133, p.p135, y.p65, y.p66 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 32 UNION ALL
SELECT 32, p.p137, p.p139, y.p67, y.p68 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 33 UNION ALL
SELECT 33, p.p141, p.p143, y.p69, y.p70 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 34 UNION ALL
SELECT 34, p.p145, p.p147, y.p71, y.p72 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 35 UNION ALL
SELECT 35, p.p149, p.p151, y.p73, y.p74 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 36 UNION ALL
SELECT 36, p.p153, p.p155, y.p75, y.p76 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 37 UNION ALL
SELECT 37, p.p157, p.p159, y.p77, y.p78 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 38 UNION ALL
SELECT 38, p.p161, p.p163, y.p79, y.p80 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 39 UNION ALL
SELECT 39, p.p165, p.p167, y.p81, y.p82 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 40 UNION ALL
SELECT 40, p.p169, p.p171, y.p83, y.p84 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 41 UNION ALL
SELECT 41, p.p173, p.p175, y.p85, y.p86 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 42 UNION ALL
SELECT 42, p.p177, p.p179, y.p87, y.p88 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 43 UNION ALL
SELECT 43, p.p181, p.p183, y.p89, y.p90 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 44 UNION ALL
SELECT 44, p.p185, p.p187, y.p91, y.p92 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 45 UNION ALL
SELECT 45, p.p189, p.p191, y.p93, y.p94 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 46 UNION ALL
SELECT 46, p.p193, p.p195, y.p95, y.p96 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 47 UNION ALL
SELECT 47, p.p197, p.p199, y.p97, y.p98 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 48 UNION ALL
SELECT 48, p.p201, p.p203, y.p99, y.p100 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 49 UNION ALL
SELECT 49, p.p205, p.p207, y.p101, y.p102 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 50 UNION ALL
SELECT p.p7, p.p13, p.p15, y.p5, y.p6 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 >= 2
END
GO
/* Создание хранимой процедуры [dbo].[prog_8_union_table_cfg] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE prog_8_union_table_cfg 
	@i_num BIGINT = 1, -- Номер маршрута для записи
	@i_x int = 0	  -- Параметр действия: 0 - создать таблицу и заполнить её параметрами определенного маршрута
					  --					1 - создать пустую таблицу
AS
BEGIN
	SET NOCOUNT ON;
	-- Создание новой таблицы
	DROP TABLE IF EXISTS [dbo].[db_t_new];
	CREATE TABLE db_t_new (
		i_id			bigint,			-- Номер п/п
		i_id_obj		bigint,			-- ID устройства
		s_obj			NVARCHAR(255),	-- KKS устройства (тег)
		i_cmd			int,			-- ID команды
		s_cmd_desc		NVARCHAR(255),	-- Описание команды
		i_time_start	bigint,			-- Время пуска
		i_time_stop		bigint			-- Время остановки
	);
	IF @i_x = 0 
	BEGIN
		-- Заполнение новой таблицы из полей таблиц db_t_route_1 и db_t_route_2 по указанному номеру маршрута
		INSERT INTO db_t_new (i_id, i_id_obj, s_obj, i_cmd, s_cmd_desc, i_time_start, i_time_stop)
		--	   i_id		i_id_obj	s_obj	i_cmd	s_cmd_desc	i_time_start	i_time_stop
		SELECT 1,		p.p9,		p.p10,	p.p11,	p.p12,		y.p3,			y.p4 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 1 UNION ALL
		SELECT 2,		p.p17,		p.p18,	p.p19,	p.p20,		y.p7,			y.p8 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 2 UNION ALL
		SELECT 3,		p.p21,		p.p22,	p.p23,	p.p24,		y.p9,			y.p10 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 3 UNION ALL
		SELECT 4,		p.p25,		p.p26,	p.p27,	p.p28,		y.p11,			y.p12 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 4 UNION ALL
		SELECT 5,		p.p29,		p.p30,	p.p31,	p.p32,		y.p13,			y.p14 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 5 UNION ALL
		SELECT 6,		p.p33,		p.p34,	p.p35,	p.p36,		y.p15,			y.p16 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 6 UNION ALL
		SELECT 7,		p.p37,		p.p38,	p.p39,	p.p40,		y.p17,			y.p18 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 7 UNION ALL
		SELECT 8,		p.p41,		p.p42,	p.p43,	p.p44,		y.p19,			y.p20 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 8 UNION ALL
		SELECT 9,		p.p45,		p.p46,	p.p47,	p.p48,		y.p21,			y.p22 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 9 UNION ALL
		SELECT 10,		p.p49,		p.p50,	p.p51,	p.p52,		y.p23,			y.p24 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 10 UNION ALL
		SELECT 11,		p.p53,		p.p54,	p.p55,	p.p56,		y.p25,			y.p26 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 11 UNION ALL
		SELECT 12,		p.p57,		p.p58,	p.p59,	p.p60,		y.p27,			y.p28 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 12 UNION ALL
		SELECT 13,		p.p61,		p.p62,	p.p63,	p.p64,		y.p29,			y.p30 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 13 UNION ALL
		SELECT 14,		p.p65,		p.p66,	p.p67,	p.p68,		y.p31,			y.p32 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 14 UNION ALL
		SELECT 15,		p.p69,		p.p70,	p.p71,	p.p72,		y.p33,			y.p34 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 15 UNION ALL
		SELECT 16,		p.p73,		p.p74,	p.p75,	p.p76,		y.p35,			y.p36 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 16 UNION ALL
		SELECT 17,		p.p77,		p.p78,	p.p79,	p.p80,		y.p37,			y.p38 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 17 UNION ALL
		SELECT 18,		p.p81,		p.p82,	p.p83,	p.p84,		y.p39,			y.p40 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 18 UNION ALL
		SELECT 19,		p.p85,		p.p86,	p.p87,	p.p88,		y.p41,			y.p42 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 19 UNION ALL
		SELECT 20,		p.p89,		p.p90,	p.p91,	p.p92,		y.p43,			y.p44 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 20 UNION ALL
		SELECT 21,		p.p93,		p.p94,	p.p95,	p.p96,		y.p45,			y.p46 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 21 UNION ALL
		SELECT 22,		p.p97,		p.p98,	p.p99,	p.p100,		y.p47,			y.p48 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 22 UNION ALL
		SELECT 23,		p.p101,		p.p102,	p.p103,	p.p104,		y.p49,			y.p50 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 23 UNION ALL
		SELECT 24,		p.p105,		p.p106,	p.p107,	p.p108,		y.p51,			y.p52 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 24 UNION ALL
		SELECT 25,		p.p109,		p.p110,	p.p111,	p.p112,		y.p53,			y.p54 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 25 UNION ALL
		SELECT 26,		p.p113,		p.p114,	p.p115,	p.p116,		y.p55,			y.p56 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 26 UNION ALL
		SELECT 27,		p.p117,		p.p118,	p.p119,	p.p120,		y.p57,			y.p58 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 27 UNION ALL
		SELECT 28,		p.p121,		p.p122,	p.p123,	p.p124,		y.p59,			y.p60 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 28 UNION ALL
		SELECT 29,		p.p125,		p.p126,	p.p127,	p.p128,		y.p61,			y.p62 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 29 UNION ALL
		SELECT 30,		p.p129,		p.p130,	p.p131,	p.p132,		y.p63,			y.p64 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 30 UNION ALL
		SELECT 31,		p.p133,		p.p134,	p.p135,	p.p136,		y.p65,			y.p66 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 31 UNION ALL
		SELECT 32,		p.p137,		p.p138,	p.p139,	p.p140,		y.p67,			y.p68 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 32 UNION ALL
		SELECT 33,		p.p141,		p.p142,	p.p143,	p.p144,		y.p69,			y.p70 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 33 UNION ALL
		SELECT 34,		p.p145,		p.p146,	p.p147,	p.p148,		y.p71,			y.p72 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 34 UNION ALL
		SELECT 35,		p.p149,		p.p150,	p.p151,	p.p152,		y.p73,			y.p74 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 35 UNION ALL
		SELECT 36,		p.p153,		p.p154,	p.p155,	p.p156,		y.p75,			y.p76 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 36 UNION ALL
		SELECT 37,		p.p157,		p.p158,	p.p159,	p.p160,		y.p77,			y.p78 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 37 UNION ALL
		SELECT 38,		p.p161,		p.p162,	p.p163,	p.p164,		y.p79,			y.p80 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 38 UNION ALL
		SELECT 39,		p.p165,		p.p166,	p.p167,	p.p168,		y.p81,			y.p82 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 39 UNION ALL
		SELECT 40,		p.p169,		p.p170,	p.p171,	p.p172,		y.p83,			y.p84 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 40 UNION ALL
		SELECT 41,		p.p173,		p.p174,	p.p175,	p.p176,		y.p85,			y.p86 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 41 UNION ALL
		SELECT 42,		p.p177,		p.p178,	p.p179,	p.p180,		y.p87,			y.p88 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 42 UNION ALL
		SELECT 43,		p.p181,		p.p182,	p.p183,	p.p184,		y.p89,			y.p90 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 43 UNION ALL
		SELECT 44,		p.p185,		p.p186,	p.p187,	p.p188,		y.p91,			y.p92 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 44 UNION ALL
		SELECT 45,		p.p189,		p.p190,	p.p191,	p.p192,		y.p93,			y.p94 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 45 UNION ALL
		SELECT 46,		p.p193,		p.p194,	p.p195,	p.p196,		y.p95,			y.p96 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 46 UNION ALL
		SELECT 47,		p.p197,		p.p198,	p.p199,	p.p200,		y.p97,			y.p98 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 47 UNION ALL
		SELECT 48,		p.p201,		p.p202,	p.p203,	p.p204,		y.p99,			y.p100 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 48 UNION ALL
		SELECT 49,		p.p205,		p.p206,	p.p207,	p.p208,		y.p101,			y.p102 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 49 UNION ALL
		SELECT p.p7,	p.p13,		p.p14,	p.p15,	p.p16,		y.p5,			y.p6 FROM db_t_route_1 p CROSS JOIN db_t_route_2 y WHERE p.p1 = @i_num AND p.p1 = y.p1 AND p.p7 > 2
	END
END
GO

/* Создание хранимой процедуры [dbo].[prog_9_inc_cnt_execute] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [prog_9_inc_cnt_execute]
	@i_route int = 0
AS
BEGIN
	SET NOCOUNT ON;
	UPDATE [dbo].[db_t_route_1] SET [p6] = [p6] + 1 WHERE [p1] = @i_route
END
/* Создание хранимой процедуры [dbo].[prog_10_Motor_WorkTime] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- EXEC [dbo].[prog_10_Motor_WorkTime] {$i_cnt_motor_send},{$s_kks},{$lr_hour}
CREATE PROCEDURE [dbo].[prog_10_Motor_WorkTime]
	@i_cnt_motor_send int = 0,
	@s_kks varchar(255) = '',
	@lr_hour bigint = 0
AS
BEGIN
	SET NOCOUNT ON;
	IF EXISTS (SELECT 1 FROM [dbo].[Motor_WorkTime] WHERE UPPER([kks]) = UPPER(@s_kks))
    BEGIN
		SELECT @i_cnt_motor_send AS i_return;
		UPDATE [dbo].[Motor_WorkTime] 
		SET [hour] = @lr_hour
		WHERE UPPER([kks]) = UPPER(@s_kks);
	END
	ELSE
	BEGIN
		SELECT -1 AS i_return;
	END
END
/* Создание хранимой процедуры [dbo].[CFG_prog_1_SELECT_obj] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[CFG_prog_1_SELECT_obj]
	@ch_OUT_x tinyint = 0,
	@ch_OUT_Search varchar(255) = ''
AS
BEGIN
	SET NOCOUNT ON;
	IF @ch_OUT_x = 0
		SELECT * FROM [dbo].[db_t_cfg_obj]
	/*
	IF @ch_OUT_x = 1
		SELECT * FROM [dbo].[db_t_cfg_obj] WHERE ([obj_cat1]=1)
	IF @ch_OUT_x = 2
		SELECT * FROM [dbo].[db_t_cfg_obj] WHERE ([obj_cat2]=1)
	IF @ch_OUT_x = 3
		SELECT * FROM [dbo].[db_t_cfg_obj] WHERE ([obj_cat3]=1)
	IF @ch_OUT_x = 10
		SELECT * FROM [dbo].[db_t_cfg_obj] WHERE ([obj_kks] LIKE @ch_OUT_Search)
	IF @ch_OUT_x = 11
		SELECT * FROM [dbo].[db_t_cfg_obj] WHERE ([obj_cat1]=1) AND ([obj_kks] LIKE @ch_OUT_Search)
	IF @ch_OUT_x = 12
		SELECT * FROM [dbo].[db_t_cfg_obj] WHERE ([obj_cat2]=1) AND ([obj_kks] LIKE @ch_OUT_Search)
	IF @ch_OUT_x = 13
		SELECT * FROM [dbo].[db_t_cfg_obj] WHERE ([obj_cat3]=1) AND ([obj_kks] LIKE @ch_OUT_Search) */
END
/* Создание хранимой процедуры [dbo].[CFG_prog_2_SELECT_obj] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[CFG_prog_2_SELECT_obj]
	@ch_OUT_x tinyint = 0,
	@ch_OUT_Search varchar(255) = ''
AS
BEGIN
	SET NOCOUNT ON;
	--IF @ch_OUT_x = 0
		SELECT * FROM [dbo].[db_t_obj] ORDER BY [id_obj] ASC
	/*
	IF @ch_OUT_x = 1
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat1]=1)
	IF @ch_OUT_x = 2
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat2]=1)
	IF @ch_OUT_x = 3
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat3]=1)
	IF @ch_OUT_x = 10
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_kks] LIKE @ch_OUT_Search)
	IF @ch_OUT_x = 11
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat1]=1) AND ([obj_kks] LIKE @ch_OUT_Search)
	IF @ch_OUT_x = 12
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat2]=1) AND ([obj_kks] LIKE @ch_OUT_Search)
	IF @ch_OUT_x = 13
		SELECT * FROM [dbo].[db_t_obj] WHERE ([obj_cat3]=1) AND ([obj_kks] LIKE @ch_OUT_Search) */
END
/* Создание хранимой процедуры [dbo].[CFG_prog_3_DropAndCreate_obj_add] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[CFG_prog_3_DropAndCreate_obj_add]
AS
BEGIN
	SET NOCOUNT ON;
	DECLARE @s_Query AS nvarchar(MAX) = '
	EXEC sys.sp_dropextendedproperty @name=N''MS_Description'' , @level0type=N''SCHEMA'',@level0name=N''dbo'', @level1type=N''TABLE'',@level1name=N''db_t_new''
	IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N''[dbo].[db_t_new]'') AND type in (N''U''))
		DROP TABLE [dbo].[db_t_new]
	SET ANSI_NULLS ON
	SET QUOTED_IDENTIFIER ON
	CREATE TABLE [dbo].[db_t_new](
		[i_id] [bigint] NULL,
		[i_id_obj] [bigint] NULL,
		[s_obj] [nvarchar](255) NULL,
		[i_cmd] [int] NULL,
		[s_cmd_desc] [nvarchar](255) NULL,
		[i_time_start] [bigint] NULL,
		[i_time_stop] [bigint] NULL
	) ON [PRIMARY]'
	EXEC sp_executesql @s_Query
END
/* Создание хранимой процедуры [dbo].[CFG_prog_4_DeleteRowOrDropAndCreate_obj_add] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[CFG_prog_4_DeleteRowOrDropAndCreate_obj_add]
	@ch_OUT_id bigint = 0,		-- id записи, которое нужно удалить
	@i_param_delete tinyint = 0	-- параметр удаления. 0 - 1 строка, 1 - все строки
AS
BEGIN
	SET NOCOUNT ON;
	IF @i_param_delete = 0
	BEGIN
		DECLARE @cnt int;
		SELECT @cnt = COUNT(*) FROM [dbo].[db_t_new] -- Количество записей в таблице
		IF @cnt > 1 
		BEGIN
			-- Удаление выбранной записи
			DELETE FROM [dbo].[db_t_new] WHERE [i_id]=@ch_OUT_id -- Удаление записи
			-- Исправление ID после удаленного
			UPDATE [dbo].[db_t_new]
			SET [i_id] = [i_id] - 1
			WHERE [i_id] > @ch_OUT_id
		END
		ELSE
		BEGIN
			-- Пересоздание таблицы
			DROP TABLE IF EXISTS [dbo].[db_t_new]
			CREATE TABLE [dbo].[db_t_new](
				[i_id] [bigint] NULL,
				[i_id_obj] [bigint] NULL,
				[s_obj] [nvarchar](255) NULL,
				[i_cmd] [int] NULL,
				[s_cmd_desc] [nvarchar](255) NULL,
				[i_time_start] [bigint] NULL,
				[i_time_stop] [bigint] NULL
			) ON [PRIMARY]
		END
	END
	ELSE
	BEGIN
		DROP TABLE IF EXISTS [dbo].[db_t_new];
		CREATE TABLE [dbo].[db_t_new](
			[i_id] [bigint] NULL,
			[i_id_obj] [bigint] NULL,
			[s_obj] [nvarchar](255) NULL,
			[i_cmd] [int] NULL,
			[s_cmd_desc] [nvarchar](255) NULL,
			[i_time_start] [bigint] NULL,
			[i_time_stop] [bigint] NULL
		) ON [PRIMARY]
	END
END
/* Создание хранимой процедуры [dbo].[CFG_prog_5_replace] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE CFG_prog_5_replace 
	@i_param_replace AS tinyint = 100,
	-- Параметры для запроса UPDATE
	@i_id AS bigint = 0,
	@i_id_obj bigint = 0,
	@s_obj nvarchar(255) = N'',
	@i_cmd int = 0,
	@s_cmd_desc nvarchar(255) = N'',
	@i_time_start bigint = 0,
	@i_time_stop bigint = 0
AS
BEGIN
	SET NOCOUNT ON;
	-- Замена устройства
	IF @i_param_replace = 0
	BEGIN
		UPDATE [dbo].[db_t_new]
		SET [i_id_obj] = @i_id_obj,
			[s_obj] = @s_obj,
			[i_cmd] = @i_cmd,
			[s_cmd_desc] = @s_cmd_desc,
			[i_time_start] = @i_time_start,
			[i_time_stop] = @i_time_stop
		WHERE [i_id] = @i_id
	END
	-- Замена действия
	IF @i_param_replace = 1
	BEGIN
		UPDATE [dbo].[db_t_new]
		SET [i_cmd] = @i_cmd,
			[s_cmd_desc] = @s_cmd_desc
		WHERE [i_id] = @i_id
	END
	-- Замена параметров времени
	IF @i_param_replace = 2
	BEGIN
		UPDATE [dbo].[db_t_new]
		SET [i_time_start] = @i_time_start,
			[i_time_stop] = @i_time_stop
		WHERE [i_id] = @i_id
	END
END
GO

/* Создание хранимой процедуры [dbo].[CFG_prog_2_SELECT_obj_one] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[CFG_prog_2_SELECT_obj_one]
	@s_Search_kks varchar(255) = ''
AS
BEGIN
	SET NOCOUNT ON;
	IF @s_Search_kks = '' OR NOT EXISTS (SELECT 1 FROM [dbo].[db_t_obj] WHERE [obj_kks] = @s_Search_kks) 
	BEGIN /* Возвращаем пустую структуру, если нет тега ККС */
		SELECT TOP 0 * FROM [dbo].[db_t_obj];
	END
	ELSE
	BEGIN
		SELECT * FROM [dbo].[db_t_obj] WHERE [obj_kks] = @s_Search_kks;
	END
END

/* Создание хранимой процедуры [dbo].[CFG_prog_6_moving] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[CFG_prog_6_moving]
	@i_command AS bit = 0,			-- Команда переноса: 0 - вверх, 1 - вниз
	@i_row_moving AS tinyint = 0	-- Номер строки для перемещения
AS
BEGIN
	DECLARE 	
	@i_id_obj AS bigint = 0,
	@s_obj AS nvarchar(255) = '',
	@i_cmd AS int = 0,
	@s_cmd_desc AS nvarchar(255) = '',
	@i_time_start AS bigint = 0,
	@i_time_stop AS bigint = 0
	SET NOCOUNT ON;
	-- Перемещение вверх
	IF @i_command = 0 
	BEGIN
		-- Сохраняем запись, которую будем менять
		SELECT	@i_id_obj = [i_id_obj],
				@s_obj = [s_obj],
				@i_cmd = [i_cmd],
				@s_cmd_desc = [s_cmd_desc],
				@i_time_start = [i_time_start],
				@i_time_stop = [i_time_stop]
		FROM [dbo].[db_t_new]
		WHERE [i_id] = @i_row_moving - 1
		-- Замена записей в новой строке
		UPDATE [dbo].[db_t_new]
		SET	[i_id_obj] =	(SELECT [i_id_obj] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[s_obj] =		(SELECT [s_obj] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[i_cmd] =		(SELECT [i_cmd] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[s_cmd_desc] =	(SELECT [s_cmd_desc] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[i_time_start] = (SELECT [i_time_start] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[i_time_stop] =	(SELECT [i_time_stop] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving)
		WHERE [i_id] = @i_row_moving - 1
		-- Замена записей в исходной строке
		UPDATE [dbo].[db_t_new]
		SET	[i_id_obj] =	@i_id_obj,
			[s_obj] =		@s_obj,
			[i_cmd] =		@i_cmd,
			[s_cmd_desc] =	@s_cmd_desc,
			[i_time_start] = @i_time_start,
			[i_time_stop] =	@i_time_stop
		WHERE [i_id] = @i_row_moving
	END
	ELSE
	BEGIN
		-- Сохраняем запись, которую будем менять
		SELECT	@i_id_obj = [i_id_obj],
				@s_obj = [s_obj],
				@i_cmd = [i_cmd],
				@s_cmd_desc = [s_cmd_desc],
				@i_time_start = [i_time_start],
				@i_time_stop = [i_time_stop]
		FROM [dbo].[db_t_new]
		WHERE [i_id] = @i_row_moving + 1
		-- Замена записей в новой строке
		UPDATE [dbo].[db_t_new]
		SET	[i_id_obj] =	(SELECT [i_id_obj] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[s_obj] =		(SELECT [s_obj] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[i_cmd] =		(SELECT [i_cmd] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[s_cmd_desc] =	(SELECT [s_cmd_desc] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[i_time_start] = (SELECT [i_time_start] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving),
			[i_time_stop] =	(SELECT [i_time_stop] FROM [dbo].[db_t_new] WHERE [i_id] = @i_row_moving)
		WHERE [i_id] = @i_row_moving + 1
		-- Замена записей в исходной строке
		UPDATE [dbo].[db_t_new]
		SET	[i_id_obj] =	@i_id_obj,
			[s_obj] =		@s_obj,
			[i_cmd] =		@i_cmd,
			[s_cmd_desc] =	@s_cmd_desc,
			[i_time_start] = @i_time_start,
			[i_time_stop] =	@i_time_stop
		WHERE [i_id] = @i_row_moving
	END
END
GO
/* Создание хранимой процедуры [dbo].[CFG_prog_7_ChangeOrCreateRoute] */
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [CFG_prog_7_ChangeOrCreateRoute]
@b_param AS TINYINT = 0,			-- Параметр выполнения: 2 - UPDATE; 0,1 - INSERT
	@i_route AS bigint = 0,				-- Номер маршрута для обработки
	@s_desc AS VARCHAR(MAX) = '',		-- Описание маршрута
	@s_change_desc AS VARCHAR(MAX) = '' -- Описание причины изменения

AS
BEGIN
	SET NOCOUNT ON
	IF (@b_param <> 2)
	BEGIN
		INSERT INTO [dbo].[db_t_route_1] ([p1] ,[p2] ,[p3] ,[p4] ,[p5] ,[p6] ,[p7] ,[p8] ,[p9] ,[p10] ,[p11] ,[p12] ,[p13] ,[p14] ,[p15] ,[p16] ,[p17] ,[p18] ,[p19] ,[p20] ,[p21] ,[p22] ,[p23] ,[p24] ,[p25] ,[p26] ,[p27] ,[p28] ,[p29] ,[p30] ,[p31] ,[p32] ,[p33] ,[p34] ,[p35] ,[p36] ,[p37] ,[p38] ,[p39] ,[p40] ,[p41] ,[p42] ,[p43] ,[p44] ,[p45] ,[p46] ,[p47] ,[p48] ,[p49] ,[p50] ,[p51] ,[p52] ,[p53] ,[p54] ,[p55] ,[p56] ,[p57] ,[p58] ,[p59] ,[p60] ,[p61] ,[p62] ,[p63] ,[p64] ,[p65] ,[p66] ,[p67] ,[p68] ,[p69] ,[p70] ,[p71] ,[p72] ,[p73] ,[p74] ,[p75] ,[p76] ,[p77] ,[p78] ,[p79] ,[p80] ,[p81] ,[p82] ,[p83] ,[p84] ,[p85] ,[p86] ,[p87] ,[p88] ,[p89] ,[p90] ,[p91] ,[p92] ,[p93] ,[p94] ,[p95] ,[p96] ,[p97] ,[p98] ,[p99] ,[p100] ,[p101] ,[p102] ,[p103] ,[p104] ,[p105] ,[p106] ,[p107] ,[p108] ,[p109] ,[p110] ,[p111] ,[p112] ,[p113] ,[p114] ,[p115] ,[p116] ,[p117] ,[p118] ,[p119] ,[p120] ,[p121] ,[p122] ,[p123] ,[p124] ,[p125] ,[p126] ,[p127] ,[p128] ,[p129] ,[p130] ,[p131] ,[p132] ,[p133] ,[p134] ,[p135] ,[p136] ,[p137] ,[p138] ,[p139] ,[p140] ,[p141] ,[p142] ,[p143] ,[p144] ,[p145] ,[p146] ,[p147] ,[p148] ,[p149] ,[p150] ,[p151] ,[p152] ,[p153] ,[p154] ,[p155] ,[p156] ,[p157] ,[p158] ,[p159] ,[p160] ,[p161] ,[p162] ,[p163] ,[p164] ,[p165] ,[p166] ,[p167] ,[p168] ,[p169] ,[p170] ,[p171] ,[p172] ,[p173] ,[p174] ,[p175] ,[p176] ,[p177] ,[p178] ,[p179] ,[p180] ,[p181] ,[p182] ,[p183] ,[p184] ,[p185] ,[p186] ,[p187] ,[p188] ,[p189] ,[p190] ,[p191] ,[p192] ,[p193] ,[p194] ,[p195] ,[p196] ,[p197] ,[p198] ,[p199] ,[p200] ,[p201] ,[p202] ,[p203] ,[p204] ,[p205] ,[p206] ,[p207] ,[p208])
		VALUES
           (@i_route,				-- Код маршрута
           @s_desc,					-- Описание маршрута
           (SELECT GETDATE()),		-- Дата и время  добавления маршрута
           '',						-- Дата и время изменения маршрута
           @s_change_desc,			-- Описание причины изменения
           0,						-- Общее количество использований маршрута для аналитики
		   0,						-- Количество устройств в маршруте
           'OK',					-- Статус маршрута для изменения или удаления
		   -- Устройства и их параметры
			0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, '')
		INSERT INTO [dbo].[db_t_route_2]
           ([p1], [p2], [p3], [p4], [p5], [p6], [p7], [p8], [p9], [p10], [p11], [p12], [p13], [p14], [p15], [p16], [p17], [p18], [p19], [p20], [p21], [p22], [p23], [p24], [p25], [p26], [p27], [p28], [p29], [p30], [p31], [p32], [p33], [p34], [p35], [p36], [p37], [p38], [p39], [p40], [p41], [p42], [p43], [p44], [p45], [p46], [p47], [p48], [p49], [p50], [p51], [p52], [p53], [p54], [p55], [p56], [p57], [p58], [p59], [p60], [p61], [p62], [p63], [p64], [p65], [p66], [p67], [p68], [p69], [p70], [p71], [p72], [p73], [p74], [p75], [p76], [p77], [p78], [p79], [p80], [p81], [p82], [p83], [p84], [p85], [p86], [p87], [p88], [p89], [p90], [p91], [p92], [p93], [p94], [p95], [p96], [p97], [p98], [p99], [p100], [p101], [p102])
		VALUES
           (@i_route,				-- Код маршрута
           0,						-- Количество устройств в маршруте
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	END
	-- Определение количества записей в таблице db_t_new
	DECLARE @i_cnt_row AS integer = 0
	SELECT @i_cnt_row = COUNT(*) FROM [dbo].[db_t_new]
	SELECT @i_cnt_row
	-- Обновление служебной информации: количество устройств
	UPDATE [dbo].[db_t_route_1] SET [p7] = @i_cnt_row WHERE [p1] = @i_route
	UPDATE [dbo].[db_t_route_2] SET [p2] = @i_cnt_row WHERE [p1] = @i_route
	-- Обновление служебной информации: Описание маршрута
	UPDATE [dbo].[db_t_route_1] SET [p2] = @s_desc WHERE [p1] = @i_route
	IF (@b_param = 2)
	BEGIN
		-- Обновление служебной информации: Дата изменения маршрута
		UPDATE [dbo].[db_t_route_1] SET [p4] = (SELECT GETDATE()) WHERE [p1] = @i_route
		-- Обновление служебной информации: Описание изменений маршрута
		UPDATE [dbo].[db_t_route_1] SET [p5] = @s_change_desc WHERE [p1] = @i_route
	END
	-- Источник		
			UPDATE r1 SET r1.p9 = n.i_id_obj, r1.p10 = n.s_obj, r1.p11 = n.i_cmd, r1.p12 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 1 AND 1 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p3 = n.[i_time_start], r2.p4 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 1 AND 1 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 3									
	UPDATE r1 SET r1.p17 = n.i_id_obj, r1.p18 = n.s_obj, r1.p19 = n.i_cmd, r1.p20 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 2 AND 2 < @i_cnt_row WHERE r1.[p1] = @i_route
	UPDATE r2 SET r2.p7 = n.[i_time_start], r2.p8 = n.i_time_stop										   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 2 AND 2 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 4									
	UPDATE r1 SET r1.p21 = n.i_id_obj, r1.p22 = n.s_obj, r1.p23 = n.i_cmd, r1.p24 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 3 AND 3 < @i_cnt_row WHERE r1.[p1] = @i_route 
	UPDATE r2 SET r2.p9 = n.[i_time_start], r2.p10 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 3 AND 3 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 5									
	UPDATE r1 SET r1.p25 = n.i_id_obj, r1.p26 = n.s_obj, r1.p27 = n.i_cmd, r1.p28 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 4 AND 4 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p11 = n.[i_time_start], r2.p12 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 4 AND 4 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 6									
	UPDATE r1 SET r1.p29 = n.i_id_obj, r1.p30 = n.s_obj, r1.p31 = n.i_cmd, r1.p32 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 5 AND 5 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p13 = n.[i_time_start], r2.p14 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 5 AND 5 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 7									
	UPDATE r1 SET r1.p33 = n.i_id_obj, r1.p34 = n.s_obj, r1.p35 = n.i_cmd, r1.p36 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 6 AND 6 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p15 = n.[i_time_start], r2.p16 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 6 AND 6 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 8									
	UPDATE r1 SET r1.p37 = n.i_id_obj, r1.p38 = n.s_obj, r1.p39 = n.i_cmd, r1.p40 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 7 AND 7 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p17 = n.[i_time_start], r2.p18 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 7 AND 7 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 9									
	UPDATE r1 SET r1.p41 = n.i_id_obj, r1.p42 = n.s_obj, r1.p43 = n.i_cmd, r1.p44 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 8 AND 8 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p19 = n.[i_time_start], r2.p20 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 8 AND 8 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 10									
	UPDATE r1 SET r1.p45 = n.i_id_obj, r1.p46 = n.s_obj, r1.p47 = n.i_cmd, r1.p48 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 9 AND 9 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p21 = n.[i_time_start], r2.p22 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 9 AND 9 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 11									
	UPDATE r1 SET r1.p49 = n.i_id_obj, r1.p50 = n.s_obj, r1.p51 = n.i_cmd, r1.p52 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 10 AND 10 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p23 = n.[i_time_start], r2.p24 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 10 AND 10 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 12									
	UPDATE r1 SET r1.p53 = n.i_id_obj, r1.p54 = n.s_obj, r1.p55 = n.i_cmd, r1.p56 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 11 AND 11 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p25 = n.[i_time_start], r2.p26 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 11 AND 11 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 13									
	UPDATE r1 SET r1.p57 = n.i_id_obj, r1.p58 = n.s_obj, r1.p59 = n.i_cmd, r1.p60 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 12 AND 12 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p27 = n.[i_time_start], r2.p28 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 12 AND 12 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 14									
	UPDATE r1 SET r1.p61 = n.i_id_obj, r1.p62 = n.s_obj, r1.p63 = n.i_cmd, r1.p64 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 13 AND 13 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p29 = n.[i_time_start], r2.p30 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 13 AND 13 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 15									
	UPDATE r1 SET r1.p65 = n.i_id_obj, r1.p66 = n.s_obj, r1.p67 = n.i_cmd, r1.p68 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 14 AND 14 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p31 = n.[i_time_start], r2.p32 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 14 AND 14 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 16									
	UPDATE r1 SET r1.p69 = n.i_id_obj, r1.p70 = n.s_obj, r1.p71 = n.i_cmd, r1.p72 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 15 AND 15 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p33 = n.[i_time_start], r2.p34 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 15 AND 15 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 17									
	UPDATE r1 SET r1.p73 = n.i_id_obj, r1.p74 = n.s_obj, r1.p75 = n.i_cmd, r1.p76 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 16 AND 16 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p35 = n.[i_time_start], r2.p36 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 16 AND 16 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 18									
	UPDATE r1 SET r1.p77 = n.i_id_obj, r1.p78 = n.s_obj, r1.p79 = n.i_cmd, r1.p80 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 17 AND 17 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p37 = n.[i_time_start], r2.p38 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 17 AND 17 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 19									
	UPDATE r1 SET r1.p81 = n.i_id_obj, r1.p82 = n.s_obj, r1.p83 = n.i_cmd, r1.p84 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 18 AND 18 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p39 = n.[i_time_start], r2.p40 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 18 AND 18 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 20									
	UPDATE r1 SET r1.p85 = n.i_id_obj, r1.p86 = n.s_obj, r1.p87 = n.i_cmd, r1.p88 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 19 AND 19 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p41 = n.[i_time_start], r2.p42 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 19 AND 19 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 21									
	UPDATE r1 SET r1.p89 = n.i_id_obj, r1.p90 = n.s_obj, r1.p91 = n.i_cmd, r1.p92 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 20 AND 20 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p43 = n.[i_time_start], r2.p44 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 20 AND 20 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 22									
	UPDATE r1 SET r1.p93 = n.i_id_obj, r1.p94 = n.s_obj, r1.p95 = n.i_cmd, r1.p96 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 21 AND 21 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p45 = n.[i_time_start], r2.p46 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 21 AND 21 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 23									
	UPDATE r1 SET r1.p97 = n.i_id_obj, r1.p98 = n.s_obj, r1.p99 = n.i_cmd, r1.p100 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 22 AND 22 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p47 = n.[i_time_start], r2.p48 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 22 AND 22 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 24									
	UPDATE r1 SET r1.p101 = n.i_id_obj, r1.p102 = n.s_obj, r1.p103 = n.i_cmd, r1.p104 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 23 AND 23 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p49 = n.[i_time_start], r2.p50 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 23 AND 23 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 25									
	UPDATE r1 SET r1.p105 = n.i_id_obj, r1.p106 = n.s_obj, r1.p107 = n.i_cmd, r1.p108 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 24 AND 24 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p51 = n.[i_time_start], r2.p52 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 24 AND 24 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 26									
	UPDATE r1 SET r1.p109 = n.i_id_obj, r1.p110 = n.s_obj, r1.p111 = n.i_cmd, r1.p112 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 25 AND 25 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p53 = n.[i_time_start], r2.p54 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 25 AND 25 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 27									
	UPDATE r1 SET r1.p113 = n.i_id_obj, r1.p114 = n.s_obj, r1.p115 = n.i_cmd, r1.p116 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 26 AND 26 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p55 = n.[i_time_start], r2.p56 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 26 AND 26 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 28									
	UPDATE r1 SET r1.p117 = n.i_id_obj, r1.p118 = n.s_obj, r1.p119 = n.i_cmd, r1.p120 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 27 AND 27 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p57 = n.[i_time_start], r2.p58 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 27 AND 27 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 29									
	UPDATE r1 SET r1.p121 = n.i_id_obj, r1.p122 = n.s_obj, r1.p123 = n.i_cmd, r1.p124 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 28 AND 28 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p59 = n.[i_time_start], r2.p60 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 28 AND 28 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 30									
	UPDATE r1 SET r1.p125 = n.i_id_obj, r1.p126 = n.s_obj, r1.p127 = n.i_cmd, r1.p128 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 29 AND 29 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p61 = n.[i_time_start], r2.p62 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 29 AND 29 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 31									
	UPDATE r1 SET r1.p129 = n.i_id_obj, r1.p130 = n.s_obj, r1.p131 = n.i_cmd, r1.p132 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 30 AND 30 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p63 = n.[i_time_start], r2.p64 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 30 AND 30 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 32									
	UPDATE r1 SET r1.p133 = n.i_id_obj, r1.p134 = n.s_obj, r1.p135 = n.i_cmd, r1.p136 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 31 AND 31 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p65 = n.[i_time_start], r2.p66 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 31 AND 31 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 33									
	UPDATE r1 SET r1.p137 = n.i_id_obj, r1.p138 = n.s_obj, r1.p139 = n.i_cmd, r1.p140 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 32 AND 32 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p67 = n.[i_time_start], r2.p68 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 32 AND 32 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 34									
	UPDATE r1 SET r1.p141 = n.i_id_obj, r1.p142 = n.s_obj, r1.p143 = n.i_cmd, r1.p144 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 33 AND 33 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p69 = n.[i_time_start], r2.p70 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 33 AND 33 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 35									
	UPDATE r1 SET r1.p145 = n.i_id_obj, r1.p146 = n.s_obj, r1.p147 = n.i_cmd, r1.p148 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 34 AND 34 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p71 = n.[i_time_start], r2.p72 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 34 AND 34 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 36									
	UPDATE r1 SET r1.p149 = n.i_id_obj, r1.p150 = n.s_obj, r1.p151 = n.i_cmd, r1.p152 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 35 AND 35 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p73 = n.[i_time_start], r2.p74 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 35 AND 35 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 37									
	UPDATE r1 SET r1.p153 = n.i_id_obj, r1.p154 = n.s_obj, r1.p155 = n.i_cmd, r1.p156 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 36 AND 36 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p75 = n.[i_time_start], r2.p76 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 36 AND 36 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 38									
	UPDATE r1 SET r1.p157 = n.i_id_obj, r1.p158 = n.s_obj, r1.p159 = n.i_cmd, r1.p160 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 37 AND 37 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p77 = n.[i_time_start], r2.p78 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 37 AND 37 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 39									
	UPDATE r1 SET r1.p161 = n.i_id_obj, r1.p162 = n.s_obj, r1.p163 = n.i_cmd, r1.p164 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 38 AND 38 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p79 = n.[i_time_start], r2.p80 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 38 AND 38 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 40									
	UPDATE r1 SET r1.p165 = n.i_id_obj, r1.p166 = n.s_obj, r1.p167 = n.i_cmd, r1.p168 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 39 AND 39 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p81 = n.[i_time_start], r2.p82 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 39 AND 39 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 41									
	UPDATE r1 SET r1.p169 = n.i_id_obj, r1.p170 = n.s_obj, r1.p171 = n.i_cmd, r1.p172 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 40 AND 40 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p83 = n.[i_time_start], r2.p84 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 40 AND 40 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 42									
	UPDATE r1 SET r1.p173 = n.i_id_obj, r1.p174 = n.s_obj, r1.p175 = n.i_cmd, r1.p176 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 41 AND 41 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p85 = n.[i_time_start], r2.p86 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 41 AND 41 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 43									
	UPDATE r1 SET r1.p177 = n.i_id_obj, r1.p178 = n.s_obj, r1.p179 = n.i_cmd, r1.p180 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 42 AND 42 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p87 = n.[i_time_start], r2.p88 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 42 AND 42 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 44									
	UPDATE r1 SET r1.p181 = n.i_id_obj, r1.p182 = n.s_obj, r1.p183 = n.i_cmd, r1.p184 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 43 AND 43 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p89 = n.[i_time_start], r2.p90 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 43 AND 43 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 45									
	UPDATE r1 SET r1.p185 = n.i_id_obj, r1.p186 = n.s_obj, r1.p187 = n.i_cmd, r1.p188 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 44 AND 44 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p91 = n.[i_time_start], r2.p92 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 44 AND 44 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 46									
	UPDATE r1 SET r1.p189 = n.i_id_obj, r1.p190 = n.s_obj, r1.p191 = n.i_cmd, r1.p192 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 45 AND 45 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p93 = n.[i_time_start], r2.p94 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 45 AND 45 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 47									
	UPDATE r1 SET r1.p193 = n.i_id_obj, r1.p194 = n.s_obj, r1.p195 = n.i_cmd, r1.p196 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 46 AND 46 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p95 = n.[i_time_start], r2.p96 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 46 AND 46 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 48									
	UPDATE r1 SET r1.p197 = n.i_id_obj, r1.p198 = n.s_obj, r1.p199 = n.i_cmd, r1.p200 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 47 AND 47 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p97 = n.[i_time_start], r2.p98 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 47 AND 47 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 49									
	UPDATE r1 SET r1.p201 = n.i_id_obj, r1.p202 = n.s_obj, r1.p203 = n.i_cmd, r1.p204 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 48 AND 48 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p99 = n.[i_time_start], r2.p100 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 48 AND 48 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Устройство 50									
	UPDATE r1 SET r1.p205 = n.i_id_obj, r1.p206 = n.s_obj, r1.p207 = n.i_cmd, r1.p208 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = 49 AND 49 < @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p101 = n.[i_time_start], r2.p102 = n.i_time_stop									   FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = 49 AND 49 < @i_cnt_row WHERE r2.[p1] = @i_route
	-- Приемник									
	UPDATE r1 SET r1.p13 = n.i_id_obj, r1.p14 = n.s_obj, r1.p15 = n.i_cmd, r1.p16 = n.s_cmd_desc	FROM [db_t_route_1] AS r1 JOIN db_t_new AS n ON n.[i_id] = @i_cnt_row WHERE r1.[p1] = @i_route								
	UPDATE r2 SET r2.p5 = n.[i_time_start], r2.p6 = n.i_time_stop										FROM [db_t_route_2] AS r2 JOIN db_t_new AS n ON n.[i_id] = @i_cnt_row WHERE r2.[p1] = @i_route
		
	-- Удаление устройств из таблицы в случае уменьшения их кол-ва
	-- Устройство 3
	UPDATE [dbo].[db_t_route_1] SET [p17] = 0, [p18] = '', [p19] = 0, [p20] = '' WHERE [p1] = @i_route AND 2 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p7] = 0, [p8] = 0 WHERE [p1] = @i_route AND 2 > @i_cnt_row
	-- Устройство 4
	UPDATE [dbo].[db_t_route_1] SET [p21] = 0, [p22] = '', [p23] = 0, [p24] = '' WHERE [p1] = @i_route AND 3 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p9] = 0, [p10] = 0 WHERE [p1] = @i_route AND 3 > @i_cnt_row
	-- Устройство 5
	UPDATE [dbo].[db_t_route_1] SET [p25] = 0, [p26] = '', [p27] = 0, [p28] = '' WHERE [p1] = @i_route AND 4 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p11] = 0, [p12] = 0 WHERE [p1] = @i_route AND 4 > @i_cnt_row
	-- Устройство 6
	UPDATE [dbo].[db_t_route_1] SET [p29] = 0, [p30] = '', [p31] = 0, [p32] = '' WHERE [p1] = @i_route AND 5 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p13] = 0, [p14] = 0 WHERE [p1] = @i_route AND 5 > @i_cnt_row
	-- Устройство 7
	UPDATE [dbo].[db_t_route_1] SET [p33] = 0, [p34] = '', [p35] = 0, [p36] = '' WHERE [p1] = @i_route AND 6 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p15] = 0, [p16] = 0 WHERE [p1] = @i_route AND 6 > @i_cnt_row
	-- Устройство 8
	UPDATE [dbo].[db_t_route_1] SET [p37] = 0, [p38] = '', [p39] = 0, [p40] = '' WHERE [p1] = @i_route AND 7 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p17] = 0, [p18] = 0 WHERE [p1] = @i_route AND 7 > @i_cnt_row
	-- Устройство 9
	UPDATE [dbo].[db_t_route_1] SET [p41] = 0, [p42] = '', [p43] = 0, [p44] = '' WHERE [p1] = @i_route AND 8 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p19] = 0, [p20] = 0 WHERE [p1] = @i_route AND 8 > @i_cnt_row
	-- Устройство 10
	UPDATE [dbo].[db_t_route_1] SET [p45] = 0, [p46] = '', [p47] = 0, [p48] = '' WHERE [p1] = @i_route AND 9 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p21] = 0, [p22] = 0 WHERE [p1] = @i_route AND 9 > @i_cnt_row
	-- Устройство 11
	UPDATE [dbo].[db_t_route_1] SET [p49] = 0, [p50] = '', [p51] = 0, [p52] = '' WHERE [p1] = @i_route AND 10 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p23] = 0, [p24] = 0 WHERE [p1] = @i_route AND 10 > @i_cnt_row
	-- Устройство 12
	UPDATE [dbo].[db_t_route_1] SET [p53] = 0, [p54] = '', [p55] = 0, [p56] = '' WHERE [p1] = @i_route AND 11 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p25] = 0, [p26] = 0 WHERE [p1] = @i_route AND 11 > @i_cnt_row
	-- Устройство 13
	UPDATE [dbo].[db_t_route_1] SET [p57] = 0, [p58] = '', [p59] = 0, [p60] = '' WHERE [p1] = @i_route AND 12 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p27] = 0, [p28] = 0 WHERE [p1] = @i_route AND 12 > @i_cnt_row
	-- Устройство 14
	UPDATE [dbo].[db_t_route_1] SET [p61] = 0, [p62] = '', [p63] = 0, [p64] = '' WHERE [p1] = @i_route AND 13 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p29] = 0, [p30] = 0 WHERE [p1] = @i_route AND 13 > @i_cnt_row
	-- Устройство 15
	UPDATE [dbo].[db_t_route_1] SET [p65] = 0, [p66] = '', [p67] = 0, [p68] = '' WHERE [p1] = @i_route AND 14 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p31] = 0, [p32] = 0 WHERE [p1] = @i_route AND 14 > @i_cnt_row
	-- Устройство 16
	UPDATE [dbo].[db_t_route_1] SET [p69] = 0, [p70] = '', [p71] = 0, [p72] = '' WHERE [p1] = @i_route AND 15 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p33] = 0, [p34] = 0 WHERE [p1] = @i_route AND 15 > @i_cnt_row
	-- Устройство 17
	UPDATE [dbo].[db_t_route_1] SET [p73] = 0, [p74] = '', [p75] = 0, [p76] = '' WHERE [p1] = @i_route AND 16 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p35] = 0, [p36] = 0 WHERE [p1] = @i_route AND 16 > @i_cnt_row
	-- Устройство 18
	UPDATE [dbo].[db_t_route_1] SET [p77] = 0, [p78] = '', [p79] = 0, [p80] = '' WHERE [p1] = @i_route AND 17 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p37] = 0, [p38] = 0 WHERE [p1] = @i_route AND 17 > @i_cnt_row
	-- Устройство 19
	UPDATE [dbo].[db_t_route_1] SET [p81] = 0, [p82] = '', [p83] = 0, [p84] = '' WHERE [p1] = @i_route AND 18 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p39] = 0, [p40] = 0 WHERE [p1] = @i_route AND 18 > @i_cnt_row
	-- Устройство 20
	UPDATE [dbo].[db_t_route_1] SET [p85] = 0, [p86] = '', [p87] = 0, [p88] = '' WHERE [p1] = @i_route AND 19 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p41] = 0, [p42] = 0 WHERE [p1] = @i_route AND 19 > @i_cnt_row
	-- Устройство 21
	UPDATE [dbo].[db_t_route_1] SET [p89] = 0, [p90] = '', [p91] = 0, [p92] = '' WHERE [p1] = @i_route AND 20 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p43] = 0, [p44] = 0 WHERE [p1] = @i_route AND 20 > @i_cnt_row
	-- Устройство 22
	UPDATE [dbo].[db_t_route_1] SET [p93] = 0, [p94] = '', [p95] = 0, [p96] = '' WHERE [p1] = @i_route AND 21 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p45] = 0, [p46] = 0 WHERE [p1] = @i_route AND 21 > @i_cnt_row
	-- Устройство 23
	UPDATE [dbo].[db_t_route_1] SET [p97] = 0, [p98] = '', [p99] = 0, [p100] = '' WHERE [p1] = @i_route AND 22 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p47] = 0, [p48] = 0 WHERE [p1] = @i_route AND 22 > @i_cnt_row
	-- Устройство 24
	UPDATE [dbo].[db_t_route_1] SET [p101] = 0, [p102] = '', [p103] = 0, [p104] = '' WHERE [p1] = @i_route AND 23 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p49] = 0, [p50] = 0 WHERE [p1] = @i_route AND 23 > @i_cnt_row
	-- Устройство 25
	UPDATE [dbo].[db_t_route_1] SET [p105] = 0, [p106] = '', [p107] = 0, [p108] = '' WHERE [p1] = @i_route AND 24 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p51] = 0, [p52] = 0 WHERE [p1] = @i_route AND 24 > @i_cnt_row
	-- Устройство 26
	UPDATE [dbo].[db_t_route_1] SET [p109] = 0, [p110] = '', [p111] = 0, [p112] = '' WHERE [p1] = @i_route AND 25 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p53] = 0, [p54] = 0 WHERE [p1] = @i_route AND 25 > @i_cnt_row
	-- Устройство 27
	UPDATE [dbo].[db_t_route_1] SET [p113] = 0, [p114] = '', [p115] = 0, [p116] = '' WHERE [p1] = @i_route AND 26 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p55] = 0, [p56] = 0 WHERE [p1] = @i_route AND 26 > @i_cnt_row
	-- Устройство 28
	UPDATE [dbo].[db_t_route_1] SET [p117] = 0, [p118] = '', [p119] = 0, [p120] = '' WHERE [p1] = @i_route AND 27 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p57] = 0, [p58] = 0 WHERE [p1] = @i_route AND 27 > @i_cnt_row
	-- Устройство 29
	UPDATE [dbo].[db_t_route_1] SET [p121] = 0, [p122] = '', [p123] = 0, [p124] = '' WHERE [p1] = @i_route AND 28 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p59] = 0, [p60] = 0 WHERE [p1] = @i_route AND 28 > @i_cnt_row
	-- Устройство 30
	UPDATE [dbo].[db_t_route_1] SET [p125] = 0, [p126] = '', [p127] = 0, [p128] = '' WHERE [p1] = @i_route AND 29 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p61] = 0, [p62] = 0 WHERE [p1] = @i_route AND 29 > @i_cnt_row
	-- Устройство 31
	UPDATE [dbo].[db_t_route_1] SET [p129] = 0, [p130] = '', [p131] = 0, [p132] = '' WHERE [p1] = @i_route AND 30 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p63] = 0, [p64] = 0 WHERE [p1] = @i_route AND 30 > @i_cnt_row
	-- Устройство 32
	UPDATE [dbo].[db_t_route_1] SET [p133] = 0, [p134] = '', [p135] = 0, [p136] = '' WHERE [p1] = @i_route AND 31 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p65] = 0, [p66] = 0 WHERE [p1] = @i_route AND 31 > @i_cnt_row
	-- Устройство 33
	UPDATE [dbo].[db_t_route_1] SET [p137] = 0, [p138] = '', [p139] = 0, [p140] = '' WHERE [p1] = @i_route AND 32 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p67] = 0, [p68] = 0 WHERE [p1] = @i_route AND 32 > @i_cnt_row
	-- Устройство 34
	UPDATE [dbo].[db_t_route_1] SET [p141] = 0, [p142] = '', [p143] = 0, [p144] = '' WHERE [p1] = @i_route AND 33 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p69] = 0, [p70] = 0 WHERE [p1] = @i_route AND 33 > @i_cnt_row
	-- Устройство 35
	UPDATE [dbo].[db_t_route_1] SET [p145] = 0, [p146] = '', [p147] = 0, [p148] = '' WHERE [p1] = @i_route AND 34 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p71] = 0, [p72] = 0 WHERE [p1] = @i_route AND 34 > @i_cnt_row
	-- Устройство 36
	UPDATE [dbo].[db_t_route_1] SET [p149] = 0, [p150] = '', [p151] = 0, [p152] = '' WHERE [p1] = @i_route AND 35 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p73] = 0, [p74] = 0 WHERE [p1] = @i_route AND 35 > @i_cnt_row
	-- Устройство 37
	UPDATE [dbo].[db_t_route_1] SET [p153] = 0, [p154] = '', [p155] = 0, [p156] = '' WHERE [p1] = @i_route AND 36 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p75] = 0, [p76] = 0 WHERE [p1] = @i_route AND 36 > @i_cnt_row
	-- Устройство 38
	UPDATE [dbo].[db_t_route_1] SET [p157] = 0, [p158] = '', [p159] = 0, [p160] = '' WHERE [p1] = @i_route AND 37 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p77] = 0, [p78] = 0 WHERE [p1] = @i_route AND 37 > @i_cnt_row
	-- Устройство 39
	UPDATE [dbo].[db_t_route_1] SET [p161] = 0, [p162] = '', [p163] = 0, [p164] = '' WHERE [p1] = @i_route AND 38 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p79] = 0, [p80] = 0 WHERE [p1] = @i_route AND 38 > @i_cnt_row
	-- Устройство 40
	UPDATE [dbo].[db_t_route_1] SET [p165] = 0, [p166] = '', [p167] = 0, [p168] = '' WHERE [p1] = @i_route AND 39 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p81] = 0, [p82] = 0 WHERE [p1] = @i_route AND 39 > @i_cnt_row
	-- Устройство 41
	UPDATE [dbo].[db_t_route_1] SET [p169] = 0, [p170] = '', [p171] = 0, [p172] = '' WHERE [p1] = @i_route AND 40 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p83] = 0, [p84] = 0 WHERE [p1] = @i_route AND 40 > @i_cnt_row
	-- Устройство 42
	UPDATE [dbo].[db_t_route_1] SET [p173] = 0, [p174] = '', [p175] = 0, [p176] = '' WHERE [p1] = @i_route AND 41 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p85] = 0, [p86] = 0 WHERE [p1] = @i_route AND 41 > @i_cnt_row
	-- Устройство 43
	UPDATE [dbo].[db_t_route_1] SET [p177] = 0, [p178] = '', [p179] = 0, [p180] = '' WHERE [p1] = @i_route AND 42 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p87] = 0, [p88] = 0 WHERE [p1] = @i_route AND 42 > @i_cnt_row
	-- Устройство 44
	UPDATE [dbo].[db_t_route_1] SET [p181] = 0, [p182] = '', [p183] = 0, [p184] = '' WHERE [p1] = @i_route AND 43 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p89] = 0, [p90] = 0 WHERE [p1] = @i_route AND 43 > @i_cnt_row
	-- Устройство 45
	UPDATE [dbo].[db_t_route_1] SET [p185] = 0, [p186] = '', [p187] = 0, [p188] = '' WHERE [p1] = @i_route AND 44 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p91] = 0, [p92] = 0 WHERE [p1] = @i_route AND 44 > @i_cnt_row
	-- Устройство 46
	UPDATE [dbo].[db_t_route_1] SET [p189] = 0, [p190] = '', [p191] = 0, [p192] = '' WHERE [p1] = @i_route AND 45 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p93] = 0, [p94] = 0 WHERE [p1] = @i_route AND 45 > @i_cnt_row
	-- Устройство 47
	UPDATE [dbo].[db_t_route_1] SET [p193] = 0, [p194] = '', [p195] = 0, [p196] = '' WHERE [p1] = @i_route AND 46 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p95] = 0, [p96] = 0 WHERE [p1] = @i_route AND 46 > @i_cnt_row
	-- Устройство 48
	UPDATE [dbo].[db_t_route_1] SET [p197] = 0, [p198] = '', [p199] = 0, [p200] = '' WHERE [p1] = @i_route AND 47 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p97] = 0, [p98] = 0 WHERE [p1] = @i_route AND 47 > @i_cnt_row
	-- Устройство 49
	UPDATE [dbo].[db_t_route_1] SET [p201] = 0, [p202] = '', [p203] = 0, [p204] = '' WHERE [p1] = @i_route AND 48 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p99] = 0, [p100] = 0 WHERE [p1] = @i_route AND 48 > @i_cnt_row
	-- Устройство 50
	UPDATE [dbo].[db_t_route_1] SET [p205] = 0, [p206] = '', [p207] = 0, [p208] = '' WHERE [p1] = @i_route AND 49 > @i_cnt_row
	UPDATE [dbo].[db_t_route_2] SET [p101] = 0, [p102] = 0 WHERE [p1] = @i_route AND 49 > @i_cnt_row
END
GO
--		Создание хранимой процедуры [dbo].[CFG_prog_8_combobox2_cmd]		// Конфигуратор маршрутов - Данные для выпадающего списка
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE CFG_prog_8_combobox2_cmd
	@KKS_to_combobox2 AS NVARCHAR(255) = N''
AS
BEGIN
	SET NOCOUNT ON;
	IF @KKS_to_combobox2 <> N''
	BEGIN
		DECLARE @combobox2 AS NVARCHAR(255) = N''
		SELECT @combobox2 = [obj_type] FROM [db_DEK].[dbo].[db_t_obj] WHERE [obj_kks] = @KKS_to_combobox2
		SELECT
			CASE
				WHEN @combobox2 IN (N'БИС', N'Вибромотор', N'Конвейер скребковый', N'Конвейер ленточный', N'Механизм выгрузки', N'Нория', N'Роторный питатель', N'Роторный питатель аспирации', N'Скальператор') THEN N' ~Пуск'
				WHEN @combobox2 IN (N'Конвейер реверсивный', N'Конвейер ленточный реверсивный') THEN N' ~Пуск вперед~Пуск реверс'
				WHEN @combobox2 IN (N'Перекидной клапан') THEN N' ~Положение 1~Положение 2'
				WHEN @combobox2 IN (N'Шибер') THEN N' ~Открыть~Закрыть'
				WHEN @combobox2 IN (N'Шибер трехпозиционный') THEN N' ~Положение 1~Положение 2~Положение 3 (Открыт)~Закрыть'
			END AS Result, @combobox2 AS Result2
	END
	ELSE
	BEGIN
		SELECT '' AS Result, '' AS Result2;
	END
END
GO