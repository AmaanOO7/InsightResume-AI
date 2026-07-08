"""
InsightResume AI
AI-Powered Resume Analyzer using Google Gemini

Author: Aman Kumar
"""

import logging
import os
import secrets
import tempfile
from datetime import datetime

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    session,
)

from utils.file_extractor import FileExtractor
from utils.gemini_client import GeminiClient
from utils.pdf_generator import PDFGenerator

# ----------------------------------------------------------
# Load Environment Variables
# ----------------------------------------------------------

load_dotenv()

# ----------------------------------------------------------
# Logging Configuration
# ----------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ----------------------------------------------------------
# Flask Configuration
# ----------------------------------------------------------

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv(
        "FLASK_SECRET_KEY",
        secrets.token_hex(32)
    ),

    UPLOAD_FOLDER=tempfile.gettempdir(),

    MAX_CONTENT_LENGTH=int(
        os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024)
    ),

    ALLOWED_EXTENSIONS={
        "pdf",
        "docx"
    }
)

# ----------------------------------------------------------
# Global AI Client
# ----------------------------------------------------------

gemini_client = None

# ----------------------------------------------------------
# Configuration Validation
# ----------------------------------------------------------

def validate_environment():
    """
    Ensure all required environment variables exist.
    """

    required = [
        "GOOGLE_API_KEY"
    ]

    missing = []

    for item in required:

        if not os.getenv(item):

            missing.append(item)

    if missing:

        raise RuntimeError(
            f"Missing environment variables: {', '.join(missing)}"
        )

# ----------------------------------------------------------
# Gemini Initialization
# ----------------------------------------------------------

def initialize_gemini():
    """
    Initialize Gemini client.

    This function is executed once when Flask starts.
    It also works correctly on Vercel because it runs
    during module import.
    """

    global gemini_client

    try:

        validate_environment()

        gemini_client = GeminiClient(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

        logger.info("✓ Google Gemini initialized successfully")

        return True

    except Exception as e:

        logger.exception("Gemini initialization failed")

        gemini_client = None

        return False


# Initialize Gemini immediately
initialize_gemini()

# ----------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------

def get_resume():

    resume = session.get("resume_text")

    if not resume:

        raise ValueError(
            "No resume uploaded."
        )

    return resume


def get_job_description():

    data = request.get_json(silent=True) or {}

    return (
        data.get("job_description", "").strip()
        or "No job description provided."
    )


def get_agent_instructions():
    """
    Read AGENT_INSTRUCTIONS.md
    """

    try:

        path = os.path.join(
            os.path.dirname(__file__),
            "AGENT_INSTRUCTIONS.md"
        )

        if not os.path.exists(path):

            return (
                "You are a professional "
                "Resume Reviewer."
            )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except Exception:

        logger.exception(
            "Unable to load AGENT_INSTRUCTIONS.md"
        )

        return (
            "You are a professional Resume Reviewer."
        )


def ensure_ai():

    if gemini_client is None:

        raise RuntimeError(
            "Gemini AI is not initialized."
        )

# ----------------------------------------------------------
# Pages
# ----------------------------------------------------------

@app.route("/")
def index():

    return render_template("index.html")


@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")

# ----------------------------------------------------------
# Health Endpoint
# ----------------------------------------------------------

@app.route("/api/health")
def health():

    return jsonify({

        "status": "healthy",

        "provider": "Google Gemini",

        "model": (
            gemini_client.get_model_name()
            if gemini_client
            else None
        ),

        "initialized": (
            gemini_client is not None
        ),

        "timestamp": datetime.utcnow().isoformat()

    })
    
    
# ==========================================================
# Resume Upload Helper Functions
# ==========================================================

def validate_uploaded_resume(uploaded_file):
    """
    Validate uploaded resume file.
    Raises ValueError if validation fails.
    """

    if uploaded_file is None:
        raise ValueError("No file uploaded.")

    if uploaded_file.filename == "":
        raise ValueError("Please select a resume.")

    if not FileExtractor.allowed_file(uploaded_file.filename):
        raise ValueError(
            "Only PDF and DOCX files are supported."
        )

    if not FileExtractor.validate_file_size(
        uploaded_file,
        max_size_mb=10
    ):
        raise ValueError(
            "File size exceeds the 10 MB limit."
        )


def extract_resume_text(uploaded_file):
    """
    Extract and validate resume text.
    """

    resume_text = FileExtractor.extract_text(uploaded_file)

    if not resume_text:
        raise ValueError(
            "Unable to extract text from the uploaded resume."
        )

    resume_text = resume_text.strip()

    if len(resume_text) < 100:
        raise ValueError(
            "The uploaded resume contains too little readable text."
        )

    return resume_text


def clear_analysis_cache():
    """
    Remove previous analysis results whenever
    a new resume is uploaded.
    """

    session.pop("analysis_data", None)
    session.pop("interview_data", None)
    session.pop("career_data", None)


# ==========================================================
# Upload Resume
# ==========================================================

@app.route("/api/upload", methods=["POST"])
def upload_resume():
    """
    Upload a resume and extract text.

    Supported:
    - PDF
    - DOCX
    """

    try:

        uploaded_file = request.files.get("resume")

        validate_uploaded_resume(uploaded_file)

        logger.info(
            "Uploading resume: %s",
            uploaded_file.filename
        )

        resume_text = extract_resume_text(
            uploaded_file
        )

        session["resume_text"] = resume_text

        session["resume_filename"] = secure_filename(
            uploaded_file.filename
        )

        clear_analysis_cache()

        logger.info(
            "Resume uploaded successfully (%s characters)",
            len(resume_text)
        )

        return jsonify({

            "success": True,

            "message": "Resume uploaded successfully.",

            "filename": uploaded_file.filename,

            "text_length": len(resume_text)

        }), 200

    except ValueError as e:

        logger.warning(str(e))

        return jsonify({

            "success": False,

            "error": str(e)

        }), 400

    except Exception as e:

        logger.exception(
            "Unexpected error while uploading resume."
        )

        return jsonify({

            "success": False,

            "error":
            "An unexpected error occurred while processing the resume."

        }), 500


# ==========================================================
# Session Status
# ==========================================================

@app.route("/api/session", methods=["GET"])
def session_status():
    """
    Return current session status.
    """

    return jsonify({

        "resume_uploaded":
            "resume_text" in session,

        "analysis_available":
            "analysis_data" in session,

        "interview_available":
            "interview_data" in session,

        "career_available":
            "career_data" in session,

        "filename":
            session.get("resume_filename")

    })


# ==========================================================
# Resume Information
# ==========================================================

@app.route("/api/resume-info", methods=["GET"])
def resume_information():
    """
    Return uploaded resume information.
    """

    resume = session.get("resume_text")

    if not resume:

        return jsonify({

            "success": False,

            "error": "No resume uploaded."

        }), 404

    return jsonify({

        "success": True,

        "filename":
            session.get("resume_filename"),

        "characters":
            len(resume),

        "estimated_words":
            len(resume.split()),

        "uploaded": True

    })
    
# ==========================================================
# AI Helper Functions
# ==========================================================

def get_resume_and_job_description():
    """
    Retrieve resume and job description.

    Raises:
        ValueError
    """

    resume_text = session.get("resume_text")

    if not resume_text:
        raise ValueError(
            "No resume uploaded. Please upload a resume first."
        )

    job_description = get_job_description()

    return resume_text, job_description


def call_ai_service(task):
    """
    Execute Gemini request based on task.
    """

    ensure_ai()

    resume_text, job_description = get_resume_and_job_description()

    instructions = get_agent_instructions()

    logger.info(
        "Executing Gemini task: %s",
        task
    )

    if task == "analysis":

        return gemini_client.analyze_resume(
            resume_text=resume_text,
            job_description=job_description,
            agent_instructions=instructions
        )

    elif task == "interview":

        return gemini_client.generate_interview_questions(
            resume_text=resume_text,
            job_description=job_description,
            agent_instructions=instructions
        )

    elif task == "career":

        return gemini_client.generate_career_suggestions(
            resume_text=resume_text,
            job_description=job_description,
            agent_instructions=instructions
        )

    raise ValueError("Unknown AI task.")
# ==========================================================
# Resume Analysis
# ==========================================================

@app.route("/api/analyze", methods=["POST"])
def analyze_resume():

    try:

        analysis = call_ai_service("analysis")

        session["analysis_data"] = analysis

        logger.info(
            "Resume analysis completed."
        )

        return jsonify({

            "success": True,

            "analysis": analysis

        })

    except ValueError as e:

        logger.warning(str(e))

        return jsonify({

            "success": False,

            "error": str(e)

        }), 400

    except Exception:

        logger.exception(
            "Resume analysis failed."
        )

        return jsonify({

            "success": False,

            "error":
            "Unable to analyze the resume."

        }), 500

# ==========================================================
# Interview Questions
# ==========================================================

@app.route("/api/interview-questions", methods=["POST"])
def generate_interview_questions():

    try:

        questions = call_ai_service("interview")

        session["interview_data"] = questions

        logger.info(
            "Interview questions generated."
        )

        return jsonify({

            "success": True,

            "questions": questions

        })

    except ValueError as e:

        logger.warning(str(e))

        return jsonify({

            "success": False,

            "error": str(e)

        }), 400

    except Exception:

        logger.exception(
            "Interview question generation failed."
        )

        return jsonify({

            "success": False,

            "error":
            "Unable to generate interview questions."

        }), 500

# ==========================================================
# Career Suggestions
# ==========================================================

@app.route("/api/career-suggestions", methods=["POST"])
def generate_career_suggestions():

    try:

        suggestions = call_ai_service("career")

        session["career_data"] = suggestions

        logger.info(
            "Career suggestions generated."
        )

        return jsonify({

            "success": True,

            "suggestions": suggestions

        })

    except ValueError as e:

        logger.warning(str(e))

        return jsonify({

            "success": False,

            "error": str(e)

        }), 400

    except Exception:

        logger.exception(
            "Career suggestion generation failed."
        )

        return jsonify({

            "success": False,

            "error":
            "Unable to generate career suggestions."

        }), 500

# ==========================================================
# PDF Export
# ==========================================================

@app.route("/api/export-pdf", methods=["POST"])
def export_pdf():
    """
    Generate and download PDF report.
    """

    try:

        analysis_data = session.get("analysis_data")

        if not analysis_data:

            return jsonify({

                "success": False,

                "error":
                "Please analyze a resume before exporting."

            }), 400

        interview_data = session.get(
            "interview_data",
            {
                "technical_questions": [],
                "hr_questions": []
            }
        )

        career_data = session.get(
            "career_data",
            {
                "suitable_roles": [],
                "salary_range": {},
                "certifications": [],
                "learning_roadmap": []
            }
        )

        filename = (
            f"resume_analysis_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        pdf_path = os.path.join(
            tempfile.gettempdir(),
            filename
        )

        PDFGenerator.generate_report(
            analysis_data=analysis_data,
            interview_data=interview_data,
            career_data=career_data,
            output_path=pdf_path
        )

        logger.info(
            "PDF report generated successfully."
        )

        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception:

        logger.exception(
            "Failed to generate PDF."
        )

        return jsonify({

            "success": False,

            "error":
            "Unable to generate PDF."

        }), 500


# ==========================================================
# Clear Session
# ==========================================================

@app.route("/api/clear-session", methods=["POST"])
def clear_session():

    try:

        session.clear()

        logger.info(
            "Session cleared."
        )

        return jsonify({

            "success": True,

            "message":
            "Session cleared successfully."

        })

    except Exception:

        logger.exception(
            "Unable to clear session."
        )

        return jsonify({

            "success": False,

            "error":
            "Unable to clear session."

        }), 500


# ==========================================================
# Global Error Handlers
# ==========================================================

@app.errorhandler(400)
def bad_request(error):

    return jsonify({

        "success": False,

        "error": "Bad Request"

    }), 400


@app.errorhandler(404)
def not_found(error):

    return render_template("404.html"), 404


@app.errorhandler(413)
def file_too_large(error):

    return jsonify({

        "success": False,

        "error":
        "Maximum upload size is 10 MB."

    }), 413


@app.errorhandler(500)
def internal_server_error(error):

    logger.exception(
        "Unhandled Internal Server Error"
    )

    return jsonify({

        "success": False,

        "error":
        "Internal Server Error"

    }), 500


# ==========================================================
# Application Startup
# ==========================================================

logger.info("=" * 70)
logger.info("InsightResume AI")
logger.info("Google Gemini Resume Analyzer")
logger.info("=" * 70)

if gemini_client:

    logger.info("Gemini initialized successfully.")

else:

    logger.warning(
        "Gemini initialization failed."
    )


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=int(
            os.getenv("PORT", 5000)
        ),

        debug=os.getenv(
            "FLASK_DEBUG",
            "False"
        ).lower() == "true"

    )


