import os
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Percorso del file JSON con i dati estratti
data_file = "/Users/simonecarta/Desktop/output_folder/processed_segments.json"

# Funzione per caricare il contesto
def load_context(data_file):
    """
    Carica il contesto combinato dai dati estratti.
    """
    if not os.path.exists(data_file):
        print("Errore: il file JSON non esiste.")
        raise FileNotFoundError(f"Il file {data_file} non esiste.")
    
    print(f"Caricamento del file JSON da: {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            print(f"File JSON caricato correttamente. Numero di voci: {len(data)}")  # Messaggio di debug
            print(f"Contenuto del contesto completo (limite 1000 caratteri): {preloaded_context[:1000]}")

        except json.JSONDecodeError as e:
            print(f"Errore di decodifica JSON: {e}")
            raise

    # Combina il contenuto dei dati in un unico contesto
    context = " ".join([entry['content'] for entry in data if 'content' in entry and entry['content'].strip()])
    
    if not context.strip():
        print("Attenzione: il contesto generato è vuoto.")
        raise ValueError("Il contesto è vuoto. Controlla i dati estratti.")
    
    print("Contesto combinato generato con successo.")  # Messaggio di debug
    return context

   

# Carica il contesto
print("Caricamento del contesto...")
try:
    preloaded_context = load_context(data_file)
    print(f"Contesto pre-caricato (primi 500 caratteri): {preloaded_context[:500]}")  # Debug pre-contesto
except Exception as e:
    print(f"Errore durante il caricamento del contesto: {e}")
    preloaded_context = None

# Inizializza il modello AI Flan-T5 XL
print("Caricamento del modello Flan-T5 XL...")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-xl")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-xl")
print("Modello caricato con successo.")

# Inizializza FastAPI
app = FastAPI()

# Definizione del formato di richiesta e risposta
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

# Funzione per generare una risposta
def generate_answer(question, context):
    """
    Genera una risposta alla domanda basandosi sul contesto fornito.
    """
    try:
        input_text = f"Domanda: {question} Contesto: {context}"
        inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(**inputs, max_length=150, num_beams=4, early_stopping=True)
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la generazione della risposta: {str(e)}")

# Endpoint API per ricevere domande
@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Endpoint per rispondere alle domande usando il modello AI.
    """
    question = request.question
    if not question.strip():
        raise HTTPException(status_code=400, detail="La domanda non può essere vuota.")
    
    # Usa il contesto pre-caricato
    if not preloaded_context:
        raise HTTPException(status_code=500, detail="Il contesto non è stato caricato correttamente.")
    
    answer = generate_answer(question, preloaded_context)
    return QueryResponse(answer=answer)

# Avvio del server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server_api:app", host="0.0.0.0", port=8000, reload=True)

print(f"Contesto pre-caricato (primi 500 caratteri): {preloaded_context[:500]}")
