CREATE TABLE sdb.source2 AS 
SELECT DISTINCT COALESCE(ROUND((DISTINCT colmax +source1.colmin)*100 /source1.colavg), SUBSTRING("KKK" , 8 , 9 ), 7 ) AS colmax
, 
MIN( ) AS column45

FROM Default.source1
WHERE SUBSTRING(source1.prod_cd, 3 , 5 ) IN ("CCC" , "DDF" , "HHH" , "NCN") 
;
