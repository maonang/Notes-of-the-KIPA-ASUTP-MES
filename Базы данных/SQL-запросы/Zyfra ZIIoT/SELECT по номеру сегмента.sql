-- 1. Определение количества сегментов выгрузки по 300 000 записей
WITH stats AS (
    SELECT
        COUNT(*) as total_records,
        CEIL(COUNT(*)::float / 300000) as total_segments
    FROM public.properties_s
    --WHERE ts >= '2025-01-01' AND ts < '2026-01-01'
)
SELECT
    total_records,
    total_segments,
    300000 as segment_size,
    (total_records % 300000) as last_segment_size
FROM stats;

-- 2. Выборка данных по номеру сегмента
WITH numbered_records AS (
    SELECT *,
           ROW_NUMBER() OVER (ORDER BY ts, id) as row_num
    FROM public.properties_s
    WHERE ts >= '2025-01-01' AND ts < '2026-01-01'
)
SELECT *
FROM numbered_records
-- Сегмент №1
WHERE row_num BETWEEN ((1 - 1) * 300000 + 1) AND (1 * 300000) -- диапазон: от AND до
-- Сегмент №2
-- WHERE row_num BETWEEN ((2 - 1) * 300000 + 1) AND (2 * 300000)
ORDER BY ts, id;
