from loguru import logger
import polars as pl
from royabot.fetcher import MarketDataFetcher
from royabot.indicators import add_natr


def process_stock_data(input_xls_path, output_xls_path):
    pl.Config.set_tbl_cols(-1)
    fetcher = MarketDataFetcher()
    filename = "daily_quotes.parquet"
    fetcher.display_parquet_stats(filename)
    newdays = fetcher.download_data_to_date(filename)
    if newdays:
        fetcher.display_parquet_stats(filename)
        logger.info(f"Downloaded {newdays} days of data.")
    df = fetcher.get_full_dataframe("./daily_quotes.parquet")
    latest_date = df.select(pl.max("date")).collect().to_numpy()[0, 0]
    df = df.with_columns(pl.col("code").cast(str))
    df_clean = (
        df.filter(pl.all_horizontal(pl.col(pl.Float32, pl.Float64).is_not_nan()))
        .drop_nulls()
        .collect()
    )
    df = add_natr(df_clean)
    df_tail = df.filter(pl.col("date") == pl.col("date").max())
    logger.info(input_xls_path)
    df_code = pl.read_excel(
        input_xls_path, read_csv_options={"infer_schema_length": 10000}
    )
    df_code = df_code.with_columns(pl.col(df_code.columns[0]).cast(str))
    df = df_code.join(
        df_tail,
        left_on=df_code.columns[0],
        right_on="code",
        how="left",
    )
    df.to_pandas().to_excel(output_xls_path, index=False)
    return latest_date


if __name__ == "__main__":
    input_xls_path = "1222.xlsx"
    output_xls_path = "1222_out.xlsx"
    process_stock_data(input_xls_path, output_xls_path)
