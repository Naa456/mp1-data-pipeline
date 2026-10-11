
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
        before, after
    )

    return df


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""

    if axis not in ("rows", "columns"):
        logger.error("Unsupported axis: %s", axis)
        raise ValueError(f"Unsupported axis: {axis}")

    if axis == "rows":
        before = len(df)
        df = df.dropna(axis=0)
        after = len(df)
    else:
        before = len(df.columns)
        df = df.dropna(axis=1)
        after = len(df.columns)

    logger.debug(
        "handle_missing: %d → %d %s",
        before, after, axis
    )

    return df


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from specified numeric columns."""

    if method not in ("iqr", "zscore"):
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    for column in columns:

        if column not in df.columns:
            logger.warning("Column not found: %s", column)
            continue

        if not pd.api.types.is_numeric_dtype(df[column]):
            logger.warning("Column is not numeric: %s", column)
            continue

        before = len(df)

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

            logger.debug(
                "%s: lower=%s, upper=%s, removed=%d, method=%s, threshold=%s",
                column, lower, upper, before - len(df),
                method, threshold
            )

        elif method == "zscore":
            mean = df[column].mean()
            std = df[column].std()

            if pd.isna(std) or std == 0:
                logger.debug(
                    "%s: removed=0, method=%s, threshold=%s",
                    column, method, threshold
                )
                continue

            zscores = (df[column] - mean).abs() / std

            df = df[zscores <= threshold]

            logger.debug(
                "%s: removed=%d, method=%s, threshold=%s",
                column, before - len(df), method, threshold
            )

    return df


def process_data(df, config):
    """Apply processing steps enabled in the configuration."""

    processing = config["processing"]

    if processing["remove_duplicates"]:
        df = remove_duplicates(df)

    if processing["missing"]["enabled"]:
        axis = processing["missing"]["axis"]
        df = handle_missing(df, axis)

    if processing["outliers"]["enabled"]:
        outlier_config = processing["outliers"]

        df = remove_outliers(
            df,
            outlier_config["columns"],
            outlier_config["method"],
            outlier_config["threshold"]
        )

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""

    rows_before = len(df_before)
    rows_after = len(df_after)

    columns_before = len(df_before.columns)
    columns_after = len(df_after.columns)

    report = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after
    }

    return report
