CREATE TABLE
    sdb.source2 AS
SELECT
    a.column1 - DATE_FORMAT (MAX(a.column4), "dd-mm-yyyy") as whatever,
    b.column2,
    MIN(b.column3),
    column4,
    case
        when b.column4 = 'OK' then Case
            when column4 = 1 then 1 - 7
            when column4 = 2 then 2
            when column4 = 3 then 2
            else 4
        end
        when c.column4 = 4 then 2
        else 3
    end as column45,
    column5,
    row_number() over (partition by column1 order by column2 DESC) as row_num
from
    (SELECT
    column1,
    column3,
    column4,
    row_number() OVER (PARTITION BY column1 ORDER BY column2 DESC) AS row_num
    from sdb.source) a
    LEFT JOIN source3 b on a.column1 = b.column56
    and a.column2 = b.column2
    left join (
        select
            column1,
            column2,
            column3
        from
            sourc4.table1
            where column4 = "NANAMI"
    ) c on a.column1 = c.column1
WHERE avacado in (select machete, abc from table2 where column1 = 1)
and avado between addition and subtraction
    OR (column1 = 3)
    OR (column3 = 2);