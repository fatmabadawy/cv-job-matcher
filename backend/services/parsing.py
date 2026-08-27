import pdfplumber
from docx import Document


def extract_text(file_path: str) -> str:
    """Extract plain text from PDF or DOCX file."""
    if file_path.lower().endswith(".pdf"):
        texts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
        return "\n".join(texts)
    elif file_path.lower().endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError(f"Unsupported file type: {file_path}")
