"""
This module contains functions to write the bible data as a text file
"""

def tsv_store_bible(bible_data: dict, file_name: str):
    """
    Writes a tsv file of bible content. The tsv contains 2 columns, namely
    `verseid_len`, 'content'.
    The first column is an integer values in hex taking exactly 10 hex digits.
    There are two types of rows: Book-Header, and Verse-Content
    - For a Book-Header row, the first column contains the IDs, and the second column contains the book name.
        - The digits [0-2) represent the book_id of a verse. 
        - The digits [2-4) represent the total number of chapters for the book.
        - The digits [4-8) represent the total number of verses for the book.
        - The digits [9-10) represent the utf-8 length of the book name, given in the second column.
    - For a Verse-Content row, the first column contains the IDs, provided in the second column contains the verse content.
        - The digits [0-2) represent the book_id of a verse. 
        - The digits [2-4) represent the chapter_id of a verse.
        - The digits [4-6) represent the verse_id of a verse.
        - The digits [6-10) represent the utf-8 length of a verse, provided in the second column of the row.

    Args:
        bible_data (dict): The data to store
        file_name (str): The file to write
    """
    def gethex(value:int, digits:int)->str:
        str_val = hex(value)[2:]
        assert digits >= len(str_val)
        return str_val.rjust(digits, '0')
    def strlenval_joined(string:str, max_len:int)->str:
        strlen = len(string.encode('utf-8'))
        return f"{gethex(strlen, max_len)}\t{string}"
    with open(file_name, 'w+', encoding='utf-8') as file:
        index_table:dict[int, str] = bible_data['index']
        for book_id, book_name in index_table.items():
            assert book_id < 128, 'bible cannot have a book with book_id >= 128'
            chap_map :dict[int, dict[int, str]] = bible_data[book_id]
            total_chapters = len(chap_map)
            assert total_chapters < 256, "bible cannot have a book with chapters >= 256"
            total_verses = sum([len(verse_map) for verse_map in chap_map.values()])
            assert total_verses < 0xffff, "bible cannot have a book with total combined verses >= 2**16"
            book_hex = gethex(book_id, 2)
            chap_total = gethex(total_chapters, 2)
            verse_total = gethex(total_verses, 4)
            file.write(f"{book_hex}{chap_total}{verse_total}{strlenval_joined(book_name, 2)}\n")
            for chap_id, chap_content in chap_map.items():
                chap_hex = gethex(chap_id, 2)
                for verse_id, verse_content in chap_content.items():
                    content_pair = strlenval_joined(verse_content, 4)
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
        file.writelines(f"'{tag_id}'='{tag_value}'\n" for tag_id, tag_value in tags.items())
        file.write("[index]\n")
        file.writelines(f"{book_id}='{book_name}'\n" for book_id, book_name in index.items())
        for book_id in index:
            chap_map:dict[int, dict[int, str]] = bible_data[book_id]
            for chap_id, chap_content in chap_map.items():
                file.write(f'[{book_id}.{chap_id}]\n')
                file.writelines(f'{verse_id}="{verse_str}"\n' for verse_id, verse_str in chap_content.items())

