from flask import Flask, render_template, request, jsonify, session
import os
import json
from werkzeug.utils import secure_filename
import secrets

from app.file_processor import FileProcessor
from app.analyzer import MedicalAnalyzer

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create uploads directory in /tmp (works on serverless)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Save the uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        # Process the file to extract patient data
        patient_data = FileProcessor.process_file(file_path)
        
        # Analyze the patient data
        analyzer = MedicalAnalyzer()
        analysis_result = analyzer.analyze_patient_data(patient_data)
        
        # Clean up - remove the uploaded file after processing
        os.remove(file_path)
        
        # Store the result in session for the results page
        session['analysis_result'] = analysis_result
        
        # Return the analysis result
        try:
            parsed_result = json.loads(analysis_result)
            return jsonify({'success': True, 'result': parsed_result})
        except json.JSONDecodeError as json_err:
            return jsonify({'error': f'Error parsing analysis result: {str(json_err)}'}), 500
    
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results():
    # Get the analysis result from the session
    analysis_result = session.get('analysis_result')
    if not analysis_result:
        return render_template('error.html', error='No analysis results found. Please upload a file first.')
    
    # Parse the JSON result
    try:
        result = json.loads(analysis_result)
        
        # Check if there's an error in the result
        if 'error' in result and result['error']:
            return render_template('error.html', 
                               error=f"Analysis Error: {result['error']}", 
                               additional_info=result.get('disclaimer', ''))
        
        return render_template('results.html', result=result)
    except json.JSONDecodeError as e:
        return render_template('error.html', 
                           error='Invalid result format. The analysis produced malformed data.', 
                           additional_info='Please try again with a different file.')

if __name__ == '__main__':
    app.run()