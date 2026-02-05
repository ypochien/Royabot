import polars as pl
from typing import Optional
from shioaji.data import DailyQuotes


def daily_quotes_to_df(daily_quote: Optional[DailyQuotes]) -> Optional[pl.DataFrame]:
    if daily_quote is None:
        return None
    # 使用 model_dump(mode='json') 確保所有日期都序列化為字串，避免警告
    data = daily_quote.model_dump(mode='json')
    df = pl.DataFrame(data=data)
    df = df.rename({col: col.lower() for col in df.columns})
    return df
