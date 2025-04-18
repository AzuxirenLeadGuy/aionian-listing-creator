import os
from enum import Enum

class Noia_Line_Type(Enum):
    """Any given line in the `.noia` file can be any of these types"""

    Comments = 0
    """An ordinary comment"""

    BookBegin = 1
    """A special comment that preceeds a new book"""

    Verse = 2
    """Verse content"""

    Header = 3
    """A header value of the `.noia` file"""

    Invalid = 4
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

def parse_line(line: str) -> tuple[Noia_Line_Type, any]:
    """
    Parse a single line of a `.noia` bible

    Args:
        line (str): The line from the `.noia` file to parse

    Returns:
        tuple[Noia_Line_Type, any]:
            returns a tuple of the Noia_Line_Type Enum and the parsed object
    """

    def parse_BookBeginLine(line: str) -> BookBeginLine | None:
        """
        Parses the line into a `BookBeginLine` object if valid/possible,
        otherwise returns a None type

        Args:
            line (str): The line to parse
        """
        if line.startswith("# BOOK") == False:
            return None
        line = line.split("\t")
        if len(line) != 5:
            return None
        try:
            return BookBeginLine(
                book_id=int(line[1]),
                short_name=line[2],
                eng_name=line[3],
                reg_name=line[4],
            )
        except:
            return None

    def parse_VerseLine(line: str) -> VerseLine | None:
        line = line.split("\t")
        if len(line) != 5:
            return None
        try:
            return VerseLine(
                book_id=int(line[0]),
                book_short_name=line[1],
                chapter_id=int(line[2]),
                verse_id=int(line[3]),
                verse=line[4],
            )
        except:
            return None

    if line.strip() == 'INDEX\tBOOK\tCHAPTER\tVERSE\tTEXT':
        return (Noia_Line_Type.Header, line)
    data = parse_VerseLine(line)
    if type(data) == VerseLine:
        return (Noia_Line_Type.Verse, data)
    data = parse_BookBeginLine(line)
    if type(data) == BookBeginLine:
        return (Noia_Line_Type.BookBegin, data)
    if line.startswith("#"):
        return (Noia_Line_Type.Comments, line[1:].strip())
    return (Noia_Line_Type.Invalid, line)

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

    class Context:
        metadata = {}
        content = {}
        listing = {}
    
        current_book_no = 0
        current_book_content = {}
        current_chapter_no = 0
        current_chapter = {}
    
    cur_context = Context()

    with open(path, "r") as file:

        def finish_chapter(context:Context):
            if len(context.current_chapter) > 0:
                context.current_book_content[context.current_chapter_no] = context.current_chapter
            context.current_chapter = {}

        def finish_book(context:Context):
            if len(context.current_book_content) > 0:
                context.content[context.current_book_no] = context.current_book_content
            context.current_book_content = {}
        
        def handle_verse_line(context:Context, value:VerseLine):
            if context.current_chapter_no != value.chapter_id:
                    finish_chapter(context)
                    context.current_chapter_no = value.chapter_id

            context.current_chapter[value.verse_id] = value.verse
        
        def handle_bookbegin_line(context:Context, value:BookBeginLine):
            finish_chapter(context)
            finish_book(context)
            context.listing[value.book_id] = value.reg_name
            context.current_book_no = value.book_id


        # Loop to iterate each line of the file
        line = file.readline()
        while line != None and len(line) > 0:

            # Try parsing line as verse content
            line_type: Noia_Line_Type
            line_type, data = parse_line(line)

            assert line_type != Noia_Line_Type.Invalid, f"Invalid line: {line}"

            if line_type==Noia_Line_Type.BookBegin:
                handle_bookbegin_line(cur_context, data)

            elif line_type == Noia_Line_Type.Verse:
                handle_verse_line(cur_context, data)

            else: # line_type in [Noia_Line_Type.Comments,Noia_Line_Type.Header]
                value : str = data
                if ':' in value:
                    index_val = value.index(':')
                    key = value[:index_val].strip()
                    value = value[index_val+1:].strip()
                    cur_context.metadata[key] = value

            # Read next line
            line = file.readline()
        
        finish_chapter(cur_context)
        finish_book(cur_context)

        return cur_context.metadata, cur_context.listing, cur_context.content
