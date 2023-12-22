import polars as pl
from typing import Optional
from shioaji.data import DailyQuotes


def daily_quotes_to_df(daily_quote: Optional[DailyQuotes]) -> pl.DataFrame:
    df = pl.DataFrame(data={**daily_quote})
    df = df.rename({col: col.lower() for col in df.columns})
    return df
