CREATE TABLE source AS
SELECT a.column1,
    column2,
    column3,
    column4,
    column45
from sdb.source_original;


CREATE TABLE source2 AS
SELECT column1,
    column2,
    column3,
    column4,
    column45
from sdb.source_original
WHERE column1 = 1
    AND column2 = 2;


CREATE TABLE new_table AS
SELECT b.column1,
    column2 as whatever,
    CASE
        WHEN a.column3 < 5 or b.column3=10 AND b.column3>2 THEN 1
        WHEN column2 > 5 THEN 2
        else 0
    end as col3,
    case
        when column4 = 5 AND column45 = 25 then 1
        when column4 = 0 then 2
        else 0
    end as col4
FROM sdb.source a
LEFT JOIN source2 b ON a.column1 = b.column1
WHERE column1 = 1
    AND column2 = 2
GROUP BY column1,
    column2;