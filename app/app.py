from flask import Flask, render_template, request, jsonify, session
import os
import json
from werkzeug.utils import secure_filename
import secrets

from app.file_processor import FileProcessor
from app.analyzer import MedicalAnalyzer

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create uploads directory if it doesn't exist
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
    print(">>> ANALYZE ENDPOINT CALLED")
    # Check if a file was uploaded
    if 'file' not in request.files:
        print(">>> ERROR: No file part in request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    print(f">>> Received file: {file.filename}")
    
    if file.filename == '':
        print(">>> ERROR: Empty filename")
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        print(f">>> ERROR: File type not allowed: {file.filename}")
        return jsonify({'error': f'File type not allowed. Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Save the uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f">>> Saving file to: {file_path}")
    file.save(file_path)
    
    try:
        # Process the file to extract patient data
        print(">>> Processing file to extract text")
        patient_data = FileProcessor.process_file(file_path)
        print(f">>> Extracted text of length: {len(patient_data)}")
        print(f">>> Sample of text: {patient_data[:100]}...")
        
        # Analyze the patient data
        print(">>> Initializing MedicalAnalyzer")
        analyzer = MedicalAnalyzer()
        print(">>> Calling analyze_patient_data")
        analysis_result = analyzer.analyze_patient_data(patient_data)
        print(f">>> Analysis complete. Result length: {len(analysis_result)}")
        print(f">>> Sample of result: {analysis_result[:100]}...")
        
        # Clean up - remove the uploaded file after processing
        print(">>> Removing uploaded file")
        os.remove(file_path)
        
        # Store the result in session for the results page
        print(">>> Storing result in session")
        session['analysis_result'] = analysis_result
        
        # Return the analysis result
        print(">>> Preparing JSON response")
        try:
            parsed_result = json.loads(analysis_result)
            print(">>> JSON parsed successfully")
            return jsonify({'success': True, 'result': parsed_result})
        except json.JSONDecodeError as json_err:
            print(f">>> ERROR parsing JSON: {str(json_err)}")
            return jsonify({'error': f'Error parsing analysis result: {str(json_err)}'}), 500
    
    except Exception as e:
        print(f">>> EXCEPTION in analyze endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        # Clean up in case of error
        if os.path.exists(file_path):
            print(">>> Cleaning up file after error")
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results():
    print(">>> Results page requested")
    # Get the analysis result from the session
    analysis_result = session.get('analysis_result')
    if not analysis_result:
        print(">>> No analysis results found in session")
        return render_template('error.html', error='No analysis results found. Please upload a file first.')
    
    # Parse the JSON result
    try:
        print(f">>> Parsing analysis result of length: {len(analysis_result)}")
        print(f">>> Analysis result sample: {analysis_result[:100]}...")
        result = json.loads(analysis_result)
        print(">>> JSON parsed successfully")
        
        # Check if there's an error in the result
        if 'error' in result and result['error']:
            print(f">>> Error found in analysis result: {result['error']}")
            return render_template('error.html', 
                                 error=f"Analysis Error: {result['error']}", 
                                 additional_info=result.get('disclaimer', ''))
        
        return render_template('results.html', result=result)
    except json.JSONDecodeError as e:
        print(f">>> JSON parsing error: {str(e)}")
        print(f">>> Raw content that failed parsing: {analysis_result}")
        return render_template('error.html', 
                             error='Invalid result format. The analysis produced malformed data.', 
                             additional_info='Please try again with a different file.')

if __name__ == '__main__':
    app.run(debug=True)