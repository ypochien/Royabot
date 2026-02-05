from loguru import logger
import polars as pl

from royabot.fetcher import MarketDataFetcher, ParquetStore
from royabot.indicators import add_natr


def fetch_and_update_data(store: ParquetStore) -> None:
    """Download new market data from Shioaji API into the parquet store."""
    store.display_stats()
    with MarketDataFetcher(store) as fetcher:
        newdays = fetcher.download_data_to_date()
        if newdays:
            store.display_stats()
            logger.info(f"Downloaded {newdays} days of data.")


def load_and_clean_data(store: ParquetStore) -> tuple[pl.DataFrame, str]:
    """Load full dataset from parquet, clean NaN/null rows.

    Returns:
        Tuple of (cleaned DataFrame, latest_date string).

    Raises:
        FileNotFoundError: If parquet file does not exist.
    """
    lf = store.read_full()
    if lf is None:
        raise FileNotFoundError(f"Parquet file not found: {store.filename}")
    latest_date = lf.select(pl.max("date")).collect().item()
    lf = lf.with_columns(pl.col("code").cast(str))
    df_clean = (
        lf.filter(pl.all_horizontal(pl.col(pl.Float32, pl.Float64).is_not_nan()))
        .drop_nulls()
        .collect()
    )
    return df_clean, latest_date


def get_latest_date_data(df: pl.DataFrame) -> pl.DataFrame:
    """Filter DataFrame to rows matching the most recent date."""
    return df.filter(pl.col("date") == pl.col("date").max())


def merge_with_stock_codes(
    df_market: pl.DataFrame, input_xls_path: str
) -> pl.DataFrame:
    """Read user's Excel stock code list and join with market data."""
    logger.info(f"Reading stock codes from: {input_xls_path}")
    df_code = pl.read_excel(
        input_xls_path, read_options={"infer_schema_length": 10000}
    )
    df_code = df_code.with_columns(pl.col(df_code.columns[0]).cast(str))
    return df_code.join(
        df_market,
        left_on=df_code.columns[0],
        right_on="code",
        how="left",
    )


def process_stock_data(input_xls_path: str, output_xls_path: str) -> str:
    """Main orchestration: fetch data, compute indicators, merge with user codes, write output.

    Args:
        input_xls_path: Path to user's Excel file with stock codes.
        output_xls_path: Path to write the enriched output Excel.

    Returns:
        The latest date string from the market data.
    """
    store = ParquetStore()

    # Step 1: Fetch and update market data
    fetch_and_update_data(store)

    # Step 2: Load and clean data
    df_clean, latest_date = load_and_clean_data(store)

    # Step 3: Compute indicators
    df_with_indicators = add_natr(df_clean)

    # Step 4: Filter to latest date
    df_latest = get_latest_date_data(df_with_indicators)

    # Step 5: Merge with user stock codes and write output
    df_result = merge_with_stock_codes(df_latest, input_xls_path)
    df_result.write_excel(output_xls_path)

    return latest_date


if __name__ == "__main__":
    from royabot.config import init_polars

    init_polars()

    input_xls_path = "1222.xlsx"
    output_xls_path = "1222_out.xlsx"
    process_stock_data(input_xls_path, output_xls_path)
