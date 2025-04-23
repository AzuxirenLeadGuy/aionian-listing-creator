import os
import json
from parse_bible import parse_noia_bible
from tqdm import tqdm
import argparse
import yaml

SOURCE_DIR_DEFAULT = "AionianBible_DataFileStandard"
DEST_DIR_DEFAULT = "aionian-json-listing"

WELCOME_MSG = "Welcome to Aionian to Json parsing software, brought to you by AzuxirenLeadGuy.      "

ERRMSG_DIR_NOT_FOUND = f"could not locate the needed directories! Ensure that this script is running from the git repository and the submodules are loaded correctly, or download the AionianBible_DataFileStandard manually to set up the input folder correctly."

if __name__ == "__main__":

    def cli_args() -> argparse.Namespace:
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
            help="The output directory where all generated json files are to be saved.",
        )
        parser.add_argument(
            "--format",
            "-f",
            type=str,
            choices=["yaml", "json"],
            default="json",
            help="The output format of the files to store",
        )
        return parser.parse_args()
    
    def store_json(data, fileptr):
        json.dump(data, fileptr, indent=1, ensure_ascii=False)
    
    def store_yaml(data, fileptr):
        yaml.dump(data, fileptr, indent=1, allow_unicode=True, width=50000)
    
    def file_store(path:str, data, func):
        with open(path, 'w+', encoding="utf8") as file:
            func(data, file)

    print(WELCOME_MSG)

    args = cli_args()
    source = args.input
    dest = args.output
    extn = args.format
    store_fn = store_json if extn == 'json' else store_yaml
    os.makedirs(dest, exist_ok=True)

    # Check for the presence of source and destination directories
    assert os.path.isdir(source) and os.path.isdir(dest), ERRMSG_DIR_NOT_FOUND

    # Prepare a list of source files
    source_list = [
        filename for filename in os.listdir(source) if filename.endswith(".noia")
    ]

    # A list of the available files in aionian-json-listing
    bible_listing = []
    size_ratios = {}

    for filename in tqdm(source_list):
        path = f"{source}/{filename}"
        metadata, listing, content = parse_noia_bible(path)
        data = {"tags": metadata, "index": listing} | content
        size_source = os.path.getsize(path)

        filename = filename.replace(".noia", f".{extn}")
        path = f"{dest}/{filename}"

        file_store(path, data, store_fn)

        size_dest = os.path.getsize(path)
        bible_listing.append(
            {
                "filename": filename,
                "bible_name": metadata["Bible Name"],
                "language": metadata["Bible Language"],
                "language_en": metadata["Bible Language English"],
                "size": size_dest,
            }
        )
        size_ratios[filename] = (
            size_source,
            size_dest,
            (size_source - size_dest) / (size_source * 1.0),
        )
    file_store(f"{dest}/bible_listing.{extn}", bible_listing, store_fn)

    print("\nAll files have been writted successfully\n")
    for filename in size_ratios:
        ss, sd, sr = size_ratios[filename]
        print(
            f"noia size: {ss} \t{extn} file size: {sd} \tReduction: {(100 * sr):.3F} %\t| File: {filename}"
        )
