from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import json
import os

# Percorso del file dei dati estratti
data_file = "/Users/simonecarta/Desktop/output_folder/output_alma.json"

def load_context(data_file):
    """
    Carica il contesto combinato dai dati estratti.
    """
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Il file {data_file} non esiste.")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Combina il contenuto di tutti i file in un unico contesto
    context = " ".join([entry['content'] for entry in data if 'content' in entry and entry['content'].strip()])
    return context

def generate_answer(question, context):
    """
    Genera una risposta alla domanda basandosi sul contesto fornito.
    """
    input_text = f"Domanda: {question} Contesto: {context}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=150, num_beams=4, early_stopping=True)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

# Configura il modello
print("Caricamento del modello Flan-T5 XL...")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-xl")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-xl")
print("Modello caricato con successo.")

# Pre-carica il contesto all'avvio del server
preloaded_context = load_context(data_file)

# Inizializza FastAPI
app = FastAPI()

# Definizione del formato di richiesta e risposta
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Endpoint per rispondere a una domanda basata sul contesto pre-caricato.
    """
    question = request.question
    
    if not question:
        raise HTTPException(status_code=400, detail="Domanda non fornita.")

    try:
        # Usa il contesto pre-caricato dai dati estratti
        context = preloaded_context
        
        # Genera la risposta
        answer = generate_answer(question, context)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la generazione della risposta: {str(e)}")
