CREATE TABLE source2 AS
SELECT column1,
    column2,
    column3,
    column4,
    column45,
    column5
from sdb.source_original
WHERE (column1 = 1
    AND column2 = 2);