#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "pypdf",
# ]
# ///

"""Combine all PDFs in a folder into one PDF, ordered by filename."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def get_pdf_writer():
    try:
        from pypdf import PdfWriter

        return PdfWriter
    except ImportError:
        pass

    try:
        from PyPDF2 import PdfWriter

        return PdfWriter
    except ImportError:
        sys.exit(
            "Missing dependency. Install one of:\n"
            "  python -m pip install pypdf\n"
            "  python -m pip install PyPDF2"
        )


DEFAULT_OUTPUT_NAME = "combined.pdf"


def combine_pdfs(input_folder: Path, output_file: Path) -> None:
    if not input_folder.is_dir():
        sys.exit(f"Input folder does not exist: {input_folder}")

    output_file = output_file.resolve()

    pdf_files = sorted(
        (
            path
            for path in input_folder.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".pdf"
            and path.resolve() != output_file
        ),
        key=lambda path: path.name.lower(),
    )

    if not pdf_files:
        sys.exit(f"No PDF files found in: {input_folder}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    PdfWriter = get_pdf_writer()
    writer = PdfWriter()

    for pdf_file in pdf_files:
        writer.append(str(pdf_file))

    with output_file.open("wb") as output:
        writer.write(output)

    print(f"Combined {len(pdf_files)} PDFs into {output_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine all PDFs in a folder into one PDF, ordered by filename."
    )
    parser.add_argument(
        "input_folder",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Folder containing PDFs to combine. Defaults to the current directory.",
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        type=Path,
        help=f"Path for the combined PDF. Defaults to {DEFAULT_OUTPUT_NAME} in the input folder.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_file = args.output_file or args.input_folder / DEFAULT_OUTPUT_NAME
    combine_pdfs(args.input_folder, output_file)


if __name__ == "__main__":
    main()
