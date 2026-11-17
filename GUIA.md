# Guía: imagen Docker en GitHub (GHCR) con GitHub Actions

## Estructura

```
app/main.py                 API FastAPI (tareas)
tests/test_main.py          pruebas unitarias (8)
requirements.txt            dependencias de la IMAGEN (fastapi, uvicorn)
requirements-dev.txt        -r requirements.txt + pytest + httpx
Dockerfile / .dockerignore  construcción de la imagen
.gitignore
.github/workflows/ci.yml    job "pruebas" + job "imagen"
```

## PREPARACIÓN

1. Instalar dependencias y validar pruebas:
   ```
   python -m pip install -r requirements-dev.txt
   python -m pytest -v
   ```
   (`requirements-dev.txt` ya incluye `requirements.txt`; en la versión inicial,
   antes de separarlos, era `python -m pip install -r requirements.txt`.)

2. Crear el repositorio Git y publicarlo:
   ```
   git init
   git config --local user.name "USUARIO"
   git config --local user.email "CORREO_DE_GITHUB"
   git add .
   git commit -m "API con pruebas y workflow"
   git branch -M main
   git remote add origin https://github.com/USUARIO/REPOSITORIO.git
   git push -u origin main
   ```

## IMAGEN

3. En GitHub → pestaña **Actions**: verificar que `pruebas` e `imagen` terminen en verde.
   La imagen aparece en el perfil → **Packages**. Si el repo es privado, el paquete
   también lo es: hazlo público (Package settings → Change visibility) o haz
   `docker login ghcr.io` con un token con permiso `read:packages`.

4. Descargar y ejecutar la imagen (nombre en minúsculas):
   ```
   docker pull ghcr.io/usuario/repositorio:latest
   docker run -d --name api-tareas -p 8000:8000 ghcr.io/usuario/repositorio:latest
   ```
   Formato: `docker run -d --name [NOMBRE] -p [PUERTO PC]:[PUERTO IMAGEN] [ENLACE DE IMAGEN]`

5. Validar la API:
   - http://localhost:8000/salud → `{"estado":"ok"}`
   - http://localhost:8000/docs → Swagger para probar `POST /tareas`, `GET /tareas`, etc.

## Errores corregidos en los steps del .yml

| Error en el original | Corrección |
|---|---|
| Steps desordenados (pruebas antes de instalar, instalar antes de configurar Python) | Orden: checkout → setup-python → instalar → pytest |
| Todo en un solo job | Dos jobs: `pruebas` e `imagen` (`needs: pruebas`, sólo construye si pasan) |
| Indentación inconsistente (`run:`, `uses:` sin alinear con `- name:`) | Cada clave del step al mismo nivel que `name` |
| `docker/login-action` sin `with:` | `registry`, `username`, `password` van dentro de `with:` |
| `uses:docker/build-push-action@v6` sin espacio | `uses: docker/build-push-action@v6` |
| `IMAGE_NAME` se calculaba pero no se usaba | `echo "name=ghcr.io/${IMAGE_NAME}"` |
| Se instalaba `requirements.txt` (sin pytest) | En el job de pruebas se instala `requirements-dev.txt` |
| Faltaba permiso para publicar en GHCR | `permissions: packages: write` en el job `imagen` |
| Faltaba `Dockerfile` | Agregado (python:3.12-slim, uvicorn en puerto 8000) |
