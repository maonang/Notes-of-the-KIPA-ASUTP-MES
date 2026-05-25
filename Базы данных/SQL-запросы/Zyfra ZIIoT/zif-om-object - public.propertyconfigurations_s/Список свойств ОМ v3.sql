-- -------------------------------------------------------------------
-- Параметры поиска (настраиваемые фильтры)
-- -------------------------------------------------------------------
WITH CTE_search_params AS (
    SELECT
        NULL::uuid		AS property_uuid,      -- Фильтр по UUID свойства
        ''::varchar		AS property_name,      -- Фильтр по наименованию свойства
        ''::varchar		AS property_path,      -- Фильтр по пути до свойства
        ''::varchar		AS tag_id,             -- Фильтр по наименовнию тега
		
		''::varchar		AS attribute_path,     -- Фильтр по пути до свойства в атрибутах формулы
		''::varchar		AS attribute_tag_id    -- Фильтр по наименованию тега в атрибутах формулы
),

-- -------------------------------------------------------------------
-- Справочник типов данных (маппинг UUID -> название типа)
-- -------------------------------------------------------------------
CTE_valuetypes_s AS (
    SELECT * FROM (VALUES
        ('ebce099b-ffa9-40e4-a4fb-8984fe1ff4ef'::uuid, 'String'),
        ('a41b6ab6-29dc-4812-9955-0b90e24f00fc'::uuid, 'Integer'),
        ('6229c2c8-ff1a-4d9f-afeb-f74355fa1199'::uuid, 'Double'),
        ('3b92faa7-0de0-47b0-8cfc-eac125757cb7'::uuid, 'Boolean'),
        ('eb9612ff-6610-4008-abc4-93c86bc36cb1'::uuid, 'DateTime'),
        ('8fcbd40c-9a59-457d-8ade-ee6f46f595fe'::uuid, 'Long'),
        ('a8670d30-b610-49c2-b44f-87669f93508e'::uuid, 'Decimal'),
        ('be770ebc-55e2-4614-bec1-6af5b3c4048f'::uuid, 'DirectoryItem'),
        ('f725baa3-0db3-44da-8725-31c7017399a7'::uuid, 'Guid')
    ) AS t(id, name)
),

-- -------------------------------------------------------------------
-- Справочник свойств для восстановления связей (propertyId)
-- Таблицы:
-- 		public.properties_s 			AS p,
-- 		public.objects_s 				AS o,
-- 		public.propertyconfigurations_s	AS pc
-- -------------------------------------------------------------------
CTE_property_lookup AS (
    SELECT DISTINCT ON (p.id)
        p.id AS property_uuid,
        CONCAT(o.path, '|', p.name) AS full_path,
        pc.configuration->>'tagId' AS tag_id
    FROM public.properties_s p
    INNER JOIN public.objects_s o 
        ON o.id = p.objectid
    LEFT JOIN public.propertyconfigurations_s pc
        ON pc.id = p.id
        AND pc.tt IS NULL
        AND NOT pc.isdeleted
    WHERE 
        p.tt IS NULL
        AND NOT p.isdeleted
        AND o.tt IS NULL
        AND NOT o.isdeleted
    ORDER BY 
        p.id, 
        pc.ts DESC NULLS LAST
),

-- -------------------------------------------------------------------
-- Поиск UUID целевого свойства по пути (для фильтрации по attribute_path)
-- Таблицы: CTE_property_lookup
-- -------------------------------------------------------------------
CTE_target_property AS (
    SELECT property_uuid
    FROM CTE_property_lookup
    WHERE full_path = (SELECT attribute_path FROM CTE_search_params WHERE attribute_path != '')
       OR full_path ILIKE '%' || (SELECT attribute_path FROM CTE_search_params WHERE attribute_path != '') || '%'
    LIMIT 1
),

-- -------------------------------------------------------------------
-- Поиск UUID свойств по тегу (для фильтрации по attribute_tag_id)
-- Таблицы: CTE_property_lookup
-- -------------------------------------------------------------------
CTE_target_property_by_tag AS (
    SELECT DISTINCT property_uuid
    FROM CTE_property_lookup
    WHERE tag_id = (SELECT attribute_tag_id FROM CTE_search_params WHERE attribute_tag_id != '')
    
    UNION
    
    -- Обработка SysTag_<UUID>
    SELECT DISTINCT 
        CASE 
            WHEN (SELECT attribute_tag_id FROM CTE_search_params WHERE attribute_tag_id != '') LIKE 'SysTag_%'
            THEN (SELECT substring(attribute_tag_id FROM 8) FROM CTE_search_params WHERE attribute_tag_id != '')::uuid
            ELSE NULL
        END AS property_uuid
    WHERE 
        (SELECT attribute_tag_id FROM CTE_search_params WHERE attribute_tag_id != '') LIKE 'SysTag_%'
        AND (SELECT substring(attribute_tag_id FROM 8) FROM CTE_search_params WHERE attribute_tag_id != '') ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
),


-- -------------------------------------------------------------------
-- Базовая информация о свойствах с определением источника данных
-- Таблицы:
-- 		public.properties_s 			AS p,
-- 		public.objects_s 				AS o,
-- 		public.propertyconfigurations_s	AS pc,
-- 		CTE_search_params 				AS sp
-- 		CTE_target_property_by_tag
-- -------------------------------------------------------------------
CTE_base_properties AS (
    SELECT DISTINCT ON (p.id)
        p.id                          AS property_id,
        p.name                        AS property_name,
        o.name                        AS object_name,
        o.path                        AS object_path,
        o.hierarchyscopeids           AS hierarchy_scope_ids,
        pc.configuration              AS property_config,
        pc.ts                         AS config_timestamp,
        p.valuetypeid                 AS value_type_id,
        
        -- Определение типа источника данных
        CASE
            WHEN pc.configuration ? 'expression' THEN 'Calculation Tag'
            WHEN pc.configuration ? 'const'       THEN 'Constant'
            WHEN pc.configuration ? 'query'       THEN 'SQL'
            WHEN pc.configuration ? 'tagId'       THEN 'Tag'
            ELSE 'Unknown'
        END AS data_source_type
            
    FROM public.properties_s p
    INNER JOIN public.objects_s o 
        ON o.id = p.objectid
    LEFT JOIN public.propertyconfigurations_s pc
        ON pc.id = p.id
        AND pc.tt IS NULL
        AND NOT pc.isdeleted
    CROSS JOIN CTE_search_params sp
    
    WHERE 
        p.tt IS NULL
        AND NOT p.isdeleted
        AND o.tt IS NULL
        AND NOT o.isdeleted
        AND (
			-- Фильтр по UUID свойства
			(sp.property_uuid IS NOT NULL AND p.id = sp.property_uuid)
			OR 
			-- Фильтр по имени свойства
			(sp.property_name IS NOT NULL AND sp.property_name != '' AND p.name = sp.property_name)
			OR 
			-- Фильтр по пути свойства
			(sp.property_path IS NOT NULL AND sp.property_path != '' AND CONCAT(o.path, '|', p.name) ILIKE '%' || sp.property_path || '%')
			OR 
			-- Фильтр по тегу
			(sp.tag_id IS NOT NULL AND sp.tag_id != '' AND pc.configuration->>'tagId' = sp.tag_id)
			OR
			-- Фильтр по пути свойства в атрибутах формулы
			(sp.attribute_path IS NOT NULL AND sp.attribute_path != '' 
				AND pc.configuration ? 'expression'
				AND EXISTS (
					SELECT 1 
					FROM jsonb_array_elements(pc.configuration->'variables') AS var_obj
					WHERE var_obj->>'type' = 'propertyId'
					  AND (var_obj->>'value')::uuid = (SELECT property_uuid FROM CTE_target_property)
				)
			)
			OR
			-- Фильтр по тегу в атрибутах формулы
			(sp.attribute_tag_id IS NOT NULL AND sp.attribute_tag_id != '' 
				AND pc.configuration ? 'expression'
				AND EXISTS (
					SELECT 1 
					FROM jsonb_array_elements(pc.configuration->'variables') AS var_obj
					WHERE var_obj->>'type' = 'propertyId'
					  AND (var_obj->>'value')::uuid IN (SELECT property_uuid FROM CTE_target_property_by_tag)
				)
			)
			OR 
			-- Если все параметры NULL или пустые строки - возвращаем все записи
			((sp.property_uuid IS NULL)
				AND (sp.property_name IS NULL OR sp.property_name = '')
				AND (sp.property_path IS NULL OR sp.property_path = '')
				AND (sp.tag_id IS NULL OR sp.tag_id = '')
				AND (sp.attribute_path IS NULL OR sp.attribute_path = '')
				AND (sp.attribute_tag_id IS NULL OR sp.attribute_tag_id = ''))
		)

    ORDER BY 
        p.id, 
        pc.ts DESC NULLS LAST
),

-- -------------------------------------------------------------------
-- Только расчетные теги (формулы)
-- Таблицы: CTE_base_properties
-- -------------------------------------------------------------------
CTE_calc_tags AS (
    SELECT
        property_id,
        property_name,
        object_name,
        object_path,
        property_config
    FROM CTE_base_properties
    WHERE data_source_type = 'Calculation Tag'
),

-- -------------------------------------------------------------------
-- Декомпозиция переменных из MVEL-выражений
-- Таблицы: CTE_calc_tags AS ct
-- -------------------------------------------------------------------
CTE_variables AS (
    SELECT
        ct.property_id,
        ct.property_name,
        (var_obj->>'value')::VARCHAR     AS variable_value,
        (var_obj->>'alias')::VARCHAR      AS alias,
        (var_obj->>'type')::VARCHAR       AS var_type,
        (var_obj->>'isTrigger')::BOOLEAN  AS is_trigger
    FROM CTE_calc_tags ct
    CROSS JOIN LATERAL jsonb_array_elements(ct.property_config->'variables') AS var_obj
),

-- -------------------------------------------------------------------
-- Поиск ссылок на свойства (propertyId -> полный путь и tagId)
-- Таблицы:
-- 		CTE_variables 			AS v,
-- 		CTE_property_lookup 	AS pl
-- -------------------------------------------------------------------
CTE_variables_resolved AS (
    SELECT
        v.property_id,
        v.property_name,
        v.alias,
        v.var_type,
        v.is_trigger,
        v.variable_value AS raw_value,
        
        -- Для propertyId подставляем полный путь, иначе оставляем raw_value
        CASE
            WHEN v.var_type = 'propertyId' THEN pl.full_path
            ELSE v.variable_value
        END AS resolved_path,
        
        -- Для propertyId извлекаем tagId, иначе NULL
        CASE
            WHEN v.var_type = 'propertyId' THEN pl.tag_id
            ELSE NULL
        END AS resolved_tag_id
        
    FROM CTE_variables v
    LEFT JOIN CTE_property_lookup pl
        ON v.var_type = 'propertyId'
		AND v.variable_value IS NOT NULL
		AND v.variable_value != '0'
		AND v.variable_value != ''
		AND v.variable_value ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'  -- Проверка что это UUID
        AND pl.property_uuid = (SELECT v.variable_value::uuid WHERE v.variable_value ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
),

-- -------------------------------------------------------------------
-- Агрегация переменных в JSON-объект для каждого расчетного тега
-- Таблицы: CTE_variables_resolved
-- -------------------------------------------------------------------
CTE_variables_aggregated AS (
    SELECT
        property_id AS property_uuid,
        jsonb_object_agg(
            alias,
            jsonb_build_object(
                'type', var_type,
                'path',			CASE WHEN var_type = 'propertyId'	THEN resolved_path END,
                'tagId',		CASE WHEN var_type = 'propertyId'	THEN COALESCE(NULLIF(resolved_tag_id, ''), 'SysTag_' || raw_value::text) END,
                'const_value',	CASE WHEN var_type = 'const'		THEN raw_value END
            )
        ) AS variables_json
    FROM CTE_variables_resolved
    GROUP BY property_id
)

-- -------------------------------------------------------------------
-- Основной фрагмент SQL-запроса
-- Таблицы:
-- 		CTE_base_properties 		AS bp,
-- 		CTE_valuetypes_s 			AS vt,
-- 		CTE_variables_aggregated 	AS var_agg
-- -------------------------------------------------------------------
SELECT
    
	bp.property_id AS "UUID",
	
	-- Путь до свойства в ОМ (с заменой \\ на \)
    REPLACE(CONCAT(bp.object_path, '|', bp.property_name), '\\\\', '\\') AS "Путь до свойства в ОМ",
    
    -- Объект
    bp.object_name AS "Объект",
    
    -- Свойство
    bp.property_name AS "Свойство",
    
    -- Источник данных
    CASE bp.data_source_type
        WHEN 'Unknown'        THEN 'Нет источника'
        WHEN 'Tag'            THEN 'Тег БДРВ'
        WHEN 'Constant'       THEN 'Константа'
        WHEN 'Calculation Tag' THEN 'Формула'
        ELSE bp.data_source_type
    END AS "Источник",
    
    -- Тип данных свойства
    vt.name AS "Тип данных свойства",
    
    -- Источник данных = Тег БДРВ
    CASE
        WHEN bp.data_source_type = 'Tag'
        THEN bp.property_config->>'tagId'
    END AS "Тег источника данных",
    
    -- Источник данных = Формула -> Тег БДРВ
    CASE
        WHEN bp.data_source_type = 'Calculation Tag' THEN
            COALESCE(
                NULLIF(TRIM(bp.property_config->>'tagId'), ''),
                'SysTag_' || bp.property_id::text
            )
        ELSE NULL
    END AS "Тег для записи результата расчета",
    
    -- Источник данных = Формула -> Атрибуты MVEL-выражения (в формате JSON)
    CASE
        WHEN bp.data_source_type = 'Calculation Tag'
        THEN var_agg.variables_json
    END AS "Атрибуты MVEL-выражения",
    
    -- Источник данных = Формула -> MVEL-выражение
    CASE
        WHEN bp.data_source_type = 'Calculation Tag'
        THEN bp.property_config->>'expression'
    END AS "MVEL-выражение",
    
    -- Источник данных = Формула -> Тип запуска расчета
    CASE
        WHEN bp.data_source_type = 'Calculation Tag' THEN
            CASE bp.property_config->>'triggerType'
                WHEN 'ListenData' THEN 'Потоковый'
                WHEN 'ByTrigger'  THEN 'По триггеру'
                WHEN 'Periodic'   THEN 'Периодический'
                WHEN 'OnDemand'   THEN 'По запросу'
                ELSE bp.property_config->>'triggerType'
            END
    END AS "Тип запуска расчета",
    
    -- Период расчета в секундах
    CASE
        WHEN bp.data_source_type = 'Calculation Tag'
        THEN (bp.property_config->>'periodInSeconds')::INT
    END AS "Период, сек",
    
    -- Период расчета в формате часы:минуты
    CASE
        WHEN bp.data_source_type = 'Calculation Tag'
            AND (bp.property_config->>'periodInSeconds') IS NOT NULL
        THEN TO_CHAR(MAKE_INTERVAL(secs => (bp.property_config->>'periodInSeconds')::INT), 'HH24:MI')
    END AS "Период, ч:мин",
    
    -- Смещение расчета в секундах
    CASE
        WHEN bp.data_source_type = 'Calculation Tag'
        THEN (bp.property_config->>'offsetInSeconds')::INT
    END AS "Смещение, сек",
    
    -- Смещение расчета в формате часы:минуты
    CASE
        WHEN bp.data_source_type = 'Calculation Tag'
            AND (bp.property_config->>'offsetInSeconds') IS NOT NULL
        THEN TO_CHAR(MAKE_INTERVAL(secs => (bp.property_config->>'offsetInSeconds')::INT), 'HH24:MI')
    END AS "Смещение, ч:мин",
    
    -- Значение константы (для источника типа 'Constant')
    CASE
        WHEN bp.data_source_type = 'Constant'
        THEN bp.property_config->>'const'
    END AS "Значение константы",
    
    -- SQL-запрос (для источника типа 'SQL')
    CASE
        WHEN bp.data_source_type = 'SQL'
        THEN bp.property_config->>'query'
    END AS "SQL-запрос",
    
    -- Строка подключения к БД (для источника типа 'SQL')
    CASE
        WHEN bp.data_source_type = 'SQL'
        THEN bp.property_config->>'connectionString'
    END AS "Подключение",
    
    -- Параметр времени для SQL-запроса
    CASE
        WHEN bp.data_source_type = 'SQL'
        THEN bp.property_config->'arguments'->>'timeArgument'
    END AS "Параметры запроса - Время",
    
    -- Интервал обновления для SQL-источника (секунды)
    CASE
        WHEN bp.data_source_type = 'SQL'
        THEN (bp.property_config->>'refreshInterval')::INT
    END AS "Интервал обновления"

FROM CTE_base_properties bp

-- Присоединяем тип данных
LEFT JOIN CTE_valuetypes_s vt
    ON vt.id = bp.value_type_id

-- Присоединяем агрегированные переменные для расчетных тегов
LEFT JOIN CTE_variables_aggregated var_agg
    ON var_agg.property_uuid = bp.property_id

ORDER BY 
    "Путь до свойства в ОМ",
    bp.property_name;