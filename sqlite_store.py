"""This module implements functions to store sqlite database of bible listing
"""
import sqlite3


def sqlite_store_bible(bible_data: dict, file_name: str, save_tags:bool=False):
    """Store the given file as json

    Args:
        data: The dictionary of data to store
        fileptr: The file to store at
    """
    TABLE_TAGS = 'TAGS'
    TABLE_BOOK = 'BOOK'
    TABLE_DATA = 'DATA'

    with sqlite3.connect(file_name) as connection:
        cursor = connection.cursor()
        if save_tags:
            data_tag: dict[str, str] = bible_data['tags']
            cursor.execute(
                f'''CREATE TABLE {TABLE_TAGS}(
                    key TEXT PRIMARY KEY,
                    value TEXT
                );'''
            )
            for item, value in data_tag.items():
                cursor.execute(f'INSERT INTO {TABLE_TAGS} VALUES(?, ?)', (item, value))
            connection.commit()
        data_index: dict[int, str] = bible_data['index']
        cursor.execute(
            f'CREATE TABLE {TABLE_BOOK}(book_id INT8 PRIMARY KEY, name TEXT);'
        )
        for item, value in data_index.items():
            cursor.execute(
                f'INSERT INTO {TABLE_BOOK} VALUES(?, ?);', (item, value))
        connection.commit()
        cursor.execute(
            f'''CREATE TABLE {TABLE_DATA}(
                book_id INT8,
                chapter_id INT8,
                verse_id INT8,
                content TEXT
            );'''
        )
        for book_id in data_index.keys():
            book_dict: dict[int, dict[int, str]] = bible_data[book_id]
            for chapter_id, chapter_dict in book_dict.items():
                for verse_id, verse_content in chapter_dict.items():
                    cursor.execute(
                        f"INSERT INTO {TABLE_DATA} VALUES(?, ?, ?, ?);",
                        (book_id, chapter_id, verse_id, verse_content),
                    )
        connection.commit()
