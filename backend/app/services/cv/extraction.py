from pathlib import Path

from docx import Document
from pypdf import PdfReader


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    lines = [ln.strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def extract_from_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return clean_text("\n".join(parts))


def extract_from_docx(path: Path) -> str:
    doc = Document(str(path))
    return clean_text("\n".join(p.text for p in doc.paragraphs))


def extract_from_txt(path: Path) -> str:
    return clean_text(path.read_text(encoding="utf-8", errors="ignore"))


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
}


def extract_cv_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_from_pdf(path)
    if suffix == ".docx":
        return extract_from_docx(path)
    if suffix == ".txt":
        return extract_from_txt(path)
    raise ValueError(f"Unsupported file type: {suffix}")
