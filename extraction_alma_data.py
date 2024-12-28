import os
import json
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
import docx
from striprtf.striprtf import rtf_to_text
import re

# Percorso della cartella di input
input_folder = "/Users/simonecarta/Desktop/ALMA"
output_folder = "/Users/simonecarta/Desktop/output_folder"
processed_files_path = os.path.join(output_folder, "processed_files.json")
error_log_path = os.path.join(output_folder, "error_log.json")

def load_processed_files():
    """Carica i file già elaborati."""
    if os.path.exists(processed_files_path):
        with open(processed_files_path, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_processed_files(processed_files):
    """Salva i file elaborati."""
    with open(processed_files_path, 'w', encoding='utf-8') as f:
        json.dump(list(processed_files), f, ensure_ascii=False, indent=4)

def extract_text_from_pdf(pdf_path):
    """Estrai testo dai PDF, con fallback su OCR."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        if not text.strip():
            images = convert_from_path(pdf_path)
            for image in images:
                text += pytesseract.image_to_string(image, lang="ita")
        return text.strip()
    except Exception as e:
        return f"Errore PDF: {e}"

def extract_text_from_docx(file_path):
    """Estrai testo dai file DOCX."""
    try:
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return f"Errore DOCX: {e}"

def extract_text_from_image(image_path):
    """Estrai testo dalle immagini."""
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang="ita").strip()
    except Exception as e:
        return f"Errore Immagine: {e}"

def process_folder(folder_path):
    """Elabora i file nella cartella di input."""
    extracted_data = []
    errors = []
    processed_files = load_processed_files()

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file in processed_files or file == ".DS_Store":
                continue

            file_path = os.path.join(root, file)
            print(f"Elaborando: {file_path}")

            if file.lower().endswith('.pdf'):
                content = extract_text_from_pdf(file_path)
            elif file.lower().endswith('.docx'):
                content = extract_text_from_docx(file_path)
            elif file.lower().endswith(('.png', '.jpg', '.jpeg')):
                content = extract_text_from_image(file_path)
            else:
                errors.append({"file": file_path, "error": "Formato non supportato"})
                continue

            extracted_data.append({"file": file, "content": content})
            processed_files.add(file)

    save_processed_files(processed_files)
    return extracted_data, errors

def save_data(data, errors):
    """Salva i dati estratti e i log degli errori."""
    os.makedirs(output_folder, exist_ok=True)
    with open(os.path.join(output_folder, "output_alma.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    with open(error_log_path, 'w', encoding='utf-8') as f:
        json.dump(errors, f, ensure_ascii=False, indent=4)

def main():
    """Esegui il processo di estrazione."""
    print("Avvio estrazione dati...")
    data, errors = process_folder(input_folder)
    save_data(data, errors)
    print("Estrazione completata!")

if __name__ == "__main__":
    main()
