"""
Main script for the Audiobook Generator.

This script provides a command-line interface to convert book files
(EPUB, PDF) into MP3 audiobooks using text-to-speech (TTS).
It parses command-line arguments, extracts text from the input file,
and then converts the extracted text to an MP3 audio file.
"""
import argparse
import os

def main():
    """
    Main function to parse arguments and orchestrate the audiobook generation.

    Handles command-line argument parsing, input file validation, text extraction
    based on file type, and text-to-speech conversion. It prints progress
    and error messages to the console.
    """
    parser = argparse.ArgumentParser(description="Convert a book file (EPUB, FB2, PDF) to an MP3 audiobook.")
    
    parser.add_argument("input_file", 
                        help="Path to the input book file (e.g., EPUB, FB2, PDF).")
    
    parser.add_argument("--output_file", 
                        help="Optional: Desired name for the output MP3 file. "
                             "If not provided, it defaults to the input file name with an .mp3 extension.")
    
    parser.add_argument("--lang", 
                        default='en', 
                        help="Optional: Language for the text-to-speech conversion (e.g., 'en', 'es'). Defaults to 'en'.")
    
    args = parser.parse_args()
    
    # Determine default output file name if not provided
    output_file = args.output_file
    if not output_file:
        base, ext = os.path.splitext(args.input_file)
        output_file = base + ".mp3"
        
    print(f"Input file: {args.input_file}")
    print(f"Output file: {output_file}")
    print(f"Language: {args.lang}")

    try:
        # Import parser and tts functions
        from parser import extract_text_from_epub, extract_text_from_pdf, extract_text_from_fb2
        from tts import convert_text_to_speech

        # Determine file type and extract text
        _, file_extension = os.path.splitext(args.input_file)
        file_extension = file_extension.lower()

        extracted_text = None
        print(f"\nExtracting text from {args.input_file}...")

        if not os.path.exists(args.input_file):
            print(f"Error: Input file '{args.input_file}' not found.")
            return

        if file_extension == '.epub':
            extracted_text = extract_text_from_epub(args.input_file)
        elif file_extension == '.pdf':
            extracted_text = extract_text_from_pdf(args.input_file)
        elif file_extension == '.fb2':
            extracted_text = extract_text_from_fb2(args.input_file)
        else:
            print(f"Error: Unsupported file type '{file_extension}'. Only .epub, .pdf, and .fb2 are supported.")
            return

        # Check if text extraction was successful (parser functions return error strings on failure)
        if extracted_text is None or extracted_text.startswith("Error:") or extracted_text.startswith("Info: FB2 body was parsed, but no text content was found"):
            # Handle cases where parser returns an error message or no text
            error_message = extracted_text if extracted_text else "Unknown error during text extraction."
            if extracted_text is not None and extracted_text.startswith("Info: FB2 body was parsed, but no text content was found"):
                 print(f"Info: No text content found in the document by the parser: {args.input_file}") # Specific message for empty FB2
            else:
                 print(f"Error during text extraction: {error_message}")
            return

        if not extracted_text.strip(): # Check if extracted text is empty or only whitespace
            print(f"Info: No text content was extracted from '{args.input_file}'. Cannot generate audiobook.")
            return

        print("Text extracted successfully. Converting to speech...")
        
        # Convert text to speech
        tts_success, tts_message = convert_text_to_speech(extracted_text, output_file, args.lang)
        
        if tts_success:
            print(f"Audiobook saved as {output_file}.")
        else:
            print(f"Error during TTS conversion: {tts_message}")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("This could be due to an issue with the input file, a problem with a library, or an internal script error.")
        # For debugging, one might want to log the full traceback, but for a user, a simpler message is better.
        # import traceback
        # print("\n--- Debug Traceback ---")
        # traceback.print_exc()
        # print("--- End Debug Traceback ---")


if __name__ == '__main__':
    main()
