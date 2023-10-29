CREATE TABLE source AS
SELECT column1,
    column2,
    column3,
    column4,
    column45,
    column5
from sdb.source_original;


CREATE TABLE source2 AS
SELECT column1,
    column2,
    column3,
    column4,
    column45,
    column5
from sdb.source_original
WHERE column1 = 1
    AND column2 = 2;


CREATE TABLE new_table AS
SELECT coalesce(b.column1, 0),
    a.column1+100 as whatever,
    CASE
        WHEN a.column3 < a.column45 or (b.column3=10 AND b.column3>2) THEN 1
        WHEN b.column2 < 5 THEN 2
        when column1 in (1,2,3) or column1 = column5 then 3
        else 0
    end as col3,
    case
        when column4 = 5 AND column45 = 25 then 1
        when c.column4 is NULL then 2
        else 0
    end as col4
FROM source a
LEFT JOIN source2 b ON (a.column1 = b.column1)
LEFT JOIN source3 c on a.column1 = c.column1
WHERE column1 = 1
    AND c.column2 = 2
    and b.column3 in (1,2,3)
GROUP BY column1,
    column2;