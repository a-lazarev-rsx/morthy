import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Add project root to sys.path to allow importing main, parser, tts
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# We will need to import 'main' to call 'main.main()'
import main as main_script # Use an alias to avoid confusion

class TestMainArgParsing(unittest.TestCase):

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True) 
    @patch('main.extract_text_from_epub', return_value="Mocked text") 
    @patch('main.convert_text_to_speech', return_value=(True, "Success")) 
    def test_argparse_input_file_only(self, mock_tts, mock_parser_epub, mock_exists, mock_parse_args): # Renamed mock_parser to mock_parser_epub
        mock_args_instance = MagicMock()
        mock_args_instance.input_file = "test.epub"
        mock_args_instance.output_file = None
        mock_args_instance.lang = "en"
        mock_parse_args.return_value = mock_args_instance

        main_script.main()

        mock_parse_args.assert_called_once()
        self.assertEqual(main_script.get_parser_func(".epub"), main_script.extract_text_from_epub)
        mock_parser_epub.assert_called_with("test.epub")
        expected_output_file = "test.mp3"
        mock_tts.assert_called_with("Mocked text", expected_output_file, "en")

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True)
    @patch('main.extract_text_from_epub', return_value="Mocked text") 
    @patch('main.convert_text_to_speech', return_value=(True, "Success"))
    def test_argparse_with_output_file(self, mock_tts, mock_parser_epub, mock_exists, mock_parse_args): # Renamed mock_parser to mock_parser_epub
        mock_args_instance = MagicMock()
        mock_args_instance.input_file = "test.epub"
        mock_args_instance.output_file = "custom.mp3"
        mock_args_instance.lang = "en"
        mock_parse_args.return_value = mock_args_instance

        main_script.main()

        mock_parse_args.assert_called_once()
        self.assertEqual(main_script.get_parser_func(".epub"), main_script.extract_text_from_epub)
        mock_parser_epub.assert_called_with("test.epub")
        mock_tts.assert_called_with("Mocked text", "custom.mp3", "en")

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True)
    @patch('main.extract_text_from_epub', return_value="Mocked text")
    @patch('main.convert_text_to_speech', return_value=(True, "Success"))
    def test_argparse_with_lang(self, mock_tts, mock_parser_epub, mock_exists, mock_parse_args): # Renamed mock_parser to mock_parser_epub
        mock_args_instance = MagicMock()
        mock_args_instance.input_file = "test.epub"
        mock_args_instance.output_file = None
        mock_args_instance.lang = "fr"
        mock_parse_args.return_value = mock_args_instance

        main_script.main()

        mock_parse_args.assert_called_once()
        self.assertEqual(main_script.get_parser_func(".epub"), main_script.extract_text_from_epub)
        mock_parser_epub.assert_called_with("test.epub")
        mock_tts.assert_called_with("Mocked text", "test.mp3", "fr")
    
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True) 
    @patch('main.extract_text_from_pdf', return_value="Mocked PDF text") 
    @patch('main.convert_text_to_speech', return_value=(True, "Success"))
    def test_argparse_input_file_pdf(self, mock_tts, mock_pdf_parser, mock_exists, mock_parse_args):
        mock_args_instance = MagicMock()
        mock_args_instance.input_file = "path/to/document.pdf"
        mock_args_instance.output_file = None
        mock_args_instance.lang = "de"
        mock_parse_args.return_value = mock_args_instance

        main_script.main()

        mock_parse_args.assert_called_once()
        self.assertEqual(main_script.get_parser_func(".pdf"), main_script.extract_text_from_pdf)
        mock_pdf_parser.assert_called_with("path/to/document.pdf")
        expected_output_file = "path/to/document.mp3"
        mock_tts.assert_called_with("Mocked PDF text", expected_output_file, "de")

    @patch('main.argparse.ArgumentParser.parse_args')
    def test_argparse_missing_input_file(self, mock_parse_args):
        # Simulate command: python main.py (no input file)
        # argparse, when set up with a required argument and it's missing,
        # will call .error() which in turn raises SystemExit.
        # We need to mock parse_args to simulate this behavior.
        
        original_argv = sys.argv
        sys.argv = ['main.py'] # Simulate no command-line arguments for input_file
        
        # Configure the mock_parse_args (which is patching argparse.ArgumentParser.parse_args)
        # to raise SystemExit, as argparse would if a required argument is missing.
        # The actual ArgumentParser instance in main.py's setup_arg_parser() will have its
        # parse_args() method replaced by this mock.
        mock_parse_args.side_effect = SystemExit(2) # Standard exit code for command line usage errors

        with self.assertRaises(SystemExit) as cm:
            main_script.main() # This will call setup_arg_parser().parse_args() -> mock_parse_args
        
        self.assertEqual(cm.exception.code, 2) # Check the exit code
        mock_parse_args.assert_called_once() # Ensure our mock was called
        
        sys.argv = original_argv # Restore original argv


class TestMainDispatchAndErrors(unittest.TestCase):

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True)
    @patch('main.convert_text_to_speech', return_value=(True, "Success"))
    @patch('main.extract_text_from_fb2')
    @patch('main.extract_text_from_pdf')
    @patch('main.extract_text_from_epub')
    def test_dispatch_epub(self, mock_epub_parser, mock_pdf_parser, mock_fb2_parser, mock_tts, mock_exists, mock_parse_args):
        mock_args = MagicMock()
        mock_args.input_file = "book.epub"
        mock_args.output_file = None
        mock_args.lang = "en"
        mock_parse_args.return_value = mock_args
        mock_epub_parser.return_value = "epub text"

        main_script.main()
        mock_epub_parser.assert_called_once_with("book.epub")
        mock_pdf_parser.assert_not_called()
        mock_fb2_parser.assert_not_called()
        mock_tts.assert_called_once_with("epub text", "book.mp3", "en")

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True)
    @patch('main.convert_text_to_speech', return_value=(True, "Success"))
    @patch('main.extract_text_from_fb2')
    @patch('main.extract_text_from_pdf')
    @patch('main.extract_text_from_epub')
    def test_dispatch_pdf(self, mock_epub_parser, mock_pdf_parser, mock_fb2_parser, mock_tts, mock_exists, mock_parse_args):
        mock_args = MagicMock()
        mock_args.input_file = "doc.pdf"
        mock_args.output_file = None
        mock_args.lang = "en"
        mock_parse_args.return_value = mock_args
        mock_pdf_parser.return_value = "pdf text"

        main_script.main()
        mock_pdf_parser.assert_called_once_with("doc.pdf")
        mock_epub_parser.assert_not_called()
        mock_fb2_parser.assert_not_called()
        mock_tts.assert_called_once_with("pdf text", "doc.mp3", "en")

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True)
    @patch('main.convert_text_to_speech', return_value=(True, "Success"))
    @patch('main.extract_text_from_fb2')
    @patch('main.extract_text_from_pdf')
    @patch('main.extract_text_from_epub')
    def test_dispatch_fb2(self, mock_epub_parser, mock_pdf_parser, mock_fb2_parser, mock_tts, mock_exists, mock_parse_args):
        mock_args = MagicMock()
        mock_args.input_file = "story.fb2"
        mock_args.output_file = None
        mock_args.lang = "en"
        mock_parse_args.return_value = mock_args
        mock_fb2_parser.return_value = "fb2 text"

        main_script.main()
        mock_fb2_parser.assert_called_once_with("story.fb2")
        mock_epub_parser.assert_not_called()
        mock_pdf_parser.assert_not_called()
        mock_tts.assert_called_once_with("fb2 text", "story.mp3", "en")

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True)
    @patch('builtins.print')
    @patch('main.convert_text_to_speech')
    @patch('main.extract_text_from_fb2')
    @patch('main.extract_text_from_pdf')
    @patch('main.extract_text_from_epub')
    def test_dispatch_unsupported_extension(self, mock_epub, mock_pdf, mock_fb2, mock_tts, mock_print, mock_exists, mock_parse_args):
        mock_args = MagicMock()
        mock_args.input_file = "archive.zip" 
        mock_args.output_file = None
        mock_args.lang = "en"
        mock_parse_args.return_value = mock_args

        main_script.main()

        mock_epub.assert_not_called()
        mock_pdf.assert_not_called()
        mock_fb2.assert_not_called()
        mock_tts.assert_not_called()
        mock_print.assert_any_call("Error: Unsupported file type '.zip'. Only .epub, .pdf, and .fb2 are supported.")

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True) 
    @patch('builtins.print')
    @patch('main.convert_text_to_speech') 
    @patch('main.extract_text_from_epub') 
    def test_main_handles_parser_error(self, mock_parser_epub, mock_tts, mock_print, mock_exists, mock_parse_args): # Renamed mock_parser to mock_parser_epub
        mock_args = MagicMock()
        mock_args.input_file = "bad.epub"
        mock_args.output_file = None
        mock_args.lang = "en"
        mock_parse_args.return_value = mock_args
        
        mock_parser_epub.return_value = "Error: Corrupted EPUB" 

        main_script.main()

        mock_parser_epub.assert_called_once_with("bad.epub")
        mock_print.assert_any_call("Error during text extraction: Error: Corrupted EPUB")
        mock_tts.assert_not_called()

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True)
    @patch('builtins.print')
    @patch('main.convert_text_to_speech')
    @patch('main.extract_text_from_pdf') 
    def test_main_handles_parser_returns_none(self, mock_parser_pdf, mock_tts, mock_print, mock_exists, mock_parse_args): # Renamed mock_parser to mock_parser_pdf
        mock_args = MagicMock()
        mock_args.input_file = "empty_or_failed.pdf"
        mock_args.output_file = None
        mock_args.lang = "en"
        mock_parse_args.return_value = mock_args
        
        mock_parser_pdf.return_value = None 

        main_script.main()
        mock_parser_pdf.assert_called_once_with("empty_or_failed.pdf")
        mock_print.assert_any_call("Error during text extraction: Unknown error during text extraction.")
        mock_tts.assert_not_called()

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True)
    @patch('builtins.print')
    @patch('main.convert_text_to_speech')
    @patch('main.extract_text_from_epub')
    def test_main_handles_empty_extracted_text(self, mock_parser_epub, mock_tts, mock_print, mock_exists, mock_parse_args): # Renamed mock_parser to mock_parser_epub
        mock_args = MagicMock()
        mock_args.input_file = "whitespace.epub"
        mock_args.output_file = None
        mock_args.lang = "en"
        mock_parse_args.return_value = mock_args
        
        mock_parser_epub.return_value = "   " 

        main_script.main()
        mock_parser_epub.assert_called_once_with("whitespace.epub")
        mock_print.assert_any_call("Info: No text content was extracted from 'whitespace.epub'. Cannot generate audiobook.")
        mock_tts.assert_not_called()

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=True)
    @patch('builtins.print')
    @patch('main.convert_text_to_speech')
    @patch('main.extract_text_from_epub', return_value="Valid text for TTS") 
    def test_main_handles_tts_failure(self, mock_parser_epub, mock_tts, mock_print, mock_exists, mock_parse_args):
        mock_args = MagicMock()
        mock_args.input_file = "tts_fail.epub"
        mock_args.output_file = "output.mp3" 
        mock_args.lang = "en"
        mock_parse_args.return_value = mock_args
        
        mock_tts.return_value = (False, "TTS API Error") 

        main_script.main()
        
        mock_parser_epub.assert_called_once_with("tts_fail.epub")
        mock_tts.assert_called_once_with("Valid text for TTS", "output.mp3", "en")
        mock_print.assert_any_call("Error during TTS conversion: TTS API Error")

    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('main.os.path.exists', return_value=False) 
    @patch('builtins.print')
    @patch('main.extract_text_from_epub') 
    @patch('main.convert_text_to_speech') 
    def test_main_input_file_not_found(self, mock_convert_tts, mock_extract_epub, mock_print, mock_exists, mock_parse_args):
        mock_args = MagicMock()
        mock_args.input_file = "nonexistent.epub"
        # No need to set output_file or lang on mock_args if main exits before using them.
        # However, parse_args returns them, so they should be attributes of the mock_args object.
        mock_args.output_file = None 
        mock_args.lang = "en"
        mock_parse_args.return_value = mock_args 

        main_script.main()

        mock_exists.assert_called_once_with("nonexistent.epub")
        mock_print.assert_any_call("Error: Input file 'nonexistent.epub' not found.")
        mock_extract_epub.assert_not_called()
        mock_convert_tts.assert_not_called()

if __name__ == '__main__':
    unittest.main()
