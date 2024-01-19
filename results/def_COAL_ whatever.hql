CREATE TABLE sdb.source2 AS 
SELECT MIN(source1.COAL)
FROM Default.source1
WHERE SUBSTRING(source1.prod_cd, 3 , 5 ) IN ("CCC" , "DDF" , "HHH" , "NCN") 
;
