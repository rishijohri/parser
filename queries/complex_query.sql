CREATE TABLE new_table AS
SELECT a.column1,
    column2 as whatever,
    CASE
        WHEN column3 < 5 THEN 1
        else 0
    end as col3,
    case
        when column4 = 5 AND column45 = 25 then 1
        when column4 = 0 then 2
        else 0
    end as col4
FROM sdb.source 
RIGHT JOIN sdb.source2 b ON a.column1 = b.column1
WHERE column1 = 1
    AND column2 = 2
GROUP BY column1,
    column2;