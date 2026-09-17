# Bases de datos columnares, Parquet y Spark

Repositorio del curso — periodo **2026-2**.

El `README.md` deja el dato **leído, parseado, depurado e imputado**. Este documento cubre el paso siguiente: **cómo se guarda** esa tabla para análisis. El CSV depurado (`data/processed/hurtos_medellin_*.csv`) es un formato de intercambio. Para consultas analíticas —contar hechos por comuna, filtrar por hora, entrenar un modelo con unas pocas columnas— conviene un formato **columnar**.

El objetivo no es “exportar a otro archivo”. Es entender **por qué** el layout físico del dato cambia el tiempo, el disco y lo que un motor como Spark puede hacer después.

```text
CSV crudo  →  parsear / depurar  →  CSV procesado  →  Parquet  →  pandas o Spark
  (texto)         (calidad)            (entrega 1)     (columnar)     (análisis)
```

---

## 1. Filas vs columnas: dos contratos distintos

Una tabla es un contrato lógico: filas (observaciones) × columnas (variables). En disco ese contrato se puede materializar de dos maneras.

### 1.1 Almacenamiento por filas (*row-oriented*)

Se escriben juntas **todas las columnas de una observación**:

```text
fila 1:  2017-01-01 16:00 | Taxi | Atraco | Aranjuez | 37 | ...
fila 2:  2017-01-01 16:00 | Taxi | Descuido | Belén | 29 | ...
```

Así viven CSV, Excel, PostgreSQL/MySQL típicos y la mayoría de sistemas **OLTP** (transaccionales): insertar, actualizar o leer **un hecho completo** es barato.

### 1.2 Almacenamiento por columnas (*column-oriented*)

Se escriben juntos **todos los valores de una variable**:

```text
medio_transporte:  Taxi, Taxi, Taxi, Metro, Bus, ...
modalidad:         Atraco, Descuido, Atraco, Cosquilleo, ...
comuna:            Aranjuez, Belén, Villa Hermosa, ...
hora:              16, 16, 10, 8, ...
```

Así viven ClickHouse, Amazon Redshift, Google BigQuery, Apache Cassandra (en un sentido amplio) y archivos **Parquet / ORC**. El caso de uso es **OLAP** (analítico): agregaciones, filtros y lecturas de **unas pocas columnas** sobre muchas filas.

### 1.3 La misma pregunta, distinto costo

“¿Cuántos hurtos de *atraco* hay por `comuna`?” no necesita `color`, `bien`, `latitud` textual ni `id_hecho`.

| Layout | Qué lee el disco | Consecuencia |
| --- | --- | --- |
| Por filas (CSV) | Casi todo el archivo, aunque solo se usen 2 columnas | I/O proporcional al **ancho** de la tabla |
| Por columnas (Parquet) | Solo `modalidad` y `comuna` | I/O proporcional a las **columnas pedidas** |

En el recorte de hurtos hay 31 columnas. Un descriptivo de hora × modalidad usa 2. En CSV se pagan las otras 29; en columnar, no.

---

## 2. Por qué importan los formatos columnares

La importancia no es “está de moda en big data”. Es una consecuencia de **cómo se analiza** un dataset científico o de negocio.

### 2.1 El análisis casi nunca usa la fila entera

En este proyecto ya ocurrió:

- Los descriptivos agrupan por `anio_mes`, `hora`, `comuna`, `modalidad`.
- El mapa usa `lat`, `lon` y un conteo.
- Un modelo predictivo elige un `y` y un puñado de `X`; el resto estorba (y a veces filtra información).

Un motor columnar **proyecta** (elige columnas) y **predica** (filtra filas) *antes* de descomprimir todo. Eso se llama *projection pushdown* y *predicate pushdown*.

### 2.2 Compresión mucho más alta

Valores vecinos de **la misma variable** se parecen: `sexo` es casi siempre `Hombre`/`Mujer`, `medio_transporte` son tres clases, `anio` son unos pocos enteros. Eso se comprime con:

- **Diccionario:** cada categoría se guarda una vez; las filas guardan un entero corto.
- **Run-length encoding (RLE):** `Taxi, Taxi, Taxi, Taxi` → `(Taxi, 4)`.
- **Delta / bit-packing** en números y fechas.

En un CSV, `Hombre` se escribe 5 000 veces como texto UTF-8. En Parquet, una vez en el diccionario.

Efectos mecánicos:

1. **Menos disco.** El mismo recorte ocupa menos que el CSV (texto + comas + fechas repetidas).
2. **Menos I/O.** Leer menos bytes es más rápido que un algoritmo “más inteligente”.
3. **Mejor uso de CPU.** Operar sobre columnas densas y tipadas se vectoriza (SIMD); parsear `"37.0"` mil veces no.

### 2.3 Tipos conservados

El CSV **no tiene esquema**. Al reabrirlo, `fecha` vuelve a `object`, `coord_imputada` puede leerse mal y `codigo_comuna` a veces llega como `4.0`. Cada notebook tiene que volver a parsear. Parquet guarda el tipo: `timestamp`, `float64`, `bool`, `dictionary`.

Eso cierra el ciclo del README: parsear una vez, persistir el contrato, no reinterpretar texto en cada gráfica.

### 2.4 Cuándo *no* es la herramienta correcta

Columnar no gana siempre.

| Situación | Mejor layout |
| --- | --- |
| Insertar / actualizar **un** hurto | Filas (OLTP) |
| Leer la ficha completa de un `id_hecho` | Filas |
| Intercambio con Excel, R, un colega sin PyArrow | CSV o Excel |
| Agregar 11 000 hechos por hora y comuna | Columnas |
| Entrenar un modelo con 8 predictores sobre millones de filas | Columnas |
| Dataset más grande que la RAM | Columnas + motor distribuido (Spark, DuckDB, Polars) |

Una base transaccional (el sistema que *captura* la denuncia) suele ser por filas. El **almacén analítico** (el que *cuenta* denuncias) suele ser columnar. Son etapas distintas, no enemigos.

---

## 3. De bases columnares a archivos columnares

Una **base de datos columnar** (Redshift, BigQuery, ClickHouse, Vertica) administra almacenamiento, índices, permisos y consultas SQL. El analista no ve archivos: ve tablas.

Un **archivo columnar** (Parquet, ORC) es el mismo principio **sin servidor**: un fichero (o un directorio de ficheros) que pandas, Spark, DuckDB o BigQuery pueden leer. Es el formato de un *data lake*.

```text
OLTP (filas)          Lago / laboratorio           OLAP (columnas)
denuncia en línea  →  Parquet en disco/S3      →  Spark / SQL analítico
```

Para este curso, Parquet es el puente: el dataset ya cabe en pandas, pero el formato es el mismo que usaría Spark si el recorte creciera a todos los delitos de Colombia.

Otros nombres que van a aparecer:

| Formato | Orientación | Para qué |
| --- | --- | --- |
| **CSV / TSV** | Filas, texto | Intercambio, depuración a ojo |
| **JSON / GeoJSON** | Documentos | Mapas, APIs; no es tabular eficiente |
| **Avro** | Filas, binario, con esquema | Colas de eventos, serializar un registro |
| **ORC** | Columnas | Ecosistema Hive/Spark, muy parecido a Parquet |
| **Parquet** | Columnas | Estándar de facto en Python, Spark y nubes |

Parquet gana en el laboratorio científico porque es **portable**, **tipado** y lo leen pandas (`pyarrow`), Spark, DuckDB, Polars y casi cualquier warehouse.

---

## 4. Qué es Apache Parquet

Parquet es un formato **binario, columnar y autodescriptivo**. “Autodescriptivo” significa que el archivo lleva el **esquema** (nombres, tipos, nulabilidad) además de los datos.

Fue creado en 2013 en el ecosistema Hadoop (Twitter / Cloudera) y hoy es un proyecto de Apache. No es una base de datos: es un **archivo** (o un conjunto de *partes*) que un motor consulta.

### 4.1 Anatomía mínima

```text
archivo.parquet
├── footer (esquema + dónde está cada columna)
└── row groups  ← bloques de ~N filas
    └── columnas
        └── páginas (datos comprimidos + diccionario)
```

- **Row group:** un lote de filas (p. ej. 50 000). Dentro, cada columna se guarda aparte. Permite leer un bloque sin abrir el archivo entero.
- **Página:** unidad de compresión. Aquí viven diccionario, RLE y el codec (`snappy`, `gzip`, `zstd`).
- **Footer:** se lee primero. Ahí está el esquema y estadísticas (min/max por columna y row group). Si se pide `anio == 2019`, un row group cuyo max es 2018 **ni se abre**. Eso es *predicate pushdown*.

### 4.2 Qué guarda que el CSV no puede

En `hurtos_medellin_hechos.csv` todo es texto separado por comas. En Parquet se puede fijar:

| Columna | Tipo razonable en Parquet |
| --- | --- |
| `fecha`, `anio_mes` | timestamp |
| `lat`, `lon`, `edad` | float64 |
| `anio`, `mes`, `hora` | int |
| `coord_imputada`, `edad_imputada` | bool |
| `sexo`, `modalidad`, `comuna`, `dia`, `franja` | dictionary (categórica) |

Las categóricas son el premio gordo de la compresión: pocas clases, muchas filas.

### 4.3 CSV vs Parquet, en una tabla

| | CSV | Parquet |
| --- | --- | --- |
| Legible en Bloc de notas | Sí | No (binario) |
| Esquema / tipos | No | Sí |
| Layout | Por filas | Por columnas |
| Compresión | Externa (`.zip`) o ninguna | Por columna, integrada |
| Leer 2 de 31 columnas | Hay que parsear el archivo | Lee esas 2 |
| Faltantes | Texto vacío, `NA`, centinelas | `null` del tipo |
| Estándar para Spark | Entrada posible, cara | Formato nativo de trabajo |
| Riesgo | Encoding, separador, decimal | Dependencia de PyArrow / Spark |

Regla del curso: **CSV para entregar y auditar la limpieza; Parquet para analizar**. El CSV depurado no se borra. Parquet es un derivado, como el mapa.

### 4.4 Particiones (idea, no obligación en este recorte)

Spark y pandas pueden escribir:

```text
hurtos/
  anio=2017/parte-0.parquet
  anio=2018/parte-0.parquet
  ...
```

Si la consulta es `anio == 2019`, no se tocan los otros directorios. Con 11 611 hechos no hace falta. Con millones de filas, `anio` o `codigo_comuna` sí son particiones naturales.

---

## 5. Qué se gana con *este* dataset

El recorte depurado son dos tablas:

| Archivo | Grano | Filas × columnas (aprox.) |
| --- | --- | --- |
| `hurtos_medellin_hechos.csv` | un registro por evento | ~11 611 × 31 |
| `hurtos_medellin_bienes.csv` | un registro por bien reportado | ~16 486 × 31 |

Siguen valiendo las reglas del notebook: **hechos** para conteos y modelos; **bienes** solo cuando la pregunta es el objeto hurtado.

Al pasar a Parquet se busca:

1. **No re-parsear** `fecha` ni las banderas de imputación en cada notebook nuevo.
2. **Leer barato** las columnas del descriptivo o del modelo (`hora`, `comuna`, `modalidad`, `medio_transporte`).
3. Dejar el dato en el formato que Spark espera, sin cambiar el recorte ni la imputación.

Lo que Parquet **no** hace: no corrige `latitud` con puntos de miles, no deshace duplicados de bienes, no justifica la imputación de edad. Si el CSV procesado está mal, el Parquet replica el error, más comprimido.

---

## 6. Introducción breve a Apache Spark

### 6.1 El problema que resuelve

pandas carga la tabla **entera en RAM**, en el proceso de una máquina. Eso basta para este recorte (~11 000 hechos, decenas de MB). No basta cuando el archivo no cabe, o cuando se quiere repartir el trabajo en varias máquinas.

**Apache Spark** es un motor de cómputo distribuido: parte los datos y las operaciones entre *workers*, mantiene resultados intermedios en memoria (no solo en disco, a diferencia del MapReduce clásico) y encadena transformaciones en un grafo (DAG).

Nació en 2009 en Berkeley (proyecto AMPLab) y es el estándar de procesamiento analítico en clústeres. En la práctica se usa sobre todo su API **DataFrame** (Spark SQL), no los RDD de bajo nivel.

### 6.2 Ideas que hay que tener claras

| Idea | En una frase |
| --- | --- |
| **Driver / executors** | Un proceso orquesta; otros ejecutan tareas en particiones |
| **Partición** | Pedazo de la tabla; Spark procesa particiones en paralelo |
| **Lazy evaluation** | `filter`, `select`, `groupBy` no corren hasta una acción (`count`, `write`, `show`) |
| **Catalyst** | El optimizador reescribe la consulta (pushdown, orden de joins) |
| **Tungsten** | Ejecución en memoria columnar *off-heap*, no fila por fila en Python |

Esa pereza no es capricho: Spark espera a ver **todo** el plan para no leer `color` si nadie lo pidió, y para no abrir row groups de Parquet que no pueden cumplir el filtro.

### 6.3 Spark y Parquet se diseñaron el uno para el otro

```text
spark.read.parquet("...").select("comuna", "modalidad").groupBy("comuna").count()
```

1. Lee el footer de Parquet (esquema + estadísticas).
2. Descarta columnas no pedidas (*projection pushdown*).
3. Si hay filtro, descarta row groups (*predicate pushdown*).
4. Descomprime páginas en columnar y agrega por partición.
5. Junta resultados en el driver.

Hacer lo mismo con CSV obliga a **parsear texto de todas las columnas** en todos los nodos. Por eso, en producción, se evita `spark.read.csv` salvo como ingestión inicial.

### 6.4 pandas vs Spark

| | pandas | Spark |
| --- | --- | --- |
| Dónde corre | Un proceso, una RAM | Clúster (o local en varios núcleos) |
| Tamaño cómodo | Caber en memoria | Más grande que una máquina |
| API | `df.groupby(...)` | `df.groupBy(...).count()` (parecida) |
| Evaluación | Ansiosa | Perezosa |
| Tipos | dtypes de NumPy | Esquema Spark (nullable, Decimal, etc.) |
| Este curso | Herramienta principal | Concepto + siguiente escala |

Con 11 000 filas Spark es **más lento** que pandas: hay overhead de JVM, serialización y planificación. Spark no se usa porque el recorte sea “big data”. Se presenta porque el formato Parquet y el modelo mental (proyectar, filtrar, agregar) son los mismos cuando el recorte crezca.

Herramientas intermedias, útiles de conocer: **DuckDB** y **Polars** hacen consultas columnares *in-process*, sin clúster, leyendo Parquet con pushdown. Para el prototipo del curso, pandas + PyArrow basta.

### 6.5 Ejemplo mínimo (lectura, no obligación de ejecutarlo aquí)

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("hurtos").getOrCreate()

hechos = spark.read.parquet("data/processed/hurtos_medellin_hechos.parquet")

resumen = (
    hechos
    .where("medio_transporte in ('Bus', 'Taxi', 'Metro')")
    .groupBy("comuna", "modalidad")
    .count()
    .orderBy("count", ascending=False)
)

resumen.show()
```

Equivalente en pandas, que es lo que el notebook de conversión usa:

```python
import pandas as pd

hechos = pd.read_parquet(
    "data/processed/hurtos_medellin_hechos.parquet",
    columns=["comuna", "modalidad", "medio_transporte"],
)
resumen = (
    hechos.groupby(["comuna", "modalidad"], observed=True)
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)
```

La diferencia de API es cosmética. La diferencia de **motor** aparece cuando `hechos` no cabe en RAM.

---

## 7. Orden recomendado en el prototipo

1. Partir de los CSV **ya depurados** (`data/processed/`), no del archivo crudo.
2. Volver a **declarar tipos** al leer el CSV (fecha, bool, categorías). El CSV no los recuerda.
3. Escribir Parquet con PyArrow (`engine="pyarrow"`).
4. Comparar **tamaño en disco** CSV vs Parquet.
5. Demostrar proyección: leer solo `hora`, `comuna`, `modalidad` y cronometrar o medir bytes.
6. Comprobar que el número de filas y un `id_hecho` de muestra coinciden (round-trip).
7. Seguir usando **hechos** para conteos; no inflar con bienes.

Notebook de esta unidad: `notebooks/csv a parquet.ipynb`.

---

## 8. Relación con el resto del repositorio

```text
README.md                          →  leer, parsear, depurar, imputar
notebooks/...hurtos...ipynb        →  descriptivos; escribe los CSV procesados
bases de datos columnares.md       →  este texto: layout físico y Spark
notebooks/csv a parquet.ipynb      →  CSV procesado → Parquet
modelos de prediccion.md           →  qué se puede anticipar sobre hechos
data/processed/hurtos_*.csv        →  entrega auditable de la limpieza
data/processed/hurtos_*.parquet    →  entrada columnar de análisis posteriores
```

Sin el README, Parquet fosiliza tipos mal parseados. Sin los descriptivos, se particiona o se indexa una columna que el recorte no sostiene. Sin Parquet, cada modelo y cada gráfica vuelven a pagar el CSV entero.

El prototipo de esta unidad se da por cumplido si: se explica por qué columnar, existe un Parquet de hechos (y opcionalmente de bienes) con tipos explícitos, se documenta la ganancia de espacio o de columnas leídas, y Spark queda situado como motor de la *misma* idea a otra escala —no como magia ni como requisito para 11 000 filas.
