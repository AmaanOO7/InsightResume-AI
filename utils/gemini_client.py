"""
InsightResume AI
Google Gemini Client

Author: Aman Kumar

Handles all AI communication using Google's Gemini API.
"""

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig


# ==========================================================
# Logging
# ==========================================================

logger = logging.getLogger(__name__)


# ==========================================================
# Gemini Client
# ==========================================================

class GeminiClient:
    """
    Google Gemini Client

    Handles all communication with Gemini.
    """

    MODEL_NAME = "gemini-2.5-flash"

    MAX_RETRIES = 3

    RETRY_DELAY = 2

    TEMPERATURE = 0.4

    TOP_P = 0.90

    MAX_OUTPUT_TOKENS = 8192

    # ------------------------------------------------------

    def __init__(self, api_key: str):

        if not api_key:

            raise ValueError(
                "GOOGLE_API_KEY is missing."
            )

        self.api_key = api_key

        self.model = None

        self._initialize()

    # ------------------------------------------------------

    def _initialize(self):

        """
        Initialize Gemini model.
        """

        try:

            genai.configure(
                api_key=self.api_key
            )

            self.model = genai.GenerativeModel(
                self.MODEL_NAME
            )

            logger.info(
                "Google Gemini initialized successfully."
            )

        except Exception:

            logger.exception(
                "Failed to initialize Gemini."
            )

            raise

    # ------------------------------------------------------

    @property
    def initialized(self):

        return self.model is not None

    # ------------------------------------------------------

    def get_model_name(self):

        return self.MODEL_NAME

    # ==========================================================
    # Internal Helpers
    # ==========================================================

    def _clean_response(
        self,
        text: str
    ) -> str:

        """
        Remove markdown wrappers.
        """

        text = text.strip()

        text = re.sub(
            r"^```json",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"^```",
            "",
            text
        )

        text = re.sub(
            r"```$",
            "",
            text
        )

        return text.strip()

    # ------------------------------------------------------

    def _extract_json(
        self,
        text: str
    ) -> Dict[str, Any]:

        """
        Extract JSON from Gemini response.
        """

        if not text:

            raise ValueError(
                "Gemini returned an empty response."
            )

        cleaned = self._clean_response(text)

        try:

            return json.loads(cleaned)

        except json.JSONDecodeError:

            pass

        start = cleaned.find("{")

        end = cleaned.rfind("}")

        if start == -1 or end == -1:

            raise ValueError(
                "No JSON object found in Gemini response."
            )

        try:

            return json.loads(
                cleaned[start:end + 1]
            )

        except json.JSONDecodeError as e:

            logger.exception(
                "Invalid JSON returned by Gemini."
            )

            raise ValueError(
                f"Unable to parse JSON.\n{e}"
            )

    # ------------------------------------------------------

    def _generate(
        self,
        prompt: str
    ) -> str:

        """
        Low-level Gemini request.
        """

        if not self.initialized:

            raise RuntimeError(
                "Gemini model is not initialized."
            )

        last_error = None

        for attempt in range(1, self.MAX_RETRIES + 1):

            try:

                logger.info(
                    "Gemini request (%s/%s)",
                    attempt,
                    self.MAX_RETRIES
                )

                response = self.model.generate_content(

                    prompt,

                    generation_config=GenerationConfig(

                        temperature=self.TEMPERATURE,

                        top_p=self.TOP_P,

                        max_output_tokens=self.MAX_OUTPUT_TOKENS

                    )

                )

                if response is None:

                    raise RuntimeError(
                        "Gemini returned no response."
                    )

                if not hasattr(response, "text"):

                    raise RuntimeError(
                        "Gemini returned empty text."
                    )

                text = response.text.strip()

                if not text:

                    raise RuntimeError(
                        "Gemini response is empty."
                    )

                return text

            except Exception as e:

                last_error = e

                logger.warning(

                    "Gemini attempt %s failed.",

                    attempt

                )

                if attempt < self.MAX_RETRIES:

                    time.sleep(
                        self.RETRY_DELAY
                    )

        logger.exception(
            "All Gemini retries failed."
        )

        raise RuntimeError(
            str(last_error)
        )

    # ==========================================================
    # Generic Methods
    # ==========================================================

    def generate_text(
        self,
        prompt: str
    ) -> str:

        """
        Generate plain text response.
        """

        return self._generate(prompt)

    # ------------------------------------------------------

    def generate_json(
        self,
        prompt: str,
        required_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        """
        Generate JSON response.

        Automatically validates required keys.
        """

        response = self.generate_text(
            prompt
        )

        data = self._extract_json(
            response
        )

        if required_keys:

            self.validate_json(

                data,

                required_keys

            )

        return data
    # ==========================================================
    # Resume Analysis
    # ==========================================================

    def analyze_resume(
        self,
        resume_text: str,
        job_description: str,
        agent_instructions: str
    ) -> Dict[str, Any]:
        """
        Analyze a resume against a target job description.
        """

        prompt = f"""
You are an ATS Resume Expert, Senior Recruiter, Hiring Manager and Career Coach.

{agent_instructions}

Compare the following Resume with the Job Description.

========================
RESUME
========================

{resume_text}

========================
JOB DESCRIPTION
========================

{job_description}

Your task:

1. Evaluate ATS compatibility.
2. Evaluate skill match.
3. Evaluate keyword match.
4. Evaluate experience relevance.
5. Evaluate education relevance.
6. Identify strengths.
7. Identify weaknesses.
8. Suggest improvements.
9. Give recruiter feedback.
10. Give ATS feedback.

Return ONLY valid JSON.

Do NOT include markdown.

Return exactly this structure:

{{
    "resume_score":0,
    "ats_score":0,
    "experience_level":"",

    "skills_found":[],

    "missing_skills":[],

    "matched_keywords":[],

    "missing_keywords":[],

    "strengths":[],

    "weaknesses":[],

    "improvements":[],

    "summary":"",

    "ats_feedback":"",

    "recruiter_feedback":""
}}

Rules:

Resume Score:
0-100

ATS Score:
0-100

Provide:

Minimum 5 strengths

Minimum 5 weaknesses

Minimum 8 improvements

Summary:
150-250 words

ATS Feedback:
120-180 words

Recruiter Feedback:
150-250 words

Compare ONLY against the supplied Job Description.

Return ONLY JSON.
"""

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

        analysis = self.generate_json(

            prompt,

            required_keys

        )

        self.validate_analysis(

            analysis

        )

        logger.info(

            "Resume analysis completed."

        )

        return analysis

    # ----------------------------------------------------------

    def validate_analysis(
        self,
        analysis: Dict[str, Any]
    ) -> bool:
        """
        Validate resume analysis response.
        """

        numeric_fields = [

            "resume_score",

            "ats_score"

        ]

        list_fields = [

            "skills_found",

            "missing_skills",

            "matched_keywords",

            "missing_keywords",

            "strengths",

            "weaknesses",

            "improvements"

        ]

        text_fields = [

            "experience_level",

            "summary",

            "ats_feedback",

            "recruiter_feedback"

        ]

        for field in numeric_fields:

            value = analysis[field]

            if not isinstance(value, (int, float)):

                raise ValueError(

                    f"{field} must be numeric."

                )

            if value < 0 or value > 100:

                raise ValueError(

                    f"{field} must be between 0 and 100."

                )

        for field in list_fields:

            if not isinstance(

                analysis[field],

                list

            ):

                raise ValueError(

                    f"{field} must be a list."

                )

        for field in text_fields:

            if not isinstance(

                analysis[field],

                str

            ):

                raise ValueError(

                    f"{field} must be text."

                )

        return True

    # ==========================================================
    # Interview Questions
    # ==========================================================

    def generate_interview_questions(
        self,
        resume_text: str,
        job_description: str,
        agent_instructions: str
    ) -> Dict[str, Any]:
        """
        Generate personalized interview questions.
        """

        prompt = f"""
You are a Senior Hiring Manager, Technical Interviewer and Career Coach.

{agent_instructions}

Carefully study BOTH documents.

========================
RESUME
========================

{resume_text}

========================
JOB DESCRIPTION
========================

{job_description}

Generate a realistic interview customized for this candidate.

Requirements

Return ONLY JSON.

Do NOT use Markdown.

Return exactly:

{{
    "domain_questions":[
        {{
            "question":"",
            "model_answer":"",
            "difficulty":"",
            "topic":"",
            "why_this_question":""
        }}
    ],

    "hr_questions":[
        {{
            "question":"",
            "model_answer":"",
            "difficulty":"",
            "quality_being_tested":"",
            "why_this_question":""
        }}
    ]
}}

Rules

Generate exactly:

6 domain-specific questions

4 HR questions

Difficulty progression

Easy

Easy

Medium

Medium

Hard

Hard

Domain questions must evaluate:

• Required skills

• Missing skills

• Projects

• Work experience

• Responsibilities

• Problem solving

• Decision making

• Real workplace scenarios

HR questions should evaluate

• Communication

• Teamwork

• Leadership

• Adaptability

• Accountability

• Career goals

Each answer should be approximately 100-180 words.

Return ONLY JSON.
"""

        required_keys = [

            "domain_questions",

            "hr_questions"

        ]

        questions = self.generate_json(

            prompt,

            required_keys

        )

        self.validate_interview_questions(

            questions

        )

        logger.info(

            "Interview questions generated."

        )

        return questions

    # ----------------------------------------------------------

    def validate_interview_questions(
        self,
        data: Dict[str, Any]
    ) -> bool:

        domain = data["domain_questions"]

        hr = data["hr_questions"]

        if not isinstance(domain, list):

            raise ValueError(

                "domain_questions must be a list."

            )

        if not isinstance(hr, list):

            raise ValueError(

                "hr_questions must be a list."

            )

        if len(domain) != 6:

            raise ValueError(

                "Exactly 6 domain questions are required."

            )

        if len(hr) != 4:

            raise ValueError(

                "Exactly 4 HR questions are required."

            )

        required_domain_fields = [

            "question",

            "model_answer",

            "difficulty",

            "topic",

            "why_this_question"

        ]

        required_hr_fields = [

            "question",

            "model_answer",

            "difficulty",

            "quality_being_tested",

            "why_this_question"

        ]

        for question in domain:

            self.validate_json(

                question,

                required_domain_fields

            )

        for question in hr:

            self.validate_json(

                question,

                required_hr_fields

            )

        return True

    # ==========================================================
    # Career Suggestions
    # ==========================================================

    def generate_career_suggestions(
        self,
        resume_text: str,
        job_description: str,
        agent_instructions: str
    ) -> Dict[str, Any]:
        """
        Generate career recommendations.
        """

        prompt = f"""
You are an experienced Career Advisor, Recruiter and Industry Mentor.

{agent_instructions}

Analyze BOTH documents carefully.

========================
RESUME
========================

{resume_text}

========================
JOB DESCRIPTION
========================

{job_description}

Recommend the best career path.

Return ONLY JSON.

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
        "currency":"",
        "period":""
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

Suggest:

5 suitable roles

5 certifications

A realistic salary range

A learning roadmap

Recommendations must be based on BOTH the Resume and the Job Description.

Return ONLY JSON.
"""

        required_keys = [

            "suitable_roles",

            "salary_range",

            "certifications",

            "learning_roadmap"

        ]

        suggestions = self.generate_json(

            prompt,

            required_keys

        )

        self.validate_career_suggestions(

            suggestions

        )

        logger.info(

            "Career suggestions generated."

        )

        return suggestions

    # ----------------------------------------------------------

    def validate_career_suggestions(
        self,
        data: Dict[str, Any]
    ) -> bool:

        if not isinstance(

            data["suitable_roles"],

            list

        ):

            raise ValueError(

                "suitable_roles must be a list."

            )

        if not isinstance(

            data["certifications"],

            list

        ):

            raise ValueError(

                "certifications must be a list."

            )

        if not isinstance(

            data["learning_roadmap"],

            list

        ):

            raise ValueError(

                "learning_roadmap must be a list."

            )

        if len(data["suitable_roles"]) != 5:

            raise ValueError(

                "Exactly 5 suitable roles are required."

            )

        if len(data["certifications"]) != 5:

            raise ValueError(

                "Exactly 5 certifications are required."

            )

        salary = data["salary_range"]

        self.validate_json(

            salary,

            [

                "min",

                "max",

                "currency",

                "period"

            ]

        )

        return True

    # ==========================================================
    # Generic JSON Validation
    # ==========================================================

    def validate_json(
        self,
        data: Dict[str, Any],
        required_keys: List[str]
    ) -> bool:
        """
        Validate that the AI response contains all required keys.
        """

        if not isinstance(data, dict):

            raise ValueError(
                "AI response is not a valid JSON object."
            )

        missing = [

            key

            for key in required_keys

            if key not in data

        ]

        if missing:

            raise ValueError(

                "Missing required JSON keys: "

                + ", ".join(missing)

            )

        return True

    # ----------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify that Gemini is responding correctly.
        """

        prompt = """
Return ONLY valid JSON.

{
    "status":"ok"
}
"""

        try:

            response = self.generate_json(

                prompt,

                ["status"]

            )

            return response.get("status") == "ok"

        except Exception:

            logger.exception(

                "Gemini health check failed."

            )

            return False

    # ----------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """
        Return Gemini client status.
        """

        return {

            "provider": "Google Gemini",

            "model": self.MODEL_NAME,

            "initialized": self.initialized,

            "health": self.health_check()

        }

    # ----------------------------------------------------------

    def close(self):
        """
        Release model resources.

        Reserved for future implementations.
        """

        self.model = None

        logger.info(

            "Gemini client closed."

        )

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def provider(self) -> str:

        return "Google Gemini"

    @property
    def version(self) -> str:

        return "4.0.0"

    @property
    def model_name(self) -> str:

        return self.MODEL_NAME

    # ==========================================================
    # Future Features
    # ==========================================================
    #
    # Future methods can be added here:
    #
    # - generate_cover_letter()
    #
    # - optimize_resume()
    #
    # - resume_chat()
    #
    # - linkedin_profile_review()
    #
    # - resume_rewriter()
    #
    # - ats_keyword_optimizer()
    #
    # - salary_negotiation_advisor()
    #
    # - recruiter_simulation()
    #
    # ==========================================================
