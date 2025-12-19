"""This module implements functions to store sqlite database of bible listing
"""
import sqlite3


def sqlite_store_bible(bible_data: dict, file_name: str):
    """Store the given file as json

    Args:
        data: The dictionary of data to store
        fileptr: The file to store at
    """
    with sqlite3.connect(file_name) as connection:
        cursor = connection.cursor()
        data_tag: dict[str, str] = bible_data['tags']
        cursor.execute(
            '''CREATE TABLE metadata(
                key TEXT PRIMARY KEY,
                value TEXT
            );'''
        )
        for item, value in data_tag.items():
            cursor.execute('INSERT INTO metadata VALUES(?, ?)', (item, value))
        connection.commit()
        data_index: dict[int, str] = bible_data['index']
        cursor.execute(
            'CREATE TABLE book_index(book_id INT8 PRIMARY KEY, name TEXT);'
        )
        for item, value in data_index.items():
            cursor.execute(
                'INSERT INTO book_index VALUES(?, ?)', (item, value))
        connection.commit()
        cursor.execute(
            '''CREATE TABLE content(
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
                        "INSERT INTO content VALUES(?, ?, ?, ?);",
                        (book_id, chapter_id, verse_id, verse_content),
                    )
        connection.commit()
