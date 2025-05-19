from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Define o modelo de dados de sensor
class DadoSensor(BaseModel):
    temperatura: float
    pressao: float
    timestamp: str  # Formato ISO 8601 esperado

# Lista em memória para armazenar os dados recebidos
dados: List[DadoSensor] = []

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
    """
    Recebe um JSON com os campos temperatura, pressao e timestamp.
    Exemplo de payload:
    {
      "temperatura": 24.3,
      "pressao": 101325,
      "timestamp": "2025-05-19T14:30:00"
    }
    """
    dados.append(dado)
    return {"mensagem": "Dado recebido com sucesso", "total": len(dados)}
