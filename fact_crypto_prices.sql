with staging as (
    select * from {{ ref('stg_crypto_data') }}
)

select
    crypto_id,
    market_rank,
    price_usd,
    volume_24h_usd,
    market_cap_usd,
    record_updated_at
from staging