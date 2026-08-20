# Introducción a la Programación Científica

Repositorio del curso — periodo **2026-2**.

Este documento cubre la **Evaluación 1** y los temas técnicos de lectura, parseo, depuración e imputación de datos en Python. El objetivo no es “hacer que el archivo corra”, sino dejar el dataset en un estado **reproducible, justificado y científicamente defendible**.

---

## Evaluación 1 — Planeación e implementación inicial

| Campo | Detalle |
| --- | --- |
| Evaluación | 1 |
| Fecha de entrega | 26 de agosto de 2026 |
| Peso | 20 % |
| Objetivo | Definir el problema, conformar el equipo e iniciar el desarrollo del proyecto. |

**Entregables principales**

- Repositorio en GitHub
- Git Flow
- README
- Definición del problema, objetivos y alcance
- Dataset seleccionado
- Estructura del proyecto
- Lectura inicial de datos
- Primer prototipo funcional

La evaluación se rige por el **capítulo XII del Reglamento Estudiantil (RE)**.

---

## 1. Flujo de trabajo con datos

Antes de modelar o graficar, el dato crudo debe pasar por cuatro etapas. Confundirlas es una de las causas más frecuentes de error en un prototipo:

```text
Leer  →  Parsear  →  Depurar  →  Imputar / eliminar
 (I/O)    (tipo)     (calidad)     (faltantes)
```

| Etapa | Pregunta que responde | Ejemplo |
| --- | --- | --- |
| Lectura | ¿Cómo entra el archivo a memoria? | `read_csv`, encoding, separador |
| Parseo | ¿Qué *significa* cada valor? | `"26/08/2026"` → `datetime` |
| Depuración | ¿El valor es válido en el dominio? | edad = `-3`, temperatura = `999` |
| Imputación / eliminación | ¿Qué hacer con lo que falta o es irrecuperable? | media, muestreo, borrar fila |

Regla de oro: **no se imputa ni se borra nada que no se haya parseado y auditado primero**. Un `NaN` que nació de un parseo mal hecho no es un faltante real.

---

## 2. Lectura de datos en Python

La librería estándar del curso para datos tabulares es **pandas**. NumPy entra después, cuando ya hay arreglos numéricos limpios.

### 2.1 Inspección antes de cargar todo

En archivos grandes, primero se mira una muestra y los metadatos:

```python
import pandas as pd

# Vista rápida: 5 filas, sin cargar el archivo completo
muestra = pd.read_csv("datos.csv", nrows=5)
print(muestra.columns.tolist())
print(muestra.dtypes)
```

Preguntas que hay que responder en esta inspección:

- ¿Cuál es el **separador**? (`,`, `;`, `\t`)
- ¿Cuál es el **encoding**? (`utf-8`, `latin-1`, `cp1252` en archivos de Windows/Excel)
- ¿El decimal es `.` o `,`?
- ¿Hay filas de título, notas o encabezados repetidos antes de los datos?
- ¿Cómo están representados los faltantes? (`NA`, `N/A`, `-`, `999`, celdas vacías)

### 2.2 Lectura controlada

```python
df = pd.read_csv(
    "datos.csv",
    sep=",",
    encoding="utf-8",
    decimal=".",
    na_values=["", "NA", "N/A", "-", "null", "999"],
    skipinitialspace=True,
)

print(df.shape)
print(df.info())
print(df.head())
print(df.describe(include="all"))
```

Otras lecturas frecuentes:

```python
df_excel = pd.read_excel("datos.xlsx", sheet_name="Hoja1")
df_json = pd.read_json("datos.json")
df_tsv = pd.read_csv("datos.tsv", sep="\t")
```

### 2.3 Errores típicos al leer

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| `UnicodeDecodeError` | Encoding incorrecto | Probar `utf-8`, `latin-1`, `cp1252` |
| Una sola columna gigante | El separador no es `,` | Usar `sep=";"` o `sep="\t"` |
| Números como texto | Decimal con coma, o miles con punto | `decimal=","`, `thousands="."` |
| Fechas como `object` | No se parsearon | Ver sección 3 |
| Filas “corridas” | Comillas o campos con el mismo separador | `quotechar='"'`, revisar el CSV a mano |

La lectura inicial del prototipo debe dejar **constancia** de: ruta del archivo, encoding, separador, número de filas/columnas y porcentaje de faltantes por variable.

---

## 3. Parseo de datos

Parsear es **interpretar** un texto crudo como un tipo con semántica: número, fecha, categoría, booleano. Un dato mal parseado contamina todo lo que sigue (estadísticos, gráficos, modelos).

### 3.1 Números

```python
df["ingreso"] = pd.to_numeric(df["ingreso"], errors="coerce")
```

`errors="coerce"` convierte lo ilegible en `NaN` en lugar de lanzar excepción. Eso es deseable, pero obliga a **contar cuántos valores se perdieron** en el parseo:

```python
perdidos_en_parseo = df["ingreso"].isna().sum()
```

Si el archivo trae formato europeo (`1.234,56`):

```python
df["ingreso"] = (
    df["ingreso"]
    .astype(str)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
)
df["ingreso"] = pd.to_numeric(df["ingreso"], errors="coerce")
```

### 3.2 Fechas

```python
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
```

En Colombia y en la mayoría de fuentes locales el día va primero. Si se omite `dayfirst=True`, `08/01/2026` puede leerse como 1 de agosto en lugar del 8 de enero.

También conviene extraer componentes solo **después** del parseo:

```python
df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month
```

### 3.3 Texto y categorías

```python
df["sexo"] = (
    df["sexo"]
    .astype(str)
    .str.strip()
    .str.lower()
    .replace({
        "m": "masculino",
        "f": "femenino",
        "masc": "masculino",
        "fem": "femenino",
        "nan": pd.NA,
    })
)
```

Sin esta normalización, `M`, `m`, `Masculino` y `" Masculino "` se cuentan como cuatro clases distintas.

### 3.4 Booleanos y códigos

Valores como `Si/No`, `1/0`, `True/False` deben unificarse **antes** de tratarlos como numéricos. Un `1` y un `"1"` no son el mismo tipo; pandas los mezcla en `object` y rompe agregaciones.

```python
mapa = {"si": True, "sí": True, "no": False, "1": True, "0": False}
df["activo"] = df["activo"].astype(str).str.strip().str.lower().map(mapa)
```

### 3.5 Criterio de parseo

Parsear no es “arreglar el dato”. Es **hacer explícito el contrato del tipo**. Si un valor no entra en ese contrato, se vuelve faltante y pasa a la etapa de depuración. No se inventa un número para que el `dtype` quede bonito.

---

## 4. Depuración de datos

Depurar es contrastar los valores parseados contra el **dominio del problema**: rangos posibles, unicidad, consistencia entre columnas y duplicados.

### 4.1 Auditoría mínima (obligatoria en el prototipo)

```python
reporte = pd.DataFrame({
    "dtype": df.dtypes.astype(str),
    "n_faltantes": df.isna().sum(),
    "pct_faltantes": df.isna().mean() * 100,
    "n_unicos": df.nunique(dropna=False),
})
print(reporte)
print("filas duplicadas:", df.duplicated().sum())
```

Complementos útiles:

```python
df["ciudad"].value_counts(dropna=False)
df.describe()
df.loc[df["edad"] < 0]
```

### 4.2 Duplicados

Hay dos tipos, y no se tratan igual:

1. **Fila idéntica completa.** Suele ser un error de captura o de concatenación. Se puede eliminar *después* de verificar que no sea un evento real repetido.
2. **Misma clave, distintos valores.** Ejemplo: dos filas con el mismo `id_paciente` y edades distintas. Eso no se borra a ciegas: hay conflicto. Se documenta y se decide con regla (última fecha, fuente más confiable, o se deja como faltante).

```python
df = df.drop_duplicates(keep="first")  # solo para copias exactas
```

### 4.3 Valores imposibles vs atípicos

| Tipo | Ejemplo | Tratamiento |
| --- | --- | --- |
| Imposible | edad = `-5`, porcentaje = `140` | No es un outlier: es un error. Se corrige si hay fuente; si no, se vuelve `NaN`. |
| Atípico verosímil | ingreso muy alto en una cola pesada | **No se borra** solo porque está lejos de la media. |
| Código centinela | `999`, `-99`, `9999` usados como “sin dato” | Recodificar a `NaN` en la lectura (`na_values`). |

Un diagrama de caja o la regla del IQR sirven para **detectar** candidatos, no para **borrarlos automáticamente**.

```python
q1, q3 = df["ingreso"].quantile([0.25, 0.75])
iqr = q3 - q1
atipicos = df[(df["ingreso"] < q1 - 1.5 * iqr) | (df["ingreso"] > q3 + 1.5 * iqr)]
```

La pregunta correcta no es “¿está lejos de la media?” sino “¿puede existir en el fenómeno que estamos midiendo?”.

### 4.4 Consistencia entre variables

Ejemplos de reglas de dominio:

- `fecha_muerte` no puede ser anterior a `fecha_nacimiento`.
- `edad` debe coincidir, con tolerancia, con el cálculo a partir de la fecha.
- Un porcentaje debe estar en `[0, 100]` si está definido así.
- Una variable derivada no puede contradecir sus componentes.

Cuando una regla se rompe, se marca la fila como inconsistente. No se “promedia” el conflicto.

---

## 5. Datos faltantes: imputar o eliminar

Un faltante no es un cero. Tratar `NaN` como `0` cambia la media, la varianza y, en muchos problemas, el sentido físico de la variable.

### 5.1 Mecanismos de ausencia

Antes de decidir, hay que preguntar **por qué falta**:

| Mecanismo | Idea | Riesgo de borrar filas |
| --- | --- | --- |
| **MCAR** | Falta al azar, sin relación con ningún dato | El sesgo es bajo, pero se pierde potencia |
| **MAR** | Falta en función de otras variables observadas (p. ej. más huecos en un grupo de edad) | Borrar sesga si ese grupo queda subrepresentado |
| **MNAR** | Falta por el propio valor (p. ej. no reportan ingresos altos) | Borrar o imputar mal **distorsiona el fenómeno** |

En la práctica casi nunca se demuestra MCAR. Por eso la eliminación masiva de filas es la última opción, no la primera.

### 5.2 Cuándo sí se pueden eliminar datos

Eliminar es válido cuando el dato **no aporta información recuperable** y la regla queda escrita en el README del proyecto:

- Filas **completamente vacías**.
- Duplicados exactos ya verificados.
- Columnas constantes o con ~100 % de faltantes (no hay señal).
- Registros de prueba (`test`, `xxx`, IDs dummy).
- Valores imposibles **sin forma de reconstruirlos**, convertidos antes a `NaN` y, si la fila queda sin ninguna variable útil, entonces sí se descarta.
- Variables irrelevantes al alcance del problema (no se “limpian”: se declaran fuera de alcance).

Proporción orientativa, no dogma: si una **columna** supera ~30–40 % de faltantes, suele ser mejor no usarla en el prototipo (o usarla solo como indicador `faltante / no faltante`) que rellenarla. Si una **fila** tiene la mayoría de campos vacíos, se puede descartar. El umbral debe justificarse con el tamaño muestral y el dominio.

```python
# Filas sin ningún valor
df = df.dropna(how="all")

# Columna casi vacía: se documenta y se deja fuera del análisis
umbral = 0.40
columnas_utiles = df.columns[df.isna().mean() < umbral]
```

### 5.3 Cuándo no se deben eliminar datos

No se borra una observación solo porque estorba al gráfico o al modelo.

- **Atípicos reales.** Un pico de temperatura, un ingreso extremo o un evento raro pueden ser el resultado científico.
- **Faltante en una sola columna.** Tirar la fila completa (eliminación listwise) desperdicia el resto de variables y sesga si el hueco no es MCAR.
- **Muestras pequeñas.** Cada fila cuenta; se imputa o se analiza por separado.
- **Ausencia informativa (MNAR).** Que falte el dato *es* información. A veces se crea una dummy `valor_faltante` y se imputa el resto.
- **No se entiende el origen del hueco.** Si no hay diagnóstico, no hay justificación para borrar.
- **Outliers producidos por un error de unidad** (`temperatura` en °F mezclada con °C). Eso se **corrige**, no se elimina.

Criterio práctico: si al quitar las filas cambia de signo una conclusión, esas filas no eran “ruido”; eran parte del fenómeno o de un sesgo que hay que reportar.

---

## 6. Imputación

Imputar es **asignar un valor plausible** a un faltante. Toda imputación inventa información. Por eso se reporta cuántos valores se imputaron, en qué variables y con qué método.

### 6.1 Imputación por media (o mediana / moda)

Se reemplaza cada `NaN` por un estadístico de los valores observados:

```python
media = df["edad"].mean()
df["edad_media"] = df["edad"].fillna(media)

mediana = df["edad"].median()
df["edad_mediana"] = df["edad"].fillna(mediana)

moda = df["ciudad"].mode(dropna=True)
df["ciudad_moda"] = df["ciudad"].fillna(moda.iloc[0] if not moda.empty else pd.NA)
```

La **mediana** es preferible a la media si hay asimetría o atípicos. La **moda** se usa en categóricas.

Ventajas: simple, rápida, conserva el tamaño muestral y, en el caso de la media, deja el promedio global casi igual.

### 6.2 Por qué la media deforma la distribución

Imputar con un único número (la media) tiene tres efectos mecánicos:

1. **Reduce la varianza.** Todos los imputados son idénticos, así que la nube de puntos se “aplasta”.
2. **Crea un pico artificial** en el histograma, justo en la media. La forma original (asimetría, bimodalidad, colas) se pierde.
3. **Debilita correlaciones.** Como los imputados no covarían con otras variables, las relaciones se atenúan.

Es aceptable como prototipo exploratorio, o cuando el porcentaje de faltantes es muy bajo (del orden de 1–5 %) y la variable es aproximadamente simétrica. No es aceptable como resultado final si se van a estimar intervalos, colas o asociaciones.

La mediana tiene el mismo problema de forma: también clava muchos puntos en un solo valor.

### 6.3 Imputación que respeta la distribución

La idea es **no pegar todos los huecos en un mismo punto**, sino rellenarlos con valores que podrían haber salido del mismo proceso que los datos observados.

**A. Muestreo de la distribución empírica (hot-deck aleatorio)**

Se toman, con reemplazo, valores ya observados:

```python
import numpy as np

obs = df["edad"].dropna()
n_faltan = df["edad"].isna().sum()

rng = np.random.default_rng(42)
imputados = rng.choice(obs.to_numpy(), size=n_faltan, replace=True)

df.loc[df["edad"].isna(), "edad"] = imputados
```

Efecto: se conservan mejor la forma, la varianza y las colas. No se asume normalidad. El azar debe quedar fijado con una semilla para que el prototipo sea reproducible.

**B. Media (o predicción) más ruido**

Si se quiere conservar el centro *y* la dispersión:

```python
obs = df["edad"].dropna()
mu, sigma = obs.mean(), obs.std()
n_faltan = df["edad"].isna().sum()

df.loc[df["edad"].isna(), "edad"] = rng.normal(mu, sigma, size=n_faltan)
```

Esto respeta media y varianza **solo si** la variable es más o menos normal. En datos sesgados (ingresos, concentraciones) el muestreo empírico (A) es más fiel que el ruido gaussiano.

**C. Imputación condicional**

Se predice el faltante a partir de otras columnas (regresión, k-NN, MICE) y, en la versión que respeta la distribución, se agrega el residual:

```text
valor_imputado = predicción + ruido_con_varianza_residual
```

Sin el ruido, k-NN o una regresión también **comprimen** la varianza, igual que la media.

| Método | ¿Preserva el centro? | ¿Preserva la forma / varianza? | Uso razonable |
| --- | --- | --- | --- |
| Media | Sí | No: pico en la media, menos varianza | Exploración, % faltante muy bajo |
| Mediana | Centro robusto | No: pico en la mediana | Datos asimétricos, mismo caveat |
| Moda | Clase más frecuente | No: infla esa clase | Categóricas con pocos huecos |
| Muestreo empírico | Aproximadamente | Sí, de forma razonable | Prototipo que no debe deformar histogramas |
| Predicción + ruido / MICE | Sí, condicional | Mejor que la media | Cuando hay variables auxiliares |

### 6.4 Imputación agrupada

Si el faltante depende de un grupo (ciudad, sexo, año), la media **global** mezcla poblaciones. Se imputa **dentro del grupo**:

```python
df["edad"] = df.groupby("ciudad")["edad"].transform(
    lambda s: s.fillna(s.median())
)
```

Aun así, si el objetivo es no deformar la distribución *dentro* del grupo, el muestreo empírico también puede hacerse por grupo.

### 6.5 Lo que la imputación no debe hacer

- Imputar **antes** de parsear y de recodificar centinelas (`999` → media es un error grave).
- Imputar la variable respuesta si el objetivo es predecirla (filtración de información).
- Presentar datos imputados como si fueran mediciones.
- Encadenar media global + borrado de atípicos + nueva media: cada paso finge más precisión.

---

## 7. Orden recomendado para el prototipo

1. Leer con encoding, separador y `na_values` explícitos.
2. Parsear tipos (números, fechas, categorías).
3. Contar cuántos `NaN` nacieron en el parseo versus los que ya venían en el archivo.
4. Depurar duplicados, centinelas e imposibles.
5. Decidir, variable por variable: dejar el faltante, imputar o eliminar.
6. Si se imputa, comparar histograma y desviación estándar **antes vs después**.
7. Dejar el código y estas decisiones en el repositorio ( notebook).

Comparación mínima que debe verse en el primer prototipo:

```python
antes = df["edad"].describe()
# ... imputación ...
despues = df["edad"].describe()
print(pd.concat([antes, despues], axis=1, keys=["antes", "despues"]))
```

Si la desviación estándar cae de forma brusca, la imputación por media (o cualquier método determinista) está aplastando la distribución.

---

## 8. Estructura sugerida del proyecto

```text
.
├── README.md
├── data/
│   ├── raw/              # archivo original, no se edita a mano
│   └── processed/        # salidas de parseo / depuración
├── notebooks/            # exploración y prototipo
├── src/                  # funciones reutilizables (lectura, limpieza)
└── requirements.txt
```

Git Flow mínimo para esta entrega: rama `main` estable, rama `develop`, y ramas `feature/...` por avance (lectura, limpieza, prototipo). Los datos crudos grandes no se suben si el proveedor lo prohíbe; en ese caso el README debe indicar la fuente y el script de descarga.

---

## 9. Criterios de la lectura inicial y del prototipo

El prototipo de la Evaluación 1 no exige un modelo final. Sí exige evidencia de que el equipo:

- eligió un dataset y definió problema, objetivos y alcance;
- puede **leer** el archivo de forma reproducible;
- **parsea** tipos en lugar de dejar todo como texto;
- **depura** con reglas de dominio, no con borrado automático de atípicos;
- justifica **qué se elimina y qué no**;
- si imputa, distingue **relleno por media** de una imputación que **no destruye la distribución**;
- deja un primer resultado funcional (tabla limpia, descriptivos o figura) generado por código.

---

## 10. Definición del problema (plantilla del equipo)

Completar en esta sección o en un documento enlazado:

- **Problema:**
- **Objetivos:**
- **Alcance (qué entra y qué no):**
- **Dataset:** nombre, fuente, licencia, número de filas y columnas
- **Variable(s) de interés:**
- **Limitaciones conocidas del dato:**
