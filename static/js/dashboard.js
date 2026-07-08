document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const resumeFile = document.getElementById('resumeFile');
    const browseBtn = document.getElementById('browseBtn');
    const uploadSection = document.getElementById('uploadSection');
    const analysisSection = document.getElementById('analysisSection');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadSuccess = document.getElementById('uploadSuccess');
    const uploadError = document.getElementById('uploadError');
    const clearSessionBtn = document.getElementById('clearSessionBtn');
    
    const generateInterviewBtn = document.getElementById('generateInterviewBtn');
    const generateCareerBtn = document.getElementById('generateCareerBtn');
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    const analyzeResumeBtn = document.getElementById('analyzeResumeBtn');
    const jobDescription = document.getElementById('jobDescription');
    
    let analysisData = null;
    let interviewData = null;
    let careerData = null;
    
    if (browseBtn) {
        browseBtn.addEventListener('click', function() {
            resumeFile.click();
        });
    }
    
    if (uploadArea) {
        uploadArea.addEventListener('click', function() {
            resumeFile.click();
        });
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                resumeFile.files = files;
                handleFileUpload(files[0]);
            }
        });
    }
    
    if (resumeFile) {
        resumeFile.addEventListener('change', function () {
            if (this.files.length > 0) {

                showUploadSuccess(
                    this.files[0].name + " selected successfully.");
            }
        });
    }
    
    if (clearSessionBtn) {
        clearSessionBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to start a new analysis? Current data will be lost.')) {
                clearSession();
            }
        });
    }
    
    if (generateInterviewBtn) {
        generateInterviewBtn.addEventListener('click', function() {
            generateInterviewQuestions();
        });
    }
    
    if (generateCareerBtn) {
        generateCareerBtn.addEventListener('click', function() {
            generateCareerSuggestions();
        });
    }
    if (analyzeResumeBtn) {

        analyzeResumeBtn.addEventListener("click", function () {

            if (!resumeFile.files.length) {
                showUploadError("Please select a resume.");
                return;
            }

            if (jobDescription.value.trim() === "") {
                showUploadError("Please paste the Job Description.");
                return;
            }

            handleFileUpload(resumeFile.files[0]);

        });

    }
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', function() {
            exportToPdf();
        });
    }
    
    function handleFileUpload(file) {
        uploadError.style.display = 'none';
        uploadSuccess.style.display = 'none';
        
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!allowedTypes.includes(file.type)) {
            showUploadError('Invalid file type. Please upload a PDF or DOCX file.');
            return;
        }
        
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            showUploadError('File size exceeds 10MB limit.');
            return;
        }
        
        const formData = new FormData();
        formData.append('resume', file);
        
        uploadProgress.style.display = 'block';
        const progressBar = uploadProgress.querySelector('.progress-bar');
        progressBar.style.width = '30%';
        
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            progressBar.style.width = '100%';
            
            if (data.error) {
                showUploadError(data.error);
                uploadProgress.style.display = 'none';
            } else {
                setTimeout(() => {
                    uploadProgress.style.display = 'none';
                    showUploadSuccess(`${data.filename} uploaded successfully! Analyzing...`);
                    
                    setTimeout(() => {
                        analyzeResume();
                    }, 1000);
                }, 500);
            }
        })
        .catch(error => {
            uploadProgress.style.display = 'none';
            showUploadError('Error uploading file. Please try again.');
            console.error('Upload error:', error);
        });
    }
    
    function analyzeResume() {
        uploadSection.style.display = 'none';
        analysisSection.style.display = 'block';
        
        const loadingSpinner = document.getElementById('loadingSpinner');
        const analysisResults = document.getElementById('analysisResults');
        
        loadingSpinner.style.display = 'block';
        analysisResults.style.display = 'none';
        
        fetch('/api/analyze', {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({

                job_description: jobDescription.value

            })

        })
        .then(response => response.json())
        .then(data => {
            loadingSpinner.style.display = 'none';
            
            if (data.error) {
                showNotification(data.error, 'error');
                uploadSection.style.display = 'block';
                analysisSection.style.display = 'none';
            } else {
                analysisData = data.analysis;
                displayAnalysisResults(data.analysis);
                analysisResults.style.display = 'block';
                showNotification('Resume analyzed successfully!', 'success');
            }
        })
        .catch(error => {
            loadingSpinner.style.display = 'none';
            showNotification('Error analyzing resume. Please try again.', 'error');
            console.error('Analysis error:', error);
            uploadSection.style.display = 'block';
            analysisSection.style.display = 'none';
        });
    }
    
    function displayAnalysisResults(analysis) {
        document.getElementById('resumeScore').textContent = analysis.resume_score + '/100';
        document.getElementById('atsScore').textContent = analysis.ats_score + '/100';
        document.getElementById('experienceLevel').textContent = analysis.experience_level;
        document.getElementById('skillsCount').textContent = analysis.skills_found.length;
        
        document.getElementById('summaryText').textContent = analysis.summary || 'No summary available.';
        
        const strengthsList = document.getElementById('strengthsList');
        strengthsList.innerHTML = '';
        analysis.strengths.forEach(strength => {
            const li = document.createElement('li');
            li.textContent = strength;
            strengthsList.appendChild(li);
        });
        
        const weaknessesList = document.getElementById('weaknessesList');
        weaknessesList.innerHTML = '';
        analysis.weaknesses.forEach(weakness => {
            const li = document.createElement('li');
            li.textContent = weakness;
            weaknessesList.appendChild(li);
        });
        
        const skillsFoundBadges = document.getElementById('skillsFoundBadges');
        skillsFoundBadges.innerHTML = '';
        analysis.skills_found.forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'badge badge-primary';
            badge.textContent = skill;
            skillsFoundBadges.appendChild(badge);
        });
        
        const missingSkillsBadges = document.getElementById('missingSkillsBadges');
        missingSkillsBadges.innerHTML = '';
        analysis.missing_skills.forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'badge badge-info';
            badge.textContent = skill;
            missingSkillsBadges.appendChild(badge);
        });
        
        const improvementsList = document.getElementById('improvementsList');
        improvementsList.innerHTML = '';
        analysis.improvements.forEach(improvement => {
            const li = document.createElement('li');
            li.textContent = improvement;
            improvementsList.appendChild(li);
        });
    }
    
    function generateInterviewQuestions() {
        const interviewSection = document.getElementById('interviewSection');
        const loadingSpinner = document.getElementById('loadingSpinner');
        
        generateInterviewBtn.disabled = true;
        generateInterviewBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
        
        fetch('/api/interview-questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                job_description: jobDescription.value
            })
        })
        .then(response => response.json())
        .then(data => {
            generateInterviewBtn.disabled = false;
            generateInterviewBtn.innerHTML = '<i class="fas fa-comments me-2"></i>Interview Prep';
            
            if (data.error) {
                showNotification(data.error, 'error');
            } else {
                interviewData = data.questions;
                displayInterviewQuestions(data.questions);
                interviewSection.style.display = 'block';
                
                interviewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                showNotification('Interview questions generated successfully!', 'success');
            }
        })
        .catch(error => {
            generateInterviewBtn.disabled = false;
            generateInterviewBtn.innerHTML = '<i class="fas fa-comments me-2"></i>Interview Prep';
            showNotification('Error generating interview questions. Please try again.', 'error');
            console.error('Interview questions error:', error);
        });
    }
    
    function displayInterviewQuestions(questions) {
        const technicalQuestions = document.getElementById('technicalQuestions');
        technicalQuestions.innerHTML = '';
        
        questions.domain_questions.forEach((q, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-item';
            questionDiv.innerHTML = `
                <div class="question-text">Q${index + 1}: ${q.question}</div>
                <div class="answer-text"><strong>Answer:</strong> ${q.model_answer}</div>
                <span class="difficulty-badge difficulty-${q.difficulty.toLowerCase()}">${q.difficulty}</span>
            `;
            technicalQuestions.appendChild(questionDiv);
        });
        
        const hrQuestions = document.getElementById('hrQuestions');
        hrQuestions.innerHTML = '';
        
        questions.hr_questions.forEach((q, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-item';
            questionDiv.innerHTML = `
                <div class="question-text">Q${index + 1}: ${q.question}</div>
                <div class="answer-text"><strong>Answer:</strong> ${q.model_answer}</div>
                <span class="difficulty-badge difficulty-${q.difficulty.toLowerCase()}">${q.difficulty}</span>
            `;
            hrQuestions.appendChild(questionDiv);
        });
    }
    
    function generateCareerSuggestions() {
        const careerSection = document.getElementById('careerSection');
        
        generateCareerBtn.disabled = true;
        generateCareerBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
        
        fetch('/api/career-suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                job_description: jobDescription.value
            })
        })
        .then(response => response.json())
        .then(data => {
            generateCareerBtn.disabled = false;
            generateCareerBtn.innerHTML = '<i class="fas fa-compass me-2"></i>Career Guide';
            
            if (data.error) {
                showNotification(data.error, 'error');
            } else {
                careerData = data.suggestions;
                displayCareerSuggestions(data.suggestions);
                careerSection.style.display = 'block';
                
                careerSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                showNotification('Career suggestions generated successfully!', 'success');
            }
        })
        .catch(error => {
            generateCareerBtn.disabled = false;
            generateCareerBtn.innerHTML = '<i class="fas fa-compass me-2"></i>Career Guide';
            showNotification('Error generating career suggestions. Please try again.', 'error');
            console.error('Career suggestions error:', error);
        });
    }
    
    function displayCareerSuggestions(suggestions) {
        const suitableRoles = document.getElementById('suitableRoles');
        suitableRoles.innerHTML = '';
        
        suggestions.suitable_roles.forEach(role => {
            const roleDiv = document.createElement('div');
            roleDiv.className = 'role-card';
            roleDiv.innerHTML = `
                <div class="role-title">
                    ${role.title}
                    <span class="role-match">${role.match_percentage}% Match</span>
                </div>
                <div class="role-description">${role.description}</div>
            `;
            suitableRoles.appendChild(roleDiv);
        });
        
        const salaryRange = document.getElementById('salaryRange');
        const salary = suggestions.salary_range;
        salaryRange.innerHTML = `
            <div class="salary-info">
                <h5 class="text-white mb-3">$${salary.min.toLocaleString()} - $${salary.max.toLocaleString()} ${salary.currency}</h5>
                <p class="text-white-50">Per ${salary.period}</p>
            </div>
        `;
        
        const certifications = document.getElementById('certifications');
        certifications.innerHTML = '';
        
        suggestions.certifications.forEach(cert => {
            const certDiv = document.createElement('div');
            certDiv.className = 'cert-item';
            certDiv.innerHTML = `
                <div class="cert-name">${cert.name}</div>
                <div class="cert-provider">${cert.provider} - Priority: ${cert.priority}</div>
                <div class="cert-reason">${cert.reason}</div>
            `;
            certifications.appendChild(certDiv);
        });
        
        const learningRoadmap = document.getElementById('learningRoadmap');
        learningRoadmap.innerHTML = '';
        
        suggestions.learning_roadmap.forEach(item => {
            const roadmapDiv = document.createElement('div');
            roadmapDiv.className = 'roadmap-item';
            roadmapDiv.innerHTML = `
                <div class="roadmap-skill">${item.skill}</div>
                <div class="roadmap-timeline">Timeline: ${item.timeline} | Priority: ${item.priority}</div>
                <div class="roadmap-resources">Resources: ${item.resources.join(', ')}</div>
            `;
            learningRoadmap.appendChild(roadmapDiv);
        });
    }
    
    function exportToPdf() {
        exportPdfBtn.disabled = true;
        exportPdfBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating PDF...';
        
        fetch('/api/export-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to generate PDF');
                });
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `resume_analysis_${new Date().getTime()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            exportPdfBtn.disabled = false;
            exportPdfBtn.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Export PDF';
            showNotification('PDF report downloaded successfully!', 'success');
        })
        .catch(error => {
            exportPdfBtn.disabled = false;
            exportPdfBtn.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Export PDF';
            showNotification(error.message || 'Error generating PDF. Please try again.', 'error');
            console.error('PDF export error:', error);
        });
    }
    
    function clearSession() {
        fetch('/api/clear-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                showNotification('Error clearing session. Please refresh the page.', 'error');
            }
        })
        .catch(error => {
            console.error('Clear session error:', error);
            location.reload();
        });
    }
    
    function showUploadError(message) {
        uploadError.style.display = 'block';
        document.getElementById('errorMessage').textContent = message;
        uploadSuccess.style.display = 'none';
    }
    
    function showUploadSuccess(message) {
        uploadSuccess.style.display = 'block';
        document.getElementById('successMessage').textContent = message;
        uploadError.style.display = 'none';
    }
});
