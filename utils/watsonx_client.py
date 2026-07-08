print(">>> Loaded utils/watsonx_client.py <<<")

import json
import time
import traceback

import google.generativeai as genai


class WatsonxClient:
    """
    Gemini-powered replacement for IBM watsonx.ai client.

    This class intentionally keeps the same class name so that
    app.py does NOT need any changes.
    """

    def __init__(self, api_key, project_id, url, model_id):
        """
        Keep constructor compatible with the previous IBM version.

        Parameters project_id, url and model_id are ignored but
        retained for compatibility with existing code.
        """

        self.api_key = api_key
        self.project_id = project_id
        self.url = url
        self.model_id = model_id

        self.model = None

        self._initialize_model()

    ####################################################################
    # INITIALIZATION
    ####################################################################

    def _initialize_model(self):

        try:

            if not self.api_key:
                raise Exception(
                    "GOOGLE_API_KEY not found inside .env file."
                )

            genai.configure(api_key=self.api_key)

            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash"
            )

            print("=" * 60)
            print("✓ Gemini initialized successfully")
            print("=" * 60)

        except Exception:

            print("=" * 60)
            print("Gemini Initialization Error")
            traceback.print_exc()
            print("=" * 60)

            raise

    ####################################################################
    # INTERNAL HELPERS
    ####################################################################

    def _extract_json(self, text):

        if not text:
            raise Exception("Gemini returned an empty response.")

        text = text.strip()

        text = text.replace("```json", "")
        text = text.replace("```", "")

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise Exception(
                "No JSON object found in AI response.\n\n"
                f"Response was:\n{text}"
            )

        json_text = text[start:end + 1]

        return json.loads(json_text)

    def _call_gemini(self, prompt, retries=3):

        if self.model is None:
            raise Exception("Gemini model not initialized.")

        last_error = None

        for attempt in range(retries):

            try:

                print("=" * 60)
                print(f"Gemini Request (Attempt {attempt + 1})")
                print("=" * 60)

                from google.generativeai.types import GenerationConfig

                response = self.model.generate_content(
                    prompt,
                    generation_config=GenerationConfig(
                        temperature=0.4,
                        top_p=0.9,
                        max_output_tokens=8192
                    )
                )

                if not response:
                    raise Exception("No response received.")

                if not hasattr(response, "text"):
                    raise Exception(
                        "Gemini returned empty text."
                    )

                text = response.text.strip()

                print("=" * 60)
                print("Gemini Response")
                print("=" * 60)
                print(text)
                print("=" * 60)

                return text

            except Exception as e:

                last_error = e

                print(
                    f"Retry {attempt+1} failed..."
                )

                time.sleep(2)

        raise Exception(last_error)

    ####################################################################
    # GENERIC RESPONSE
    ####################################################################

    def generate_response(self, prompt):

        return self._call_gemini(prompt)

    ####################################################################
    # RESUME ANALYSIS
    ####################################################################

    def analyze_resume(
        self,
        resume_text,
        job_description,
        agent_instructions
    ):

        prompt = f"""
            You are an expert ATS Resume Reviewer, Senior Recruiter, Hiring Manager and Career Coach.

            {agent_instructions}

            You are given:

            1. Candidate Resume
            2. Target Job Description

            Your job is to compare BOTH documents exactly like a recruiter.

            Resume

            {resume_text}

            Job Description

            {job_description}

            Return ONLY valid JSON.

            No markdown.

            No explanation.

            Return exactly:

            {{
                "resume_score": 0,
                "ats_score": 0,
                "experience_level": "",

                "skills_found": [],

                "missing_skills": [],

                "matched_keywords": [],

                "missing_keywords": [],

                "strengths": [],

                "weaknesses": [],

                "improvements": [],

                "summary": "",

                "ats_feedback": "",

                "recruiter_feedback": ""
            }}

            Rules

            Resume Score:
            0-100

            ATS Score:
            0-100

            Compare the resume directly against the Job Description.

            Find:

            • Missing Skills

            • Missing Keywords

            • Matching Keywords

            • Experience Match

            • Education Match

            • Responsibilities Match

            • ATS Compatibility

            • Never ask duplicate or similar questions.

            • Questions should test different competencies.

            • Cover as many important job requirements as possible.

            • If the candidate appears overqualified,
            increase question difficulty.

            • If the candidate appears junior,
            focus on fundamentals before advanced scenarios

            Strengths:
            minimum 5

            Weaknesses:
            minimum 5

            Improvements:
            minimum 8

            Summary:
            150-250 words

            ATS Feedback:
            minimum 120 words

            Recruiter Feedback:
            minimum 150 words

            Return ONLY JSON.
            """
        try:

            response = self.generate_response(prompt)

            analysis = self._extract_json(response)

            required_keys = [
                "resume_score",
                "ats_score",
                "experience_level",
                "skills_found",
                "missing_skills",
                "matched_keywords",
                "missing_keywords",
                "strengths",
                "weaknesses",
                "improvements",
                "summary",
                "ats_feedback",
                "recruiter_feedback"
            ]

            for key in required_keys:

                if key not in analysis:

                    raise Exception(
                        f"Missing key '{key}' in Gemini response."
                    )

            return analysis

        except Exception:

            print("=" * 60)
            print("RESUME ANALYSIS ERROR")
            traceback.print_exc()
            print("=" * 60)

            raise

    ####################################################################
    # INTERVIEW QUESTIONS
    ####################################################################

    def generate_interview_questions(
        self,
        resume_text,
        job_description,
        agent_instructions
    ):

        prompt = f"""
            You are a world-class Hiring Manager, Talent Acquisition Specialist, Recruitment Consultant, Industry Expert, Career Coach, Subject Matter Expert, and Professional Interviewer with more than 20 years of interviewing and hiring experience.

            {agent_instructions}

            You have successfully interviewed and hired candidates across technical, non-technical, managerial, business, finance, healthcare, education, engineering, marketing, customer service, operations, HR, BPO, sales, government, and many other industries.

            Your first responsibility is to carefully identify the target job role, required experience level, required skills, and hiring expectations from BOTH the Candidate Resume and the Target Job Description.

            Never assume the candidate belongs to any specific industry.

            Automatically adapt your interviewing style, terminology, difficulty level, and evaluation criteria according to the target job role.

            =========================================================
            CANDIDATE RESUME
            =========================================================

            {resume_text}

            =========================================================
            TARGET JOB DESCRIPTION
            =========================================================

            {job_description}

            =========================================================
            YOUR OBJECTIVE
            =========================================================

            Generate a realistic interview that closely resembles an actual interview conducted by an experienced interviewer hiring for this exact role.

            The interview should evaluate whether the candidate is genuinely capable of performing the responsibilities mentioned in the Job Description.

            The interview should gradually become more challenging, beginning with fundamental concepts and progressing to practical, analytical, scenario-based, and decision-making questions.

            =========================================================
            ANALYZE BOTH DOCUMENTS
            =========================================================

            Compare the Resume with the Job Description and evaluate:

            • Skills that match
            • Skills that are missing
            • Candidate's work experience
            • Projects
            • Responsibilities
            • Education
            • Certifications
            • Achievements
            • Domain knowledge
            • Industry terminology
            • Required tools/software/platforms
            • Leadership experience
            • Communication skills
            • Problem-solving ability
            • Decision-making ability
            • Adaptability
            • Learning ability
            • Career progression
            • Overall suitability for the target role

            =========================================================
            QUESTION DISTRIBUTION
            =========================================================

            Generate exactly

            6 Domain-Specific Questions

            Difficulty progression:

            Question 1 → Easy

            Question 2 → Easy

            Question 3 → Medium

            Question 4 → Medium

            Question 5 → Hard

            Question 6 → Hard

            Generate exactly

            4 HR / Behavioural Questions

            Difficulty progression:

            Easy

            Medium

            Medium

            Hard

            =========================================================
            DOMAIN-SPECIFIC QUESTIONS
            =========================================================

            The questions must be based primarily on the Job Description and then customized using the Resume.

            Questions may include:

            • Job-specific knowledge
            • Practical experience
            • Resume projects
            • Daily work responsibilities
            • Industry best practices
            • Real workplace situations
            • Case studies
            • Scenario-based questions
            • Decision making
            • Troubleshooting
            • Process improvement
            • Client handling
            • Customer interaction
            • Stakeholder management
            • Leadership
            • Communication
            • Risk handling
            • Quality improvement
            • Productivity
            • Performance optimization
            • Compliance
            • Ethics
            • Domain-specific tools and software

            If important skills or responsibilities are missing from the Resume but are required by the Job Description, generate interview questions around those areas to evaluate the candidate's understanding and readiness to learn.

            Avoid generic textbook questions.

            Every question should feel like it came from a real interviewer.

            =========================================================
            MODEL ANSWERS
            =========================================================

            For every question generate an ideal answer.

            The answer should:

            • Be simple and easy to understand.
            • Sound natural when spoken in an interview.
            • Include important industry keywords naturally.
            • Demonstrate practical understanding.
            • Explain WHY the answer is correct.
            • Mention best practices where appropriate.
            • Include a real-world example whenever possible.
            • Be professional yet conversational.
            • Be detailed enough to help the candidate prepare confidently.
            • Be approximately 100–180 words.

            The answers should help the candidate succeed in an actual interview.

            =========================================================
            HR / BEHAVIOURAL QUESTIONS
            =========================================================

            Evaluate areas such as:

            • Communication
            • Teamwork
            • Leadership
            • Ownership
            • Accountability
            • Conflict Resolution
            • Time Management
            • Problem Solving
            • Learning Ability
            • Adaptability
            • Stress Management
            • Customer Focus
            • Professional Ethics
            • Career Goals
            • Decision Making
            • Collaboration
            • Initiative
            • Motivation

            =========================================================
            OUTPUT FORMAT
            =========================================================

            Return ONLY valid JSON.

            Do NOT use Markdown.

            Do NOT include explanations.

            Return exactly:

            {{
                "domain_questions": [
                    {{
                        "question": "",
                        "model_answer": "",
                        "difficulty": "Easy",
                        "topic": "",
                        "why_this_question": ""
                    }}
                ],
                "hr_questions": [
                    {{
                        "question": "",
                        "model_answer": "",
                        "difficulty": "Easy",
                        "quality_being_tested": "",
                        "why_this_question": ""
                    }}
                ]
            }}

            =========================================================
            RULES
            =========================================================

            • Return exactly 6 domain-specific questions.
            • Return exactly 4 HR/Behavioural questions.
            • Difficulty values must only be Easy, Medium, or Hard.
            • Every question must be personalized using BOTH the Resume and Job Description.
            • Do not repeat similar questions.
            • Questions should reflect real hiring practices.
            • Return ONLY valid JSON.
            """
        try:

            response = self.generate_response(prompt)

            questions = self._extract_json(response)

            if "domain_questions" not in questions:
                raise Exception(
                    "domain_questions missing in AI response."
                )

            if "hr_questions" not in questions:
                raise Exception(
                    "hr_questions missing in AI response."
                )

            if not isinstance(
                questions["domain_questions"],
                list
            ):
                raise Exception(
                    "domain_questions must be a list."
                )

            if not isinstance(
                questions["hr_questions"],
                list
            ):
                raise Exception(
                    "hr_questions must be a list."
                )

            return questions

        except Exception:

            print("=" * 60)
            print("INTERVIEW QUESTION ERROR")
            traceback.print_exc()
            print("=" * 60)

            raise

    ####################################################################
    # CAREER SUGGESTIONS
    ####################################################################

    def generate_career_suggestions(
        self,
        resume_text,
        job_description,
        agent_instructions
    ):

        prompt = f"""
            You are an experienced Career Advisor,
            Industry Mentor,
            Recruitment Specialist,
            and Hiring Manager.

            {agent_instructions}

            You are given:

            1. Candidate Resume
            2. Target Job Description

            Analyze BOTH documents carefully.

            Resume

            {resume_text}

            Job Description

            {job_description}

            Your task is to recommend the BEST career path considering BOTH the candidate profile and the target role.

            Return ONLY valid JSON.

            No markdown.

            No explanations.

            Return exactly:

            {{
                "suitable_roles":[
                    {{
                        "title":"",
                        "description":"",
                        "match_percentage":0
                    }}
                ],

                "salary_range":{{
                    "min":0,
                    "max":0,
                    "currency":"USD",
                    "period":"annual"
                }},

                "certifications":[
                    {{
                        "name":"",
                        "provider":"",
                        "priority":"",
                        "reason":""
                    }}
                ],

                "learning_roadmap":[
                    {{
                        "skill":"",
                        "timeline":"",
                        "resources":[],
                        "priority":""
                    }}
                ]
            }}

            Requirements

            - Suggest 5 suitable roles.
            - Base suggestions on BOTH the Resume and the Job Description.
            - Consider:
                • Candidate experience
                • Technical skills
                • Soft skills
                • Education
                • Missing skills
                • Career goals inferred from the target job
            - Recommend 5 certifications that improve the candidate's chances for THIS job.
            - Learning roadmap should specifically help the candidate become a stronger match for the uploaded Job Description.
            - Salary should be realistic for the suggested role.
            - Return ONLY JSON.
            """
        try:

            response = self.generate_response(prompt)

            suggestions = self._extract_json(response)

            required_keys = [
                "suitable_roles",
                "salary_range",
                "certifications",
                "learning_roadmap"
            ]

            for key in required_keys:

                if key not in suggestions:

                    raise Exception(
                        f"Missing '{key}' in AI response."
                    )

            if not isinstance(
                suggestions["suitable_roles"],
                list
            ):
                raise Exception(
                    "suitable_roles must be a list."
                )

            if not isinstance(
                suggestions["certifications"],
                list
            ):
                raise Exception(
                    "certifications must be a list."
                )

            if not isinstance(
                suggestions["learning_roadmap"],
                list
            ):
                raise Exception(
                    "learning_roadmap must be a list."
                )

            salary = suggestions["salary_range"]

            if not isinstance(salary, dict):
                raise Exception(
                    "salary_range must be a JSON object."
                )

            salary_keys = [
                "min",
                "max",
                "currency",
                "period"
            ]

            for key in salary_keys:

                if key not in salary:

                    raise Exception(
                        f"salary_range missing '{key}'"
                    )

            return suggestions

        except Exception:

            print("=" * 60)
            print("CAREER SUGGESTIONS ERROR")
            traceback.print_exc()
            print("=" * 60)

            raise

    ####################################################################
    # JSON VALIDATOR
    ####################################################################

    def validate_json(
        self,
        data,
        required_keys
    ):
        """
        Generic validator used by future modules.
        """

        if not isinstance(data, dict):

            raise Exception(
                "AI response is not a JSON object."
            )

        missing = []

        for key in required_keys:

            if key not in data:

                missing.append(key)

        if missing:

            raise Exception(
                "Missing JSON keys: "
                + ", ".join(missing)
            )

        return True
     ####################################################################
    # SAFE AI CALL
    ####################################################################

    def generate_json(
        self,
        prompt,
        required_keys=None
    ):
        """
        Generic helper used by future features.

        It:
        - Calls Gemini
        - Extracts JSON
        - Validates required keys
        """

        response = self.generate_response(prompt)

        data = self._extract_json(response)

        if required_keys:

            self.validate_json(
                data,
                required_keys
            )

        return data

    ####################################################################
    # LOGGING
    ####################################################################

    def log(self, title, value=None):

        print("=" * 60)

        print(title)

        if value is not None:

            print(value)

        print("=" * 60)

    ####################################################################
    # HEALTH CHECK
    ####################################################################

    def health_check(self):
        """
        Verify that Gemini is responding correctly.
        """

        prompt = """
Return ONLY this JSON.

{
    "status":"ok"
}
"""

        try:

            response = self.generate_json(
                prompt,
                ["status"]
            )

            return response["status"] == "ok"

        except Exception:

            traceback.print_exc()

            return False

    ####################################################################
    # MODEL INFORMATION
    ####################################################################

    def get_model_name(self):

        return "gemini-2.5-flash"

    ####################################################################
    # FUTURE FEATURES
    ####################################################################
    #
    # The following methods will be implemented in the next upgrade:
    #
    # - analyze_resume_with_job_description()
    #
    # - calculate_ats_match()
    #
    # - generate_cover_letter()
    #
    # - optimize_resume()
    #
    # - recruiter_feedback()
    #
    # - resume_chat()
    #
    ####################################################################
    ####################################################################
    # COMPATIBILITY METHODS
    ####################################################################

    def is_initialized(self):
        """
        Returns True if the AI model has been initialized.
        """

        return self.model is not None

    def get_status(self):
        """
        Returns current client status.
        """

        return {
            "provider": "Google Gemini",
            "model": self.get_model_name(),
            "initialized": self.is_initialized()
        }

    ####################################################################
    # CLEANUP
    ####################################################################

    def close(self):
        """
        Cleanup resources.

        Reserved for future use.
        """

        self.model = None

    ####################################################################
    # DEBUG
    ####################################################################

    def debug_prompt(self, prompt):
        """
        Prints prompt for debugging.
        """

        self.log("PROMPT", prompt)

    def debug_response(self, response):
        """
        Prints response for debugging.
        """

        self.log("RESPONSE", response)

    ####################################################################
    # VERSION
    ####################################################################

    @property
    def version(self):
        return "3.0.0"

    @property
    def provider(self):
        return "Google Gemini"

    @property
    def ai_model(self):
        return self.get_model_name()

    ####################################################################
    # END OF CLASS
    ####################################################################