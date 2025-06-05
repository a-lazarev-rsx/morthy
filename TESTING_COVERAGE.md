# Frontend Test Coverage Audit - 2025-06-05

## Summary
- Added tests for `App.tsx` and `main.tsx`.
- Achieved 100% test coverage for `App.tsx`, `main.tsx`, `components/ui/button.tsx`, `components/ui/card.tsx`, and `lib/utils.ts`.
- Overall frontend code coverage significantly improved.

## Coverage Report

```
-------------------|---------|----------|---------|---------|-------------------
File               | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s
-------------------|---------|----------|---------|---------|-------------------
All files          |   55.76 |    71.42 |      50 |   55.76 |
 vite-react-app    |       0 |        0 |       0 |       0 |
  ...css.config.js |       0 |        0 |       0 |       0 | 1-6
  ...ind.config.js |       0 |        0 |       0 |       0 | 1-86
 ...-react-app/src |     100 |      100 |     100 |     100 |
  App.tsx          |     100 |      100 |     100 |     100 |
  main.tsx         |     100 |      100 |     100 |     100 |
 .../components/ui |     100 |      100 |     100 |     100 |
  button.tsx       |     100 |      100 |     100 |     100 |
  card.tsx         |     100 |      100 |     100 |     100 |
 ...ct-app/src/lib |     100 |      100 |     100 |     100 |
  utils.ts         |     100 |      100 |     100 |     100 |
-------------------|---------|----------|---------|---------|-------------------
```

**Note:** Configuration files (`postcss.config.js`, `tailwind.config.js`) are not included in the coverage metrics for application logic.

---
*(Existing content of TESTING_COVERAGE.md will be below this line)*
# Test Coverage Documentation for Morthy Audiobook Generator
=======
## Backend Test Coverage Audit (as of 2025-06-05)

Overall backend code coverage: **50%**

### Coverage Summary by Module:
- **main.py**: 90%
- **parser.py**: 41%
- **tts.py**: 43%
- **web_app.py**: 53%

### Detailed Analysis and Areas for Improvement:

**parser.py (41% coverage)**
- Missing lines indicate that specific error handling branches, edge cases in content extraction (e.g., unusual structures in EPUB/FB2, specific PDF layouts), or variations in file encodings might not be fully tested.
- **Suggestion**: Add tests for more diverse valid and malformed/corrupted EPUB, PDF, and FB2 files. Consider testing files with different encodings if applicable.

**tts.py (43% coverage)**
- Missing lines suggest that not all error conditions from the gTTS library (e.g., network issues, specific API errors beyond basic ones) or file system errors (e.g., issues writing the MP3 file to disk if not fully mocked) are covered. The core success path seems tested, but robustness for failures could be improved.
- **Suggestion**: Mock more specific gTTS exceptions and os-level errors during file save operations to test error handling paths.

**web_app.py (53% coverage)**
- Missing lines likely relate to:
    - Successful file upload and processing paths for each supported file type (EPUB, PDF, FB2). Current tests only cover the index page and unsupported file type uploads.
    - Specific error handling during file processing within the web context (e.g., if `extract_text_from_*` or `convert_text_to_speech` functions (called by `main_web`) return errors).
    - Testing the `download_file` route.
    - Edge cases in form submissions (e.g., no file selected, different languages chosen).
- **Suggestion**: Add tests for successful uploads of EPUB, PDF, and FB2 files, verifying the response and that audio generation is triggered. Test error handling when backend processing fails. Add tests for the download route.

### Full Text Report:
```
Name         Stmts   Miss  Cover   Missing
------------------------------------------
main.py         52      5    90%   76, 95-97, 106
parser.py      215    127    41%   38-39, 71, 85, 110-112, 120, 124, 127-136, 163-170, 189-197, 206-209, 214-374
tts.py          42     24    43%   45-85
web_app.py      68     32    53%   16, 18, 33, 36, 38-73, 88, 91
------------------------------------------
TOTAL          377    188    50%
```

---
