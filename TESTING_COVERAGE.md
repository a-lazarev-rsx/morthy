# Test Coverage Documentation for Morthy Audiobook Generator

This document outlines the current state of test coverage for the Morthy Audiobook Generator, identifies gaps, and proposes necessary additions to ensure robustness and reliability.

## 1. Current Test Coverage Summary

The project utilizes Python's `unittest` framework. Existing tests are organized into modules within the `tests/` directory.

### 1.1. `parser.py` (Text Extraction)

*   **`extract_text_from_epub`**: 
    *   Covered: Valid EPUB, non-existent EPUB, malformed EPUB (e.g., not a zip file), EPUB with empty textual content but present HTML tags.
    *   Mechanism: Uses dummy EPUB files created programmatically using the `ebooklib` library.
*   **`extract_text_from_pdf`**:
    *   Covered: Valid PDF, non-existent PDF, malformed PDF (e.g., a text file renamed to `.pdf`).
    *   Mechanism: Uses dummy PDF files created programmatically using `reportlab`.
*   **`extract_text_from_fb2`**:
    *   **No test coverage.** Tests are explicitly omitted in `tests/test_parser.py` due to unresolved `ImportError` issues with the required `fb2` parsing library. The function itself includes error handling for when the library is not found.

### 1.2. `tts.py` (Text-to-Speech)

*   **`convert_text_to_speech`**:
    *   Covered: Successful conversion, empty input text, invalid output file extension (not `.mp3`), invalid language code (simulating `ValueError`), and gTTS API/network errors (simulating `gTTSError`).
    *   Mechanism: Uses `unittest.mock` to patch the `gTTS` class and its methods, avoiding actual calls to the gTTS service and file system operations for MP3 creation.

### 1.3. `main.py` (Main Script Logic)

*   **No dedicated unit tests.** The command-line argument parsing, file type dispatch logic, orchestration of parser and TTS calls, and overall error handling within `main.py` are not directly unit-tested.

### 1.4. Integration Testing

*   **No dedicated integration tests.** There are no tests that verify the end-to-end workflow of the application, from command-line invocation (simulated) through parsing and TTS (mocked), for any file type.

## 2. Identified Gaps and Areas for Improvement

Based on the current status, the key areas for improving test coverage are:

1.  **Unit Tests for `main.py`**: Essential for validating the core application logic.
2.  **Integration Tests**: Crucial for ensuring all components work together correctly.
3.  **FB2 Parsing Tests**: Dependent on resolving the underlying library issues for `extract_text_from_fb2`.

## 3. Proposed Additional Unit Tests for `main.py`

A new test file, e.g., `tests/test_main.py`, should be created to house the following unit tests. Mocking (`unittest.mock`) will be essential for isolating `main.py`'s logic.

*   **Argument Parsing (`argparse`)**:
    *   Test successful parsing with only the input file.
    *   Test successful parsing with input file and `--output_file`.
    *   Test successful parsing with input file and `--lang`.
    *   Test handling of missing required input file argument (e.g., expect `SystemExit`).
*   **File Type Dispatch Logic**:
    *   Test that `parser.extract_text_from_epub` is called for `.epub` files.
    *   Test that `parser.extract_text_from_pdf` is called for `.pdf` files.
    *   Test that `parser.extract_text_from_fb2` is called for `.fb2` files.
    *   Test handling of unsupported file extensions (e.g., `.txt`), ensuring an appropriate error message is printed and no parser is called.
*   **Default Output File Name Generation**:
    *   Test that an input like `book.epub` defaults to `book.mp3` for the output.
    *   Test that an input like `path/to/book.pdf` defaults to `path/to/book.mp3`.
*   **Error Handling (from `parser` and `tts` modules)**:
    *   Test that `main.py` correctly prints error messages returned by parser functions (e.g., if `extract_text_from_epub` returns "Error: Corrupted EPUB").
    *   Test that `main.py` handles cases where a parser returns `None` or empty/whitespace-only text.
    *   Test that `main.py` correctly prints error messages if `convert_text_to_speech` returns `(False, "TTS Error")`.
*   **Input File Existence Check**:
    *   Test the initial check in `main.py` for `os.path.exists(args.input_file)` and that it prints an error if the file is not found, preventing further processing.

**Mocking Strategy**: Utilize `unittest.mock.patch` for `sys.argv`, `argparse.ArgumentParser.parse_args`, `parser` module functions, `tts.convert_text_to_speech`, `os.path.exists`, and `builtins.print`.

## 4. Proposed Integration Tests

Integration tests should verify the flow between `main.py`, `parser.py` (using actual dummy files), and `tts.py` (mocked). A new file like `tests/test_integration.py` is recommended.

*   **Successful End-to-End Conversion (EPUB & PDF)**:
    *   For EPUB: Simulate `main.py` execution with a valid dummy EPUB. Verify the correct text is extracted (by checking the `text` argument passed to the mocked `tts.convert_text_to_speech`) and that `tts.convert_text_to_speech` is called with correct parameters. Verify success messages.
    *   For PDF: Similar to EPUB, using a valid dummy PDF.
*   **Main Application Error Handling**:
    *   Test `main.py`'s behavior when a (real) dummy parser input file is malformed (e.g., a corrupt EPUB), ensuring the error from the parser is caught and reported correctly by `main.py`, and TTS is not attempted.
    *   Test `main.py`'s behavior when `tts.convert_text_to_speech` (mocked) returns an error, ensuring it's reported correctly.
    *   Test `main.py` with an unsupported file type (e.g., `.txt`), verifying the correct error message and that no parsing/TTS occurs.
    *   Test `main.py` with a non-existent input file, verifying the correct error message.

**Fixture and Mocking Strategy**: Use temporary valid/invalid dummy files for EPUB/PDF inputs. Always mock `tts.convert_text_to_speech`. Use `@patch('sys.argv')` and `@patch('builtins.print')`.

## 5. Strategy for FB2 Test Coverage

FB2 support in `parser.py` is currently hampered by `ImportError` issues related to the `fb2` library.

1.  **Blocker**: Comprehensive testing of `extract_text_from_fb2` is blocked until these library import and functionality issues are resolved.
2.  **Resolution Steps**:
    *   Identify the correct, functional `fb2` Python library.
    *   Ensure it's properly installed and added to `requirements.txt`.
    *   Verify `parser.py` can successfully use it.
3.  **Required Unit Tests (Post-Resolution)**:
    *   Extraction from a valid, simple FB2 file.
    *   Handling of non-existent FB2 files.
    *   Handling of malformed/corrupt FB2 files (behavior depends on the library).
    *   Handling of FB2 files with no `<body>` or no text content.
4.  **Integration Testing (Post-Resolution)**:
    *   Include FB2 files in the end-to-end integration tests for `main.py` once unit tests for FB2 parsing are successful.

## 6. Recommendations

*   **Prioritize `main.py` Unit Tests**: These will provide significant value by covering the core application logic.
*   **Implement Integration Tests**: Start with EPUB and PDF to ensure the main workflows are solid.
*   **Address FB2 Library Issue**: If FB2 support is a priority, resolving the library dependency is the first step. Otherwise, this feature's (and its tests') status should be clearly marked as deferred or experimental.
*   **Test Data Management**: For integration tests, establish a clean way to manage dummy input files (e.g., a dedicated `tests/fixtures/` directory).

By addressing these areas, the Morthy Audiobook Generator will have a more comprehensive test suite, leading to higher quality and easier maintenance.
