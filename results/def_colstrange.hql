CREATE TABLE sdb.source1 AS 
SELECT true_source.abc, 
true_source.def
FROM Default.true_source
;
CREATE TABLE sdb.source2 AS 
SELECT ( CASE 
	WHEN (source1.abc = 'GREAT'  OR  source1.abc = 'OUTSTANDING' ) AND source1.review > 4  THEN 22 
	WHEN source1.abc = 'GOOD'  THEN 21 
	WHEN source1.abc = 'what-are-you'  THEN CASE 
	WHEN source1.def = 'here'  THEN 1 
	WHEN source1.def = 'villain'  THEN 2 
	ELSE 3 
END 
	ELSE 20 
END )  AS colstrange

FROM Default.source1
WHERE SUBSTRING(source1.prod_cd, 3 , 5 ) IN ("CCC" , "DDF" , "HHH" , "NCN") 
;
