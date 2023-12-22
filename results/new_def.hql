CREATE TABLE sdb.source2 AS 
SELECT CASE
WHEN source3.column4 = 'OK' THEN
        CASE
        WHEN column4 = 1 THEN 1
        WHEN column4 = 2 THEN 2
        WHEN column4 = 3 THEN 2
        ELSE 4
END
WHEN column4 = 4 THEN 2
ELSE 3
END AS column45

FROM sdb.source_original
LEFT JOIN source3 b ON source_original.column1 = source3.column56 AND  source_original.column2 = source3.column2
JOIN ( SELECT column1, column2, column3 FROM sourc4.table1 WHERE column4 = "NANAMI" )  c ON source_original.column1 = table1.column1
WHERE (column1 IN (1, 2, 3)  AND  (b.column2 = 2 OR  colym6 <> 7)  ) OR (column1 = 3) OR (column3 = 2)