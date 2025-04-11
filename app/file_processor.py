import os
import PyPDF2
import docx

class FileProcessor:
    """
    A class to process different types of medical files and extract patient data.
    Supports PDF, DOCX, and TXT files.
    """
    
    @staticmethod
    def process_file(file_path):
        """
        Process a file and extract its content based on file extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Extracted text content from the file
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.txt':
            return FileProcessor._process_txt(file_path)
        elif file_extension == '.pdf':
            return FileProcessor._process_pdf(file_path)
        elif file_extension == '.docx':
            return FileProcessor._process_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    @staticmethod
    def _process_txt(file_path):
        """Process a text file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    @staticmethod
    def _process_pdf(file_path):
        """Process a PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    
    @staticmethod
    def _process_docx(file_path):
        """Process a DOCX file."""
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)