from loguru import logger
import polars as pl


def add_natr(df: pl.DataFrame, timeperiod: int = 3) -> pl.DataFrame:
    import talib.abstract as ta

    df = pl.concat(
        [
            p_df.with_columns(ta.NATR(p_df, timeperiod=timeperiod).alias("natr"))
            for p_df in df.partition_by("code")
        ]
    )
    logger.info(df.with_columns(pl.col("natr").round(2)))
    return df.with_columns(pl.col("natr").round(2))


if __name__ == "__main__":
    from royabot.config import init_polars
    from royabot.fetcher import ParquetStore

    init_polars()

    store = ParquetStore()
    lf = store.read_full()
    df_clean = (
        lf.filter(pl.all_horizontal(pl.col(pl.Float32, pl.Float64).is_not_nan()))
        .drop_nulls()
        .collect()
    )
    df_with_natr = add_natr(df_clean)
    df_with_natr = df_with_natr.with_columns(pl.col("natr").round(2))
    print(df_with_natr)
