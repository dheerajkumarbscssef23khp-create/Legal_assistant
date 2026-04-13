import docx
import PyPDF2
from io import BytesIO  # Required for safe handling of binary file streams

def extract_text_from_file(file):
    filename = file.filename.lower()
    
    # FIX 1: Read the entire file content into a binary buffer first
    # This prevents the stream from being consumed multiple times and handles binary data safely
    file_content = file.read() 
    buffer = BytesIO(file_content)
    
    # --- Text File Handling ---
    if filename.endswith(".txt"):
        # FIX 2: Use utf-8 with an error handler ('ignore') for robustness
        try:
            return file_content.decode("utf8", errors='ignore') 
        except:
             # Fallback to a non-failing encoding if utf-8 fails completely
             return file_content.decode("latin-1", errors='ignore')

    # --- PDF File Handling ---
    elif filename.endswith(".pdf"):
        try:
            # FIX 3: Pass the binary buffer (not the Flask FileStorage object) to PyPDF2
            reader = PyPDF2.PdfReader(buffer)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            # Return error message string instead of raising an exception that crashes the server
            return "" # Returning an empty string will trigger the check in backend-main.py

    # --- DOCX File Handling ---
    elif filename.endswith(".docx"):
        try:
            # FIX 4: Pass the binary buffer (not the Flask FileStorage object) to docx.Document
            doc = docx.Document(buffer)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return "" # Returning an empty string will trigger the check in backend-main.py

    else:
        return "Unsupported file format."