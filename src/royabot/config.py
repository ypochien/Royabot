import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY", "")
SECRET_KEY = os.environ.get("SECRET_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

PARQUET_FILENAME = "daily_quotes.parquet"
DOWNLOADS_DIR = Path("downloads")


def init_polars():
    """Configure polars display settings. Call once at application startup."""
    import polars as pl

    pl.Config.set_tbl_cols(-1)
