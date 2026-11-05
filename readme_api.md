# API de hurtos de Medellín

Este documento explica qué es la API de `api_hurtos.py`, por qué está hecha con **FastAPI**, en qué formato responde, qué códigos HTTP usa y cómo encaja en el proyecto.

El notebook analiza el CSV en el computador de quien lo corre. La API hace otra cosa: deja ese mismo archivo **consultable por HTTP**, para que otro programa (el navegador, otro notebook, un script) pida datos sin abrir el CSV.

---

## 1. Qué es una API y qué sirve aquí

**API** (*Application Programming Interface*) es un contrato: un programa ofrece operaciones con un nombre, unos parámetros y una respuesta predecible. Quien llama no necesita saber cómo está guardado el dato por dentro.

Esta API es una **API HTTP** (también llamada API web o REST en su forma más simple). El contrato es:

| Pieza | En este proyecto |
| --- | --- |
| Quién pide | El navegador, `/docs`, `requests` en Python, otro notebook |
| Cómo pide | Una URL y el método **GET** (solo lectura) |
| Qué recibe | Un objeto **JSON** |
| De dónde sale el dato | `data/processed/hurtos_medellin_hechos.csv` |

No es una base de datos. Al arrancar, pandas lee el CSV **una sola vez** y lo deja en memoria. Cada petición filtra o resume ese `DataFrame`. Si cambia el archivo, hay que reiniciar el proceso para volver a leerlo.

Sirve cuatro cosas:

| Ruta | Para qué |
| --- | --- |
| `GET /` | Orientación: cuántas filas hay, nombres de columnas y ejemplos de URL |
| `GET /hechos` | Lista paginada, con filtros opcionales (`comuna`, `modalidad`, `sexo`, `franja`, `nombre_barrio`, `anio`) |
| `GET /hechos/{indice}` | Un solo hecho por su posición en el CSV (la primera fila de datos es `0`) |
| `GET /resumen` | Conteo de filas por una columna categórica (`comuna` por defecto) |

Ejemplos, con el servidor ya corriendo:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/hechos?limite=5
http://127.0.0.1:8000/hechos?comuna=Aranjuez&anio=2017
http://127.0.0.1:8000/hechos/0
http://127.0.0.1:8000/resumen?columna=comuna
```

La página interactiva para probarlas sin escribir código es [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). FastAPI la genera sola a partir de las funciones del archivo (OpenAPI / Swagger).

---

## 2. Por qué FastAPI

El curso ya usa pandas para la tabla. Faltaba una capa delgada que traduzca “quiero las filas de Aranjuez en 2017” a una petición HTTP y devuelva JSON. **FastAPI** hace esa traducción.

| Motivo | Qué aporta en este archivo |
| --- | --- |
| Poco código | Cada ruta es una función Python con `@app.get(...)`. No hay que armar el servidor a mano. |
| Tipos | `anio: int`, `limite: int`, `columna: str` se validan antes de entrar a la función. Un `anio=abc` no llega a pandas. |
| Límites | `Query(20, ge=1, le=500)` impide pedir 0 filas o medio millón en una sola respuesta. |
| Documentación | `/docs` sale del mismo código. Si cambia un parámetro, la página se actualiza al reiniciar. |
| Errores explícitos | `HTTPException` convierte “índice fuera de rango” o “columna no permitida” en una respuesta HTTP con mensaje, no en un traceback para el cliente. |

**Uvicorn** es el programa que escucha el puerto. FastAPI define las rutas; Uvicorn recibe las conexiones y llama a esas funciones. Por eso el arranque es:

```text
pip install fastapi uvicorn
python api_hurtos.py
```

Eso deja el servicio en `http://127.0.0.1:8000`. `127.0.0.1` es la propia máquina: desde otra computadora de la red no se alcanza, y eso basta para el ejemplo del curso.

Otras opciones (Flask, solo la biblioteca estándar) servirían para lo mismo. FastAPI se eligió porque valida parámetros, limita `limite` y publica `/docs` sin código extra.

---

## 3. Formato: JSON

Toda respuesta exitosa es **JSON** (`Content-Type: application/json`). JSON es texto con objetos `{}`, listas `[]`, números, textos, `true` / `false` y `null`. Cualquier lenguaje lo lee; no hace falta pandas del otro lado.

Pandas guarda huecos como `NaN`. **`NaN` no es JSON válido**, así que `a_registros` los pasa a `null` antes de responder. Un cliente ve ausencia de dato, no un valor numérico raro.

Forma de cada respuesta:

`GET /hechos?limite=1` (recortado):

```json
{
  "total": 12345,
  "desde": 0,
  "limite": 1,
  "hechos": [
    {
      "comuna": "Aranjuez",
      "modalidad": "Atraco",
      "anio": 2017
    }
  ]
}
```

`total` es cuántas filas cumplen el filtro. `desde` y `limite` dicen qué página se devolvió. `hechos` es solo esa página, no el CSV entero.

`GET /hechos/0` devuelve **un objeto**, no una lista.

`GET /resumen?columna=comuna`:

```json
{
  "columna": "comuna",
  "conteo": {
    "La Candelaria": 800,
    "Aranjuez": 600
  }
}
```

Las claves de `conteo` son los valores de la columna; los números son cuántas filas hay en cada uno, de mayor a menor.

Los filtros de texto no distinguen mayúsculas (`Aranjuez` y `aranjuez` coinciden). El año se compara como número.

---

## 4. Códigos HTTP

El **código de estado** dice si la petición salió bien, si el cliente la armó mal o si el recurso no existe. El cuerpo JSON explica el detalle.

| Código | Nombre | Cuándo lo devuelve esta API |
| --- | --- | --- |
| **200** | OK | La ruta existe, los parámetros son válidos y hay respuesta. Es el caso normal de `/`, `/hechos`, `/hechos/{indice}` y `/resumen`. |
| **400** | Bad Request | `GET /resumen` con una columna que no está en la lista permitida (`comuna`, `modalidad`, `sexo`, `franja`, `anio`, `dia`). El cuerpo trae `detail` con las opciones. |
| **404** | Not Found | `GET /hechos/{indice}` con un índice menor que 0 o mayor o igual al número de filas. También si se pide una ruta que no existe (`/otra`). |
| **422** | Unprocessable Entity | FastAPI rechaza el parámetro antes de ejecutar la función: `limite` fuera de 1–500, `desde` negativo, `anio` o `indice` que no son enteros. El cuerpo lista qué campo falló. |

Un error de esta API se ve así:

```json
{
  "detail": "Columna no permitida. Use una de: comuna, modalidad, sexo, franja, anio, dia."
}
```

Si el CSV no está en `data/processed/hurtos_medellin_hechos.csv`, el proceso **no arranca**: `cargar_csv` lanza `FileNotFoundError` al importar el módulo. Eso no es un 404 HTTP; el puerto nunca se abre.

Si nadie ejecuta `python api_hurtos.py`, el navegador no recibe un código HTTP: la conexión falla porque no hay proceso escuchando.

---

## 5. Cómo funciona en este proyecto

```text
hurtos_medellin_hechos.csv
        │
        ▼
  pandas (una lectura al arrancar)
        │
        ▼
  DataFrame en memoria  ──►  FastAPI (rutas GET)
        │                         │
        │                         ▼
        │                    Uvicorn :8000
        │                         │
        └──── filtro / página / conteo ──► JSON
```

1. **Arranque.** `python api_hurtos.py` importa el módulo, lee el CSV y llama a `uvicorn.run` en el puerto 8000.
2. **Petición.** El cliente hace GET. FastAPI valida tipos y rangos. Si fallan, responde 422 y la función no corre.
3. **Filtro.** `/hechos` parte del `DataFrame` completo y se queda con las filas que coinciden. `desde` y `limite` recortan la página (`iloc`). Por defecto, 20 filas desde la posición 0.
4. **Respuesta.** `a_registros` convierte la página a una lista de diccionarios, con `null` donde había `NaN`, y FastAPI la serializa a JSON con código 200.
5. **Resumen.** `/resumen` no devuelve filas: agrupa con `value_counts` sobre una columna de la lista blanca. Una columna fuera de esa lista es 400, para no exponer conteos de campos que el ejemplo no contempla (por ejemplo identificadores).

En el repositorio el análisis sigue viviendo en los notebooks (`notebooks/analisis de hurtos medellin.ipynb` y el de Manrique). La API no entrena modelos ni grafica: solo **publica** la tabla ya procesada para consultarla por URL.

Para pedir lo mismo desde Python, con el servidor encendido en otra terminal:

```python
import requests

r = requests.get(
    "http://127.0.0.1:8000/hechos",
    params={"comuna": "Aranjuez", "anio": 2017, "limite": 5},
    timeout=30,
)
r.raise_for_status()
datos = r.json()
print(datos["total"], len(datos["hechos"]))
```

`raise_for_status()` convierte un 400, 404 o 422 en una excepción. Si la respuesta fue 200, `r.json()` es el diccionario de la sección 3.
