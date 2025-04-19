import os
import json
from parse_bible import parse_noia_bible
from tqdm import tqdm

SOURCE_DIR = "AionianBible_DataFileStandard"
DEST_DIR = "aionian-json-listing"

WELCOME_MSG = "Welcome to Aionian to Json parsing software, brought to you by AzuxirenLeadGuy.      "

ERRMSG_DIR_NOT_FOUND = f"could not locate the needed directories! Ensure that this script is running from the git repository and the submodules are loaded correctly, or download the AionianBible_DataFileStandard manually, and ensure that the output folder '{DEST_DIR}' is also present"


if __name__ == "__main__":

    print(WELCOME_MSG)

    # Check for the presence of source and destination directories
    assert os.path.isdir(SOURCE_DIR) and os.path.isdir(DEST_DIR), ERRMSG_DIR_NOT_FOUND

    # Remove all existing json files from DEST_DIR
    for filename in os.listdir(DEST_DIR):
        if filename.endswith(".json") == False:
            continue
        os.remove(f"{DEST_DIR}/{filename}")

    # Prepare a list of source files
    source_list = [
        filename for filename in os.listdir(SOURCE_DIR) if filename.endswith(".noia")
    ]

    # A list of the available files in aionian-json-listing
    bible_listing = []

    for filename in tqdm(source_list):
        metadata, listing, content = parse_noia_bible(f"{SOURCE_DIR}/{filename}")
        data = {"metadata": metadata, "listing": listing, "content": content}

        filename = filename.replace(".noia", ".json")
        path = f"{DEST_DIR}/{filename}"

        with open(path, "w", encoding='utf8') as file:
            json.dump(data, file, ensure_ascii=False)

        bible_listing.append(
            {
                "filename": filename,
                "bible_name": metadata["Bible Name"],
                "language": metadata["Bible Language"],
                "language_en": metadata["Bible Language English"],
                "size": os.path.getsize(path),
            }
        )
    with open(f"{DEST_DIR}/bible_listing.json", 'w+', encoding='utf8') as file:
        json.dump(bible_listing, file, ensure_ascii=False)

    print("\nAll files have been writted successfully\n")
