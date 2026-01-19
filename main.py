"""
The main function that prepares a listing for each noia file
"""
import os
import json
import argparse
from tqdm import tqdm

from parse_bible import parse_noia_bible
from custom_text_format import custom_text_format
from sqlite_store import sqlite_store_bible
from tsv_tar_store import tsv_tar_store_bible

SOURCE_DIR_DEFAULT = "AionianBible_DataFileStandard"
DEST_DIR_DEFAULT = "aionian-json-listing"

WELCOME_MSG = "Welcome to Aionian to Json parsing software by AzuxirenLeadGuy."

ERRMSG_DIR_NOT_FOUND = """
could not locate the needed directories!
Ensure that this script is running from
the git repository and the submodules
are loaded correctly, or download the
AionianBible_DataFileStandard manually
to set up the input folder correctly."""


class BibleListingItem:
    """Represents a single item of listing"""
    filename: str
    bible_name: str
    bible_name_en: str
    language: str
    language_en: str
    size: int

    def __init__(
        self,
        filename: str,
        bible_name_en: str,
        bible_name: str,
        language_en: str,
        language: str,
        size: int,
    ) -> None:
        """
        Initializes a listing item

        Args:
            filename (str): The file name of the listing file
            bible_name_en (str): The title of the listing file in english
            bible_name (str): The title of the listing file
            language_en (str): The language of the listing file in english
            language (str): The language of the listing file
            size (int): The size of the listing file in bytes
        """
        self.filename = filename
        self.bible_name_en = bible_name_en
        self.bible_name = bible_name
        self.language_en = language_en
        self.language = language
        self.size = size

    def tsv_line(self) -> str:
        """
        Returns a tab-separated line to write in the listing tsv file
        """
        line = f'{self.filename}\t{self.bible_name_en}\t{self.bible_name}'
        line += f'\t{self.language_en}\t{self.language}\t{self.size}\n'
        return line


if __name__ == "__main__":

    def cli_args() -> argparse.Namespace:
        """Prepares the parser for command line arguments for the function

        Returns:
            argparse.Namespace: The parsed command line arguments
        """
        parser = argparse.ArgumentParser(prog="aionian-listing-creator")
        parser.add_argument(
            "--input",
            "-i",
            type=str,
            default=SOURCE_DIR_DEFAULT,
            help="The source directory where all *.noia files are kept",
        )
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            default=DEST_DIR_DEFAULT,
            help="The output directory where all generated files are written.",
        )
        parser.add_argument(
            "--format",
            "-f",
            type=str,
            choices=["json", "sqlite", "tar", "txt"],
            default="json",
            help="The output format of the files to store",
        )
        return parser.parse_args()

    def store_json(data, file_name):
        """Store the given file as json

        Args:
            data: The dictionary of data to store
            fileptr: The file to store at
        """
        with open(file_name, "w+", encoding="utf8") as file:
            json.dump(data, file, indent=1, ensure_ascii=False)

    print(WELCOME_MSG)

    args = cli_args()
    source = args.input
    extn = args.format
    dest = f"{args.output}/{extn}"
    store_fn = store_json
    if extn == "tar":
        store_fn = tsv_tar_store_bible
    elif extn == "sqlite":
        store_fn = sqlite_store_bible
    elif extn == "txt":
        store_fn = custom_text_format
    os.makedirs(dest, exist_ok=True)

    # Check for the presence of source and destination directories
    assert os.path.isdir(source) and os.path.isdir(dest), ERRMSG_DIR_NOT_FOUND

    # Prepare a list of source files
    source_list = [
        name for name in os.listdir(source) if name.endswith(".noia")
    ]

    # A list of the available files in aionian-json-listing
    bible_listing: list[BibleListingItem] = []
    size_ratios = {}

    for filename in tqdm(source_list):
        FILE_PATH = f"{source}/{filename}"
        metadata, index, content = parse_noia_bible(FILE_PATH)
        fulldata = {"tags": metadata, "index": index} | content
        size_source = os.path.getsize(FILE_PATH)

        filename = filename.replace(".noia", f".{extn}")
        FILE_PATH = f"{dest}/{filename}"

        store_fn(fulldata, FILE_PATH)

        size_dest = os.path.getsize(FILE_PATH)
        bible_listing.append(
            BibleListingItem(
                filename=filename,
                bible_name_en=metadata['Bible Name English'],
                bible_name=metadata['Bible Name'],
                language_en=metadata['Bible Language English'],
                language=metadata['Bible Language'],
                size=size_dest,
            )
        )
        size_ratios[filename] = (
            size_source,
            size_dest,
            (size_source - size_dest) / (size_source * 1.0),
        )
    bible_listing.sort(key=lambda x: x.filename)
    ls_name = f'{dest}/{extn}_listing.tsv'
    with open(ls_name, 'w+', encoding='utf8') as listing_file:
        for item in bible_listing:
            listing_file.write(item.tsv_line())

    print("\nAll files have been writted successfully\n")
    for filename, ratio in size_ratios.items():
        ss, sd, sr = ratio
        LINE = f"noia size: {ss} \t{extn} file size: {sd} \t"
        LINE += f"Reduction: {(100 * sr):.3F} %\t| File: {filename}"
        print(LINE)
