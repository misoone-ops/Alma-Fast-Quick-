import json
import pytesseract

from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# Percorso del file PDF
pdf_path = "/Users/simonecarta/Desktop/code2024/Nutrizione_5a.pdf"

# Converti il PDF in immagini (una per ogni pagina)
images = convert_from_path(pdf_path)

# Prendi la prima pagina come immagine (se hai più pagine, modifica questo)
image = images[0]

# Esegui OCR sull'immagine per estrarre il testo
text = pytesseract.image_to_string(image, lang="ita")
print("Testo estratto:")
print(text)


text = pytesseract.image_to_string(image, lang="ita")

# Percorsi delle cartelle di input e output
input_folder_1 = "/Users/simonecarta/Desktop/input_folder_1"  # Prima cartella di input
input_folder_2 = "/Users/simonecarta/Desktop/input_folder_2"  # Seconda cartella di input
output_folder = "/Users/simonecarta/Desktop/output_folder"    # Cartella di output

# Configurazione di Tesseract OCR
# pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"  # Cambia percorso su Linux/Mac se necessario


# Funzione per estrarre testo da immagini
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Errore durante l'elaborazione dell'immagine: {e}"

# Funzione per estrarre testo da PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Errore durante l'elaborazione del PDF: {e}"

# Funzione per elaborare i file di una cartella
def process_folder(folder_path):
    extracted_data = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Elaborando file: {file_path}")
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                text = extract_text_from_image(file_path)
            elif file.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif file.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    text = txt_file.read().strip()
            else:
                print(f"Formato non supportato: {file}")
                continue
            
            extracted_data.append({"file": file, "content": text})
    return extracted_data

# Elaborazione di entrambe le cartelle
def main():
    os.makedirs(output_folder, exist_ok=True)  # Crea la cartella di output se non esiste
    
    # Elaborazione della prima cartella
    print("Elaborazione della prima cartella...")
    data_1 = process_folder(input_folder_1)
    
    # Elaborazione della seconda cartella
    print("Elaborazione della seconda cartella...")
    data_2 = process_folder(input_folder_2)
    
    # Salvataggio dei risultati in JSON
    output_file_1 = os.path.join(output_folder, "output_folder_1.json")
    output_file_2 = os.path.join(output_folder, "output_folder_2.json")
    
    with open(output_file_1, 'w', encoding='utf-8') as f1:
        json.dump(data_1, f1, ensure_ascii=False, indent=4)
    with open(output_file_2, 'w', encoding='utf-8') as f2:
        json.dump(data_2, f2, ensure_ascii=False, indent=4)
    
    print("Elaborazione completata! I risultati sono stati salvati in JSON.")

if __name__ == "__main__":
    main()
