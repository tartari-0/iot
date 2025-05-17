from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

dados = []

@app.get("/", response_class=HTMLResponse)
async def mostrar_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "dados": dados})

@app.post("/enviar")
async def receber_dado(valor: str = Form(...)):
    dados.append(valor)
    return RedirectResponse(url="/", status_code=303)