"""
Data Processing Pipeline - CLI Template

DS 3500 - MP1

Usage:
    python pipeline.py --input data.csv --output clean.csv --config config.yaml
    python pipeline.py --input data.csv --output clean.csv --config config.yaml --verbose
"""

import argparse
import logging
import sys
from pathlib import Path

from data_loaders import load_data
from data_processor import process_data, create_cleaning_report


logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    """Configure logging for the pipeline."""

    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
    )


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Process an input file and save the results."
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to the input file"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file"
    )

    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to the output file"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def validate_input(filepath):
    """Check whether the input path exists and is a file."""

    path = Path(filepath)

    if path.is_file():
        logger.info("Input file validated: %s", filepath)
        return True

    logger.error("Input file not found: %s", filepath)
    return False


def main():
    """Main pipeline function."""

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

    except ValueError:
        sys.exit(1)

    original_data = data.copy()

    try:
        cleaned_data = process_data(data, config)

    except ValueError:
        sys.exit(1)

    report = create_cleaning_report(
        original_data,
        cleaned_data
    )

    print(report)

    logger.info(
        "Processing complete: %d → %d rows",
        len(original_data),
        len(cleaned_data)
    )

    cleaned_data.to_csv(
        args.output,
        index=False
    )

    logger.info(
        "Saved cleaned data to %s",
        args.output
    )


if __name__ == "__main__":
    main()