"""
Parser module for extracting text content from various book file formats.

This module provides functions to extract plain text from EPUB, PDF, and
FB2 files. Each function handles a specific file type, including error
handling for common issues like file not found or corrupted files.
"""
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import sys
import traceback

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
    Extracts structured text content from an FB2 file using a recursive approach.
    It attempts to preserve paragraph and section structure with newlines.

    Args:
        filepath (str): The path to the FB2 file.

    Returns:
        str: The extracted text content, or an error message if extraction fails.
    """
    try:
        from lxml import etree  # Import lxml

        with open(filepath, 'rb') as fb2_file:
            fb2_content = fb2_file.read()

        # Parse the XML content
        tree = etree.fromstring(fb2_content)

        # Define the FB2 namespace
        ns = {'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0'}

        # Find the <body> element using the standard namespace
        body_element = tree.find('fb:body', namespaces=ns)

        if body_element is None:
            # If not found, try a namespace-agnostic XPath
            body_elements = tree.xpath('//*[local-name()="body"]')
            if body_elements:
                body_element = body_elements[0]
            else:
                # If still not found after both attempts
                return "Info: FB2 file has no body content or body tag is not standard."

        
        text_parts = []

        
        text_parts = []

        # Inner recursive function to process each element and its children
        def process_element(element, current_text_parts):
            if element is None:
                return

            tag_name = etree.QName(element.tag).localname

            if tag_name == 'p':
                # Paragraphs: extract text, strip surrounding whitespace, append with a single newline.
                # Text from inline tags (<em>, <strong>, <a>, etc.) is included.
                para_text = element.xpath("string(.//text())") 
                if para_text: 
                    stripped_text = para_text.strip()
                    if stripped_text:
                        current_text_parts.append(stripped_text)
                        current_text_parts.append('\n')
            elif tag_name == 'title':
                # Titles: extract text, strip, append with two newlines for separation.
                title_text = element.xpath("string(.//text())")
                if title_text:
                    stripped_text = title_text.strip()
                    if stripped_text:
                        current_text_parts.append(stripped_text)
                        current_text_parts.append('\n\n')
            elif tag_name == 'section':
                # Sections: manage spacing before and after their content.
                # Ensure a double newline before starting a new section if not already present.
                if current_text_parts and not "".join(current_text_parts[-2:]).endswith('\n\n'):
                    if not "".join(current_text_parts[-1:]).endswith('\n'):
                        current_text_parts.append('\n')
                    current_text_parts.append('\n')

                for child in element: # Recursively process children of the section
                    process_element(child, current_text_parts)
                
                # Ensure a double newline after the section content if not already present.
                if current_text_parts and not "".join(current_text_parts[-2:]).endswith('\n\n'):
                    if not "".join(current_text_parts[-1:]).endswith('\n'):
                        current_text_parts.append('\n')
                    current_text_parts.append('\n')
            elif tag_name == 'empty-line':
                # Empty lines: append a single newline.
                current_text_parts.append('\n')
            elif tag_name in ['epigraph', 'cite', 'poem', 'subtitle']:
                # Other block elements: extract text, strip, ensure double newline separation.
                block_text = element.xpath("string(.//text())")
                if block_text:
                    stripped_text = block_text.strip()
                    if stripped_text:
                        if current_text_parts and not "".join(current_text_parts[-2:]).endswith('\n\n'):
                            if not "".join(current_text_parts[-1:]).endswith('\n'): current_text_parts.append('\n')
                            current_text_parts.append('\n')
                        
                        current_text_parts.append(stripped_text)
                        current_text_parts.append('\n\n')
            else:
                # Default: For other elements (e.g., <body> itself, or other containers),
                # recursively process their children without adding specific formatting at this level.
                for child in element:
                    process_element(child, current_text_parts)

        # Start the recursive processing from the found <body> element
        process_element(body_element, text_parts)

        # Join all collected text parts
        extracted_text = "".join(text_parts)

        # Normalize newlines: replace sequences of 3 or more newlines with exactly two.
        # Also, strip any leading/trailing whitespace from the final text.
        if extracted_text:
            extracted_text = re.sub(r'\n{3,}', '\n\n', extracted_text)
            extracted_text = extracted_text.strip() 

        if not extracted_text: # If after all processing, the text is empty
            return "Info: FB2 body was found, but no text content was extracted from it."
        return extracted_text

    except FileNotFoundError:
        return f"Error: FB2 file not found at path: {filepath}"
    except etree.XMLSyntaxError as e:
        return f"Error: Invalid or corrupted FB2 file. XMLSyntaxError: {e}"
    except ImportError:
        # This handles the case where lxml is not installed, though it should be.
        return "Error: lxml library not found. Please install it (e.g., pip install lxml)."
    except Exception as e:
        print("\n--- Traceback for unexpected error in extract_text_from_fb2 ---", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print("--- End Traceback ---", file=sys.stderr)
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
