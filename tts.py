"""
Text-to-Speech (TTS) module for converting text to audio files.

This module uses the gTTS (Google Text-to-Speech) library to convert
a given text string into an MP3 audio file. It includes error handling
for common TTS-related issues.
"""
from gtts import gTTS, gTTSError
import os

def convert_text_to_speech(text: str, output_filepath: str, lang: str = 'en'):
    """
    Converts a text string to speech and saves it as an MP3 file.

    Args:
        text (str): The text to convert to speech.
        output_filepath (str): The path to save the output MP3 file.
        lang (str, optional): The language of the text. Defaults to 'en'.

    Returns:
        bool: True if conversion was successful and file was saved, False otherwise.
        str: A message indicating success or failure.
    """
    if not text:
        return False, "Error: Input text cannot be empty."
    if not output_filepath.lower().endswith('.mp3'):
        return False, "Error: Output filepath must end with .mp3"

    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_filepath)
        return True, f"Successfully converted text to speech and saved to {output_filepath}"
    except gTTSError as e:
        # This can catch issues like language not supported or network errors if gTTS hits API limits or has issues.
        # Example: gTTSError: Failed to connect. Detail: All gTTS TLDs are blocked.
        return False, f"gTTS Error: {e}"
    except ValueError as e:
        # Catch ValueError specifically, as gTTS raises this for unsupported languages
        # when lang_check is True (default).
        return False, f"ValueError (likely unsupported language): {e}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    sample_text = "Hello, this is a test of the text-to-speech conversion using gTTS."
    output_filename = "test_audio.mp3"
    
    print(f"Attempting to convert text to speech and save as '{output_filename}'...")
    
    success, message = convert_text_to_speech(sample_text, output_filename)
    
    if success:
        print(message)
        # Check if file exists as an extra verification
        if os.path.exists(output_filename):
            print(f"File '{output_filename}' created successfully.")
            # Optional: Play the audio if a player is available (platform dependent)
            # For example, on Linux: os.system(f"xdg-open {output_filename}")
            # On macOS: os.system(f"open {output_filename}")
            
            # Clean up the test file
            try:
                os.remove(output_filename)
                print(f"Cleaned up test file '{output_filename}'.")
            except OSError as e:
                print(f"Error cleaning up test file '{output_filename}': {e}")
        else:
            print(f"Error: Conversion reported success, but file '{output_filename}' was not found.")
    else:
        print(message)

    # Test with empty text
    print("\nTesting with empty text:")
    success_empty, message_empty = convert_text_to_speech("", "empty_text.mp3")
    print(message_empty)

    # Test with invalid language
    print("\nTesting with invalid language code:")
    success_lang, message_lang = convert_text_to_speech("Test", "invalid_lang.mp3", lang="xx")
    print(message_lang)
    
    # Test with invalid output filename
    print("\nTesting with invalid output filename:")
    success_fname, message_fname = convert_text_to_speech("Test", "invalid_fname.txt")
    print(message_fname)
