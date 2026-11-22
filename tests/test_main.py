import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def limpiar_tareas():
    main.tareas.clear()
    main.siguiente_id = 1
    yield


def test_raiz():
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"mensaje": "API funcionando"}


def test_salud():
    respuesta = client.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_listar_vacio():
    assert client.get("/tareas").json() == []


def test_crear_tarea():
    respuesta = client.post("/tareas", json={"titulo": "Estudiar Docker"})
    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "id": 1,
        "titulo": "Estudiar Docker",
        "completada": False,
        "prioridad": "media",
    }


def test_obtener_tarea():
    client.post("/tareas", json={"titulo": "Subir a GitHub"})
    respuesta = client.get("/tareas/1")
    assert respuesta.status_code == 200
    assert respuesta.json()["titulo"] == "Subir a GitHub"


def test_obtener_tarea_inexistente():
    assert client.get("/tareas/99").status_code == 404


def test_crear_tarea_invalida():
    assert client.post("/tareas", json={}).status_code == 422


def test_eliminar_tarea():
    client.post("/tareas", json={"titulo": "Borrar"})
    assert client.delete("/tareas/1").status_code == 204
    assert client.get("/tareas/1").status_code == 404


def test_version():
    respuesta = client.get("/version")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"api": "API de tareas", "version": main.APP_VERSION}


def test_estado():
    client.post("/tareas", json={"titulo": "Contar"})
    datos = client.get("/estado").json()
    assert datos["estado"] == "activo"
    assert datos["version"] == main.APP_VERSION
    assert datos["tareas_registradas"] == 1


def test_crear_tarea_con_prioridad():
    respuesta = client.post("/tareas", json={"titulo": "Entregar", "prioridad": "alta"})
    assert respuesta.status_code == 201
    assert respuesta.json()["prioridad"] == "alta"


def test_prioridad_invalida():
    assert client.post("/tareas", json={"titulo": "X", "prioridad": "urgente"}).status_code == 422
