"""
Parser module for extracting text content from various book file formats.

This module provides functions to extract plain text from EPUB, PDF, and
(partially implemented) FB2 files. Each function handles a specific file
type, including error handling for common issues like file not found or
corrupted files.
"""
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_text_from_epub(filepath):
    """
    Extracts text content from an EPUB file.

    Args:
        filepath (str): The path to the EPUB file.

    Returns:
        str: The extracted text content, or an error message if extraction fails.
    """
    try:
        book = epub.read_epub(filepath)
        content = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Use BeautifulSoup to parse HTML content and extract text
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                content.append(soup.get_text())
        return "\n".join(content)
    except FileNotFoundError:
        return "Error: EPUB file not found."
    except ebooklib.epub.EpubException:
        return "Error: Invalid or corrupted EPUB file."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def extract_text_from_fb2(filepath):
    """
    Extracts text content from an FB2 file.

    Args:
        filepath (str): The path to the FB2 file.

    Returns:
        str: The extracted text content, or an error message if extraction fails.
    """
    try:
        # Attempt to import the fb2 library and its necessary components.
        # The common import path found in documentation for 'python-fb2' or 'fb2'
        # is often related to an FB2Tree or similar parser object.
        from fb2 import FB2TreeV2 # Trying FB2TreeV2 as seen in some versions/forks
                                 # or use 'from fb2.fb2 import FB2Tree' if that's standard for your installed lib
                                 # This is the most likely point of failure if the library is not found or structured differently.
    except ImportError:
        return "Error: fb2 library not found or FB2TreeV2 (or FB2Tree) class not found within it. Please install/check the library (e.g., pip install fb2 or python-fb2)."

    try:
        # Open the FB2 file in binary read mode, as it's XML-based.
        with open(filepath, 'rb') as fb2_file:
            # Parse the FB2 file using the imported tree object.
            # The exact instantiation might vary (e.g., FB2Tree(file_obj) or FB2Tree.parse(file_obj))
            # For the fb2 package (0.2.1), it's typically FB2Tree(file_obj).
            # Let's stick to FB2Tree for now as it's more common with the base 'fb2' package.
            from fb2.fb2 import FB2Tree # Re-affirming the more standard import for the parsing part.
            tree = FB2Tree(fb2_file)

        # The main content is usually within the <body> of an FB2 file.
        body = tree.get_body()
        if not body:
            return "Error: FB2 file has no body content."

        # The fb2 library (especially version 0.2.1 which uses lxml)
        # typically provides a way to get the raw XML of elements.
        # We can then use BeautifulSoup to robustly extract all text, stripping XML tags.
        if hasattr(body, 'raw_xml'):
            # body.raw_xml() should give the XML string of the <body> element.
            soup = BeautifulSoup(body.raw_xml(), 'xml') # Use the 'xml' parser for FB2
            extracted_text = soup.get_text(separator='\n', strip=True)
            if extracted_text:
                return extracted_text
            else:
                return "Info: FB2 body was parsed, but no text content was found after stripping tags."
        else:
            # Fallback if raw_xml() is not available (less likely for fb2 0.2.1)
            # This would require more specific knowledge of the library's element structure.
            # For now, we'll indicate that the primary method failed.
            return "Error: FB2 library's body object does not support 'raw_xml()' for text extraction. Cannot extract text."

    except FileNotFoundError:
        return "Error: FB2 file not found at path: " + filepath
    except Exception as e:
        # Catching a broader range of exceptions that might occur during parsing
        # (e.g., XML parsing errors within the fb2 library, unexpected file structure).
        return f"An unexpected error occurred during FB2 parsing: {e}"

def extract_text_from_pdf(filepath):
    """
    Extracts text content from a PDF file.

    Args:
        filepath (str): The path to the PDF file.

    Returns:
        str: The extracted text content, or an error message if extraction fails.
    """
    try:
        import PyPDF2
        text_content = []
        with open(filepath, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            if reader.is_encrypted:
                # Attempt to decrypt with an empty password, as per PyPDF2 examples for some encrypted files
                try:
                    if reader.decrypt('') == PyPDF2.PasswordType.OWNER_PASSWORD:
                         pass # Successfully decrypted with empty owner password
                    elif reader.decrypt('') == PyPDF2.PasswordType.USER_PASSWORD:
                         pass # Successfully decrypted with empty user password
                    else: # This path might mean decryption failed or was partial
                        return "Error: PDF file is encrypted and could not be decrypted with an empty password."
                except Exception as decrypt_error:
                     return f"Error: PDF file is encrypted and decryption failed. {decrypt_error}"
            
            for page in reader.pages:
                text_content.append(page.extract_text() or "") # Ensure None is handled
        return "\n".join(text_content)
    except FileNotFoundError:
        return f"Error: PDF file not found at path: {filepath}"
    except PyPDF2.errors.PdfReadError:
        return f"Error: Could not read PDF. The file might be corrupted or not a valid PDF: {filepath}"
    except ImportError:
        return "Error: PyPDF2 library not found. Please install it (e.g., pip install PyPDF2)."
    except Exception as e:
        return f"An unexpected error occurred during PDF parsing: {e}"

if __name__ == '__main__':
    # Example usage (optional - for testing purposes)
    # Create a dummy EPUB file for testing
    book = epub.EpubBook()
    book.set_identifier('id123456')
    book.set_title('Sample Book')
    book.set_language('en')
    book.add_author('Author Name')

    # Create a chapter
    c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='en')
    c1.content = u'<h1>Introduction</h1><p>This is a sample EPUB created for testing purposes.</p>'

    # Add chapter to the book
    book.add_item(c1)

    # Define Table of Contents
    book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = 'BODY {color: black;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Create spine
    book.spine = ['nav', c1]

    # Create EPUB file
    epub_filepath = 'sample.epub'
    epub.write_epub(epub_filepath, book, {})
    print(f"'{epub_filepath}' created for testing.")

    extracted_epub_text = extract_text_from_epub(epub_filepath)
    print("\nExtracted Text from EPUB:")
    print(extracted_epub_text)

    # Test EPUB with a non-existent file
    non_existent_epub = "non_existent.epub"
    print(f"\nTesting EPUB with non-existent file: {non_existent_epub}")
    error_epub_text = extract_text_from_epub(non_existent_epub)
    print(error_epub_text)

    # Test EPUB with a non-epub file
    non_epub_file = "not_an_epub.txt"
    with open(non_epub_file, "w", encoding="utf-8") as f:
        f.write("This is not an EPUB file.")
    print(f"\nTesting EPUB with a non-EPUB file: {non_epub_file}")
    error_epub_text = extract_text_from_epub(non_epub_file)
    print(error_epub_text)

    # --- FB2 Test Section ---
    print("\n--- FB2 Tests ---")
    fb2_filepath = 'sample.fb2'
    # Create a dummy FB2 file for testing
    # FB2 is XML-based. This is a very minimal example.
    fb2_content = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">
<description>
    <title-info>
        <genre>antique</genre>
        <author><first-name>Sample</first-name><last-name>Author</last-name></author>
        <book-title>Sample FB2 Book</book-title>
        <lang>en</lang>
    </title-info>
    <document-info>
        <author><nickname>Tester</nickname></author>
        <date>2024-01-01</date>
        <version>1.0</version>
    </document-info>
</description>
<body>
    <section><title><p>Chapter 1</p></title>
        <p>This is the first paragraph of the sample FB2 file.</p>
        <p>This is <em>emphasized</em> text in the second paragraph.</p>
    </section>
    <section><title><p>Chapter 2</p></title>
        <p>Another paragraph in a new chapter.</p>
    </section>
</body>
</FictionBook>
"""
    with open(fb2_filepath, "w", encoding="utf-8") as f:
        f.write(fb2_content)
    print(f"'{fb2_filepath}' created for testing.")

    extracted_fb2_text = extract_text_from_fb2(fb2_filepath)
    print("\nExtracted Text from FB2:")
    print(extracted_fb2_text)

    # Test FB2 with a non-existent file
    non_existent_fb2 = "non_existent.fb2"
    print(f"\nTesting FB2 with non-existent file: {non_existent_fb2}")
    error_fb2_text = extract_text_from_fb2(non_existent_fb2)
    print(error_fb2_text)

    # Test FB2 with a non-fb2 file (e.g., the dummy epub)
    print(f"\nTesting FB2 with a non-FB2 file: {epub_filepath}")
    error_fb2_text = extract_text_from_fb2(epub_filepath) # Using the epub as a non-fb2
    print(error_fb2_text)

    # Clean up dummy files
    import os
    if os.path.exists(epub_filepath): os.remove(epub_filepath)
    if os.path.exists(non_epub_file): os.remove(non_epub_file)
    if os.path.exists(fb2_filepath): os.remove(fb2_filepath)
    
    # --- PDF Test Section ---
    print("\n--- PDF Tests ---")
    pdf_filepath = 'sample.pdf'

    # Create a dummy PDF file for testing using reportlab (if available) or a simpler method
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(pdf_filepath, pagesize=letter)
        c.drawString(100, 750, "Hello World!")
        c.drawString(100, 730, "This is a sample PDF document created for testing.")
        c.showPage()
        c.drawString(100, 750, "This is page 2.")
        c.save()
        print(f"'{pdf_filepath}' created for testing using reportlab.")
        
        extracted_pdf_text = extract_text_from_pdf(pdf_filepath)
        print("\nExtracted Text from PDF:")
        print(extracted_pdf_text)

        # Test with a non-existent PDF file
        non_existent_pdf = "non_existent.pdf"
        print(f"\nTesting PDF with non-existent file: {non_existent_pdf}")
        error_pdf_text = extract_text_from_pdf(non_existent_pdf)
        print(error_pdf_text)

        # Test PDF with a non-PDF file (e.g., the dummy epub)
        print(f"\nTesting PDF with a non-PDF file (epub): {epub_filepath}")
        # Recreate epub_filepath for this test if it was removed
        if not os.path.exists(epub_filepath):
            # Minimal epub recreation for testing invalid PDF read
            book_temp = epub.EpubBook()
            book_temp.set_identifier('id_temp_epub')
            book_temp.set_title('Temp Epub for PDF Test')
            c1_temp = epub.EpubHtml(title='Intro', file_name='chap_temp.xhtml')
            c1_temp.content = u'<p>temp</p>'
            book_temp.add_item(c1_temp)
            book_temp.spine = ['nav', c1_temp]
            epub.write_epub(epub_filepath, book_temp, {})

        error_pdf_text = extract_text_from_pdf(epub_filepath)
        print(error_pdf_text)
        if os.path.exists(pdf_filepath): os.remove(pdf_filepath)

    except ImportError:
        print("reportlab not found, skipping PDF generation and some PDF tests.")
        # Test with a non-existent PDF file (still valid test)
        non_existent_pdf = "non_existent.pdf"
        print(f"\nTesting PDF with non-existent file: {non_existent_pdf}")
        error_pdf_text = extract_text_from_pdf(non_existent_pdf)
        print(error_pdf_text)

    print("\nCleaned up dummy files (if any were created).")
