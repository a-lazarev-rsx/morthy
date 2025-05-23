# Audiobook Generator

A command-line tool to convert book files (currently EPUB and PDF) into MP3 audiobooks using Text-to-Speech (TTS).

## Features

*   Supports EPUB (.epub) and PDF (.pdf) file formats.
*   Converts extracted text to speech using Google Text-to-Speech (gTTS).
*   Allows specifying output MP3 filename.
*   Allows specifying the language for TTS.
*   Basic error handling for file issues and TTS conversion.
*   Includes a suite of unit tests.

## Requirements

The following Python libraries are required:

*   `EbookLib>=0.19` (for EPUB parsing)
*   `PyPDF2>=3.0.1` (for PDF parsing)
*   `gTTS>=2.5.4` (for Text-to-Speech)
*   `BeautifulSoup4>=4.13.4` (for HTML processing in EPUBs)
*   `lxml>=5.4.0` (XML processing, often a dependency for EbookLib)
*   `reportlab>=4.4.1` (for creating sample PDFs in the test suite)

## Installation

1.  Clone this repository (or download the source files).
2.  Ensure you have Python 3.6+ installed.
3.  Install the required libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script from the command line using `python main.py`.

**Syntax:**

```bash
python main.py <input_file> [--output_file <output_name.mp3>] [--lang <language_code>]
```

**Arguments:**

*   `input_file`: (Required) Path to the input book file. Supported formats: `.epub`, `.pdf`.
*   `--output_file`: (Optional) Desired name for the output MP3 file. If not provided, it defaults to the input file name with an `.mp3` extension (e.g., `mybook.epub` becomes `mybook.mp3`).
*   `--lang`: (Optional) Language code for the text-to-speech conversion (e.g., 'en' for English, 'es' for Spanish). Defaults to 'en'.

**Examples:**

1.  **Convert an EPUB file with default output name and English language:**
    ```bash
    python main.py my_book.epub
    ```
    *(Output will be `my_book.mp3`)*

2.  **Convert a PDF file with a custom output name and Spanish language:**
    ```bash
    python main.py "My Document.pdf" --output_file "audio_doc.mp3" --lang es
    ```

**Supported Formats:**

*   EPUB (.epub)
*   PDF (.pdf)

*Note: FB2 (.fb2) support was initially planned and has partial implementation in `parser.py` but is currently non-functional due to unresolved library import issues for the `fb2` package. It is considered a feature for future improvement.*

## Error Handling

The script includes handling for common errors such as:

*   Input file not found.
*   Unsupported file formats.
*   Errors during text extraction from files (e.g., corrupted files, encrypted PDFs that cannot be opened).
*   Errors during the Text-to-Speech conversion (e.g., invalid language code, network issues with gTTS).
*   Empty or no extractable text content in the input file.
*   Unexpected issues during processing (caught by a general error handler).

Error messages are printed to the console to inform the user.

## Running Tests

Unit tests are provided to ensure the functionality of individual components (parsing, TTS). To run the tests:

1.  Make sure you are in the project's root directory.
2.  Ensure all dependencies, including `reportlab` (for PDF test fixtures), are installed.
3.  Run the following command:
    ```bash
    python -m unittest discover tests
    ```

## Contributing

Contributions are welcome! If you find a bug or have an idea for an improvement, please feel free to open an issue or submit a pull request.

*(This is a sample project, so active maintenance might vary)*
