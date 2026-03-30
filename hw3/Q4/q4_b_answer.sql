






-- a)
SELECT tc1.table_name, COUNT(DISTINCT tc2.table_name)
FROM information_schema.table_constraints tc1
    JOIN information_schema.referential_constraints rc1
        ON tc1.constraint_name = rc1.constraint_name
    JOIN information_schema.table_constraints tc2
        ON rc1.unique_constraint_name = tc2.constraint_name
WHERE tc1.table_schema = 'q4'
GROUP BY tc1.table_name
HAVING COUNT(DISTINCT tc2.table_name) >= 2;

-- b)
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'q4'
  AND (data_type LIKE '%date%' OR data_type LIKE '%timestamp%');


-- c)
SELECT
    COUNT(DISTINCT flight_number) AS flight_number_distinct,
    COUNT(DISTINCT departure_date) AS departure_date_distinct,
    COUNT(DISTINCT plane_type) AS plane_type_distinct
FROM flight;

-- d)
SELECT tc.table_name, COUNT(kcu.column_name) AS num_columns
FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
        AND tc.table_name = kcu.table_name
WHERE tc.table_schema = 'q4'
  AND tc.constraint_type = 'PRIMARY KEY'
GROUP BY tc.table_name
HAVING COUNT(kcu.column_name) > 1;

-- e)
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'q4'
  AND column_name LIKE '%name%';
