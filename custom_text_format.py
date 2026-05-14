"""
This module contains functions to write the bible data as a text file
"""

def tsv_store_bible(bible_data: dict, file_name: str):
    """
    Writes a tsv file of bible content. The tsv contains 2 columns, namely
    `verseid_len`, 'content'.
    The first column is an integer values in hex taking exactly 10 hex digits.
    The digits [0-2) represent the book_id of a verse. 
    The digits [2-4) represent the chapter_id of a verse.
    The digits [4-6) represent the verse_id of a verse.
    The digits [6-10) represent the utf-8 length of a verse.
    The second column is the utf-8 encoded string, representing the verse.
    All bibles stored as tsv has a special/meta row for each book:
    Chapter 0, Verse 0 of a book contains the (regional, utf-8) name of the book

    Args:
        bible_data (dict): The data to store
        file_name (str): The file to write
    """
    def gethex(value:int, digits:int)->str:
        str_val = hex(value)[2:]
        assert digits >= len(str_val)
        return str_val.rjust(digits, '0')
    def strlenval_joined(string:str)->str:
        strlen = len(string.encode('utf-8'))
        return f"{gethex(strlen, 4)}\t{string}"
    with open(file_name, 'w+', encoding='utf-8') as file:
        index_table:dict[int, str] = bible_data['index']
        for book_id, book_name in index_table.items():
            chap_map :dict[int, dict[int, str]] = bible_data[book_id]
            assert (0 not in chap_map) or (0 not in chap_map[0]), 'bible cannot have a book with chapter:verse=0:0'
            book_hex = gethex(book_id, 2)
            file.write(f"{book_hex}0000{strlenval_joined(book_name)}\n")
            for chap_id, chap_content in chap_map.items():
                chap_hex = gethex(chap_id, 2)
                for verse_id, verse_content in chap_content.items():
                    content_pair = strlenval_joined(verse_content)
                    verse_hex = gethex(verse_id, 2)
                    file.write(f"{book_hex}{chap_hex}{verse_hex}{content_pair}\n")



def custom_toml_format(bible_data: dict, file_name: str):
    """
    Custom function to efficiently store bible data as toml file

    Args:
        bible_data (dict): The data to store
        file_name (str): The file to write
    """
    with open(file_name, "w+", encoding="utf8") as file:
        tags: dict[str, str] = bible_data["tags"]
        index: dict[int, str] = bible_data["index"]
        file.write("[tags]\n")
        for tag_id, tag_value in tags.items():
            file.write(f"'{tag_id}'='{tag_value}'\n")
        file.write("[index]\n")
        for book_id, book_name in index.items():
            file.write(f"{book_id}='{book_name}'\n")
        for book_id in index.keys():
            chap_map:dict[int, dict[int, str]] = bible_data[book_id]
            for chap_id, chap_content in chap_map.items():
                file.write(f'[{book_id}.{chap_id}]\n')
                for verse_id, verse_str in chap_content.items():
                    file.write(f'{verse_id}="{verse_str}"\n')

