CREATE TABLE sdb.source2 AS 
SELECT source_original.column1, 
source_original.column2, 
source_original.column3
FROM sdb.source_original
WHERE source_original.column1 = 1 AND  source_original.column2 = 2
;
CREATE TABLE Default.source AS 
SELECT source_original.column1, 
source_original.column2, 
source_original.column3, 
source_original.column45, 
source_original.column5
FROM sdb.source_original
;
CREATE TABLE Default.new_table AS 
SELECT CASE 
WHEN COALESCE(source.column3, 99) < source.column45 OR  (source2.column3 = 10 AND  source2.column3 > 2)   THEN TRIM(source.ABRACADABRA, 99)
WHEN source2.column2 < 5 THEN 2
WHEN source.column1 IN (1, 2, 3)  OR  source.column1 = source.column5 THEN 3
ELSE 0
END AS col3

FROM Default.source
LEFT JOIN sdb.source2 b ON (source.column1 = source2.column1)  
LEFT JOIN sdb.source3 c ON source.column1 = source3.column1
WHERE source.column1 = 1 AND  source3.column2 = 2 AND  source2.column3 IN (1, 2, 3)  OR  source.column2 = 1
GROUP BY source.column1, source.column2
;
