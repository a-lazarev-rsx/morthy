import unittest
import os
import sys

# Add project root to sys.path to allow importing parser module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from parser import extract_text_from_epub, extract_text_from_pdf, extract_text_from_fb2
from ebooklib import epub # For creating dummy EPUB
from reportlab.pdfgen import canvas # For creating dummy PDF
from reportlab.lib.pagesizes import letter

# Define a directory for test fixtures
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

class TestEpubParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create dummy EPUB file
        cls.sample_epub_path = os.path.join(FIXTURES_DIR, "sample.epub")
        cls.malformed_epub_path = os.path.join(FIXTURES_DIR, "malformed.epub")
        cls.empty_content_epub_path = os.path.join(FIXTURES_DIR, "empty_content.epub")

        # Valid EPUB
        book = epub.EpubBook()
        book.set_identifier('id_sample_epub')
        book.set_title('Sample EPUB')
        book.set_language('en')
        c1 = epub.EpubHtml(title='Intro', file_name='chap1.xhtml', lang='en')
        c1.content = u'<h1>Chapter 1</h1><p>This is sample EPUB content.</p><p>Second paragraph.</p>'
        book.add_item(c1)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ['nav', c1]
        epub.write_epub(cls.sample_epub_path, book, {})

        # Malformed EPUB (just a text file with .epub extension)
        with open(cls.malformed_epub_path, "w") as f:
            f.write("This is not a valid EPUB file.")

        # EPUB with no text content in its document items
        book_empty = epub.EpubBook()
        book_empty.set_identifier('id_empty_epub')
        book_empty.set_title('Empty Content EPUB')
        book_empty.set_language('en')
        c_empty = epub.EpubHtml(title='Empty', file_name='chap_empty.xhtml', lang='en')
        c_empty.content = u'<h1></h1><p></p>' # No actual text
        book_empty.add_item(c_empty)
        book_empty.add_item(epub.EpubNcx())
        book_empty.add_item(epub.EpubNav())
        book_empty.spine = ['nav', c_empty]
        epub.write_epub(cls.empty_content_epub_path, book_empty, {})


    def test_extract_text_from_valid_epub(self):
        text = extract_text_from_epub(self.sample_epub_path)
        self.assertIn("This is sample EPUB content.", text)
        self.assertIn("Second paragraph.", text)
        self.assertNotIn("Error:", text)

    def test_extract_text_from_non_existent_epub(self):
        text = extract_text_from_epub("non_existent.epub")
        self.assertEqual(text, "Error: EPUB file not found.")

    def test_extract_text_from_malformed_epub(self):
        text = extract_text_from_epub(self.malformed_epub_path)
        self.assertTrue(text.startswith("Error: Invalid or corrupted EPUB file.") or \
                        text.startswith("An unexpected error occurred"), # ebooklib can raise different errors
                        f"Unexpected message: {text}")


    def test_extract_text_from_empty_content_epub(self):
        text = extract_text_from_epub(self.empty_content_epub_path)
        # The current parser extracts titles from chapters even if paragraph text is empty.
        # The sample "empty_content.epub" has a chapter titled "Empty".
        # It also includes the book title "Empty Content EPUB" from the <title> tag in the xhtml file.
        # The epub library might also add book title to text items.
        # Let's check if it contains the chapter title or book title.
        # Upon inspection of how ebooklib and BeautifulSoup extract text,
        # it will include text from <title> tags within the XHTML files.
        # The c_empty.content was '<h1></h1><p></p>', but it's wrapped in an XHTML structure
        # by ebooklib which includes a <head><title>Empty Content EPUB</title></head> if not specified,
        # or uses the chapter title.
        # The actual content string is 'Empty Content EPUB\n\n\nEmpty\n\n\n'
        # So, we expect the title of the book or chapter.
        self.assertIn("Empty Content EPUB", text, "Text from empty content EPUB should include title.")
        self.assertIn("Empty", text, "Text from empty content EPUB should include chapter title.")
        # Check that there isn't more than just titles and whitespace
        cleaned_text = text.replace("Empty Content EPUB", "").replace("Empty", "").strip()
        self.assertEqual(cleaned_text, "", "Text from empty content EPUB should primarily be titles.")


    @classmethod
    def tearDownClass(cls):
        os.remove(cls.sample_epub_path)
        os.remove(cls.malformed_epub_path)
        os.remove(cls.empty_content_epub_path)

class TestPdfParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sample_pdf_path = os.path.join(FIXTURES_DIR, "sample.pdf")
        cls.malformed_pdf_path = os.path.join(FIXTURES_DIR, "malformed.pdf")
        # For encrypted PDF, PyPDF2 handles basic password-less encrypted files if permissions allow.
        # Creating a truly encrypted PDF that needs a password is more complex for a simple unit test setup.
        # We will test PyPDF2's behavior with a file it *thinks* is encrypted or cannot decrypt easily.

        # Valid PDF
        c = canvas.Canvas(cls.sample_pdf_path, pagesize=letter)
        c.drawString(100, 750, "Hello PDF.")
        c.drawString(100, 730, "This is a test PDF document.")
        c.showPage()
        c.drawString(100, 750, "Page two content.")
        c.save()

        # Malformed PDF (text file with .pdf extension)
        with open(cls.malformed_pdf_path, "w") as f:
            f.write("This is not a PDF file.")

    def test_extract_text_from_valid_pdf(self):
        text = extract_text_from_pdf(self.sample_pdf_path)
        self.assertIn("Hello PDF.", text)
        self.assertIn("This is a test PDF document.", text)
        self.assertIn("Page two content.", text)
        self.assertFalse(text.startswith("Error:"))

    def test_extract_text_from_non_existent_pdf(self):
        text = extract_text_from_pdf("non_existent.pdf")
        self.assertEqual(text, "Error: PDF file not found at path: non_existent.pdf")

    def test_extract_text_from_malformed_pdf(self):
        text = extract_text_from_pdf(self.malformed_pdf_path)
        self.assertTrue(text.startswith("Error: Could not read PDF."), f"Unexpected message: {text}")
    
    # Placeholder for encrypted PDF test - actual encryption is hard to setup simply
    # For now, this will behave like a malformed PDF if PyPDF2 can't open it.
    # If PyPDF2 *can* open it (e.g. passwordless but restricted), text might be empty.
    def test_extract_text_from_non_pdf_file(self):
        # Use the malformed_pdf_path (which is just a text file)
        # This tests how extract_text_from_pdf handles a file that is not a PDF.
        text = extract_text_from_pdf(self.malformed_pdf_path)
        self.assertTrue(text.startswith("Error: Could not read PDF."), 
                        f"Unexpected message for non-PDF file test: {text}")

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.sample_pdf_path)
        os.remove(cls.malformed_pdf_path)

# FB2 tests are omitted for now due to persistent ImportError with the fb2 library in the environment.
# If the fb2 library import was resolved, tests would follow a similar pattern:
# 1. Create a sample.fb2 in setUpClass.
# 2. Test valid FB2 extraction.
# 3. Test non-existent FB2.
# 4. Test malformed FB2.

import tempfile
import shutil

class TestFB2Parser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a dedicated temp directory for FB2 test files
        cls.test_dir = tempfile.mkdtemp(prefix="fb2_tests_")

        cls.sample_fb2_path = os.path.join(cls.test_dir, "sample.fb2")
        cls.no_body_fb2_path = os.path.join(cls.test_dir, "no_body.fb2")
        cls.empty_body_fb2_path = os.path.join(cls.test_dir, "empty_body.fb2")
        cls.special_chars_fb2_path = os.path.join(cls.test_dir, "special_chars.fb2")
        cls.malformed_xml_path = os.path.join(cls.test_dir, "malformed.xml.fb2") # .fb2 to be picked by parser
        cls.non_fb2_path = os.path.join(cls.test_dir, "plain.txt")

        with open(cls.sample_fb2_path, "w", encoding="utf-8") as f:
            f.write(cls._create_sample_fb2_basic_content())
        with open(cls.no_body_fb2_path, "w", encoding="utf-8") as f:
            f.write(cls._create_sample_fb2_no_body_content())
        with open(cls.empty_body_fb2_path, "w", encoding="utf-8") as f:
            f.write(cls._create_sample_fb2_empty_body_content())
        with open(cls.special_chars_fb2_path, "w", encoding="utf-8") as f:
            f.write(cls._create_sample_fb2_special_chars_content())
        with open(cls.malformed_xml_path, "w", encoding="utf-8") as f:
            f.write(cls._create_malformed_xml_content())
        with open(cls.non_fb2_path, "w", encoding="utf-8") as f:
            f.write("This is a plain text file, not FB2 or XML.")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir)

    @staticmethod
    def _create_sample_fb2_basic_content():
        return """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description><title-info><book-title>Test Book</book-title></title-info></description>
<body>
    <section><title><p>Chapter 1</p></title>
        <p>This is paragraph one.</p>
        <p>This is paragraph two with <em>emphasis</em>.</p>
    </section>
    <section><title><p>Chapter 2</p></title>
        <p>Another paragraph.</p>
    </section>
</body>
</FictionBook>"""

    @staticmethod
    def _create_sample_fb2_no_body_content():
        return """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description><title-info><book-title>No Body Book</book-title></title-info></description>
</FictionBook>"""

    @staticmethod
    def _create_sample_fb2_empty_body_content():
        return """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description><title-info><book-title>Empty Body Book</book-title></title-info></description>
<body></body>
</FictionBook>"""

    @staticmethod
    def _create_sample_fb2_special_chars_content():
        return """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description><title-info><book-title>Special Chars Book</book-title></title-info></description>
<body>
    <section><p>Text with &lt;less than&gt; and &amp;ampersand&amp;.</p>
        <p>Some <strong>bold</strong> and <em>italic</em> text.</p>
        <p>A line with preserved spaces:  A  B  C  </p>
        <p>A\nnewline character (should become space).</p>
    </section>
</body>
</FictionBook>"""
# Note: The current parser implementation normalizes spaces, so "A  B  C" -> "A B C"
# and "\n" -> " ".

    @staticmethod
    def _create_malformed_xml_content():
        return """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<body>
    <section><p>This is a malformed XML because of a missing closing tag.
</FictionBook>""" # Missing </p> and </section>

    def test_extract_text_from_valid_fb2(self):
        expected_text = "Chapter 1 This is paragraph one. This is paragraph two with emphasis. Chapter 2 Another paragraph."
        text = extract_text_from_fb2(self.sample_fb2_path)
        self.assertEqual(text, expected_text)

    def test_extract_text_no_body(self):
        text = extract_text_from_fb2(self.no_body_fb2_path)
        self.assertEqual(text, "Info: FB2 file has no body content or body tag is not standard.")

    def test_extract_text_empty_body(self):
        text = extract_text_from_fb2(self.empty_body_fb2_path)
        self.assertEqual(text, "Info: FB2 body was found, but no text content was extracted from it.")

    def test_extract_text_special_chars(self):
        # Based on current parser: string(.//text()) and then ' '.join(text.split())
        # "Text with <less than> and &ampersand&." -> "Text with <less than> and &ampersand&." (XML entities are resolved by parser)
        # "Some bold and italic text."
        # "A line with preserved spaces:  A  B  C" -> "A line with preserved spaces: A B C"
        # "A newline character (should become space)." -> "A newline character (should become space)."
        expected_text = "Text with <less than> and &ampersand&. Some bold and italic text. A line with preserved spaces: A B C A newline character (should become space)."
        text = extract_text_from_fb2(self.special_chars_fb2_path)
        self.assertEqual(text, expected_text)

    def test_extract_text_from_non_fb2_file(self):
        # This will raise XMLSyntaxError because plain text is not valid XML
        text = extract_text_from_fb2(self.non_fb2_path)
        self.assertTrue(text.startswith("Error: Invalid or corrupted FB2 file. XMLSyntaxError:"), f"Unexpected message: {text}")

    def test_extract_text_file_not_found(self):
        text = extract_text_from_fb2("non_existent_file.fb2")
        self.assertEqual(text, "Error: FB2 file not found at path: non_existent_file.fb2")

    def test_extract_text_malformed_xml(self):
        text = extract_text_from_fb2(self.malformed_xml_path)
        self.assertTrue(text.startswith("Error: Invalid or corrupted FB2 file. XMLSyntaxError:"), f"Unexpected message: {text}")


if __name__ == '__main__':
    unittest.main()
