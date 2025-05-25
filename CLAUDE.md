# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

Morthy is an audiobook generator with dual architecture:

### Python Backend (Root Directory)
- **Core Module**: `main.py` - CLI entry point for converting books (EPUB, PDF, FB2) to MP3
- **Parser Module**: `parser.py` - Text extraction from different book formats using ebooklib, PyPDF2, BeautifulSoup
- **TTS Module**: `tts.py` - Text-to-speech conversion using Google TTS (gTTS)
- **Web Interface**: `web_app.py` - Flask web server for file uploads and processing
- **Templates**: `templates/` - HTML templates for Flask web interface

### React Frontend (frontend/vite-react-app/)
- **Framework**: Vite + React 19 + Tailwind CSS + shadcn/ui components
- **Structure**: Standard Vite React app with component library integration
- **Components**: Located in `src/components/ui/` using shadcn/ui patterns

## Development Commands

### Python Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run CLI tool
python main.py <input_file> [--output_file <output.mp3>] [--lang <language>]

# Run web interface
python web_app.py

# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_parser
python -m unittest tests.test_tts
python -m unittest tests.test_web_app
```

### React Frontend
```bash
# Navigate to frontend directory
cd frontend/vite-react-app

# Install dependencies (may need legacy peer deps for React 19)
npm install --legacy-peer-deps

# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Run tests
npm run test
```

## Key Technical Details

### Text Processing Pipeline
1. **File Upload** → **Parser Module** (format-specific extraction) → **TTS Module** (gTTS conversion) → **MP3 Output**
2. **Parser functions** return error strings on failure, not exceptions
3. **Web app** creates `uploads/` and `generated_audio/` directories automatically
4. **FB2 support** is partially implemented but non-functional due to library issues

### File Structure Patterns
- **Tests**: Use unittest framework with fixtures in `tests/fixtures/`
- **Flask app**: Uses Werkzeug for secure file uploads
- **React components**: Follow shadcn/ui conventions with TypeScript support
- **Error handling**: Parser functions return descriptive error strings rather than raising exceptions

### Important Notes
- The React frontend uses React 19 which may require `--legacy-peer-deps` flag for npm install
- FB2 format support exists but has import issues with the fb2 library
- gTTS requires internet connection for text-to-speech conversion
- Test files create temporary fixtures and clean them up automatically