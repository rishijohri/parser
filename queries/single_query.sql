CREATE TABLE sdb.source2 AS
SELECT column1,
    column2,
    column3,
    column4,
    case when (column4=3 and column4=1) or column1=3  then 1
    when column4=4 then 2
    else 3 end as column45,
    column5
from sdb.source_original
LEFT JOIN source2 b on a.column1=b.column1 and a.column2=b.column2
WHERE (column1 = 1
    AND column2 = 2) OR (column1=3);
