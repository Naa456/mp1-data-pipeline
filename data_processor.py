import logging
import pandas as pd

logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    logger.debug(
        "remove_duplicates: %d → %d rows",
        before,
        after
    )

    return df


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""

    if axis == "rows":
        before = len(df)
        df = df.dropna()
        after = len(df)

        logger.debug(
            "handle_missing: %d → %d rows",
            before,
            after
        )

    elif axis == "columns":
        before = len(df.columns)
        df = df.dropna(axis=1)
        after = len(df.columns)

        logger.debug(
            "handle_missing: %d → %d columns",
            before,
            after
        )

    else:
        logger.error("Unsupported axis: %s", axis)
        raise ValueError(f"Unsupported axis: {axis}")

    return df


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""

    if method not in ["iqr", "zscore"]:
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    before = len(df)

    for column in columns:

        if column not in df.columns:
            logger.warning("Column not found: %s", column)
            continue

        if not pd.api.types.is_numeric_dtype(df[column]):
            logger.warning("Column is not numeric: %s", column)
            continue

        if method == "iqr":
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr

            df = df[
                (df[column] >= lower) &
                (df[column] <= upper)
            ]

        elif method == "zscore":
            mean = df[column].mean()
            std = df[column].std()

            if std == 0:
                continue

            z_scores = (df[column] - mean) / std

            df = df[z_scores.abs() <= threshold]

    after = len(df)

    logger.debug(
        "remove_outliers: method=%s threshold=%s removed=%d",
        method,
        threshold,
        before - after
    )

    return df

def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""

    processing = config["processing"]

    if processing["remove_duplicates"]:
        df = remove_duplicates(df)

    if processing["missing"]["enabled"]:
        df = handle_missing(
            df,
            axis=processing["missing"]["axis"]
        )

    if processing["outliers"]["enabled"]:
        df = remove_outliers(
            df,
            columns=processing["outliers"]["columns"],
            method=processing["outliers"]["method"],
            threshold=processing["outliers"]["threshold"]
        )

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""

    report = {
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "rows_removed": len(df_before) - len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "columns_removed": len(df_before.columns) - len(df_after.columns)
    }

    return report