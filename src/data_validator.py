import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data."""

    df = df.copy()
    before = len(df)

    for col in required_columns:
        if col not in df.columns:
            logger.error("Required column missing: %s", col)
            raise ValueError(f"Required column missing: {col}")

    for col in numeric_columns:
        if col not in df.columns:
            logger.error("Numeric column missing: %s", col)
            raise ValueError(f"Numeric column missing: {col}")

        invalid_rows = []

        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except (ValueError, TypeError):
                    invalid_rows.append(i)

        if invalid_rows:
            logger.warning(
                "Removed %d rows with invalid numeric values in %s",
                len(invalid_rows),
                col
            )
            df = df.drop(index=invalid_rows)

        df[col] = pd.to_numeric(df[col])

    logger.debug(
        "Validation: %d -> %d rows",
        before,
        len(df)
    )

    return df
