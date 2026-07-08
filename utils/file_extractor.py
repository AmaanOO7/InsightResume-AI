import os
import PyPDF2
from docx import Document


class FileExtractor:
    """Extract text from uploaded PDF and DOCX files"""

    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    @staticmethod
    def allowed_file(filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in FileExtractor.ALLOWED_EXTENSIONS
        )

    @staticmethod
    def extract_text_from_pdf(file):
        try:
            file.seek(0)

            pdf_reader = PyPDF2.PdfReader(file)

            text = ""

            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            file.seek(0)

            return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {e}")

    @staticmethod
    def extract_text_from_docx(file):
        try:
            file.seek(0)

            document = Document(file)

            text = ""

            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"

            file.seek(0)

            return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {e}")

    @staticmethod
    def extract_text(file):
        """
        Extract text directly from uploaded file.
        """

        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            return FileExtractor.extract_text_from_pdf(file)

        elif filename.endswith(".docx"):
            return FileExtractor.extract_text_from_docx(file)

        raise ValueError("Unsupported file type.")

    @staticmethod
    def validate_file_size(file, max_size_mb=10):
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        return size <= max_size_mb * 1024 * 1024
