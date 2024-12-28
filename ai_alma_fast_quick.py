import os
import json
from transformers import pipeline
import threading
import time
from multiprocessing import Pool
import itertools

# Percorso del nuovo file JSON generato dal processo di segmentazione dei dati
data_file = "/Users/simonecarta/Desktop/output_folder/processed_segments.json"

# Verifica che il file esista
if not os.path.exists(data_file):
    raise FileNotFoundError(f"Il file {data_file} non esiste. Assicurati che l'elaborazione sia stata completata correttamente.")

# Carica i segmenti dal file JSON
def load_segments(data_file):
    with open(data_file, 'r', encoding='utf-8') as f:
        try:
            segments = json.load(f)
            return segments
        except json.JSONDecodeError as e:
            raise ValueError(f"Errore nel leggere il file JSON: {e}")

segments = load_segments(data_file)

if not segments:
    raise ValueError("Il file dei segmenti è vuoto. Controlla il processo di segmentazione e ripeti l'elaborazione.")

# Inizializza il modello di QA (Question Answering) usando Hugging Face
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", device=0)

# Cache delle risposte
cache = {}

# Funzione per mostrare un messaggio di attesa
stop_loading = threading.Event()
def loading_message():
    print("Elaborazione in corso...", end="", flush=True)
    while not stop_loading.is_set():
        time.sleep(0.5)
        print(".", end="", flush=True)
    print("\n")

# Funzione per rispondere a una domanda usando i segmenti (con cache)
def get_answer(question, segments):
    if question in cache:
        return cache[question]

    best_answer = None
    best_score = -float('inf')

    for segment in segments:
        try:
            result = qa_pipeline(question=question, context=segment)
            if result['score'] > best_score:
                best_score = result['score']
                best_answer = result['answer']
        except Exception as e:
            print(f"Errore durante l'elaborazione del segmento: {e}")

    cache[question] = best_answer if best_answer else "Non è stato possibile generare una risposta."
    return cache[question]

# Modalità interattiva per porre domande
def interactive_mode():
    print("--- Modalità interattiva: inserisci domande manualmente (digita 'exit' per uscire) ---")
    while True:
        question = input("Inserisci una domanda: ")
        if question.lower() == 'exit':
            print("Uscita dalla modalità interattiva.")
            break

        # Avvia il messaggio di attesa in un thread separato
        global stop_loading
        stop_loading.clear()
        loading_thread = threading.Thread(target=loading_message)
        loading_thread.start()

        # Ottieni la risposta
        answer = get_answer(question, segments)

        # Ferma il messaggio di attesa
        stop_loading.set()
        loading_thread.join()

        print(f"\nRisposta: {answer}\n")

# Avvio della modalità interattiva
if __name__ == "__main__":
    interactive_mode()
