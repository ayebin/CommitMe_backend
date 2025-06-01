import os
import easyocr
from PIL import Image
from docx import Document
import fitz 

# EasyOCR 객체 생성
reader = easyocr.Reader(['ko', 'en']) 

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    return '\n'.join([text[1] for text in reader.readtext(image_path)])

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ''
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            all_text += f'\n--- Page {i+1} (text layer) ---\n{text}'
        else:
            # 텍스트가 없으면 이미지로 변환 후 OCR 수행
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_result = reader.readtext(img)
            ocr_text = '\n'.join([res[1] for res in ocr_result])
            all_text += f'\n--- Page {i+1} (OCR) ---\n{ocr_text}'
    return all_text


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return '\n'.join(para.text for para in doc.paragraphs)

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
        print("🔍 이미지에서 한글 OCR 수행 중...")
        return extract_text_from_image(file_path)
    
    elif ext == '.pdf':
        print("📄 PDF에서 한글 OCR 수행 중...")
        return extract_text_from_pdf(file_path)
    
    elif ext == '.docx':
        print("📝 워드에서 텍스트 추출 중 (OCR 아님)...")
        return extract_text_from_docx(file_path)
    
    else:
        return "❌ 지원하지 않는 파일 형식입니다."