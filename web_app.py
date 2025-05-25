import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from parser import extract_text_from_epub, extract_text_from_pdf, extract_text_from_fb2
from tts import convert_text_to_speech

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
GENERATED_AUDIO_FOLDER = 'generated_audio'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_AUDIO_FOLDER'] = GENERATED_AUDIO_FOLDER

# Create directories if they don't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(GENERATED_AUDIO_FOLDER):
    os.makedirs(GENERATED_AUDIO_FOLDER)

ALLOWED_EXTENSIONS = {'epub', 'pdf', 'fb2'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', endpoint='upload_page')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('show_result', success=False, error_message="No file part"))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('show_result', success=False, error_message="No selected file"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_filepath)

        file_ext = filename.rsplit('.', 1)[1].lower()
        extracted_text = None
        error_message = None # Initialize error_message

        if file_ext == 'epub':
            extracted_text = extract_text_from_epub(input_filepath)
        elif file_ext == 'pdf':
            extracted_text = extract_text_from_pdf(input_filepath)
        elif file_ext == 'fb2':
            extracted_text = extract_text_from_fb2(input_filepath)
        
        if not extracted_text or extracted_text.strip() == "" or extracted_text.startswith("Error:"):
            if extracted_text and extracted_text.startswith("Error:"):
                 error_message = extracted_text # Use the specific error from parser
            elif not extracted_text or extracted_text.strip() == "":
                 error_message = "No text content found in the uploaded file."
            else:
                 error_message = "Error during text extraction."
            return redirect(url_for('show_result', success=False, error_message=error_message))

        output_filename = filename.rsplit('.', 1)[0] + '.mp3'
        output_filepath = os.path.join(app.config['GENERATED_AUDIO_FOLDER'], output_filename)
        
        # Assuming convert_text_to_speech returns True on success, False on failure
        # and potentially logs errors or returns an error message.
        # For now, we'll stick to a generic TTS error if it returns False.
        success_tts = convert_text_to_speech(extracted_text, output_filepath, lang='en')
        if success_tts:
            return redirect(url_for('show_result', success=True, filename=output_filename))
        else:
            error_message = "Error during text-to-speech conversion. Please ensure the text is valid and try again."
            return redirect(url_for('show_result', success=False, error_message=error_message))
    else:
        file_ext_provided = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else "none"
        error_message = f"Unsupported file type: '.{file_ext_provided}'. Supported types are EPUB, PDF, and FB2."
        return redirect(url_for('show_result', success=False, error_message=error_message))

@app.route('/result')
def show_result():
    success = request.args.get('success') == 'True'
    filename = request.args.get('filename')
    error_message = request.args.get('error_message')
    return render_template('result.html', success=success, filename=filename, error_message=error_message)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['GENERATED_AUDIO_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
