import os
from enum import Enum


class NoiaLineType(Enum):
    """Any given line in the `.noia` file can be any of these types"""

    COMMENT_LINE = 0
    """An ordinary comment"""

    BOOK_START_LINE = 1
    """A special comment that preceeds a new book"""

    VERSE_LINE = 2
    """Verse content"""

    HEADER_LINE = 3
    """A header value of the `.noia` file"""

    INVALID = 4
    """This line shows that the file being read is corrupted/invalid noia bible database"""


class BookBeginLine:
    """The data representing a BookBegin section line"""

    book_id: int
    """The integer id for the book"""

    short_name: str
    """The short name for the book"""

    eng_name: str
    """The full english name of the book"""

    reg_name: str
    """The regional name of the book, possibly in unicode"""

    def __init__(self, book_id: int, short_name: str, eng_name: str, reg_name: str):
        self.book_id = book_id
        self.short_name = short_name
        self.eng_name = eng_name
        self.reg_name = reg_name


class VerseLine:
    """Data related to a verse line from the `.noia` file"""

    book_id: int
    """The integer ID of the book"""

    book_short_name: str
    """The short name of the book"""

    chapter_id: int
    """The integer ID of the chapter"""

    verse_id: int
    """The integer ID of the verse"""

    verse: str
    """The verse content"""

    def __init__(
        self,
        book_id: int,
        book_short_name: str,
        chapter_id: int,
        verse_id: int,
        verse: str,
    ):
        self.book_id = book_id
        self.book_short_name = book_short_name
        self.chapter_id = chapter_id
        self.verse_id = verse_id
        self.verse = verse


def parse_line(line: str) -> tuple:
    """
    Parse a single line of a `.noia` bible

    Args:
        line (str): The line from the `.noia` file to parse

    Returns:
        tuple[Noia_Line_Type, any]:
            returns a tuple of the Noia_Line_Type Enum and the parsed object
    """

    def parse_book_begin_line(line: str) -> BookBeginLine | None:
        """Try to parse line as a BookBeginLine object, if valid

        Args:
            line (str): The line to parse

        Returns:
            BookBeginLine | None: If line is a valid verse line, a
             BookBeginLine object ir returned,
             otherwise a None object is returned
        """
        if line.startswith("# BOOK") is False:
            return None
        line_parts = line.split("\t")
        if len(line_parts) != 5:
            return None
        try:
            return BookBeginLine(
                book_id=int(line_parts[1]),
                short_name=line_parts[2],
                eng_name=line_parts[3],
                reg_name=line_parts[4],
            )
        except:
            return None

    def parse_verse_line(line: str) -> VerseLine | None:
        """Try to parse line as a VerseLine object, if valid

        Args:
            line (str): The line to parse

        Returns:
            VerseLine | None: If line is a valid verse line, a
             VerseLine object ir returned,
             otherwise a None object is returned
        """
        line_parts = line.split("\t")
        if len(line_parts) != 5:
            return None
        try:
            return VerseLine(
                book_id=int(line_parts[0]),
                book_short_name=line_parts[1],
                chapter_id=int(line_parts[2]),
                verse_id=int(line_parts[3]),
                verse=line_parts[4],
            )
        except:
            return None

    line = line.strip()
    if line == "INDEX\tBOOK\tCHAPTER\tVERSE\tTEXT":
        return (NoiaLineType.HEADER_LINE, line)
    data = parse_verse_line(line)
    if isinstance(data, VerseLine):
        return (NoiaLineType.VERSE_LINE, data)
    data = parse_book_begin_line(line)
    if isinstance(data, BookBeginLine):
        return (NoiaLineType.BOOK_START_LINE, data)
    if line.startswith("#"):
        return (NoiaLineType.COMMENT_LINE, line[1:].strip())
    return (NoiaLineType.INVALID, line)


class Context:
    """
    Private class for parsing noia file.
    """

    metadata: dict
    """The list of metadata entries"""

    content: dict
    """The collection of chapters and verses within all books"""

    listing: dict
    """The list of books of bible available in this database"""

    current_book_no: int
    """State variable for the current book number"""

    current_book_content: dict
    """State variable for the current book content"""

    current_chapter_no: int
    """State variable for the current chapter number"""

    current_chapter: dict
    """State variable for the current chapter content"""

    def __init__(self):
        self.metadata = {}
        self.content = {}
        self.listing = {}
        self.current_book_no = 0
        self.current_book_content = {}
        self.current_chapter_no = 0
        self.current_chapter = {}

    def finish_chapter(self):
        """
        Update and complete the dictionaries for the current chapter

        Args:
            self (_Context): The Context object
        """
        if len(self.current_chapter) > 0:
            self.current_book_content[self.current_chapter_no] = self.current_chapter
        self.current_chapter = {}

    def finish_book(self):
        """
        Finalizes the dictionaries for any book and chapter in the instance

        Args:
            self (_Context): The Context object
        """
        if len(self.current_book_content) > 0:
            # """Complete the content for this book"""
            self.content[self.current_book_no] = self.current_book_content
        self.current_book_content = {}

    def handle_verse_line(self, line: VerseLine):
        """
        Input a single line containing bible verse

        Args:
            line (VerseLine): The verse parsed from the current line
        """
        if self.current_chapter_no != line.chapter_id:
            self.finish_chapter()
            self.current_chapter_no = line.chapter_id

        self.current_chapter[line.verse_id] = line.verse

    def handle_bookbegin_line(self, line: BookBeginLine):
        """
        Input a single line containing the header before a new bible book

        Args:
            line (VerseLine): The header line parsed from the current line
        """
        self.finish_chapter()
        self.finish_book()
        self.listing[line.book_id] = line.reg_name
        self.current_book_no = line.book_id

    def handle_comment_line(self, value: str):
        """
        Handle single line of comment

        Args:
            self (_Context): The Context object
            value (str): The comment line being read
        """
        if ":" not in value:
            return
        index_val = value.index(":")
        key = value[:index_val].strip()
        value = value[index_val + 1:].strip()
        self.metadata[key] = value

    def handle_eof(self):
        """Close all content as EOF(End of File) reached

        Args:
            self (_Context): The Context object
        """
        self.finish_chapter()
        self.finish_book()


def parse_noia_bible(path: str) -> tuple[dict, dict, dict]:
    """
    Parses a single *.noia bible file

    Args:
                    path (str): The path of the noia file to read and parse

    Returns:
                    tuple[dict, dict, dict]: A tuple of dictionaries,
                    namely `metadata`, `listing`, `content`.
                    `metadata` details the summary details given as comments.
                    `listing` details the list of books in this bible and IDs.
                    `content` contains the content for each book in the file.

    """
    assert os.path.isfile(path), "invalid path for file"

    cur_context = Context()
    with open(path, "r") as file:
        # Loop to iterate each line of the file
        line = file.readline()
        while line is not None and len(line) > 0:
            # Try parsing line as verse content
            line_type: NoiaLineType
            line_type, data = parse_line(line)

            assert line_type != NoiaLineType.INVALID, f"Invalid line: {line}"

            if line_type == NoiaLineType.BOOK_START_LINE:
                cur_context.handle_bookbegin_line(data)

            elif line_type == NoiaLineType.VERSE_LINE:
                cur_context.handle_verse_line(data)

            else:  # line_type in [Noia_Line_Type.Comments,Noia_Line_Type.Header]
                cur_context.handle_comment_line(data)

            # Read next line
            line = file.readline()

        cur_context.handle_eof()
        return cur_context.metadata, cur_context.listing, cur_context.content
