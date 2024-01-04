CREATE TABLE
    sdb.source2 AS
SELECT
    a.column1 - DATE_FORMAT (MAX(a.column4), "dd-mm-yyyy") as whatever,
    ADD_MONTHS(b.column2, -6) + abc as column2,
    MIN(b.column3),
    (column4 + column3) + (column3 + column4) as column4,
    column5
from
    (SELECT
    column1,
    column3,
    column4
    from sdb.source
    where something between 4 and 5 or abc = 33) a
    LEFT JOIN source3 b on a.column1 = b.column56
    where something between 4 and 5 and (
        abc = 33 or bss = 32
    ) ;