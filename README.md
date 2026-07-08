# InsightResume AI

<div align="center">

![InsightResume AI](https://img.shields.io/badge/InsightResume-AI-4F46E5?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask)
![Google Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google)

# AI-Powered Resume Analyzer

Upload your resume and job description to receive ATS analysis, recruiter feedback, interview questions, and career guidance powered by Google's Gemini AI.

Live Demo • Features • Installation • Screenshots

</div>

---

## Overview

InsightResume AI is an AI-powered Resume Intelligence platform that analyzes resumes against job descriptions using Google's Gemini AI.

The application provides:

- Resume Quality Score
- ATS Compatibility Score
- Skill Gap Analysis
- Keyword Matching
- Personalized Recruiter Feedback
- AI-generated Interview Questions
- Career Recommendations
- Professional PDF Reports

The project is built using Flask, Python, HTML, CSS, JavaScript and Google Gemini.

## Key Features

✅ Resume ATS Analysis

✅ AI Recruiter Review

✅ Skill Gap Detection

✅ Keyword Matching

✅ Personalized Interview Questions

✅ Career Suggestions

✅ PDF Report Generation

✅ Responsive UI

✅ Google Gemini AI Integration

✅ PDF & DOCX Resume Support

## 📋 Prerequisites

## Requirements

Python 3.11+

Google Gemini API Key

Flask

Internet Connection

## 🔧 Installation

### 1. Clone the Repository

--Bash

git clone https://github.com/YOUR_USERNAME/InsightResume-AI.git

cd InsightResume-AIx

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

Create .env

GOOGLE_API_KEY=YOUR_API_KEY

FLASK_SECRET_KEY=YOUR_SECRET

MAX_FILE_SIZE=10485760

Run

python app.py

The application will start at `http://localhost:5000`

### Using the Application

1. **Upload Resume**
   - Navigate to the dashboard
   - Upload your resume (PDF or DOCX)
   - Wait for automatic analysis

2. **View Analysis**
   - Review your resume score and ATS compatibility
   - Check identified skills and recommendations
   - Read strengths, weaknesses, and improvements

3. **Generate Interview Questions**
   - Click "Interview Prep" button
   - Review technical and HR questions
   - Study model answers

4. **Get Career Guidance**
   - Click "Career Guide" button
   - Explore suitable job roles
   - Review salary estimates and certifications
   - Follow the learning roadmap

5. **Export Report**
   - Click "Export PDF" button
   - Download comprehensive analysis report
   - Share or save for future reference

---

## 📁 Project Structure

```
insightresume-ai/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Your configuration (not in git)
├── README.md                  # This file
├── AGENT_INSTRUCTIONS.md      # AI agent customization
│
├── templates/                 # HTML templates
│   ├── index.html            # Landing page
│   └── dashboard.html        # Main dashboard
│
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css         # Main stylesheet
│   ├── js/
│   │   ├── main.js           # Common JavaScript
│   │   └── dashboard.js      # Dashboard functionality
│   └── images/               # Image assets
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── file_extractor.py     # PDF/DOCX text extraction
│   ├── watsonx_client.py     # Google Gemini AI integration
│   └── pdf_generator.py      # PDF report generation
│
└── uploads/                   # Temporary file storage
```

---

## 🎨 Customization

### Agent Instructions

Edit `AGENT_INSTRUCTIONS.md` to customize:

- **Personality & Tone**: Adjust the AI's communication style
- **Review Style**: Modify analysis approach and scoring
- **ATS Strictness**: Change compatibility checking parameters
- **Career Domain**: Focus on specific industries
- **Interview Mix**: Adjust question distribution
- **Safety Rules**: Update ethical guidelines

Changes take effect on the next analysis.

### UI Customization

Edit `static/css/style.css` to modify:

- Color scheme (CSS variables in `:root`)
- Layout and spacing
- Animations and transitions
- Responsive breakpoints

### Model Configuration

In `utils/watsonx_client.py`, adjust:

- `DECODING_METHOD`: greedy, sample
- `MAX_NEW_TOKENS`: Response length
- `TEMPERATURE`: Creativity (0.0-1.0)
- `TOP_K` and `TOP_P`: Sampling parameters

---

## 🔒 Security

- **Session-based**: Data stored only during active session
- **Automatic Cleanup**: Uploaded files deleted after processing
- **No Persistence**: Resume content not saved to database
- **Secure File Handling**: Validated file types and sizes
- **Environment Variables**: Sensitive data in `.env` file
- **HTTPS Ready**: Configure reverse proxy for production

---

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   FLASK_SECRET_KEY=<strong-random-key>
   ```

2. **Use Production Server**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set Up Reverse Proxy** (Nginx/Apache)
4. **Enable HTTPS** (Let's Encrypt)
5. **Configure Firewall**
6. **Set Up Monitoring**
7. **Regular Backups**

### Deployment Platforms

Deploy on

Vercel

Render

Railway

PythonAnywhere

Azure

AWS

Google Cloud Run

---

## 🧪 Testing

### Manual Testing

1. **Upload Test**
   - Upload valid PDF/DOCX files
   - Test file size limits
   - Test invalid file types

2. **Analysis Test**
   - Verify all scores display correctly
   - Check skills extraction
   - Validate recommendations

3. **Interview Questions Test**
   - Generate questions multiple times
   - Verify question quality
   - Check answer relevance

4. **Career Suggestions Test**
   - Validate job role matches
   - Check salary ranges
   - Verify certification recommendations

5. **PDF Export Test**
   - Generate and download PDF
   - Verify all sections included
   - Check formatting

### API Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Upload resume
curl -X POST -F "resume=@sample_resume.pdf" http://localhost:5000/api/upload

# Analyze resume (requires session)
curl -X POST http://localhost:5000/api/analyze
```

---

## 🐛 Troubleshooting

### Common Issues

**1. watsonx.ai Connection Error**
- Verify API key and Project ID in `.env`
- Check internet connection
- Ensure watsonx.ai service is active

**2. File Upload Fails**
- Check file size (max 10MB)
- Verify file format (PDF or DOCX)
- Ensure `uploads/` directory exists

**3. PDF Generation Error**
- Install reportlab: `pip install reportlab`
- Check write permissions in `uploads/`

**4. Module Import Error**
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

**5. Port Already in Use**
- Change port in `app.py`: `app.run(port=5001)`
- Or kill process using port 5000

---

## 📚 API Documentation

### Endpoints

#### `GET /`
Landing page

#### `GET /dashboard`
Main dashboard interface

#### `POST /api/upload`
Upload resume file
- **Body**: multipart/form-data with `resume` file
- **Response**: `{success: true, filename: string, text_length: number}`

#### `POST /api/analyze`
Analyze uploaded resume
- **Response**: `{success: true, analysis: object}`

#### `POST /api/interview-questions`
Generate interview questions
- **Response**: `{success: true, questions: object}`

#### `POST /api/career-suggestions`
Generate career suggestions
- **Response**: `{success: true, suggestions: object}`

#### `POST /api/export-pdf`
Export analysis as PDF
- **Response**: PDF file download

#### `POST /api/clear-session`
Clear session data
- **Response**: `{success: true, message: string}`

#### `GET /api/health`
Health check endpoint
- **Response**: `{status: string, gemini_initialized: boolean, timestamp: string}`

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

---

## 🙏 Acknowledgments

- **Google Gemini ai** - AI model and infrastructure
- **Flask** - Web framework
- **Bootstrap** - UI components
- **Font Awesome** - Icons
- **ReportLab** - PDF generation

---

## 📞 Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Contact: support@insightresume.ai
- Documentation: [docs.insightresume.ai](https://docs.insightresume.ai)

---

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Multi-language support
- [ ] Resume templates
- [ ] Comparison with job descriptions
- [ ] LinkedIn profile analysis
- [ ] Cover letter generation

### Version 1.2 (Planned)
- [ ] User accounts and history
- [ ] Resume builder
- [ ] Job board integration
- [ ] Email notifications
- [ ] Advanced analytics dashboard

---

<div align="center">

**Built with ❤️ by Aman Kumar using Google Gemini AI**

[⬆ Back to Top](#insightresume-ai)

</div>
