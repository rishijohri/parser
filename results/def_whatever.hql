CREATE TABLE sdb.source2 AS 
SELECT column1 -DATE_FORMAT(MAX(column4), MIN(source.dd-mm-yyyy)) AS whatever

FROM ( SELECT column1, column3, column4 FROM sdb.source WHERE something BETWEEN 4 AND 5 OR  abc = 33 ) 
LEFT JOIN Default.source3 b ON column1 = source3.column56
WHERE source.something BETWEEN 4 AND 5 AND  (source.abc = 33 OR  source.bss = 32)  
;
