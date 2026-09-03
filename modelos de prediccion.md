# Modelos de predicción

Documento del curso **Introducción a la Programación Científica** (2026-2). Complementa el `README.md` de lectura, parseo, depuración e imputación.

Los descriptivos del notebook (`analisis de hurtos medellin.ipynb`) responden *qué pasó* en el recorte de hurtos a personas en Medellín (bus / taxi / metro). Un modelo predictivo responde otra pregunta: **dado lo que ya sabemos de un hecho (o de un momento y un lugar), ¿qué es razonable esperar?**

No sustituye a la limpieza. Se entrena sobre `hechos` (un registro por evento), no sobre `df_i` (bienes): si un hurto reporta celular y billetera, contar dos filas infla el fenómeno y el modelo aprende el duplicado, no el delito.

---

## 1. Qué es un modelo predictivo

Un modelo predictivo es una función que, a partir de variables de entrada **X** (predictores, *features*), produce una estimación de una variable de salida **y** (objetivo, *target*):

```text
ŷ = f(X)
```

`f` no se programa a mano regla por regla. Se **ajusta** con ejemplos donde X e y ya se observaron, de modo que el error entre `ŷ` y `y` sea pequeño *en datos que el modelo no vio*. Esa última cláusula es la diferencia entre memorizar la tabla y aprender un patrón.

En este curso, “modelo” no significa inteligencia artificial opaca. Significa un objeto matemático con tres piezas explícitas:

| Pieza | Pregunta | Ejemplo en hurtos |
| --- | --- | --- |
| **Objetivo y** | ¿Qué queremos anticipar? | ¿El hurto fue *atraco* o *cosquilleo*? |
| **Predictores X** | ¿Con qué información, disponible *antes* o *al lado* del hecho, lo inferimos? | hora, día, medio de transporte, comuna |
| **Forma de f** | ¿Qué familia de funciones usamos? | regresión logística, árbol, bosque aleatorio |

Si y no está bien definida, o X contiene la respuesta disfrazada, no hay modelo: hay tautología.

### 1.1 Predicción vs descripción

| | Descriptivo (lo que ya hicimos) | Predictivo |
| --- | --- | --- |
| Pregunta | ¿Cómo se distribuyen los hurtos? | ¿Qué y esperaríamos en un caso nuevo? |
| Éxito | Tabla, mapa o gráfico fiel al recorte | Error bajo en un conjunto **de prueba** |
| Riesgo típico | Confundir denuncia con crimen real | Sobreajuste: el modelo “adivina” el pasado y falla mañana |

Los hallazgos descriptivos *sí* informan al modelo: ya vimos que la mañana concentra cosquilleo en el sistema de transporte y que de noche sube el peso del atraco. Eso sugiere que `hora` y `medio_transporte` son predictores plausibles de `modalidad`. El modelo no descubre magia; cuantifica y pone a prueba esa hipótesis.

### 1.2 Supervisado (lo que usaremos) vs no supervisado

- **Supervisado:** cada fila tiene y conocida. Clasificar modalidad, estimar un conteo. Es el caso de este documento.
- **No supervisado:** no hay y; se buscan grupos o densidades (el hexbin y el mapa de barrios se parecen más a esto). Útil para explorar, no para “predecir una etiqueta”.

---

## 2. Cómo funcionan

### 2.1 El ciclo, sin jerga

1. **Definir y.** Una columna, o una recodificación clara (p. ej. `es_atraco = modalidad == "Atraco"`).
2. **Elegir X.** Solo variables que tendríamos en un caso nuevo. No el ID del hecho, no el texto crudo de latitud, no una columna que *es* y con otro nombre.
3. **Separar datos.** Una parte **entrena** `f`; otra, que no se tocó, **evalúa**. Si el modelo ve la prueba durante el ajuste, la nota es trampa.
4. **Ajustar.** El algoritmo mueve los parámetros de `f` para reducir un error (pérdida) en el entrenamiento.
5. **Evaluar.** Se compara `ŷ` con y real en la prueba, con una métrica adecuada al problema.
6. **Interpretar.** ¿El error es mejor que un baseline tonto? ¿El patrón coincide con el dominio (hora, centro, transporte)?

```text
hechos limpios  →  X, y  →  tren / prueba  →  f ajustada  →  métricas  →  decisión
```

### 2.2 Clasificación y regresión

| Tipo | y es… | Pregunta típica | Métrica de arranque |
| --- | --- | --- | --- |
| **Clasificación** | una clase (texto o 0/1) | ¿Atraco o cosquilleo? | exactitud, *recall* de la clase rara, matriz de confusión |
| **Regresión** | un número | ¿Cuántos hechos esperamos el martes a las 8 en la comuna 10? | MAE, RMSE |
| **Conteo / serie** | un número por tiempo o por celda espacial | ¿Sube o baja el volumen el próximo mes? | MAE sobre el futuro, no sobre un split aleatorio |

En nuestro archivo la mayoría de preguntas naturales son **clasificación**. La regresión aparece si agregamos: `hechos.groupby(["anio_mes", "comuna"]).size()`.

### 2.3 Entrenamiento y generalización

El modelo puede hacer dos cosas opuestas:

- **Subajuste:** `f` es demasiado simple (p. ej. “siempre cosquilleo”). No captura el pico de la mañana.
- **Sobreajuste:** `f` memoriza barrios y horas exactas del 2017–2019 y falla en 2020, o en un barrio con pocos casos.

La separación tren/prueba existe para detectar eso. En datos **temporales** (hurtos con fecha) un split aleatorio es optimista: el modelo “ve” el mismo año a ambos lados. Es más honesto entrenar en el pasado y probar en el futuro:

```text
entrenar:  fecha < 2019-01-01
probar:    fecha >= 2019-01-01
```

### 2.4 El baseline es obligatorio

Antes de un bosque aleatorio se evalúa un modelo nulo:

- Clasificación: predecir **siempre la clase mayoritaria** (aquí, *Cosquilleo*, ~48 % de los hechos; *Atraco* ~36 %).
- Regresión: predecir siempre la **media** (o la mediana) del tren.

Si el modelo sofisticado no gana al nulo de forma clara, no aporta. En ciencia eso se reporta; no se esconde.

### 2.5 Filtración de información (*data leakage*)

Ocurre cuando X contiene, directa o indirectamente, a y. El accuracy se dispara y el modelo es inútil en producción.

En este dataset, ejemplos de filtración:

| X sospechoso | Por qué |
| --- | --- |
| `conducta_especial` para predecir `modalidad` | A menudo describe el mismo modus (“A taxista”, “De celular”). |
| `lat` y `lon` para predecir `nombre_barrio` | La coordenada *define* el barrio. |
| `categoria_bien` / `bien` para predecir el hecho si el objetivo es el evento | El bien se conoce *después* del hurto, y además `hechos` ya deduplicó por evento: el bien no es atributo del hecho único de forma limpia. |
| Imputar y con información de la prueba | El futuro se filtró al pasado. |

Regla: **¿esta variable existiría en el momento en que yo querría hacer la predicción?** Si no, no entra en X.

---

## 3. Cómo funcionan en Python

La librería estándar para el prototipo es **scikit-learn** (`sklearn`). pandas arma la tabla; sklearn no debe recibir columnas de texto crudo ni `NaN` sin un plan.

Añadir al entorno:

```text
scikit-learn
```

### 3.1 Matriz X y vector y

sklearn espera números. Las categóricas (`medio_transporte`, `franja`, `comuna`) se convierten con **one-hot**: cada clase vira una columna 0/1. Un `Pipeline` hace el encode **solo con información del tren**, para no filtrar la prueba.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

hechos = pd.read_csv("../data/processed/hurtos_medellin_hechos.csv", parse_dates=["fecha"])

# Problema mínimo: dos modus operandi que ya vimos como regímenes distintos
subset = hechos[hechos["modalidad"].isin(["Atraco", "Cosquilleo"])].copy()
y = (subset["modalidad"] == "Atraco").astype(int)

num = ["hora", "edad"]
cat = ["franja", "dia", "medio_transporte", "lugar", "sexo"]
X = subset[num + cat]
```

### 3.2 Split, pipeline y ajuste

```python
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

prep = ColumnTransformer(
    [
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ]
)

modelo = Pipeline(
    [
        ("prep", prep),
        ("clf", LogisticRegression(max_iter=1000)),
    ]
)

nulo = Pipeline(
    [
        ("prep", prep),
        ("clf", DummyClassifier(strategy="most_frequent")),
    ]
)

modelo.fit(X_tr, y_tr)
nulo.fit(X_tr, y_tr)

print("nulo   ", nulo.score(X_te, y_te))
print("logística", modelo.score(X_te, y_te))
print(classification_report(y_te, modelo.predict(X_te), target_names=["Cosquilleo", "Atraco"]))
print(confusion_matrix(y_te, modelo.predict(X_te)))
```

Qué hace cada objeto:

| Objeto | Rol |
| --- | --- |
| `train_test_split(..., stratify=y)` | Misma proporción de atraco/cosquilleo en tren y prueba |
| `ColumnTransformer` | Escala números y codifica categorías **por separado** |
| `OneHotEncoder(handle_unknown="ignore")` | Una clase nueva en la prueba no rompe el predict |
| `Pipeline` | El preproceso se reajusta en cada fold; no hay encode “a mano” sobre todo el `df` |
| `DummyClassifier` | Baseline: siempre la clase más frecuente del tren |
| `LogisticRegression` | `f` lineal: cada feature suma (o resta) al log-odds de “atraco” |

La **regresión logística** no es “solo estadística antigua”: es el primer modelo interpretable. Un coeficiente positivo de `franja=Noche` a favor de atraco *debería* alinearse con el cruce `franja × modalidad` del notebook. Si no se alinea, o hay un bug o el modelo está usando un atajo.

### 3.3 Split temporal (preferible aquí)

```python
corte = pd.Timestamp("2019-01-01")
tr = subset[subset["fecha"] < corte]
te = subset[subset["fecha"] >= corte]

X_tr, y_tr = tr[num + cat], (tr["modalidad"] == "Atraco").astype(int)
X_te, y_te = te[num + cat], (te["modalidad"] == "Atraco").astype(int)
```

2020 está truncado en el archivo (y coincide con pandemia). Un test que sea *solo* 2020 puede lucir peor por cambio de régimen, no porque el modelo sea inútil. Eso se documenta, no se “arregla” mezclando años.

### 3.4 Un modelo un poco más flexible

```python
from sklearn.ensemble import RandomForestClassifier

bosque = Pipeline(
    [
        ("prep", prep),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=20,
            random_state=42,
            n_jobs=-1,
        )),
    ]
)
bosque.fit(X_tr, y_tr)
```

`min_samples_leaf=20` evita árboles que parten barrios con 3 hurtos. Más árboles no sustituyen un y mal definido.

Para **regresión** de un conteo mensual el esqueleto es el mismo: `RandomForestRegressor` o `LinearRegression`, y la métrica pasa a ser MAE (`mean_absolute_error`), no accuracy.

### 3.5 Predecir casos nuevos

```python
nuevos = pd.DataFrame(
    {
        "hora": [8, 22],
        "edad": [28, 40],
        "franja": ["Mañana (6-11)", "Noche (18-23)"],
        "dia": ["Lunes", "Sábado"],
        "medio_transporte": ["Metro", "Taxi"],
        "lugar": ["Estación del Metro", "Vía pública"],
        "sexo": ["Mujer", "Hombre"],
    }
)
proba_atraco = modelo.predict_proba(nuevos)[:, 1]
```

`predict` devuelve la clase; `predict_proba` la probabilidad. En operación suele importar más el umbral (¿alertar si P(atraco) > 0.4?) que el 0/1 por defecto.

---

## 4. Por qué son útiles

En este problema no se trata de “predecir el crimen a una persona”. El archivo **no identifica víctimas futuras**; identifica *hechos ya denunciados* en tres medios de transporte. La utilidad es operativa y analítica, con ese límite a la vista.

1. **Cuantificar un patrón que ya vimos.** El cruce hora × modalidad es una tabla. El modelo dice cuánto de ese patrón **se sostiene** en datos no usados para mirar la tabla.
2. **Priorizar.** Si P(atraco | noche, taxi, vía pública) es alta, no se “caza” a nadie: se describe un perfil de hecho más compatible con arma y con otro tipo de respuesta que el cosquilleo del metro a las 7 a.m.
3. **Compactar muchas variables a la vez.** Un gráfico 2D no cruza hora, medio, lugar, sexo y día. `f` sí; luego se inspeccionan coeficientes o importancias para no dejar una caja negra.
4. **Detectar cambio de régimen.** Si el modelo entrenado hasta 2018 se degrada en 2019–2020, el fenómeno (o el registro) cambió. Eso es un resultado científico, no un fracaso del código.
5. **Forzar honestidad sobre el dato.** Al elegir y y X aparecen las limitaciones del recorte: solo bus/taxi/metro, denuncia ≠ incidencia, Candelaria hipertrofiada en la muestra.

No son útiles para:

- declarar que un barrio “es peligroso” a partir de un accuracy de notebook;
- imputar intención individual;
- extrapolar a peatones, residencias o comunas casi ausentes en el archivo;
- reemplazar el mapa y los descriptivos: el modelo *se apoya* en ellos.

---

## 5. Cómo usarlos en *nuestro* dataset

Archivo de trabajo: `data/processed/hurtos_medellin_hechos.csv` (~11 600 hechos únicos). Cada fila es un evento de hurto a persona, no un bien. El recorte de Kaggle **solo** trae `Autobus`, `Taxi` y `Metro`.

### 5.1 Tres problemas que sí tienen sentido

Los tres salen de la lectura breve del notebook (dos modus, pico matutino, concentración en Candelaria / comuna 10). No se inventan y ajenos al EDA.

**A. Clasificar el modus operandi (el prototipo recomendado)**

| | |
| --- | --- |
| **y** | `modalidad ∈ {Atraco, Cosquilleo}` (tirar las clases raras al primer prototipo: descuido, raponazo, etc., o agruparlas en “otra”) |
| **X razonable** | `hora` o `franja`, `dia`, `medio_transporte`, `lugar`, `sexo`, `edad`, `codigo_comuna` |
| **X que no entra** | `conducta_especial`, `arma_medio` (el arma *es* casi la definición de atraco), `bien` |
| **Por qué sirve** | Son dos regímenes: cosquilleo en hora pico de bus/metro vs atraco, más nocturno y armado. El modelo prueba si hora + medio + lugar bastan para separarlos. |
| **Baseline** | siempre *Cosquilleo* |
| **Cuidado** | clases no equilibradas del todo; reportar *recall* de atraco, no solo accuracy |

**B. ¿El hecho cae en el núcleo espacial?**

| | |
| --- | --- |
| **y** | `en_candelaria = nombre_barrio == "La Candelaria"` o `codigo_comuna == 10` |
| **X razonable** | `hora`, `franja`, `dia`, `medio_transporte`, `lugar`, `modalidad` |
| **X que no entra** | `lat`, `lon`, `nombre_barrio`, `codigo_barrio`, `sede_receptora` si replica la zona |
| **Por qué sirve** | El ~15 % de hechos en un solo barrio y ~39 % en comuna 10 no es un mapa uniforme. Pregunta: ¿el perfil (metro, mañana, cosquilleo) ya delata el centro, sin GPS? |
| **Cuidado** | desbalance fuerte; accuracy alta prediciendo “no Candelaria” no demuestra nada. Usar F1 o *recall* de la clase positiva. |

**C. Volumen en el tiempo (regresión de conteos)**

| | |
| --- | --- |
| **y** | número de hechos por `anio_mes`, o por (`anio_mes`, `comuna`) |
| **X razonable** | mes, año, rezago (conteo del mes anterior), indicador de comuna |
| **Por qué sirve** | El EDA mostró subida hasta 2019 y caída en 2020. Un modelo de serie pone número a “¿qué esperaríamos el mes siguiente *si el régimen no cambia*?” |
| **Cuidado** | pocos puntos mensuales; 2020 no es un test limpio. No usar split aleatorio de filas de hechos para este y: hay que **agregar primero** y cortar por tiempo. |

Un cuarto problema tentador, **¿lleva arma de fuego?**, se solapa con A: `arma_medio` y `modalidad` no son independientes. Solo tiene sentido si X **no** incluye la modalidad.

### 5.2 Construcción de y y X sobre `hechos`

```python
hechos = pd.read_csv("../data/processed/hurtos_medellin_hechos.csv", parse_dates=["fecha"])

# A — dos clases del EDA
proto = hechos.loc[hechos["modalidad"].isin(["Atraco", "Cosquilleo"])].copy()
proto["y_atraco"] = (proto["modalidad"] == "Atraco").astype(int)

# B — núcleo espacial (comuna 10, no el GPS)
hechos["y_comuna10"] = (hechos["codigo_comuna"].astype("Int64") == 10).astype(int)

# C — serie mensual
mensual = (
    hechos.dropna(subset=["fecha"])
    .set_index("fecha")
    .resample("MS")
    .size()
    .rename("n_hechos")
    .to_frame()
)
mensual["n_lag1"] = mensual["n_hechos"].shift(1)
mensual["mes"] = mensual.index.month
```

Unidades: **hechos**, no bienes. Si se quiere un modelo de *objeto hurtado* (`categoria_bien`), entonces sí se usa `hurtos_medellin_bienes.csv`, y el objetivo deja de ser el evento.

### 5.3 Qué esperar del prototipo A (sin ejecutar magia)

Hipótesis que el modelo debería poder apoyar, porque ya salieron en descriptivos:

- `franja` mañana + `Metro` / `Autobus` + estación o bus → baja P(atraco), alta P(cosquilleo).
- `franja` noche/madrugada + `Taxi` + vía pública → sube P(atraco).

Si la logística invierte esos signos, se revisa el encode y las filas, no se “túnea” el bosque hasta que el accuracy suba.

### 5.4 Métricas que importan *aquí*

| Situación | No basta | Usar |
| --- | --- | --- |
| Cosquilleo vs atraco | accuracy sola | matriz de confusión, recall de atraco |
| Candelaria (~15 %) | accuracy | F1 de la clase positiva, o precisión-recall |
| Conteos mensuales | R² en el tren | MAE en meses **posteriores** al corte |

Exactitud 80 % puede ser un modelo ciego si el 80 % de las filas son una sola clase.

### 5.5 Orden recomendado en el notebook

1. Partir de `hechos` ya parseado (no del CSV crudo con `627.623.616`).
2. Fijar **un** problema (A, B o C). Escribir y en una oración.
3. Listar X y tachar filtraciones.
4. Dummy / media como baseline.
5. Logística + pipeline (interpretable).
6. Un modelo no lineal solo si gana al anterior en la **prueba**.
7. Contrastar coeficientes o importancias con los gráficos de hora, comuna y modalidad.
8. Redactar límites: recorte a tres medios, denuncia, corte de 2020, imputación previa de ~4 % de coordenadas (no usar `lat`/`lon` imputadas como si fueran GPS de alta fe).

---

## 6. Lo que un modelo no debe hacer en este curso

- Entrenar sobre datos sin parsear (`latitud` como texto con puntos de miles).
- Tratar `NaN` como 0 en hora, edad o coordenadas.
- Usar `hechos` duplicando bienes.
- Publicar un ranking de barrios “más peligrosos” con un random forest y 20 filas en la cola.
- Optimizar accuracy hasta que el gráfico se vea bien.
- Mezclar el conjunto de prueba en el `OneHotEncoder` global (`pd.get_dummies` sobre todo el `df` antes del split es una filtración clásica). Por eso el `Pipeline`.

---

## 7. Relación con el resto del repositorio

```text
README.md                     →  leer, parsear, depurar, imputar
notebooks/...hurtos...ipynb   →  descriptivos y mapa (qué ocurrió)
modelos de prediccion.md      →  este texto: qué se puede anticipar, y cómo
data/processed/hurtos_*.csv   →  entrada del prototipo predictivo
```

Sin las etapas del README, el modelo aprende artefactos (coordenadas rotas, `edad = -1`, `Sin dato` como clase). Sin los descriptivos, se elige un y que el recorte no puede sostener (p. ej. hurto residencial, que no está en el archivo).

El prototipo predictivo de este curso se da por cumplido si: el problema está escrito, hay baseline, hay split honesto, hay una métrica que no sea vanidad, y la interpretación no contradice el dominio ni finge GPS donde solo hay tres medios de transporte.
