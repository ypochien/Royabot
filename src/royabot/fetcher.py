from typing import Optional
import datetime as dt
from loguru import logger
import polars as pl
import shioaji as sj
from royabot import config

from royabot.util import daily_quotes_to_df

pl.Config.set_tbl_cols(-1)


class MarketDataFetcher:
    def __init__(self):
        logger.info(f"Shioaji API logged in - {sj.__version__}")
        self.parquet_filename = "daily_quotes.parquet"

    def get_daily_quote(
        self, query_date: dt.date = dt.date.today()
    ) -> Optional[pl.DataFrame]:
        try:
            return daily_quotes_to_df(self.api.daily_quotes(query_date))
        except Exception as e:
            logger.error(f"Error getting daily quote: {e}")
            return None

    def display_parquet_stats(self, filename: str):
        try:
            df = pl.read_parquet(filename)
            if df.shape[0] > 0:
                earliest_date = df.select(pl.min("date")).to_numpy()[0, 0]
                latest_date = df.select(pl.max("date")).to_numpy()[0, 0]
                total_records = df.shape[0]
                logger.info(
                    f"Parquet stats - Earliest date: {earliest_date}, Latest date: {latest_date}, Total records: {total_records}"
                )
            else:
                logger.info("Parquet file is empty.")
        except FileNotFoundError:
            logger.info("Parquet file not found.")

    def get_latest_date_from_parquet(self, filename: str) -> dt.date:
        try:
            df = pl.read_parquet(filename)
            if df.shape[0] > 0:
                latest_date_row = df.select(pl.max("date")).to_numpy()
                latest_date_str = (
                    latest_date_row[0, 0] if latest_date_row.size > 0 else None
                )
                if latest_date_str:
                    # 将字符串转换为 datetime.date 对象
                    latest_date = dt.datetime.strptime(
                        latest_date_str, "%Y-%m-%d"
                    ).date()
                    return latest_date
                else:
                    return None
            else:
                return None
        except FileNotFoundError:
            return None

    def download_data_to_date(self, filename: str) -> int:
        self.api = sj.Shioaji()
        self.api.login(config.API_KEY, config.SECRET_KEY, fetch_contract=False)
        latest_date = self.get_latest_date_from_parquet(filename)
        start_date = (
            latest_date + dt.timedelta(days=1)
            if latest_date
            else dt.date.today() - dt.timedelta(days=60)
        )
        end_date = dt.date.today()

        total_days = (end_date - start_date).days + 1
        current_date = start_date
        if total_days <= 0:
            return None

        while current_date <= end_date:
            progress = ((current_date - start_date).days + 1) / total_days * 100

            if current_date.weekday() not in [5, 6]:
                df = self.get_daily_quote(current_date)
                self.append_to_parquet(df, filename, overwrite=True)
                records_today = df.shape[0] if df is not None else 0

                logger.info(
                    f"Downloading data for {current_date} ({records_today} records): Progress {progress:.2f}%"
                )
            else:
                logger.info(f"Skipping weekend {current_date} Progress {progress:.2f}%")

            current_date += dt.timedelta(days=1)
        self.api.logout()
        return total_days

    def save_to_parquet(self, df: pl.DataFrame, filename: str):
        if df.shape[0] > 0:
            df.write_parquet(filename)

    def append_to_parquet(
        self, df: pl.DataFrame, filename: str, overwrite: bool = True
    ):
        if df is None:
            return
        if df.shape[0] > 0:  # 确保DataFrame不为空
            try:
                existing_df = pl.read_parquet(filename)

                new_dates = df["date"]
                existing_dates = existing_df["date"]

                duplicates = new_dates.is_in(existing_dates)

                if duplicates.sum() > 0:
                    if overwrite:
                        existing_df = existing_df.filter(
                            ~existing_df["date"].is_in(new_dates[duplicates])
                        )
                    else:
                        df = df.filter(~duplicates)

                combined_df = pl.concat([existing_df, df])
                combined_df.write_parquet(filename)

            except FileNotFoundError:
                self.save_to_parquet(df, filename)

    def get_full_dataframe(self, filename: str) -> Optional[pl.DataFrame]:
        try:
            return pl.scan_parquet(filename)
        # pl.read_parquet(filename)
        except FileNotFoundError:
            logger.error("Parquet file not found.")
            return None
        except Exception as e:
            logger.error(f"Error reading Parquet file: {e}")
            return None

    def logout(self):
        self.api.logout()


if __name__ == "__main__":
    logger.info(f"Shioaji API - {sj.__version__}")
    fetcher = MarketDataFetcher()
    filename = "daily_quotes.parquet"
    fetcher.display_parquet_stats(filename)
    newdays = fetcher.download_data_to_date(filename)
    if newdays:
        fetcher.display_parquet_stats(filename)
        logger.info(f"Downloaded {newdays} days of data.")

    df = fetcher.get_full_dataframe("daily_quotes.parquet")
    logger.info(df.collect().shape[0])
    logger.info(df.head().collect())
    logger.info(df.tail().collect())
    fetcher.logout()
