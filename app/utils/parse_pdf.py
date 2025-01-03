import io
from pypdf import PdfReader

def parse_pdf_file(pdf_file):
    """
    Extracts text from an uploaded PDF file.
    """
    try:
        pdf_stream = io.BytesIO(pdf_file.read())
        reader = PdfReader(pdf_stream)
        extracted_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
        return extracted_text
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")