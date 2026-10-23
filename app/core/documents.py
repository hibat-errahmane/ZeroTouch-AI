from pathlib import Path
import pymupdf

class DocumentError(ValueError):
    pass

def extract_text(content: bytes, suffix: str) -> str:
    if suffix == ".txt":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DocumentError("TXT documents must use UTF-8 encoding.") from exc
        if any(ord(char) < 32 and char not in "\n\r\t" for char in text):
            raise DocumentError("The TXT file contains binary control characters.")
    elif suffix == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise DocumentError("The file does not have a valid PDF signature.")
        try:
            with pymupdf.open(stream=content, filetype="pdf") as document:
                if document.needs_pass:
                    raise DocumentError("Password-protected PDFs are not supported.")
                if len(document) > 100:
                    raise DocumentError("PDFs may contain at most 100 pages.")
                text = "\n".join(page.get_text() for page in document)
        except DocumentError:
            raise
        except Exception as exc:
            raise DocumentError("The PDF could not be read. Upload an intact text-based PDF.") from exc
    else:
        raise DocumentError("Only PDF and TXT documents are supported.")
    if not text.strip():
        raise DocumentError("No text found. Scanned PDFs need OCR, which is not available in Phase 1.")
    if len(text) > 1_000_000:
        raise DocumentError("Extracted text exceeds the one-million-character limit.")
    return text.strip()

def safe_name(filename: str) -> str:
    return Path(filename.replace("\\", "/")).name[:200]
