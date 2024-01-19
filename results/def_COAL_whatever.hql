CREATE TABLE sdb.source2 AS 
SELECT column1 -DATE_FORMAT(MAX(column4), MIN(source1.dd-mm-yyyy)) AS whatever
, 
MIN(source1.COAL)
FROM Default.source1
WHERE SUBSTRING(source1.prod_cd, 3 , 5 ) IN ("CCC" , "DDF" , "HHH" , "NCN") 
;
