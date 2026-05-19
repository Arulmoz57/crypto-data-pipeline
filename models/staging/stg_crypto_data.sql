with source as (
    select * from {{ source('raw_sources', 'RAW_MARKET_DATA') }}
),

cleaned as (
    select
        cast(crypto_id as integer) as crypto_id,
        cast(name as varchar) as crypto_name,
        cast(symbol as varchar) as crypto_ticker,
        cast(market_rank as integer) as market_rank,
        cast(price_usd as float) as price_usd,
        cast(volume_24h_usd as float) as volume_24h_usd,
        cast(market_cap_usd as float) as market_cap_usd,
        to_timestamp(last_updated_at) as record_updated_at
    from source
)

select * from cleaned
