# Quinto parcial · Reparación, gráficos y modelo

Repositorio del curso — periodo **2026-2**.

| Campo | Detalle |
| --- | --- |
| Evaluación | Quinto parcial |
| Publicación | miércoles 18 de noviembre de 2026 |
| Entrega | **miércoles 25 de noviembre de 2026, 23:59** |
| Modalidad | los mismos grupos de la Evaluación 1 y de la Tarea 2 |
| Dónde se entrega | el **repositorio del grupo** |
| Entregables | diapositivas HTML interactivas y un video montado en el README del grupo |

El grupo ya reparó los datos, hizo los gráficos y ajustó el modelo de predicción en la [Tarea 2](tarea%202.md). Este parcial pide **explicar ese trabajo**: recorrerlo en diapositivas HTML y dejar un video de esa explicación en el README del equipo. La reparación es la de esa tarea (lectura, parseo, depuración e imputación, en el [README del curso](README.md)); los gráficos y el modelo, los de la misma entrega. El contrato del modelo está en [`modelos de prediccion.md`](modelos%20de%20prediccion.md).

Un push a *este* repositorio del curso no cuenta. Un grupo nuevo, armado solo para este parcial, tampoco.

---

## 1. Qué se entrega

En el repositorio del grupo, antes del miércoles 25 a las 23:59:

1. Una carpeta `quinto_parcial/` con un `index.html` y las imágenes que ese archivo use.
2. En el `README.md` del grupo, una sección `## Quinto parcial` con el video.

El HTML y el video cuentan el notebook de la Tarea 2. Las cifras que se dicen tienen que poder encontrarse ahí. Este parcial no pide otro dataset, otra limpieza ni otro modelo.

---

## 2. Las diapositivas

Un solo HTML. Se abre con doble clic, sin instalar nada, sin servidor y sin internet. Las flechas izquierda y derecha cambian de diapositiva. En pantalla se lee el número de la diapositiva y el total.

El reproductor puede parecerse al de la clase de grafos (flechas y contador). El contenido es el análisis del grupo. Exportar el notebook a PDF, o pegar capturas en un PowerPoint, deja este punto en cero.

Las diapositivas van en este orden.

### 2.1 Reparación

La reparación es lo que ya está en el notebook: lectura, parseo, auditoría, depuración e imputación.

- Cómo entró el archivo: encoding, separador y valores que se trataron como faltante.
- Qué se parseó (números, fechas, categorías) y qué huecos nacieron en ese parseo.
- Qué se auditó: faltantes, duplicados e imposibles.
- Variable por variable, la decisión que ya tomaron: dejar el hueco, imputar o eliminar, y por qué.
- Si imputaron, el método (media, mediana, moda, muestreo, por grupo) y qué le pasó a la distribución. Una media que aplasta la desviación estándar se dice en la diapositiva.

### 2.2 Gráficos

Cada figura que el grupo usa para sostener la pregunta, como mínimo las dos de la Tarea 2.

- La figura está en la diapositiva (imagen exportada del notebook, en la misma carpeta).
- El título es la pregunta, la misma del notebook.
- Al lado, la lectura: una cifra que se ve en la figura y qué no alcanza a concluirse con ella.

### 2.3 Modelo de predicción

- **y** en una oración.
- **X**: qué entra y qué se dejó por fuera porque no existiría al momento de predecir, o porque es la respuesta con otro nombre.
- Cómo se separó entrenamiento y prueba.
- El baseline (clase mayoritaria, o media o mediana del entrenamiento) y el número que obtuvo.
- La métrica del modelo en la prueba, al lado del baseline.
- Si el modelo gana al nulo, y qué no se puede concluir.

---

## 3. El video

Duración: **6 a 10 minutos**. Se ve el `index.html` en el navegador, con la dirección en pantalla, y se oye la explicación. Aparecer en cámara es opcional.

El recorrido sigue el orden de las diapositivas: pregunta del dataset, reparación, gráficos y modelo. En el modelo se dicen en voz alta el baseline, la métrica y el límite.

Cada integrante habla al menos un tramo y dice su nombre al empezarlo. El video se graba sobre el HTML ya cerrado: si el archivo cambia después, el video y las diapositivas dejan de corresponder.

---

## 4. El video en el README

En el `README.md` del repositorio del grupo, una sección visible:

```markdown
## Quinto parcial

- Video: https://…
- Diapositivas: `quinto_parcial/index.html`
```

Ahí van el enlace del video y la ruta del `index.html` dentro del repo.

El enlace abre sin pedir permiso adicional: YouTube no listado, Drive con acceso por enlace, u otro equivalente. Si el repositorio es privado, inviten a `alejandro.salgar@gmail.com` como lector antes del plazo. Un enlace que pide acceso, o que solo abre el dueño, deja el video en cero.

---

## 5. Qué se revisa

La nota va de 0,0 a 5,0.

| Criterio | Puntos |
| --- | --- |
| `index.html` en el repo del grupo: abre con doble clic, las flechas cambian de diapositiva y se ve el contador | 0,8 |
| Reparación del notebook: lectura, parseo, auditoría y la decisión por variable, con el porqué | 1,4 |
| Gráficos del notebook en las diapositivas, cada uno con su pregunta y una lectura | 1,0 |
| Modelo: y, X, separación entrenamiento/prueba, baseline, métrica y el límite de lo que se puede concluir | 1,3 |
| Video de 6 a 10 minutos en el README del grupo: se ve el HTML, se oye la explicación y habla cada integrante | 0,5 |
| **Total** | **5,0** |

La evaluación se rige por el **capítulo XII del Reglamento Estudiantil (RE)**.

---

## 6. Recordatorio

El plazo es el **miércoles 25 de noviembre de 2026, a las 20:00**. Se califica lo que esté en el repositorio del grupo a esa hora: el `index.html` y el video en el README.
