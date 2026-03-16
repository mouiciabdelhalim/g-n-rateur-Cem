import logging
# Removed unused import io
import PyPDF2
from docx import Document

logger = logging.getLogger(__name__)

def extract_text_from_file(uploaded_file) -> str:
    """
    Extract text content from an uploaded Streamlit file (.pdf, .docx, .txt).
    Returns the extracted string or raises an Exception.
    """
    if uploaded_file is None:
        return ""
        
    filename = uploaded_file.name.lower()
    
    try:
        if filename.endswith(".pdf"):
            return _extract_from_pdf(uploaded_file)
        elif filename.endswith(".docx"):
            return _extract_from_docx(uploaded_file)
        elif filename.endswith(".txt"):
            return str(uploaded_file.read(), "utf-8", errors="replace")
        else:
            raise ValueError(f"Extension non supportée: {filename}")
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction de {filename}: {e}")
        raise e

def _extract_from_pdf(uploaded_file) -> str:
    reader = PyPDF2.PdfReader(uploaded_file)
    extracted_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text.append(text)
    return "\n".join(extracted_text)

def _extract_from_docx(uploaded_file) -> str:
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])
