import io
import logging
import pdfplumber

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> str:

    text = ""

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        logger.error(f"Error reading PDF with pdfplumber: {e}")
        raise ValueError(
            f"Failed to parse PDF document: {str(e)}"
        )

    text = text.strip()

    if len(text) < 100:

        try:
            import pytesseract
            from pdf2image import convert_from_path

            pytesseract.get_tesseract_version()

            logger.info(
                "Text extraction empty. Attempting OCR..."
            )

            raise ValueError(
                "This document appears to be a scanned image. "
                "OCR is currently not fully configured on this environment "
                "(requires Poppler and Tesseract system binaries)."
            )

        except (ImportError, Exception):

            raise ValueError(
                "This PDF is a scanned image and contains no selectable text. "
                "Please upload a standard text-based PDF or configure "
                "Tesseract/Poppler on the server."
            )

    return text