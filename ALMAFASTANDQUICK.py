import os
import json
from PIL import Image
import pytesseract
import pdfplumber
from pdf2image import convert_from_path
import docx
from odf.opendocument import load
from odf.text import P
import subprocess

# Percorsi delle cartelle di input e output
input_folder_1 = "/Users/simonecarta/Desktop/input_folder_1"
input_folder_2 = "/Users/simonecarta/Desktop/input_folder_2"
output_folder = "/Users/simonecarta/Desktop/output_folder"

# Percorso del file per registrare i file già elaborati
processed_files_path = os.path.join(output_folder, "processed_files.json")

# Carica i file già elaborati
def load_processed_files():
    if os.path.exists(processed_files_path):
        with open(processed_files_path, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

# Salva i file elaborati
def save_processed_files(processed_files):
    with open(processed_files_path, 'w', encoding='utf-8') as f:
        json.dump(list(processed_files), f, ensure_ascii=False, indent=4)

# Funzione per estrarre testo da file .doc
def extract_text_from_doc(file_path):
    try:
        result = subprocess.run(['antiword', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Errore durante l'elaborazione del file .doc: {e}"

# Funzione per estrarre testo da file .ai
def extract_text_from_ai(file_path):
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang="ita")
        return text.strip()
    except Exception as e:
        return f"Errore durante l'elaborazione del file .ai: {e}"

# Funzione per estrarre testo da immagini
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="ita")
        return text.strip()
    except Exception as e:
        return f"Errore durante l'elaborazione dell'immagine: {e}"

# Funzione per estrarre testo da PDF
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Errore durante l'elaborazione del PDF: {e}"

# Funzione per estrarre testo da file Word (.docx)
def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"Errore durante l'elaborazione del file Word: {e}"

# Funzione per estrarre testo da file RTF
def extract_text_from_rtf(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as rtf_file:
            rtf_content = rtf_file.read()
            return rtf_to_text(rtf_content)
    except Exception as e:
        return f"Errore durante l'elaborazione del file RTF: {e}"

# Funzione per estrarre testo da file ODT
def extract_text_from_odt(file_path):
    try:
        odt_file = load(file_path)
        all_text = []
        for paragraph in odt_file.getElementsByType(P):
            all_text.append(paragraph.firstChild.data if paragraph.firstChild else "")
        return "\n".join(all_text)
    except Exception as e:
        return f"Errore durante l'elaborazione del file ODT: {e}"

# Funzione per elaborare i file di una cartella
def process_folder(folder_path, processed_files):
    extracted_data = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file == ".DS_Store" or file in processed_files:
                continue  # Ignora file .DS_Store o già elaborati

            file_path = os.path.join(root, file)
            print(f"Elaborando file: {file_path}")
            
            # Gestione dei file in base all'estensione
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                text = extract_text_from_image(file_path)
            elif file.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif file.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    text = txt_file.read().strip()
            elif file.lower().endswith('.docx'):
                text = extract_text_from_docx(file_path)
            elif file.lower().endswith('.rtf'):
                text = extract_text_from_rtf(file_path)
            elif file.lower().endswith('.odt'):
                text = extract_text_from_odt(file_path)
            elif file.lower().endswith('.ai'):
                text = extract_text_from_ai(file_path)
            elif file.lower().endswith('.doc'):  # Aggiunta gestione file .doc
                text = extract_text_from_doc(file_path)
            else:
                print(f"Formato non supportato: {file}")
                continue
            
            extracted_data.append({"file": file, "content": text})
            processed_files.add(file)  # Aggiungi il file alla lista dei file elaborati
    return extracted_data

# Funzione principale
def main():
    os.makedirs(output_folder, exist_ok=True)  # Crea la cartella di output se non esiste
    
    # Carica i file già elaborati
    processed_files = load_processed_files()
    
    # Elaborazione della prima cartella
    print("Elaborazione della prima cartella...")
    data_1 = process_folder(input_folder_1, processed_files)
    
    # Elaborazione della seconda cartella
    print("Elaborazione della seconda cartella...")
    data_2 = process_folder(input_folder_2, processed_files)
    
    # Salvataggio dei risultati in JSON
    output_file_1 = os.path.join(output_folder, "output_folder_1.json")
    output_file_2 = os.path.join(output_folder, "output_folder_2.json")
    
    with open(output_file_1, 'w', encoding='utf-8') as f1:
        json.dump(data_1, f1, ensure_ascii=False, indent=4)
    with open(output_file_2, 'w', encoding='utf-8') as f2:
        json.dump(data_2, f2, ensure_ascii=False, indent=4)
    
    # Salva i file elaborati
    save_processed_files(processed_files)
    
    print("Elaborazione completata! I risultati sono stati salvati in JSON.")

if __name__ == "__main__":
    main()
