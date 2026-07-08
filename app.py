import os
import json
import traceback
import tempfile
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime
import secrets

from utils.file_extractor import FileExtractor
from utils.watsonx_client import WatsonxClient
from utils.pdf_generator import PDFGenerator

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 10485760))
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

if app.config['UPLOAD_FOLDER'] != tempfile.gettempdir():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ai_client = None

def initialize_ai():
    """Initialize Gemini AI client"""
    global ai_client
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        project_id = os.getenv('WATSONX_PROJECT_ID')
        url = os.getenv('WATSONX_URL', 'https://eu-de.ml.cloud.ibm.com')
        model_id = os.getenv('MODEL_ID', 'ibm/granite-4-h-small')
        
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY must be set in the .env file.")
        
        ai_client = WatsonxClient(api_key, project_id, url, model_id)
        return True
    
    except Exception as e:
        print("=" * 60)
        print("Gemini Initialization Error")
        traceback.print_exc()
        print("=" * 60)
        return False

# ------------------------------------------------
# Initialize AI when the module loads (Required for Vercel)
# ------------------------------------------------
initialize_ai()

def load_agent_instructions():
    """Load agent instructions from file"""
    try:
        instructions_path = os.path.join(os.path.dirname(__file__), 'AGENT_INSTRUCTIONS.md')
        if os.path.exists(instructions_path):
            with open(instructions_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '## Agent Configuration' in content:
                    config_section = content.split('## Agent Configuration')[1].split('##')[0]
                    return config_section.strip()
        return "You are a professional and helpful resume reviewer."
    except Exception as e:
        print(f"Error loading agent instructions: {str(e)}")
        return "You are a professional and helpful resume reviewer."

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """Handle resume upload and text extraction"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not FileExtractor.allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and DOCX are allowed'}), 400
        
        if not FileExtractor.validate_file_size(file, max_size_mb=10):
            return jsonify({'error': 'File size exceeds 10MB limit'}), 400
        
        filename = secure_filename(file.filename)

        resume_text = FileExtractor.extract_text(file)
        
        if not resume_text or len(resume_text.strip()) < 100:
            return jsonify({
                'error': 'Resume text is too short or empty. Please upload a valid resume.'
            }), 400
        
        session['resume_text'] = resume_text
        session['resume_filename'] = filename
        
        return jsonify({
            'success': True,
            'message': 'Resume uploaded successfully',
            'filename': filename,
            'text_length': len(resume_text)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing resume: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():

    data = request.get_json()

    job_description = ""

    if data:
        job_description = data.get("job_description", "")

    job_description = job_description or "No job description provided."

    """Analyze resume using watsonx.ai"""
    try:
        if not ai_client:
            return jsonify({'error': 'AI service not initialized. Please check your configuration.'}), 500
        
        resume_text = session.get('resume_text')
        if not resume_text:
            return jsonify({'error': 'No resume uploaded. Please upload a resume first.'}), 400
        
        agent_instructions = load_agent_instructions()

        print("=" * 60)
        print("Reached /api/analyze")
        print("ai_client:", ai_client)
        print("Resume length:", len(resume_text))
        print("Calling AIClient.analyze_resume()")
        print("=" * 60)
        
        analysis = ai_client.analyze_resume(resume_text=resume_text, job_description=job_description, agent_instructions=agent_instructions)
        
        session['analysis_data'] = analysis
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        import traceback

        print("=" * 60)
        print("ANALYZE RESUME ERROR")
        traceback.print_exc()
        print("=" * 60)

        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/interview-questions', methods=['POST'])
def generate_interview_questions():
    """Generate interview questions using watsonx.ai"""
    try:
        if not ai_client:
            return jsonify({'error': 'AI service not initialized. Please check your configuration.'}), 500
        
        data = request.get_json()

        job_description = ""

        if data:
            job_description = data.get("job_description", "")

        job_description = job_description or "No job description provided."

        resume_text = session.get("resume_text")

        data = request.get_json(silent=True) or {}

        job_description = (
            data.get("job_description", "").strip()
            or "No job description provided."
        )

        agent_instructions = load_agent_instructions()

        questions = ai_client.generate_interview_questions(
            resume_text,
            job_description,
            agent_instructions
        )
        
        session['interview_data'] = questions
        
        return jsonify({
            'success': True,
            'questions': questions
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating interview questions: {str(e)}'}), 500

@app.route('/api/career-suggestions', methods=['POST'])
def generate_career_suggestions():
    """Generate career suggestions using watsonx.ai"""
    try:
        if not ai_client:
            return jsonify({'error': 'AI service not initialized. Please check your configuration.'}), 500
        
        data = request.get_json()

        job_description = ""

        if data:
            job_description = data.get("job_description", "")

        job_description = job_description or "No job description provided."

        resume_text = session.get("resume_text")

        data = request.get_json(silent=True) or {}

        job_description = (
            data.get("job_description", "").strip()
            or "No job description provided."
        )

        agent_instructions = load_agent_instructions()

        suggestions = ai_client.generate_career_suggestions(
            resume_text,
            job_description,
            agent_instructions
        )
        
        session['career_data'] = suggestions
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating career suggestions: {str(e)}'}), 500

@app.route('/api/export-pdf', methods=['POST'])
def export_pdf():
    """Export analysis report as PDF"""
    try:
        analysis_data = session.get('analysis_data')
        interview_data = session.get('interview_data')
        career_data = session.get('career_data')
        
        if not analysis_data:
            return jsonify({'error': 'No analysis data available. Please analyze a resume first.'}), 400
        
        if not interview_data:
            interview_data = {'technical_questions': [], 'hr_questions': []}
        
        if not career_data:
            career_data = {'suitable_roles': [], 'salary_range': {}, 'certifications': [], 'learning_roadmap': []}
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"resume_analysis_{timestamp}.pdf"

        pdf_path = os.path.join(
            tempfile.gettempdir(),
            pdf_filename
        )
        
        PDFGenerator.generate_report(
            analysis_data,
            interview_data,
            career_data,
            pdf_path
        )
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=pdf_filename,
            mimetype="application/pdf"
        )
        
    except Exception as e:
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Clear session data"""
    try:
        if 'resume_filepath' in session:
            filepath = session['resume_filepath']
            if os.path.exists(filepath):
                os.remove(filepath)
        
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Session cleared successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error clearing session: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'watsonx_initialized': ai_client is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File size exceeds 10MB limit'}), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("InsightResume AI - Starting Application")
    print("=" * 60)
    
    app.run(
        debug=os.getenv("FLASK_DEBUG", "True") == "True",
        host="0.0.0.0",
        port=5000
    )
