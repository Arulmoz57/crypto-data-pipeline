import os
import requests
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# Load the keys and passwords from your hidden .env file
load_dotenv()

def fetch_crypto_data():
    print("📡 Fetching real-time market data from CoinMarketCap API...")
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    
    # We want the top 50 cryptocurrencies priced in USD
    parameters = {'start': '1', 'limit': '50', 'convert': 'USD'}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.getenv('CMC_API_KEY'),
    }
    
    response = requests.get(url, params=parameters, headers=headers)
    
    # Catch any HTTP errors safely
    response.raise_for_status() 
    data = response.json()['data']
    
    # Parse and clean the deeply nested JSON structure into flat rows
    processed_records = []
    for coin in data:
        processed_records.append({
            "CRYPTO_ID": int(coin['id']),
            "NAME": str(coin['name']),
            "SYMBOL": str(coin['symbol']),
            "MARKET_RANK": int(coin['cmc_rank']),
            "PRICE_USD": float(coin['quote']['USD']['price']),
            "VOLUME_24H_USD": float(coin['quote']['USD']['volume_24h']),
            "MARKET_CAP_USD": float(coin['quote']['USD']['market_cap']),
            "LAST_UPDATED_AT": str(coin['last_updated'])
        })
    
    # Convert list of dictionaries into a clean Pandas Dataframe
    df = pd.DataFrame(processed_records)
    print(f"✅ Successfully extracted {len(df)} records from API.")
    return df

def load_to_snowflake(df):
    print("❄️ Connecting to Snowflake Data Warehouse...")
    
    # Establish connection using configuration from .env
    conn = snowflake.connector.connect(
        user=os.getenv('SF_USER'),
        password=os.getenv('SF_PASSWORD'),
        account=os.getenv('SF_ACCOUNT'),
        warehouse='CRYPTO_WH',
        database='CRYPTO_DB',
        schema='RAW'
    )
    
    print("🚀 Writing dataframe chunks into table 'RAW_MARKET_DATA'...")
    try:
        # write_pandas automatically maps data types and streams data efficiently
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name='RAW_MARKET_DATA',
            auto_create_table=True, # Automatically creates the table structure if it doesn't exist
            overwrite=True          # Overwrites existing data to represent the latest market state
        )
        if success:
            print(f"🎉 Success! Loaded {nrows} rows across {nchunks} chunk(s) into Snowflake.")
    except Exception as e:
        print(f"❌ Error uploading to Snowflake: {str(e)}")
    finally:
        conn.close()
        print("🔌 Database connection closed cleanly.")

if __name__ == "__main__":
    # Execute the end-to-end Python pipeline
    try:
        market_df = fetch_crypto_data()
        load_to_snowflake(market_df)
    except Exception as e:
        print(f"💥 Pipeline Failed: {str(e)}")