from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import json
import os
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Define o modelo de dados de sensor
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

def salvar_volume_total(valor: float):
    with open(arquivo_volume, "w") as f:
        json.dump({"volume_total_corrigido": valor}, f)

def carregar_volume_total() -> float:
    if os.path.exists(arquivo_volume):
        with open(arquivo_volume, "r") as f:
            data = json.load(f)
            return data.get("volume_total_corrigido", 0.0)
    return 0.0

def calcular_volume_corrigido(pressao_psi: float, temperatura_c: float) -> float:
    pressao_ATM = pressao_psi * 0.068046
    vol_corr = (VOLUME * (pressao_ATM + PATM * 1.01325) * (STD_TEMP + 273.15)) / \
               ((temperatura_c + 273.15) * (STD_PATM * 1.01325))
    return vol_corr

# Ao iniciar, carregar volume total salvo
volume_total_corrigido = carregar_volume_total()

@app.get("/", response_class=HTMLResponse)
async def mostrar_dashboard(request: Request):
    """
    Renderiza o template HTML com a lista de dados no contexto.
    """
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "dados": dados}
    )

@app.post("/enviar", response_class=JSONResponse)
async def receber_dado(dado: DadoSensor):
    global volume_total_corrigido
    dados.append(dado)
    """
    Recebe um JSON com os campos temperatura, pressao e timestamp.
    Exemplo de payload:
    {
      "temperatura": 24.3,
      "pressao": 101325,
      "timestamp": "2025-05-19T14:30:00"
    }
    """
    vol_corr = calcular_volume_corrigido(dado.pressao, dado.temperatura)
    volume_total_corrigido += vol_corr
    # Salva no arquivo JSON após atualizar
    salvar_volume_total(volume_total_corrigido)
    return {"mensagem": "Dado recebido com sucesso", "total": len(dados),"volume_total_corrigido": volume_total_corrigido}
    
@app.get("/api/dados", response_class=JSONResponse)
async def get_dados():
    return {
        "dados": dados[-100:],
        "volume_total_corrigido": volume_total_corrigido
    }