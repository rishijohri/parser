CREATE TABLE sdb.source2 AS 
SELECT  AS row_num

FROM ( SELECT column1, column3, column4, row_num FROM sdb.source ) 
LEFT JOIN Default.source3 b ON a.column1 = source3.column56 AND  a.column2 = source3.column2
LEFT JOIN ( SELECT column1, column2, column3 FROM sourc4.table1 WHERE column4 = "NANAMI" )  c ON a.column1 = table1.column1
WHERE source.avacado IN (4, 2, 2, 7)  AND  source.avado BETWEEN source.addition AND source.subtraction OR  (source.column1 = 3) OR (source.column3 = 2)  
;
