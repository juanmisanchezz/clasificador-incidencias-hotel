from modelo import cargar, generar, mensajes
from huggingface_hub import HfApi, snapshot_download

carpeta = "modelos/lora-hotel"

api = HfApi()
usuario = api.whoami()["name"]
repo = usuario + "/clasificador-incidencias-hotel-lora"

ficha = open(carpeta + "/README.md").read().replace("USUARIO", usuario)
open(carpeta + "/README.md", "w").write(ficha)

api.create_repo(repo, exist_ok=True)
api.upload_folder(
    repo_id=repo,
    folder_path=carpeta,
    allow_patterns=["adapter_config.json", "adapter_model.safetensors", "README.md"],
    commit_message="Adaptador LoRA del clasificador de incidencias",
)
print("Subido a https://huggingface.co/" + repo)

descargado = snapshot_download(repo)
modelo, tokenizer = cargar(descargado)
print(generar(modelo, tokenizer, mensajes("La tarjeta de mi habitación no abre la puerta")))
