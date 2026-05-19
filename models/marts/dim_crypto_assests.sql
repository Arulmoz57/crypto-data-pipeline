with staging as (
    select * from {{ ref('stg_crypto_data') }}
)

select distinct
    crypto_id,
    crypto_name,
    crypto_ticker
from staging
