import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import shutil # For cleaning up fixtures directory

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import main as main_script
from ebooklib import epub
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'temp_integration_fixtures')

class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if os.path.exists(FIXTURES_DIR):
            shutil.rmtree(FIXTURES_DIR) # Clean up from previous runs if any
        os.makedirs(FIXTURES_DIR)

        # Create dummy EPUB
        cls.sample_epub_path = os.path.join(FIXTURES_DIR, "sample.epub")
        cls.epub_content_paragraph1 = "This is sample EPUB content for integration test."
        cls.epub_content_paragraph2 = "Another paragraph to verify extraction."
        
        book = epub.EpubBook()
        book.set_identifier('id_integ_epub')
        book.set_title('Sample Integration EPUB')
        book.set_language('en')
        c1 = epub.EpubHtml(title='Chapter 1', file_name='chap1.xhtml', lang='en')
        c1.content = f'<h1>Chapter 1</h1><p>{cls.epub_content_paragraph1}</p><p>{cls.epub_content_paragraph2}</p>'
        book.add_item(c1)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ['nav', c1]
        epub.write_epub(cls.sample_epub_path, book, {})

        # Create dummy PDF
        cls.sample_pdf_path = os.path.join(FIXTURES_DIR, "sample.pdf")
        cls.pdf_content_line1 = "Hello PDF for integration test."
        cls.pdf_content_line2 = "This is a test PDF document for Morthy."
        cls.pdf_content_page2 = "Page two of integration PDF."

        c = canvas.Canvas(cls.sample_pdf_path, pagesize=letter)
        textobject = c.beginText(100, 750)
        textobject.textLine(cls.pdf_content_line1)
        textobject.textLine(cls.pdf_content_line2)
        c.drawText(textobject)
        c.showPage() 
        textobject = c.beginText(100, 750)
        textobject.textLine(cls.pdf_content_page2)
        c.drawText(textobject)
        c.save()
        
        # Create a malformed EPUB (e.g., a text file with .epub extension)
        cls.malformed_epub_path = os.path.join(FIXTURES_DIR, "malformed.epub")
        with open(cls.malformed_epub_path, "w") as f:
            f.write("This is not a valid EPUB zip file.")

        # Create a dummy unsupported file (.txt)
        cls.sample_unsupported_path = os.path.join(FIXTURES_DIR, "document.txt")
        with open(cls.sample_unsupported_path, "w") as f:
            f.write("This is a plain text file and is unsupported.")
        
        # Path for a non-existent file
        cls.non_existent_file_path = os.path.join(FIXTURES_DIR, "non_existent_book.epub")


    @classmethod
    def tearDownClass(cls):
        if os.path.exists(FIXTURES_DIR):
            shutil.rmtree(FIXTURES_DIR)

    @patch('main.convert_text_to_speech') 
    @patch('builtins.print') 
    def test_successful_epub_conversion_flow(self, mock_print, mock_tts):
        mock_tts.return_value = (True, "Successfully converted to audio.") 
        
        output_mp3_filename = 'output_epub.mp3'
        output_mp3_path = os.path.join(FIXTURES_DIR, output_mp3_filename)
        
        test_args = ['main.py', self.sample_epub_path, '--output_file', output_mp3_path, '--lang', 'fr']
        
        with patch.object(sys, 'argv', test_args):
            main_script.main()

        self.assertTrue(mock_tts.called, "convert_text_to_speech was not called.")
        args, kwargs = mock_tts.call_args
        extracted_text = args[0]
        output_file_called = args[1]
        lang_called = args[2]

        self.assertIn(self.epub_content_paragraph1, extracted_text)
        self.assertIn(self.epub_content_paragraph2, extracted_text)
        self.assertEqual(output_mp3_path, output_file_called)
        self.assertEqual('fr', lang_called)

        expected_success_message = f"Audiobook saved as {output_mp3_path}."
        mock_print.assert_any_call(expected_success_message)
        mock_print.assert_any_call("Successfully converted to audio.")

    @patch('main.convert_text_to_speech')
    @patch('builtins.print')
    def test_successful_pdf_conversion_flow(self, mock_print, mock_tts):
        mock_tts.return_value = (True, "Successfully converted PDF to audio.")
        
        expected_output_pdf_mp3_path = os.path.join(FIXTURES_DIR, 'sample.mp3')
        if os.path.exists(expected_output_pdf_mp3_path): 
            os.remove(expected_output_pdf_mp3_path)

        test_args = ['main.py', self.sample_pdf_path] 
        
        with patch.object(sys, 'argv', test_args):
            main_script.main()

        self.assertTrue(mock_tts.called)
        args, kwargs = mock_tts.call_args
        extracted_text = args[0]
        output_file_called = args[1]
        lang_called = args[2] 

        self.assertIn(self.pdf_content_line1, extracted_text)
        self.assertIn(self.pdf_content_line2, extracted_text)
        self.assertIn(self.pdf_content_page2, extracted_text)
        self.assertEqual(expected_output_pdf_mp3_path, output_file_called)
        self.assertEqual('en', lang_called) # Default language

        mock_print.assert_any_call(f"Audiobook saved as {expected_output_pdf_mp3_path}.")
        mock_print.assert_any_call("Successfully converted PDF to audio.")
        if os.path.exists(expected_output_pdf_mp3_path): 
             os.remove(expected_output_pdf_mp3_path)

    @patch('main.convert_text_to_speech')
    @patch('builtins.print')
    def test_main_handles_corrupted_epub_integration(self, mock_print, mock_tts):
        test_args = ['main.py', self.malformed_epub_path]
        
        with patch.object(sys, 'argv', test_args):
            main_script.main()

        mock_tts.assert_not_called()
        # The parser.py->extract_text_from_epub returns "Error: Invalid or corrupted EPUB file."
        # main.py prints "Error during text extraction: " + that message.
        mock_print.assert_any_call("Error during text extraction: Error: Invalid or corrupted EPUB file.")

    @patch('main.convert_text_to_speech')
    @patch('builtins.print')
    def test_main_handles_tts_api_error_integration(self, mock_print, mock_tts):
        mock_tts.return_value = (False, "gTTS Network Error") # Simulate TTS failure
        
        test_args = ['main.py', self.sample_epub_path] # Using valid EPUB
        
        with patch.object(sys, 'argv', test_args):
            main_script.main()
            
        mock_tts.assert_called_once() # TTS should be called
        # main.py prints "Error during TTS conversion: " + message from TTS
        mock_print.assert_any_call("Error during TTS conversion: gTTS Network Error")

    @patch('main.extract_text_from_epub')
    @patch('main.extract_text_from_pdf')
    @patch('main.extract_text_from_fb2')
    @patch('main.convert_text_to_speech')
    @patch('builtins.print')
    def test_main_handles_unsupported_file_type_integration(self, mock_print, mock_tts, mock_fb2_parser, mock_pdf_parser, mock_epub_parser):
        test_args = ['main.py', self.sample_unsupported_path] # .txt file
        
        with patch.object(sys, 'argv', test_args):
            main_script.main()

        mock_epub_parser.assert_not_called()
        mock_pdf_parser.assert_not_called()
        mock_fb2_parser.assert_not_called()
        mock_tts.assert_not_called()
        mock_print.assert_any_call("Error: Unsupported file type '.txt'. Only .epub, .pdf, and .fb2 are supported.")

    @patch('main.extract_text_from_epub') # Patch to check it's not called
    @patch('main.extract_text_from_pdf')   # Patch to check it's not called
    @patch('main.extract_text_from_fb2')  # Patch to check it's not called
    @patch('main.convert_text_to_speech') # Patch to check it's not called
    @patch('builtins.print')
    def test_main_handles_input_file_not_found_integration(self, mock_print, mock_tts, mock_fb2_parser, mock_pdf_parser, mock_epub_parser):
        test_args = ['main.py', self.non_existent_file_path]
        
        with patch.object(sys, 'argv', test_args):
            main_script.main()
        
        mock_epub_parser.assert_not_called()
        mock_pdf_parser.assert_not_called()
        mock_fb2_parser.assert_not_called()
        mock_tts.assert_not_called()
        mock_print.assert_any_call(f"Error: Input file '{self.non_existent_file_path}' not found.")


if __name__ == '__main__':
    unittest.main()
