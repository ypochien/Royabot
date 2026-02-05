from typing import Optional
import datetime as dt

from loguru import logger
import polars as pl
import shioaji as sj

from royabot import config
from royabot.util import daily_quotes_to_df


class ParquetStore:
    """Handles reading and writing market data to parquet files."""

    def __init__(self, filename: str = None):
        self.filename = filename or config.PARQUET_FILENAME

    def display_stats(self) -> None:
        try:
            df = pl.read_parquet(self.filename)
            if df.shape[0] > 0:
                earliest_date = df.select(pl.min("date")).item()
                latest_date = df.select(pl.max("date")).item()
                total_records = df.shape[0]
                logger.info(
                    f"Parquet stats - Earliest: {earliest_date}, "
                    f"Latest: {latest_date}, Total: {total_records}"
                )
            else:
                logger.info("Parquet file is empty.")
        except FileNotFoundError:
            logger.info("Parquet file not found.")

    def get_latest_date(self) -> Optional[dt.date]:
        try:
            df = pl.read_parquet(self.filename)
            if df.shape[0] > 0:
                latest_date_str = df.select(pl.max("date")).item()
                if latest_date_str is not None:
                    return dt.datetime.strptime(latest_date_str, "%Y-%m-%d").date()
            return None
        except FileNotFoundError:
            return None

    def save(self, df: pl.DataFrame) -> None:
        if df.shape[0] > 0:
            df.write_parquet(self.filename)

    def append(self, df: pl.DataFrame, overwrite: bool = True) -> None:
        if df is None:
            return
        if df.shape[0] == 0:
            return
        try:
            existing_df = pl.read_parquet(self.filename)
            # Build (date, code) keys for dedup
            new_keys = df.select("date", "code")
            existing_keys = existing_df.select("date", "code")
            merged = new_keys.join(existing_keys, on=["date", "code"], how="inner")
            if merged.shape[0] > 0:
                if overwrite:
                    # Remove existing rows that match new (date, code) pairs
                    existing_df = existing_df.join(
                        merged, on=["date", "code"], how="anti"
                    )
                else:
                    # Remove new rows that already exist
                    df = df.join(merged, on=["date", "code"], how="anti")
            combined_df = pl.concat([existing_df, df])
            combined_df.write_parquet(self.filename)
        except FileNotFoundError:
            self.save(df)

    def read_full(self) -> Optional[pl.LazyFrame]:
        """Returns a LazyFrame for the full parquet dataset."""
        try:
            return pl.scan_parquet(self.filename)
        except FileNotFoundError:
            logger.error("Parquet file not found.")
            return None
        except Exception as e:
            logger.error(f"Error reading Parquet file: {e}")
            return None


class MarketDataFetcher:
    """Fetches market data from Shioaji API. Use as a context manager."""

    def __init__(self, store: ParquetStore = None):
        self.store = store or ParquetStore()
        self.api = None

    def __enter__(self):
        self.api = sj.Shioaji()
        self.api.login(config.API_KEY, config.SECRET_KEY, fetch_contract=False)
        logger.info(f"Shioaji API logged in - {sj.__version__}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.api:
            self.api.logout()
            logger.info("Shioaji API logged out.")
        return False

    def get_daily_quote(
        self, query_date: dt.date = None
    ) -> Optional[pl.DataFrame]:
        if query_date is None:
            query_date = dt.date.today()
        try:
            return daily_quotes_to_df(self.api.daily_quotes(query_date))
        except Exception as e:
            logger.error(f"Error getting daily quote for {query_date}: {e}")
            return None

    def download_data_to_date(self) -> Optional[int]:
        """Download market data from last stored date to today.

        Returns the number of calendar days covered, or None if already up to date.
        """
        latest_date = self.store.get_latest_date()
        start_date = (
            latest_date + dt.timedelta(days=1)
            if latest_date
            else dt.date.today() - dt.timedelta(days=60)
        )
        end_date = dt.date.today()
        total_days = (end_date - start_date).days + 1
        if total_days <= 0:
            return None

        current_date = start_date
        while current_date <= end_date:
            progress = ((current_date - start_date).days + 1) / total_days * 100
            if current_date.weekday() not in [5, 6]:
                df = self.get_daily_quote(current_date)
                self.store.append(df, overwrite=True)
                records_today = df.shape[0] if df is not None else 0
                logger.info(
                    f"Downloading data for {current_date} "
                    f"({records_today} records): Progress {progress:.2f}%"
                )
            else:
                logger.info(
                    f"Skipping weekend {current_date} Progress {progress:.2f}%"
                )
            current_date += dt.timedelta(days=1)
        return total_days


if __name__ == "__main__":
    config.init_polars()

    store = ParquetStore()
    store.display_stats()

    with MarketDataFetcher(store) as fetcher:
        newdays = fetcher.download_data_to_date()
        if newdays:
            store.display_stats()
            logger.info(f"Downloaded {newdays} days of data.")

    lf = store.read_full()
    if lf is not None:
        logger.info(lf.collect().shape[0])
        logger.info(lf.head().collect())
        logger.info(lf.tail().collect())
