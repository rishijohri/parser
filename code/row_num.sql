create table extra_test as
select as_of_dt,
customer_id,
reviews
from (
    SELECT
        as_of_dt,
        customer_id,
        reviews,
        row_number() over (partition by customer_id order by as_of_dt desc) as row_num
)