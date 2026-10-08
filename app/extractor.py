import io
from pypdf import PdfReader

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts plain text from raw PDF bytes using pypdf.
    
    Raises:
        ValueError: If PDF is corrupted, empty, or scanned without extractable text.
    """
    if not pdf_bytes or len(pdf_bytes) == 0:
        raise ValueError("Provided PDF file is empty (0 bytes).")

    try:
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
        
        extracted_pages = []
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(page_text.strip())
                
        full_text = "\n".join(extracted_pages).strip()
        
        if not full_text:
            raise ValueError(
                "PDF contains no extractable text. It may be an image-only scanned document or password protected."
            )
            
        return full_text
        
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to read PDF file: {str(e)}")

def extract_text(input_data, filename: str = None) -> str:
    """
    Unified text extraction helper that handles both raw string text and binary PDF uploads.
    """
    if isinstance(input_data, str):
        cleaned = input_data.strip()
        if not cleaned:
            raise ValueError("Input text is empty.")
        return cleaned
    elif isinstance(input_data, bytes):
        return extract_text_from_pdf(input_data)
    else:
        raise ValueError(f"Unsupported input type: {type(input_data)}")
