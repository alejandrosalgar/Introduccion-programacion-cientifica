# Tarea 2 · Primer análisis en Google Colab

Repositorio del curso — periodo **2026-2**.

| Campo | Detalle |
| --- | --- |
| Tarea | 2 |
| Fecha de entrega | **miércoles 14 de octubre de 2026** |
| Peso | 10 % |
| Dónde se entrega | el **mismo repositorio de grupo** de la Evaluación 1 |
| Entregable | notebook en **Google Colab** + URL en el README del equipo |

El objetivo no es rehacer los hurtos de Medellín. Es **abrir Colab** y repetir el ciclo que ya vimos —leer, parsear, depurar, graficar y predecir— sobre **otra** base tabular.

Un CSV chico y bien trabajado vale lo mismo que un archivo grande. El tamaño no suma puntos. Quien no ha visto bases de datos elige un CSV de unas cientos de filas; quien va adelantado puede usar más columnas, Parquet o un modelo menos lineal. No se exige Spark ni SQL.

---

## 1. Entrega

1. Trabaje en el **repositorio de grupo** (el de la Evaluación 1). Un push a *este* repositorio del curso **no** cuenta.
2. Cree un notebook en [Google Colab](https://colab.research.google.com/).
3. En el **README** del repo del equipo, deje una sección visible (por ejemplo `## Tarea 2`) con la **URL del Colab**.
4. Comparta el notebook así:
   - **Compartir** → añadir **`alejandro.salgar@gmail.com`** con permiso de **Lector** (como mínimo).
   - Acceso general: **Cualquiera que tenga el enlace** → **Lector**, para que la URL del README abra.

Sin el correo del docente en el compartir, **no se revisa**. Un enlace que pide permiso o que solo ve el dueño tampoco cuenta.

El notebook debe poder ejecutarse **de arriba abajo** en Colab (Runtime → Run all) sin celdas rotas ni rutas de su computador (`C:\Users\...`).

---

## 2. Cómo empezar en Colab

1. Entre a [colab.research.google.com](https://colab.research.google.com/) con una cuenta de Google.
2. **Archivo → Nuevo cuaderno**. Ponga un título claro (`tarea2-analisis.ipynb`).
3. Cargue el dato de una de estas formas (elija una y déjela escrita):

```python
# Opción A: archivo que usted sube en la sesión
from google.colab import files
uploaded = files.upload()  # elija el CSV / Excel

import pandas as pd
df = pd.read_csv(list(uploaded.keys())[0])  # ajuste sep= y encoding= si hace falta
```

```python
# Opción B: URL pública (datos.gov.co, raw de GitHub, etc.)
import pandas as pd
df = pd.read_csv("https://.../datos.csv")
```

4. Si necesita un paquete que Colab no trae:

```python
# %pip install scikit-learn
```

pandas, NumPy, matplotlib y seaborn ya vienen. scikit-learn también suele estar; instálelo solo si falla el `import`.

5. Fije una **semilla** cuando use azar (split, imputación por muestreo, modelo):

```python
import numpy as np
rng = np.random.default_rng(42)
```

El runtime de Colab **se borra** al desconectarse. Si subió el CSV con `files.upload()`, vuelva a subirlo o léalo desde URL. No asuma que el archivo sigue en `/content` al día siguiente.

---

## 3. Dataset

Cualquier tabla (CSV o Excel), **distinta** de `hurtos_medellin_hechos` / `hurtos_medellin_bienes`.

Fuentes razonables: [datos.gov.co](https://www.datos.gov.co/), Kaggle, UCI, un Excel propio con licencia clara.

En una celda Markdown del Colab (o en el README del equipo, junto a la URL) anote:

- nombre y **fuente** (enlace);
- número de filas y columnas **después** de leer;
- **problema** en una oración: qué quiere describir o anticipar;
- **y** (objetivo) y de dónde sale.

No use el recorte de hurtos del curso. Si el archivo es enorme y Colab se queda sin RAM, tome una muestra reproducible (`df.sample(n=..., random_state=42)`) y **dígalo**.

---

## 4. Qué tiene que incluir el notebook

Las tres piezas son las del curso. El material está en el [`README.md`](README.md) (lectura, parseo, depuración, imputación) y en [`modelos de prediccion.md`](modelos%20de%20prediccion.md) (baseline, split, métrica).

### 4.1 Limpieza

- Leer con encoding, separador y `na_values` explícitos si hace falta.
- Parsear tipos (números, fechas, categorías). Contar cuántos `NaN` nacieron en el parseo.
- Auditar faltantes, duplicados e imposibles.
- Decidir, variable por variable, si se deja el hueco, se imputa o se elimina —y **escribir por qué**.
- No borrar atípicos solo porque estorban al gráfico o al modelo.

### 4.2 Gráficos

Al menos **dos** figuras (matplotlib o seaborn). El título es una **pregunta**, no un nombre de columna.

Ejemplos de título: “¿La tarde concentra más casos que la mañana?” / “¿El ingreso se asocia con la zona?”.

### 4.3 Predicción

Un modelo **cualquiera** (regresión logística, lineal, árbol…). Lo obligatorio no es el algoritmo; es el contrato científico:

- **y** escrito en una oración.
- **X** que existiría en el momento de predecir (sin filtración: no meta la respuesta con otro nombre).
- Separar **tren** y **prueba**.
- Un **baseline** (clase mayoritaria o media/mediana del tren) **antes** del modelo.
- Una métrica que no sea solo accuracy de vanidad (si hay desbalance, recall/F1 o matriz de confusión; si y es numérica, MAE).
- Un párrafo: ¿el modelo gana al nulo? ¿el patrón tiene sentido en el dominio? ¿qué **no** se puede concluir?

Pueden adaptar el `Pipeline` + `DummyClassifier` / `LogisticRegression` de `modelos de prediccion.md` §3.

No se pide Spark, SQL, mapa ni bosque aleatorio. Quien quiera ir más lejos puede; no baja la nota de quien entregue el mínimo bien hecho.

---

## 5. Qué se evalúa

| Criterio | Qué se espera |
| --- | --- |
| Acceso | URL del Colab en el README del **repo de grupo**; compartido con `alejandro.salgar@gmail.com` |
| Colab | Corre de arriba abajo; no depende de rutas locales |
| Limpieza | Tipos parseados; faltantes auditados; decisiones justificadas |
| Gráficos | Dos figuras con título-pregunta |
| Predicción | y, baseline, split, métrica honesta, párrafo de límites |
| Dataset | Distinto de hurtos; fuente citada. El tamaño no puntúa |

La evaluación se rige por el **capítulo XII del Reglamento Estudiantil (RE)**.

---

## 6. Recordatorios

- El plazo es el **14 de octubre de 2026**. El enlace tiene que estar en el README del equipo ese día.
- Añada **`alejandro.salgar@gmail.com`** en Compartir. “Cualquiera con el enlace” no sustituye ese paso si el docente no aparece como lector.
- No suba al GitHub un CSV que el proveedor prohíba redistribuir; deje la fuente y el código de lectura.
- Un accuracy alto con un baseline igual de alto no es un resultado: es la clase mayoritaria. Repórtelo.
