# import PyPDF2

# class PDFExtractor:
#     """Class for extracting text from PDF files"""
    
#     def extract_text(self, file_path):
#         """
#         Extract text from a PDF file
        
#         Args:
#             file_path: Path to the PDF file
            
#         Returns:
#             str: Extracted text from the PDF
#         """
#         try:
#             text = ""
#             with open(file_path, 'rb') as file:
#                 reader = PyPDF2.PdfReader(file)
#                 for page in reader.pages:
#                     text += page.extract_text()
#             return text
#             # print("text:",text)
#         except Exception as e:
#             print(f"Error extracting text from PDF: {str(e)}")
#             raise

import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
import easyocr
import io
import os
import numpy as np
from typing import Optional, List
import warnings
warnings.filterwarnings('ignore')

class PDFTextExtractor:
    """
    A comprehensive PDF text extractor that handles both regular text and text within images.
    
    Features:
    - Extracts structured text and tables using pdfplumber
    - Extracts text from images using EasyOCR
    - Supports multiple languages
    - GPU acceleration support
    - Memory efficient processing
    """
    
    def __init__(self, languages: List[str] = ['en'], gpu: bool = False):
        """
        Initialize the PDF text extractor.
        
        Args:
            languages (List[str]): List of language codes for OCR (default: ['en'])
                                 Supported: 'en', 'es', 'fr', 'de', 'zh', 'ja', 'ko', etc.
            gpu (bool): Whether to use GPU acceleration for OCR (default: False)
        """
        self.languages = languages
        self.gpu = gpu
        self.ocr_reader = None
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """Initialize EasyOCR reader for image text extraction."""
        self.ocr_reader = easyocr.Reader(self.languages, gpu=self.gpu, verbose=False)
    
    def extract_text(self, file_path: str, include_images: bool = True) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            include_images (bool): Whether to extract text from images using OCR
            
        Returns:
            str: Complete extracted text from the PDF
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            RuntimeError: If extraction fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        complete_text = ""
        
        try:
            # Extract structured text
            structured_text = self._extract_structured_text(file_path)
            complete_text += "=== STRUCTURED TEXT & TABLES ===\n"
            complete_text += structured_text
            
            # Extract text from images if requested
            if include_images:
                image_text = self._extract_image_text(file_path)
                if image_text.strip():
                    complete_text += "\n\n=== TEXT FROM IMAGES ===\n"
                    complete_text += image_text
            
            return complete_text.strip()
            
        except Exception as e:
            raise RuntimeError(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_structured_text(self, file_path: str) -> str:
        """Extract structured text and tables using pdfplumber."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract regular text
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text.strip() + "\n"
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        text += f"\n--- Tables from Page {page_num + 1} ---\n"
                        for table_num, table in enumerate(tables):
                            text += f"Table {table_num + 1}:\n"
                            for row in table:
                                if row:
                                    clean_row = [str(cell).strip() if cell else "" for cell in row]
                                    text += " | ".join(clean_row) + "\n"
                            text += "\n"
        except Exception as e:
            pass
        
        return text
    
    def _extract_image_text(self, file_path: str) -> str:
        """Extract text from images using EasyOCR."""
        if not self.ocr_reader:
            return ""
        
        text = ""
        try:
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            # Convert to numpy array for EasyOCR
                            img_data = pix.tobytes("png")
                            pil_image = Image.open(io.BytesIO(img_data))
                            img_array = np.array(pil_image)
                            
                            # Extract text using EasyOCR
                            results = self.ocr_reader.readtext(img_array)
                            
                            if results:
                                text += f"\n--- Image {img_index + 1} from Page {page_num + 1} ---\n"
                                for (bbox, extracted_text, confidence) in results:
                                    if confidence > 0.5:  # Filter low confidence
                                        text += f"{extracted_text.strip()} "
                                text += "\n"
                        
                        pix = None  # Free memory
                        
                    except Exception as e:
                        continue
            
            doc.close()
            
        except Exception as e:
            pass
        
        return text
    
    def extract_text_only(self, file_path: str) -> str:
        """
        Extract only structured text (no OCR on images) - faster processing.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Structured text only
        """
        return self.extract_text(file_path, include_images=False)
    
    def extract_images_info(self, file_path: str) -> List[dict]:
        """
        Get information about images in the PDF without extracting text.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            List[dict]: List of dictionaries containing image information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        images_info = []
        try:
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:
                            images_info.append({
                                'page': page_num + 1,
                                'index': img_index + 1,
                                'width': pix.width,
                                'height': pix.height,
                                'colorspace': pix.colorspace.name if pix.colorspace else 'Unknown'
                            })
                        
                        pix = None
                        
                    except Exception as e:
                        continue
            
            doc.close()
            
        except Exception as e:
            pass
        
        return images_info
    
    def get_pdf_info(self, file_path: str) -> dict:
        """
        Get basic information about the PDF.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            dict: PDF information including page count, images count, etc.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        info = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'page_count': 0,
            'images_count': 0,
            'has_text': False,
            'has_tables': False
        }
        
        try:
            # Get page count and check for text/tables
            with pdfplumber.open(file_path) as pdf:
                info['page_count'] = len(pdf.pages)
                
                for page in pdf.pages:
                    if not info['has_text'] and page.extract_text():
                        info['has_text'] = True
                    
                    if not info['has_tables'] and page.extract_tables():
                        info['has_tables'] = True
                    
                    if info['has_text'] and info['has_tables']:
                        break
            
            # Count images
            images_info = self.extract_images_info(file_path)
            info['images_count'] = len(images_info)
            
        except Exception as e:
            pass
        
        return info
    
    def set_languages(self, languages: List[str]):
        """
        Change the languages for OCR processing.
        
        Args:
            languages (List[str]): List of language codes
        """
        self.languages = languages
        self._initialize_ocr()
    
    def set_gpu(self, gpu: bool):
        """
        Enable or disable GPU acceleration.
        
        Args:
            gpu (bool): Whether to use GPU acceleration
        """
        self.gpu = gpu
        self._initialize_ocr()
    
    def extract_page_text(self, file_path: str, page_number: int, include_images: bool = True) -> str:
        """
        Extract text from a specific page.
        
        Args:
            file_path (str): Path to the PDF file
            page_number (int): Page number (1-indexed)
            include_images (bool): Whether to include OCR on images
            
        Returns:
            str: Text from the specified page
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        text = ""
        
        try:
            # Extract structured text from specific page
            with pdfplumber.open(file_path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    raise ValueError(f"Page number {page_number} is out of range (1-{len(pdf.pages)})")
                
                page = pdf.pages[page_number - 1]
                page_text = page.extract_text()
                if page_text:
                    text += f"--- Page {page_number} ---\n"
                    text += page_text.strip() + "\n"
                
                # Extract tables from specific page
                tables = page.extract_tables()
                if tables:
                    text += f"\n--- Tables from Page {page_number} ---\n"
                    for table_num, table in enumerate(tables):
                        text += f"Table {table_num + 1}:\n"
                        for row in table:
                            if row:
                                clean_row = [str(cell).strip() if cell else "" for cell in row]
                                text += " | ".join(clean_row) + "\n"
                        text += "\n"
            
            # Extract text from images on specific page
            if include_images and self.ocr_reader:
                doc = fitz.open(file_path)
                page = doc.load_page(page_number - 1)
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:
                            img_data = pix.tobytes("png")
                            pil_image = Image.open(io.BytesIO(img_data))
                            img_array = np.array(pil_image)
                            
                            results = self.ocr_reader.readtext(img_array)
                            
                            if results:
                                text += f"\n--- Image {img_index + 1} from Page {page_number} ---\n"
                                for (bbox, extracted_text, confidence) in results:
                                    if confidence > 0.5:
                                        text += f"{extracted_text.strip()} "
                                text += "\n"
                        
                        pix = None
                        
                    except Exception as e:
                        continue
                
                doc.close()
                
        except Exception as e:
            raise RuntimeError(f"Error extracting text from page {page_number}: {str(e)}")
        
        return text.strip()

# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = PDFTextExtractor(languages=['en'], gpu=False)
    
    # Example usage
    file_path = "sample.pdf"  # Replace with your PDF file
    
    # Extract all text
    text = extractor.extract_text(file_path)
    print("Complete Text:")
    print("-" * 50)
    print(text[:500] + "..." if len(text) > 500 else text)
    
    # Get PDF info
    info = extractor.get_pdf_info(file_path)
    print(f"\nPDF Info: {info}")