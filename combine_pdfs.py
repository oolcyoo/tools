import argparse
import os

from PyPDF2 import PdfMerger


def combine_pdfs_in_directory(directory_path, output_filename):
    merger = PdfMerger()
    pdf_files = sorted(
        filename for filename in os.listdir(directory_path) if filename.lower().endswith(".pdf")
    )

    for filename in pdf_files:
        pdf_path = os.path.join(directory_path, filename)
        merger.append(pdf_path)

    with open(output_filename, "wb") as output_file:
        merger.write(output_file)


def parse_args():
    parser = argparse.ArgumentParser(description="Combine all PDFs in a directory into one file.")
    parser.add_argument("directory", help="Directory containing PDF files to combine.")
    parser.add_argument(
        "-o",
        "--output",
        default="combined.pdf",
        help="Output PDF filename. Defaults to combined.pdf.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    combine_pdfs_in_directory(args.directory, args.output)
    print(f"PDFs combined into '{args.output}' successfully.")


if __name__ == "__main__":
    main()
