CREATE TABLE Default.source AS 
SELECT source_original.column1 AS column1
, source_original.column2 AS column2
, source_original.column3 AS column3
, source_original.column45 AS column45
, source_original.column5 AS column5
FROM sdb.source_original

CREATE TABLE sdb.source2 AS 
SELECT source_original.column1 AS column1
, source_original.column2 AS column2
, source_original.column3 AS column3
FROM sdb.source_original

CREATE TABLE Default.new_table AS 
SELECT column1+100 AS whatever
, CASE 
WHEN (source.column3 < source.column45 OR )
 WHEN (sdb.source2.column3 = 10 AND sdb.source2.column3 > 2  )
 THEN 1
 WHEN (sdb.source2.column2 < 5  )
 THEN 2
 WHEN (source.column1 IN (1,2,3) OR source.column1 = source.column5  )
 THEN 3
 ELSE 0
END AS col3
FROM Default.source
LEFT JOIN sdb.source2 ON (source.column1 = sdb.source2.column1  )
 

