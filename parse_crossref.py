"""
This module contains functions to parse the read and filter cross-references
from the Open Bible Cross-References database file.
"""

from typing import NamedTuple


class Verse(NamedTuple):
    book: int = 0
    chap: int = 0
    verse: int = 0


def parse_verse(value: str) -> Verse:
    book_map: dict[str, int] = {
        "Gen": 1,
        "Exod": 2,
        "Lev": 3,
        "Num": 4,
        "Deut": 5,
        "Josh": 6,
        "Judg": 7,
        "Ruth": 8,
        "1Sam": 9,
        "2Sam": 10,
        "1Kgs": 11,
        "2Kgs": 12,
        "1Chr": 13,
        "2Chr": 14,
        "Ezra": 15,
        "Neh": 16,
        "Esth": 17,
        "Job": 18,
        "Ps": 19,
        "Prov": 20,
        "Eccl": 21,
        "Song": 22,
        "Isa": 23,
        "Jer": 24,
        "Lam": 25,
        "Ezek": 26,
        "Dan": 27,
        "Hos": 28,
        "Joel": 29,
        "Amos": 30,
        "Obad": 31,
        "Jonah": 32,
        "Mic": 33,
        "Nah": 34,
        "Hab": 35,
        "Zeph": 36,
        "Hag": 37,
        "Zech": 38,
        "Mal": 39,
        "Matt": 40,
        "Mark": 41,
        "Luke": 42,
        "John": 43,
        "Acts": 44,
        "Rom": 45,
        "1Cor": 46,
        "2Cor": 47,
        "Gal": 48,
        "Eph": 49,
        "Phil": 50,
        "Col": 51,
        "1Thess": 52,
        "2Thess": 53,
        "1Tim": 54,
        "2Tim": 55,
        "Titus": 56,
        "Phlm": 57,
        "Heb": 58,
        "Jas": 59,
        "1Pet": 60,
        "2Pet": 61,
        "1John": 62,
        "2John": 63,
        "3John": 64,
        "Jude": 65,
        "Rev": 66,
    }
    assert value.count(".") == 2
    [book_key, chapstr, versestr] = value.split(".")
    assert book_key in book_map
    return Verse(
        book=book_map[book_key],
        chap=int(chapstr),
        verse=int(versestr),
    )


class RefernceToVerse(NamedTuple):
    source: Verse = Verse()
    dest_start: Verse = Verse()
    dest_end: Verse | None = None
    votes: int = 0


def ReadDatabase(path: str, min_votes: int):
    max_voted_verse = RefernceToVerse(Verse(), votes=100000)
    with open(path) as file:
        for readline in file:
            line = readline.strip()
            if len(line) == 0:
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            result: RefernceToVerse
            [source_str, dest_str, votes_str] = parts
            assert source_str.count(".") == 2
            source_verse = parse_verse(source_str)
            if "-" not in dest_str:
                result = RefernceToVerse(
                    source=source_verse,
                    dest_start=parse_verse(dest_str),
                    dest_end=None,
                    votes=int(votes_str),
                )
            else:
                dest_parts = dest_str.split("-")
                assert len(dest_parts) == 2
                result = RefernceToVerse(
                    source=source_verse,
                    dest_start=parse_verse(dest_parts[0]),
                    dest_end=parse_verse(dest_parts[1]),
                    votes=int(votes_str),
                )
            if result.votes < max_voted_verse.votes:
                max_voted_verse = result
            if result.votes >= min_votes:
                print(f"Found instance: {result._asdict()}")
    print(f"Maximum voted reference is {max_voted_verse}")


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--file", "-f", help="The path of the text database")
    args = argparser.parse_args()
    path: str = args.file
    assert type(path) is str and len(path) > 0
    ReadDatabase(path, 100)
