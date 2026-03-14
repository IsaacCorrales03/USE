# USE – Especificación Técnica

## Estructura de archivos

```
eventos/
├── __init__.py
├── votar_pelicula.py
├── preventa_dona.py
models/
├── peliculas.py
├── votos.py
├── preventa.py
├── propuesta.py          ← nuevo
templates/
├── eventos/
│   ├── votar_pelicula.html
│   └── preventa.html
├── propuestas.html       ← nuevo
```

---

## Registro de eventos

`eventos/__init__.py` expone un diccionario estático que mapea cada slug a su handler y template:

```python
EVENTOS = {
    "votar-pelicula": {
        "nombre": "Votación de películas",
        "handler": "eventos.votar_pelicula",
        "template": "eventos/votar_pelicula.html",
    },
    "preventa": {
        "nombre": "Preventa de donas",
        "handler": "eventos.preventa_dona",
        "template": "eventos/preventa.html",
    },
}
```

---

## Feature: Sistema de propuestas

### Modelo – `models/propuesta.py`

| Campo        | Tipo      | Restricciones              |
|--------------|-----------|----------------------------|
| `id`         | Integer   | PK, autoincrement          |
| `descripcion`| Text      | NOT NULL                   |
| `votos`      | Integer   | NOT NULL, default `0`      |

```python
class Propuesta(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    votos       = db.Column(db.Integer, nullable=False, default=0)
```

---

### Rutas

#### `GET /propuestas`

- Recupera todas las propuestas de la base de datos.
- Las ordena por `votos DESC`.
- Renderiza `propuestas.html`.

#### `POST /propuestas/crear`

1. Lee `descripcion` del form.
2. Valida que no esté vacía; si lo está, redirige con error.
3. Crea una nueva `Propuesta` y la guarda.
4. Redirige a `GET /propuestas`.

#### `POST /propuestas/<int:id>/votar`

1. Busca la propuesta por `id` (404 si no existe).
2. Ejecuta las dos verificaciones de abuso (ver sección siguiente).
3. Si pasan, incrementa `votos += 1` y guarda.
4. Actualiza el estado de la cookie.
5. Redirige a `GET /propuestas`.

---

### Prevención de abuso

Un voto se acepta **solo si se cumplen ambas condiciones**:

| Mecanismo | Regla |
|-----------|-------|
| IP rate-limit | La misma IP no puede votar la misma propuesta más de una vez cada **30 segundos** |
| Cookie tracking | El `id` de la propuesta no debe existir ya en la cookie `voted_proposals` |

#### IP Rate Limiting

Usa un diccionario en memoria (o Redis si el proyecto escala) con la clave `(ip, propuesta_id)` y el timestamp del último voto.

```python
# Estructura en memoria
vote_timestamps: dict[tuple[str, int], float] = {}

RATE_LIMIT_SECONDS = 30

def check_ip_rate_limit(ip: str, propuesta_id: int) -> bool:
    """Retorna True si el voto está permitido."""
    key = (ip, propuesta_id)
    last = vote_timestamps.get(key, 0)
    if time.time() - last < RATE_LIMIT_SECONDS:
        return False
    vote_timestamps[key] = time.time()
    return True
```

#### Cookie Vote Tracking

La cookie `voted_proposals` almacena una lista JSON de IDs ya votados.

```python
# Leer
raw = request.cookies.get("voted_proposals", "[]")
voted: list[int] = json.loads(raw)

# Verificar
if propuesta_id in voted:
    # rechazar voto
    ...

# Aceptar y actualizar
voted.append(propuesta_id)
response = make_response(redirect(url_for("propuestas")))
response.set_cookie("voted_proposals", json.dumps(voted), max_age=60*60*24*365)
```

#### Flujo completo del endpoint de voto

```
POST /propuestas/<id>/votar
        │
        ▼
  ¿IP votó en los últimos 30s? ──── Sí ──▶ redirect + flash("Ya votaste recientemente")
        │ No
        ▼
  ¿ID en cookie voted_proposals? ── Sí ──▶ redirect + flash("Ya votaste esta propuesta")
        │ No
        ▼
  propuesta.votos += 1
  db.session.commit()
  añadir ID a cookie
        │
        ▼
  redirect /propuestas
```

---

### Template – `propuestas.html`

- Lista las propuestas ordenadas de mayor a menor votos.
- Cada tarjeta muestra: posición, `descripcion` y contador de `votos`.
- Botón de voto deshabilitado visualmente si el ID ya está en `voted_proposals` (pasar el set desde el backend o leerlo con JS desde la cookie).
- Formulario para crear una nueva propuesta (campo de texto + submit).
- Mensajes flash para errores y confirmaciones.

---

### Sin autenticación

No se requiere login. La protección es de buena fe mediante IP + cookie, suficiente para un contexto escolar donde el objetivo es reducir spam accidental, no fraude deliberado.