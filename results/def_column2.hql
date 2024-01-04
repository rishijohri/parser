CREATE TABLE sdb.source2 AS 
SELECT  ADD_MONTHS( source3.column2, -6) AS column2

FROM ( SELECT column1, column3, column4 FROM sdb.source WHERE  something BETWEEN  4 AND  5 OR   abc =  33 ) 
LEFT JOIN Default.source3 b ON  a.column1 =  source3.column56
WHERE  source.something BETWEEN  4 AND  5 AND  ( source.abc =  33 OR   source.bss =  32)  
;
