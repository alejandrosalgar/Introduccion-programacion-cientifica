"""API de ejemplo: expone el CSV de hurtos de Medellín por HTTP.

Lee ``data/processed/hurtos_medellin_hechos.csv`` una sola vez al arrancar
y responde JSON. No es una base de datos: el archivo queda en memoria.

Arranque (desde la raíz del repositorio):

    pip install fastapi uvicorn
    python api_hurtos.py

Luego abra http://127.0.0.1:8000/docs para probar los endpoints.
"""

from pathlib import Path

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, Query

CSV_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "processed"
    / "hurtos_medellin_hechos.csv"
)

COLUMNAS_RESUMEN = ("comuna", "modalidad", "sexo", "franja", "anio", "dia")


def cargar_csv(ruta: Path) -> pd.DataFrame:
    if not ruta.is_file():
        raise FileNotFoundError(f"No está el CSV: {ruta}")
    return pd.read_csv(ruta)


def a_registros(frame: pd.DataFrame) -> list[dict]:
    """NaN de pandas no es JSON válido: se convierte en null."""
    limpio = frame.astype(object).where(pd.notna(frame), None)
    return limpio.to_dict(orient="records")


datos = cargar_csv(CSV_PATH)

app = FastAPI(
    title="Hurtos de Medellín",
    description="Ejemplo mínimo: un CSV leído con pandas y servido con FastAPI.",
)


@app.get("/")
def raiz_api() -> dict:
    return {
        "filas": int(len(datos)),
        "columnas": datos.columns.tolist(),
        "docs": "/docs",
        "ejemplos": [
            "/hechos?limite=5",
            "/hechos?comuna=Aranjuez&anio=2017",
            "/hechos/0",
            "/resumen?columna=comuna",
        ],
    }


@app.get("/hechos")
def listar_hechos(
    comuna: str | None = None,
    modalidad: str | None = None,
    sexo: str | None = None,
    franja: str | None = None,
    nombre_barrio: str | None = None,
    anio: int | None = None,
    limite: int = Query(20, ge=1, le=500),
    desde: int = Query(0, ge=0),
) -> dict:
    """Lista hechos con filtros opcionales y paginación (desde / limite)."""
    vista = datos
    filtros = {
        "comuna": comuna,
        "modalidad": modalidad,
        "sexo": sexo,
        "franja": franja,
        "nombre_barrio": nombre_barrio,
    }
    for columna, valor in filtros.items():
        if valor is None:
            continue
        vista = vista[vista[columna].astype(str).str.casefold() == valor.casefold()]
    if anio is not None:
        vista = vista[vista["anio"] == anio]

    pagina = vista.iloc[desde : desde + limite]
    return {
        "total": int(len(vista)),
        "desde": desde,
        "limite": limite,
        "hechos": a_registros(pagina),
    }


@app.get("/hechos/{indice}")
def un_hecho(indice: int) -> dict:
    """Un registro por su posición en el CSV (la primera fila de datos es 0)."""
    if indice < 0 or indice >= len(datos):
        raise HTTPException(
            status_code=404,
            detail=f"Índice fuera de rango. Hay {len(datos)} filas (0 a {len(datos) - 1}).",
        )
    return a_registros(datos.iloc[[indice]])[0]


@app.get("/resumen")
def resumen(columna: str = "comuna") -> dict:
    """Conteo de filas por una columna categórica."""
    if columna not in COLUMNAS_RESUMEN:
        raise HTTPException(
            status_code=400,
            detail=f"Columna no permitida. Use una de: {', '.join(COLUMNAS_RESUMEN)}.",
        )
    conteo = (
        datos[columna]
        .fillna("(sin dato)")
        .astype(str)
        .value_counts()
        .sort_values(ascending=False)
    )
    return {
        "columna": columna,
        "conteo": {clave: int(valor) for clave, valor in conteo.items()},
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
