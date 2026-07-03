"""
main.py — Backend FastAPI per Archivio Felix the Cat

Variabili d'ambiente richieste:
    NOCODB_API_TOKEN
    NOCODB_FILM_TABLE_ID
    NOCODB_SCENE_TABLE_ID

Struttura cartelle attesa in /app/static/:
    static/
    ├── fotogrammi/   ← JPG serviti staticamente
    └── xml/          ← XML MODS, PREMIS, Dublin Core
"""

import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Felix the Cat — Archivio Digitale")

NOCODB_BASE   = "https://app.nocodb.com"
API_TOKEN     = os.environ.get("NOCODB_API_TOKEN", "")
FILM_TABLE_ID = os.environ.get("NOCODB_FILM_TABLE_ID", "")
SCENE_TABLE_ID= os.environ.get("NOCODB_SCENE_TABLE_ID", "")

HEADERS = {"xc-auth": API_TOKEN}

# ── Static files ──
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Frontend ──
@app.get("/")
def index():
    return FileResponse("static/index.html")

# ── API Film ──
@app.get("/api/film")
async def get_film():
    url = f"{NOCODB_BASE}/api/v2/tables/{FILM_TABLE_ID}/records?limit=100"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=HEADERS)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    data = r.json()
    return data.get("list", [])

# ── API Scene per film ──
@app.get("/api/scene/{film_id}")
async def get_scene(film_id: str):
    where = f"(identificativo_film,eq,{film_id})"
    url   = f"{NOCODB_BASE}/api/v2/tables/{SCENE_TABLE_ID}/records?where={where}&limit=200&sort=numero_scena"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=HEADERS)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    data = r.json()
    return data.get("list", [])
