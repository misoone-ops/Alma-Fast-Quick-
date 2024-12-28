import os
import json

# Percorso del file JSON generato dal processo di estrazione dei dati
data_file = "/Users/simonecarta/Desktop/output_folder/output_alma.json"
output_segments_file = "/Users/simonecarta/Desktop/output_folder/processed_segments.json"

def load_extracted_data(data_file):
    """
    Carica i dati estratti dal file JSON.
    """
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Il file {data_file} non esiste.")

    with open(data_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            print(f"File JSON caricato correttamente. Numero di voci: {len(data)}")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Errore nel leggere il file JSON: {e}")

def segment_content(data, max_segment_length=500):
    """
    Suddivide il contenuto in segmenti più piccoli.
    - max_segment_length: Massima lunghezza in caratteri per segmento.
    """
    segments = []
    for entry in data:
        if 'content' in entry and entry['content'].strip():
            content = entry['content']
            while len(content) > max_segment_length:
                # Trova il punto di suddivisione più vicino (es. punto o spazio)
                split_point = content.rfind('.', 0, max_segment_length)
                if split_point == -1:
                    split_point = content.rfind(' ', 0, max_segment_length)
                if split_point == -1:
                    split_point = max_segment_length

                # Aggiungi il segmento e riduci il contenuto rimanente
                segments.append(content[:split_point + 1].strip())
                content = content[split_point + 1:].strip()
            if content:
                segments.append(content)

    print(f"Segmenti generati: {len(segments)}")
    return segments

def save_segments(segments, output_file):
    """
    Salva i segmenti generati in un file JSON.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(segments, f, ensure_ascii=False, indent=4)
    print(f"Segmenti salvati in: {output_file}")

def main():
    """
    Esegui il processo di segmentazione.
    """
    print("Caricamento dei dati estratti...")
    data = load_extracted_data(data_file)

    print("Generazione dei segmenti...")
    segments = segment_content(data, max_segment_length=500)

    print("Salvataggio dei segmenti...")
    save_segments(segments, output_segments_file)

    print("Processo di segmentazione completato!")

if __name__ == "__main__":
    main()

