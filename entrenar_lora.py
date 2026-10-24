from modelo import cargar, mensajes
from transformers import set_seed
from datasets import Dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer
import json
import time
import platform

set_seed(42)

modelo, tokenizer = cargar()
modelo.config.use_cache = False

print("Modelo cargado")

def preparar (archivo):
    filas = []
    for linea in open(archivo):
        ejemplo = json.loads(linea)
        conversacion = mensajes(ejemplo["incidencia"])
        respuesta = json.dumps(ejemplo["objetivo"], ensure_ascii=False)
        pregunta = tokenizer.apply_chat_template(conversacion, 
                    tokenize=False, 
                    add_generation_prompt=True, 
                    enable_thinking=False)
        completo = tokenizer.apply_chat_template(conversacion +
                [{"role": "assistant", "content": respuesta}],
                tokenize=False,
                add_generation_prompt=False,
                enable_thinking=False)
        ids_completo = tokenizer(completo, add_special_tokens=False)["input_ids"]
        ids_pregunta = tokenizer(pregunta, add_special_tokens=False)["input_ids"]
        n = len(ids_pregunta)
        filas.append({
            "input_ids": ids_completo,
            "attention_mask": [1] * len(ids_completo),
            "labels": [-100] * n + ids_completo[n:],
            "completion_mask": [0] * n + [1] * (len(ids_completo) - n),
        })
    return Dataset.from_list(filas)

datos_train = preparar("datos/train.jsonl")
datos_validacion = preparar("datos/validacion.jsonl")

config_lora = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)

config_entreno = SFTConfig(
    output_dir="modelos/lora-hotel/checkpoints",
    num_train_epochs=2,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=0.0002,
    logging_steps=10,
    save_strategy="no",
    eval_strategy="epoch",
    max_length=768,
    packing=False,
    completion_only_loss=True,
    report_to="none",
    dataset_kwargs={"skip_prepare_dataset": True},
    fp16=False,
    bf16=False,
    seed=42,
    dataloader_pin_memory=False,
    optim="adamw_torch",
)

entrenador = SFTTrainer(
    model=modelo,
    processing_class=tokenizer,
    args=config_entreno,
    train_dataset=datos_train,
    eval_dataset=datos_validacion,
    peft_config=config_lora,
)

inicio = time.perf_counter()
resultado = entrenador.train()
minutos = (time.perf_counter() - inicio) / 60

entrenador.save_model("modelos/lora-hotel")
tokenizer.save_pretrained("modelos/lora-hotel")

print("Entrenamiento terminado en", round(minutos, 1), "minutos")
print("Hardware:", platform.platform(), "|", modelo.device)
print(resultado.metrics)
