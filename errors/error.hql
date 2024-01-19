CREATE TABLE
    sdb.source2 AS
SELECT
    
    
    
    
    
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
from
    source1
where SUBSTRING(prod_cd, 3, 5) in ("CCC", "DDF", "HHH", "NCN") ;