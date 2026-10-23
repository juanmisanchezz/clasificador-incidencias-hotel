import os
import torch
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM

load_dotenv()

def cargar(adaptador=None):
    if torch.backends.mps.is_available():
        dispositivo = "mps"
    else:
        dispositivo = "cpu"
    nombre = os.getenv("OPEN_MODEL_ID")
    tokenizer = AutoTokenizer.from_pretrained(nombre)
    modelo = AutoModelForCausalLM.from_pretrained(nombre, dtype=torch.float32).to(dispositivo)
    modelo.eval()

    return modelo, tokenizer

def generar(modelo, tokenizer, mensajes):
    texto = tokenizer.apply_chat_template(mensajes, 
            tokenize=False, 
            add_generation_prompt=True, 
            enable_thinking=False)
    entradas = tokenizer(texto, return_tensors="pt").to(modelo.device)
    with torch.inference_mode():
        salidas = modelo.generate(
                **entradas, do_sample= False, max_new_tokens= 180, pad_token_id=tokenizer.eos_token_id
                )
        nuevos = salidas[0, entradas["input_ids"].shape[1] :]
        respuesta = tokenizer.decode(nuevos, skip_special_tokens=True)
    
    return respuesta