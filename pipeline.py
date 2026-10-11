
"""
Data Processing Pipeline - DS3500 MP1 Part 4

Usage:
python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml --verbose
"""

import argparse
import logging
import sys

from src import (
    create_cleaning_report,
    load_data,
    process_data,
    save_data,
    setup_logging,
    validate_dataframe,
    validate_input,
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Validate, clean, and save an input dataset."
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to the input CSV file"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to the YAML configuration file"
    )

    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to the output CSV file"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable detailed logging"
    )

    return parser.parse_args()


def main():
    """Run the complete data processing pipeline."""

    args = parse_arguments()

    setup_logging(args.verbose)

    logger.debug(
        "Arguments parsed: input=%s, output=%s, config=%s",
        args.input,
        args.output,
        args.config
    )

    if not validate_input(args.input):
        sys.exit(1)

    if not validate_input(args.config):
        sys.exit(1)

    try:
        data = load_data(args.input)
        config = load_data(args.config)

    except ValueError as error:
        logger.error("Loading failed: %s", error)
        sys.exit(1)

    validation_settings = config["validation"]

    required_columns = validation_settings["required_columns"]
    numeric_columns = validation_settings["numeric_columns"]

    original_rows = len(data)

    try:
        validated_data = validate_dataframe(
            data,
            required_columns,
            numeric_columns
        )

    except ValueError as error:
        logger.error("Validation failed: %s", error)
        sys.exit(1)

    logger.info(
        "Validation complete: %d -> %d rows",
        original_rows,
        len(validated_data)
    )

    original_data = validated_data.copy()

    try:
        cleaned_data = process_data(
            validated_data,
            config
        )

    except ValueError as error:
        logger.error("Processing failed: %s", error)
        sys.exit(1)

    report = create_cleaning_report(
        original_data,
        cleaned_data
    )

    logger.info(
        "Processing complete: %d -> %d rows",
        len(original_data),
        len(cleaned_data)
    )

    output_path = save_data(
        cleaned_data,
        args.output
    )

    logger.info(
        "Saved cleaned data to %s",
        output_path
    )

    print("\nCleaning report:")
    print(report)


if __name__ == "__main__":
    main()
