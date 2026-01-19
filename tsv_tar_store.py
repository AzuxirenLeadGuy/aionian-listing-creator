"""
This module implements to store the bible database as
a tar of csv files
"""
import tarfile
import io

# TODO: Change this file to tsv


def tsv_tar_store_bible(bible_data: dict, file_name: str):
    """
    Writes a tar file with the encoded csv files

    Args:
        bible_data (dict): The data to store
        file_name (str): The file to write
    """
    with tarfile.open(file_name, mode='x') as file:
        def write_rows_to_csv_buffer(
            file_name: str,
            rows: list[list],
        ):
            with io.BytesIO() as buffer:
                for row in rows:
                    row_str = '\t'.join([str(val) for val in row]) + '\n'
                    buffer.write(row_str.encode('utf-8'))
                info = tarfile.TarInfo(file_name)
                info.size = buffer.tell()
                buffer.seek(0)
                file.addfile(
                    info,
                    fileobj=buffer,
                )
        csv_rows = [[tag, value] for tag, value in bible_data['tags'].items()]
        write_rows_to_csv_buffer('tags.tsv', csv_rows)
        index: dict[int, str] = bible_data['index']
        csv_rows = [[book_id, name] for book_id, name in list(index.items())]
        write_rows_to_csv_buffer('index.tsv', csv_rows)
        for book_id in index.keys():
            chapter_dict: dict[int, dict[int, str]] = bible_data[book_id]
            csv_rows = []
            for chapter_id, chapter_content in chapter_dict.items():
                csv_rows += [
                    [chapter_id, verse_id, verse]
                    for verse_id, verse in chapter_content.items()
                ]
            write_rows_to_csv_buffer(f'{book_id}.tsv', csv_rows)
        file.close()
