CREATE TABLE sdb.source2 AS 
SELECT (  source.column4 + source.column3) / (  source.column22 * 1000)  AS column4

FROM ( SELECT column1, column3, column4 FROM sdb.source WHERE  something BETWEEN  4 AND  5 OR   abc =  33 ) 
LEFT JOIN Default.source3 b ON  a.column1 =  source3.column56
WHERE  source.something BETWEEN  4 AND  5 AND  ( source.abc =  33 OR   source.bss =  32)  
;
