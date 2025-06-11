import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Modelo de dados de sensor
class DadoSensor(BaseModel):
    temperatura: float
    pressao: float
    timestamp: str  # Formato ISO 8601 esperado

# Lista em memória para armazenar os dados recebidos
dados: List[DadoSensor] = []
volume_total_corrigido = 0.0
arquivo_volume = "volume_total.json"

# Constantes do cálculo
VOLUME = 1
PATM = 1
STD_PATM = 1
STD_TEMP = 20

# Função para salvar o volume total corrigido no arquivo JSON
def salvar_volume_total(valor: float):
    with open(arquivo_volume, "w") as f:
        json.dump({"volume_total_corrigido": valor}, f)

# Função para carregar o volume total corrigido do arquivo JSON
def carregar_volume_total() -> float:
    if os.path.exists(arquivo_volume):
        with open(arquivo_volume, "r") as f:
            data = json.load(f)
            return data.get("volume_total_corrigido", 0.0)
    return 0.0

# Função para calcular o volume corrigido
def calcular_volume_corrigido(pressao_pa: float, temperatura_c: float) -> float:
    pressao_bar = pressao_pa / 100000
    vol_corr = (VOLUME * (pressao_bar + PATM * 1.01325) * (STD_TEMP + 273.15)) / \
               ((temperatura_c + 273.15) * (STD_PATM * 1.01325))
    return vol_corr

# Carregar o volume total corrigido ao iniciar
volume_total_corrigido = carregar_volume_total()

# Rota para exibir o dashboard
@app.get("/", response_class=HTMLResponse)
async def mostrar_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "dados": dados,
        "volume_total_corrigido": volume_total_corrigido
    })

# Rota para receber os dados de sensor no formato JSON
@app.post("/enviar", response_class=JSONResponse)
async def receber_dado(dado: DadoSensor):
    global volume_total_corrigido
    dados.insert(0, dado)  # Adiciona o dado mais recente no topo

    vol_corr = calcular_volume_corrigido(dado.pressao, dado.temperatura)
    volume_total_corrigido += vol_corr

    # Salva o novo volume total corrigido no arquivo JSON
    salvar_volume_total(volume_total_corrigido)

    return {
        "mensagem": "Dado recebido com sucesso",
        "total": len(dados),
        "volume_total_corrigido": volume_total_corrigido
    }

# Rota para fornecer os dados recebidos via API
@app.get("/api/dados", response_class=JSONResponse)
async def get_dados():
    return {
        "dados": dados[-100:],  # Retorna os últimos 100 dados
        "volume_total_corrigido": volume_total_corrigido
    }
