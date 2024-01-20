CREATE TABLE sdb.source2 AS 
SELECT MIN(CASE 
	WHEN column4 = 'Ops'  THEN CASE 
	WHEN source1.column4 = 1  THEN 1 - 7 
	WHEN source1.column4 = 2  THEN "OK GOOGLE" 
	WHEN source1.column4 = 3  THEN 2 
	ELSE 4 
END 
	WHEN column4 = 4  THEN 2 
	ELSE 3 
END ) AS column45

FROM Default.source1
WHERE SUBSTRING(source1.prod_cd, 3 , 5 ) IN ("CCC" , "DDF" , "HHH" , "NCN") 
;
