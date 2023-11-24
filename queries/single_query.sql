CREATE TABLE sdb.source2 AS
SELECT a.column1,
    column2,
    column3,
    column4,
    case when (b.column4='OK' and a.column5=1) or substr(column1, 1, 1)=3  then 1
    when column4=4 then 2
    else 3 end as column45,
    column5
from sdb.source_original a
LEFT JOIN source3 b on a.column1=b.column56 and a.column2=b.column2
WHERE (column1 = 1
    AND b.column2 = 2) OR (column1=3);
