WITH
-- Параметры поиска
search_params AS (
    SELECT
        NULL::varchar AS property_name,  -- NULL или Наименование свойства
        NULL::uuid AS property_uuid,     -- NULL или UUID свойства
        NULL::varchar AS property_path,  -- NULL или Путь к свойству (часть или полный)
        NULL::varchar AS tag_id          -- NULL или tagId для поиска свойств, использующих этот тег
),
target_properties AS (
    SELECT
        p.id AS property_uuid,
        p.name AS property_name,
        CONCAT(o.path, '|', p.name) AS full_path
    FROM public.properties_s p
    INNER JOIN public.objects_s o ON p.objectid = o.id
        AND o.tt IS NULL
        AND NOT o.isdeleted
    CROSS JOIN search_params sp
    WHERE p.tt IS NULL
        AND NOT p.isdeleted
        AND (
            (sp.property_name IS NOT NULL AND p.name = sp.property_name)
            OR
            (sp.property_uuid IS NOT NULL AND p.id = sp.property_uuid)
            OR
            (sp.property_path IS NOT NULL AND CONCAT(o.path, '|', p.name) ILIKE '%' || sp.property_path || '%')
            OR
            (sp.tag_id IS NOT NULL AND EXISTS (
                SELECT 1
                FROM public.propertyconfigurations_s pc
                WHERE pc.id = p.id
                    AND pc.tt IS NULL
                    AND NOT pc.isdeleted
                    AND pc.configuration ->> 'tagId' = sp.tag_id
            ))
        )
)
SELECT
    tp.full_path AS "Полный путь к искомому свойству",
    tp.property_name AS "Наименование искомого свойства",
    tp.property_uuid AS "UUID искомого свойства",
    pc.ts AS "Дата изменения расчетного свойства",
    CONCAT(o.path, '|', p.name) AS "Путь к расчетному свойству",
    p.id AS "UUID расчетного свойства",
    pc.configuration AS "Конфигурация расчетного свойства"
FROM public.propertyconfigurations_s pc
INNER JOIN public.properties_s p ON pc.id = p.id
    AND p.tt IS NULL
    AND NOT p.isdeleted
INNER JOIN public.objects_s o ON p.objectid = o.id
    AND o.tt IS NULL
    AND NOT o.isdeleted
INNER JOIN target_properties tp ON TRUE
WHERE pc.tt IS NULL
    AND NOT pc.isdeleted
    AND pc.configuration ? 'variables'
    AND EXISTS (
        SELECT 1
        FROM jsonb_array_elements(pc.configuration->'variables') AS var
        WHERE var->>'value' = tp.property_uuid::text
            AND var->>'type' = 'propertyId'
    )
ORDER BY tp.full_path, CONCAT(o.path, '|', p.name) ASC;