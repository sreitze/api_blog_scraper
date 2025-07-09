# Instrucciones de uso API + scraper:
# 1. Instalar dependencias mediante pip install -r requirements.txt, y playwright install
# 2. Ejecutar el scraper con fastapi dev main.py
# 3. Hacer peticiones POST a las rutas /scrap-blog-category o /scrap-blog según las instrucciones de cada endpoint.
# 4. Los resultados se guardarán en una hoja de Google Sheets y se enviará un webhook con el enlace a la hoja.
# 5. Asegurarse de tener las credenciales de Google Sheets configuradas correctamente para uso de las API,
#    incluyendo el archivo creds.json en la raíz del proyecto.

from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from scraper_por_categoria import scrap_and_save
from scraper_completo import scrap_and_save_all_categories
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

app = FastAPI()

executor = ThreadPoolExecutor()

class Payload(BaseModel):
    categoria: Optional[str] = None
    webhook: str

# Ejemplo de uso:
# curl -X POST http://localhost:8000/scrap-blog-category \
# -H "Content-Type: application/json" \
# -d '{
#   "categoria": "Xepelin",
#   "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
# }'
@app.post("/scrap-blog-category")
async def scrap_blog(payload: Payload):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, scrap_and_save, payload.categoria, payload.webhook)
    return {"status": "Scraping en progreso"}

# Ejemplo de uso:
# curl -X POST http://localhost:8000/scrap-blog \
# -H "Content-Type: application/json" \
# -d '{
#   "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
# }'
@app.post("/scrap-blog")
async def scrap_blog(payload: Payload):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, scrap_and_save_all_categories, payload.webhook)
    return {"status": "Scraping en progreso"}