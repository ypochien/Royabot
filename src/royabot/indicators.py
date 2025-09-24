from loguru import logger
import talib.abstract as ta
from royabot.fetcher import MarketDataFetcher
import polars as pl

pl.Config.set_tbl_cols(-1)


def add_natr(df: pl.DataFrame, timeperiod: int = 3) -> pl.DataFrame:
    df = pl.concat(
        [
            p_df.with_columns(ta.NATR(p_df, timeperiod=timeperiod).alias("natr"))
            for p_df in df.partition_by("code")
        ]
    )
    logger.info(df.with_columns(pl.col("natr").round(2)))
    return df.with_columns(pl.col("natr").round(2))


if __name__ == "__main__":
    fetcher = MarketDataFetcher()
    df = fetcher.get_full_dataframe("daily_quotes.parquet")
    df_clean = (
        df.filter(pl.all_horizontal(pl.col(pl.Float32, pl.Float64).is_not_nan()))
        .drop_nulls()
        .collect()
    )
    df_with_natr = add_natr(df_clean)
    df_with_natr = df_with_natr.with_columns(pl.col("natr").round(2))

    print(df_with_natr)
