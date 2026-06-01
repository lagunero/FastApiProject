AGENTS.md
===========

Breve checklist (qué leer primero)
- Leer `main.py` para entender el arranque y los routers registrados.
- Revisar `app/database.py` + `init.sql` para entender cómo se crea y inicializa la base de datos SQLite.
- Inspeccionar `app/routers/*`, `app/models.py` y `app/schemas.py` para los contratos (DTOs) y conversiones UUID <-> bytes.

Puntos clave para un agente de programación (acción inmediata)

1) Arquitectura general
- Proyecto FastAPI modular: entrada en `main.py` que registra 3 routers: `auth`, `users`, `hello`.
- Base de datos: SQLite en `data/mydatabase.db` creada por `app/database.py::init_db()` usando `init.sql` si el archivo no existe.
- ORM: SQLAlchemy clásico con `declarative_base()` en `app/models.py`. El `User.id` se guarda como LargeBinary (UUID.bytes).

2) Autenticación y autorización
- JWT: utilidades en `app/utils/auth.py` — algoritmo HS256, `SECRET_KEY` en `app/config.py`, expiración por defecto 15 minutos.
- Login: `POST /auth/login` en `app/routers/auth.py` crea token vía `create_access_token`.
- Credenciales demo: `app/utils/password.py` contiene `DEMO_CREDENTIALS` ("user"/"admin" con password "password").
- Patrón: los endpoints protegidos obtienen header `Authorization: Bearer <token>` y llaman `verify_token(token)` que devuelve {"username": ...} o None.

3) Patrones de datos y conversiones específicas del proyecto
- UUIDs: se almacenan como bytes en DB. Conversión usada en `app/routers/users.py`:
  - lectura: `uuid.UUID(bytes=bytes_value)` y retorno como string con `str(uuid_obj)` (función `uuid_to_string`).
  - escritura: UUID generada con `uuid.uuid4().bytes` en la entidad SQLAlchemy.
- DTOs: `app/schemas.py::UserDto` usa alias de Pydantic (camelCase en la API, snake_case en el modelo) y `model_config = ConfigDict(populate_by_name=True)`.
  - Ejemplo: `firstName` es alias de `first_name`.

4) Acceso a DB y patrones de sesión
- `app/database.py` exporta `SessionLocal` (sessionmaker). Los routers usan `db = SessionLocal()` y siempre cierran con `finally: db.close()` (no usan la dependencia FastAPI `Depends(get_db)` aunque `get_db()` existe).
- Ten cuidado: `connect_args={'check_same_thread': False}` y `StaticPool` para SQLite en memoria/archivo; esto puede influir en tests/threads.

5) Documentación y contratos
- `openapi.yaml` en el root contiene la especificación OpenAPI completa (incluye securitySchemes, ejemplos y servidores con `http://localhost:9080`). Úsalo como referencia para formatos y respuestas esperadas.

6) Workflows importantes (comandos)
- Ejecutar servidor localmente (PowerShell):
  - python -m uvicorn main:app --host 0.0.0.0 --port 9080
  - o ejecutar `python main.py` (el script llama a uvicorn en __main__).
- Ejecutar pruebas integradas de ejemplo (requiere servidor corriendo):
  - python test_api.py

7) Variables de entorno y configuración
- `app/config.py` define `SECRET_KEY`, `ALGORITHM` (HS256) y `ACCESS_TOKEN_EXPIRE_MINUTES` (15). Cambiar `SECRET_KEY` en producción.
- DB: hardcode `DATABASE_URL`/path en `app/database.py` a `data/mydatabase.db` — agentes que modifican el esquema deben actualizar `init.sql` también.

8) Contribuir cambios observando convenciones del código
- Mantener camelCase en la API (schemas) y snake_case en modelos/DB.
- Evitar cambiar el tipo de `User.id` a texto sin adaptar las conversiones en `app/routers/users.py` y `init.sql` (usa BLOBs con valores hex en inserts).

9) Puntos de fricción y riesgos conocidos
- Credenciales demo y contraseñas en texto plano (`init.sql` y `app/utils/password.py`) — cambiar con cuidado si se añaden pruebas de seguridad.
- Algunas funciones (p. ej. `get_db`) existen pero no se usan en todos los routers; al refactorizar, prefiera injectar dependencias con `Depends(get_db)` para consistencia.

Archivos clave (rápida referencia)
- `main.py` — arranque y routers
- `app/config.py` — secrets y tiempo de expiración
- `app/database.py`, `init.sql` — creación y carga inicial de BD
- `app/models.py`, `app/schemas.py` — modelo y DTOs (aliasing)
- `app/routers/*` — lógica de endpoints (auth, users, hello)
- `app/utils/*` — auth helpers y credenciales demo
- `openapi.yaml` — contrato completo y ejemplos
- `test_api.py` — suite de integración orientativa

Si necesitas modificar o agregar endpoints: inspecciona `openapi.yaml` para ejemplos de payload/response y mantén la convención camelCase en las respuestas JSON.

Snippets útiles
- Obtener token JWT desde Python (útil para pruebas unitarias/integración):

  ```python
  import requests

  resp = requests.post("http://localhost:9080/auth/login", json={"username":"user","password":"password"})
  token = resp.json().get("token")
  print(token)
  ```

- Usar curl / PowerShell para login y acceder a un endpoint protegido:

  ```powershell
  # Login y guardar token en variable (PowerShell)
  $resp = curl -Method POST -Uri http://localhost:9080/auth/login -Body '{"username":"user","password":"password"}' -Headers @{ 'Content-Type' = 'application/json' }
  $token = ($resp.Content | ConvertFrom-Json).token

  # Llamada a endpoint protegido
  curl -Method GET -Uri http://localhost:9080/api/v1/hello -Headers @{ 'Authorization' = "Bearer $token" }
  ```

- Inspeccionar la base de datos SQLite (ver filas y BLOB UUID hex):

  ```powershell
  sqlite3 data\\mydatabase.db "SELECT hex(id), user_name, email, created_at FROM user LIMIT 5;"
  ```

- Convertir bytes UUID a string en Python (ejemplo para debug fuera del ORM):

  ```python
  import uuid
  b = bytes.fromhex("a55a8e8e9a5c4dbb8caf82c7a67a3037")
  print(str(uuid.UUID(bytes=b)))
  ```

- Ejecutar la suite de integración de ejemplo (requiere servidor corriendo):

  ```powershell
  python test_api.py
  ```

- Crear un token JWT manualmente (útil para pruebas con expiración personalizada):

  ```python
  from app.utils.auth import create_access_token
  token = create_access_token({"sub":"user"}, expires_in_minutes=60)
  print(token)
  ```

+Automatización y comandos rápidos
+
+1) Instalar el paquete en modo editable y exponer scripts (recomendado para desarrolladores):
+
+```powershell
+python -m pip install -e .
+# Luego estarán disponibles los comandos:
+# fp-start    -> inicia el servidor (equivalente a `python main.py`)
+# fp-test-api -> ejecuta la suite de integración (equivalente a `python test_api.py`)
+# fp-init-db  -> fuerza la inicialización de la base de datos desde `init.sql`
+```
+
+2) Alternativa sin instalar: usar los módulos directamente
+
+```powershell
+python main.py           # inicia el servidor (uvicorn)
+python -m test_api       # ejecuta las pruebas de integración
+python -c "from app.database import init_db; init_db()"  # inicializa la BD
+```
+
+Colección Postman
+- Archivo: `postman_collection.json` (raíz del proyecto). Importarlo en Postman y usar la variable `baseUrl` (por defecto http://localhost:9080) y `token` para Authorization.
