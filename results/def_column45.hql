CREATE TABLE sdb.source2 AS 
SELECT MIN( CASE 
WHEN source3.column4 = 'Ops' THEN 
	CASE 
	WHEN source.column4 = 1 THEN 1
	WHEN source.column4 = 2 THEN "OK GOOGLE"
	WHEN source.column4 = 3 THEN 2
	ELSE 4
END
WHEN column4 = 4 THEN 2
ELSE 3
END ) AS column45

FROM ( SELECT column1, column3, column4 FROM sdb.source WHERE something BETWEEN 4 AND 5 OR  abc = 33 ) 
LEFT JOIN Default.source3 b ON column1 = source3.column56
WHERE source.something BETWEEN 4 AND 5 AND  (source.abc = 33 OR  source.bss = 32)  
;
