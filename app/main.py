from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

APP_VERSION = "1.0.0"

app = FastAPI(title="API de tareas", version=APP_VERSION)

tareas: dict[int, dict] = {}
siguiente_id = 1
inicio = datetime.now(timezone.utc)


class TareaEntrada(BaseModel):
    titulo: str
    completada: bool = False


@app.get("/")
def raiz():
    return {"mensaje": "API funcionando"}


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.get("/version")
def version():
    return {"api": app.title, "version": APP_VERSION}


@app.get("/estado")
def estado():
    return {
        "estado": "activo",
        "version": APP_VERSION,
        "tareas_registradas": len(tareas),
        "en_linea_desde": inicio.isoformat(),
    }


@app.get("/tareas")
def listar_tareas():
    return list(tareas.values())


@app.post("/tareas", status_code=201)
def crear_tarea(entrada: TareaEntrada):
    global siguiente_id
    tarea = {"id": siguiente_id, **entrada.model_dump()}
    tareas[siguiente_id] = tarea
    siguiente_id += 1
    return tarea


@app.get("/tareas/{tarea_id}")
def obtener_tarea(tarea_id: int):
    if tarea_id not in tareas:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tareas[tarea_id]


@app.delete("/tareas/{tarea_id}", status_code=204)
def eliminar_tarea(tarea_id: int):
    if tareas.pop(tarea_id, None) is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
