CREATE TABLE
    sdb.source2 AS
SELECT
    DISTINCT COALESCE(ROUND((DISTINCT b.colmax+colmin)*100/colavg), SUBSTRING("KKK", 8, 9), 7) as colmax,
    a.column1 - DATE_FORMAT (MAX(a.column4), MIN(dd-mm-yyyy)) as whatever,
    ADD_MONTHS(b.column2 + col1, 6) as column2,
    MIN(b.column3),
    (column4 + column3) / (column22 * 1000) as column4,
    MIN(case
        when b.column4 = 'Ops' then Case
            when column4 = 1 then 1 - 7
            when column4 = 2 then "OK GOOGLE"
            when column4 = 3 then 2
            else 4
        end
        when c.column4 = 4 then 2
        else 3
    end) as column45,
    case WHEN abc = 'GREAT' then 22
    when abc = 'GOOD' then 21
    when abc = 'what-are-you' then
        case when def = 'here' then 1
        when def = 'villain' then 2
        else 3 END
    else 20 end as colstrange, 
    MIN(COAL)
from
    source1
where SUBSTRING(prod_cd, 3, 5) in ("CCC", "DDF", "HHH", "NCN") ;