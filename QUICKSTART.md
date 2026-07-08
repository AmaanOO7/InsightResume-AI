# Quick Start Guide

Get InsightResume AI up and running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- IBM Cloud account with watsonx.ai access
- IBM Cloud API Key
- watsonx.ai Project ID

## Step 1: Get IBM Credentials

1. Go to [IBM Cloud](https://cloud.ibm.com/)
2. Create or access your watsonx.ai service
3. Get your **API Key**:
   - Go to Manage → Access (IAM) → API keys
   - Create a new API key or use existing
4. Get your **Project ID**:
   - Open watsonx.ai
   - Create or open a project
   - Copy the Project ID from project settings

## Step 2: Configure Application

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   IBM_CLOUD_API_KEY=your_actual_api_key_here
   WATSONX_PROJECT_ID=your_actual_project_id_here
   ```

3. (Optional) Generate a secure Flask secret key:
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Add it to `.env` as `FLASK_SECRET_KEY`

## Step 3: Start the Application

### Windows
Double-click `start.bat` or run:
```bash
start.bat
```

### macOS/Linux
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start application
python app.py
```

## Step 4: Access the Application

Open your browser and go to:
```
http://localhost:5000
```

## Step 5: Test the Application

1. Click "Get Started" or "Analyze Resume"
2. Upload a sample resume (PDF or DOCX)
3. Wait for AI analysis (30-60 seconds)
4. Review the results:
   - Resume Score
   - ATS Score
   - Skills Analysis
   - Strengths & Weaknesses
5. Generate interview questions
6. Get career suggestions
7. Export PDF report

## Troubleshooting

### "watsonx.ai not initialized"
- Check your API key and Project ID in `.env`
- Verify your IBM Cloud account has watsonx.ai access
- Ensure the watsonx.ai service is active

### "Module not found" error
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Port 5000 already in use
- Change port in `app.py`: `app.run(port=5001)`
- Or stop the process using port 5000

### File upload fails
- Check file size (max 10MB)
- Verify file format (PDF or DOCX only)
- Ensure `uploads/` directory exists

## Next Steps

- Customize AI behavior in `AGENT_INSTRUCTIONS.md`
- Modify UI colors in `static/css/style.css`
- Read full documentation in `README.md`
- Deploy to production (see README.md)

## Support

For detailed documentation, see `README.md`

For issues:
- Check the console output for error messages
- Review the troubleshooting section
- Verify all prerequisites are met

---

**Ready to transform resumes with AI!** 🚀
