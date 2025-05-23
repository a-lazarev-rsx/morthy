import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add project root to sys.path to allow importing tts module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from tts import convert_text_to_speech, gTTS # Import gTTS for isinstance check if needed, or gTTSError

# Define a directory for test output (if any files are temporarily created)
TEST_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
if not os.path.exists(TEST_OUTPUT_DIR):
    os.makedirs(TEST_OUTPUT_DIR)

class TestTextToSpeech(unittest.TestCase):

    def tearDown(self):
        # Clean up any files created during tests
        test_mp3_file = os.path.join(TEST_OUTPUT_DIR, "test_audio.mp3")
        if os.path.exists(test_mp3_file):
            os.remove(test_mp3_file)
        
        error_mp3_file = os.path.join(TEST_OUTPUT_DIR, "error_audio.mp3")
        if os.path.exists(error_mp3_file):
            os.remove(error_mp3_file)

    @patch('tts.gTTS') # Mock the gTTS class in the tts module
    def test_convert_text_to_speech_success(self, mock_gtts_class):
        # Configure the mock gTTS instance and its save method
        mock_gtts_instance = MagicMock()
        mock_gtts_class.return_value = mock_gtts_instance
        
        text = "Hello world"
        output_filepath = os.path.join(TEST_OUTPUT_DIR, "test_audio.mp3")
        
        success, message = convert_text_to_speech(text, output_filepath, lang='en')
        
        self.assertTrue(success)
        self.assertEqual(message, f"Successfully converted text to speech and saved to {output_filepath}")
        mock_gtts_class.assert_called_once_with(text=text, lang='en', slow=False)
        mock_gtts_instance.save.assert_called_once_with(output_filepath)
        # We don't check for os.path.exists here because gTTS().save() is mocked.
        # If we wanted to test file creation, we'd need a more complex mock or allow file creation.

    def test_convert_text_to_speech_empty_text(self):
        output_filepath = os.path.join(TEST_OUTPUT_DIR, "error_audio.mp3")
        success, message = convert_text_to_speech("", output_filepath)
        self.assertFalse(success)
        self.assertEqual(message, "Error: Input text cannot be empty.")

    def test_convert_text_to_speech_invalid_output_extension(self):
        success, message = convert_text_to_speech("test", "test_audio.txt")
        self.assertFalse(success)
        self.assertEqual(message, "Error: Output filepath must end with .mp3")

    @patch('tts.gTTS')
    def test_convert_text_to_speech_invalid_language(self, mock_gtts_class):
        # Simulate gTTS raising a ValueError for an invalid language
        mock_gtts_class.side_effect = ValueError("Language not supported: xx")
        
        text = "This will fail"
        output_filepath = os.path.join(TEST_OUTPUT_DIR, "error_audio.mp3")
        
        success, message = convert_text_to_speech(text, output_filepath, lang='xx')
        
        self.assertFalse(success)
        self.assertEqual(message, "ValueError (likely unsupported language): Language not supported: xx")
        mock_gtts_class.assert_called_once_with(text=text, lang='xx', slow=False)

    @patch('tts.gTTS')
    def test_convert_text_to_speech_gtts_error(self, mock_gtts_class):
        # Import gTTSError from tts module for this test
        from tts import gTTSError as TTS_gTTSError 

        # Configure the mock to raise gTTSError on save
        mock_gtts_instance = MagicMock()
        mock_gtts_instance.save.side_effect = TTS_gTTSError("Failed to connect or other API error")
        mock_gtts_class.return_value = mock_gtts_instance
        
        text = "Another test"
        output_filepath = os.path.join(TEST_OUTPUT_DIR, "error_audio.mp3")
        
        success, message = convert_text_to_speech(text, output_filepath)
        
        self.assertFalse(success)
        self.assertEqual(message, "gTTS Error: Failed to connect or other API error")
        mock_gtts_class.assert_called_once_with(text=text, lang='en', slow=False)
        mock_gtts_instance.save.assert_called_once_with(output_filepath)

    # Test for unexpected error (e.g., permission denied to write file, if not mocking .save())
    # This is harder to test reliably with mocks for .save() unless the mock itself raises an OSError.
    # For now, we assume that if .save() was not mocked and failed with OSError,
    # the `except Exception as e:` in tts.py would catch it.
    @patch('tts.gTTS')
    def test_convert_text_to_speech_unexpected_error_on_save(self, mock_gtts_class):
        mock_gtts_instance = MagicMock()
        mock_gtts_instance.save.side_effect = OSError("Simulated permission denied")
        mock_gtts_class.return_value = mock_gtts_instance

        text = "Text for unexpected error test"
        output_filepath = os.path.join(TEST_OUTPUT_DIR, "error_audio.mp3")

        success, message = convert_text_to_speech(text, output_filepath)

        self.assertFalse(success)
        self.assertEqual(message, "An unexpected error occurred: Simulated permission denied")


if __name__ == '__main__':
    unittest.main()
