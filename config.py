import os
from dotenv import load_dotenv

load_dotenv()

GOUPC_API_KEY: str = os.getenv("GOUPC_API_KEY", "")
BESTBUY_API_KEY: str = os.getenv("BESTBUY_API_KEY", "")
EBAY_APP_ID: str = os.getenv("EBAY_APP_ID", "")
EBAY_APP_SECRET: str = os.getenv("EBAY_APP_SECRET", "")
SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
