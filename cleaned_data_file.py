import os
import json
import re

# Percorso del file JSON con i dati estratti
data_file = "/Users/simonecarta/Desktop/output_folder/processed_segments.json"

# Percorso del file JSON per salvare i dati puliti
cleaned_data_file = "/Users/simonecarta/Desktop/output_folder/cleaned_output_alma.json"

def load_data(file_path):
    """
    Carica i dati dal file JSON.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Il file {file_path} non esiste.")

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            print(f"Dati caricati correttamente. Numero di voci: {len(data)}")
            return data
        except json.JSONDecodeError as e:
            print(f"Errore nel leggere il file JSON: {e}")
            raise

def clean_text(text):
    """
    Pulisce il testo rimuovendo rumore, caratteri speciali e uniformando la formattazione.
    """
    # Rimuovi caratteri non necessari
    text = re.sub(r'[\n\t]', ' ', text)  # Rimuovi newline e tabulazioni
    text = re.sub(r'\s+', ' ', text)  # Riduci spazi multipli a uno
    text = re.sub(r'[•°"“”‘’´`]', '', text)  # Rimuovi simboli non utili
    text = re.sub(r'[^\w\s,.!?;:%-]', '', text)  # Rimuovi caratteri speciali

    # Uniforma spaziatura e punteggiatura
    text = re.sub(r'\s,', ',', text)
    text = re.sub(r'\s\.', '.', text)
    text = re.sub(r'\s! ', '! ', text)
    text = re.sub(r'\s\?', '? ', text)
    text = re.sub(r'\s;', '; ', text)

    # Rimuovi testo ripetitivo o placeholder (es. segnaposto non utili)
    text = re.sub(r'(\b[A-Za-z]+\b) \1', r'\1', text)  # Rimuovi parole ripetute consecutive

    # Rimuovi eventuali spazi finali
    return text.strip()

def clean_data(data):
    """
    Applica la pulizia del testo ai dati estratti.
    """
    cleaned_data = []
    for entry in data:
        if 'content' in entry and entry['content'].strip():
            cleaned_entry = {
                "file": entry.get("file", ""),
                "content": clean_text(entry['content'])
            }
            cleaned_data.append(cleaned_entry)
    return cleaned_data

def save_cleaned_data(file_path, cleaned_data):
    """
    Salva i dati puliti in un file JSON.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
    print(f"Dati puliti salvati con successo in: {file_path}")

# Pipeline principale
if __name__ == "__main__":
    try:
        # Carica i dati estratti
        extracted_data = load_data(data_file)

        # Pulisci i dati
        cleaned_data = clean_data(extracted_data)

        # Salva i dati puliti
        save_cleaned_data(cleaned_data_file, cleaned_data)

    except Exception as e:
        print(f"Errore durante il processo di pulizia dei dati: {e}")
