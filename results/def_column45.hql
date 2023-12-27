CREATE TABLE sdb.source2 AS 
SELECT CASE 
WHEN source3.column4 = 'OK' THEN 
	CASE 
	WHEN source.column4 = 1 THEN 1
	WHEN source.column4 = 2 THEN 2
	WHEN source.column4 = 3 THEN 2
	ELSE 4
END
WHEN table1.column4 = 4 THEN 2
ELSE 3
END AS column45

FROM ( SELECT column1, column3, column4, row_num FROM sdb.source2 ) 
LEFT JOIN Default.source3 b ON a.column1 = source3.column56 AND  a.column2 = source3.column2
LEFT JOIN ( SELECT column1, column2, column3 FROM sourc4.table1 WHERE column4 = "NANAMI" )  c ON a.column1 = table1.column1
;
