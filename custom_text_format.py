def custom_text_format(bible_data: dict, file_name: str):
    with open(file_name, "w+", encoding="utf8") as file:
        tags: dict[str, str] = bible_data["tags"]
        index: dict[int, str] = bible_data["index"]
        len_chap = 0
        max_v_len = 0
        for book_id, book_name in index.items():
            book_map: dict[int, dict[int, str]] = bible_data[book_id]
            for chapter_map in book_map.values():
                len_chap += 1
                for verse_str in chapter_map.values():
                    max_v_len = max(max_v_len, len(verse_str))
        file.write(f"{len(tags)}\t{len(index)}\t{len_chap}\t{max_v_len}\n")
        for tag_key, tag_value in tags.items():
            file.write(f"{tag_key}\t{tag_value}\n")
        for book_id, book_name in index.items():
            book_map: dict[int, dict[int, str]] = bible_data[book_id]
            file.write(f"{book_id}\t{book_name}\t{len(book_map)}\n")
            for chapter_id, chapter_map in book_map.items():
                file.write(f"{chapter_id}\t{len(chapter_map)}\n")
                for verse_id, verse_str in chapter_map.items():
                    file.write(f"{verse_id}\t{verse_str}\n")
