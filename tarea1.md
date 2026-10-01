# Tarea 1 · Algoritmos greedy en LeetCode

**Curso:** Análisis de algoritmos · ITM · 2026-2  
**Tema:** algoritmos greedy (voraces)  
**Entrega:** repositorio **individual** de cada estudiante (no el repositorio del curso).

En clase se vio el patrón greedy: ordenar o puntuar candidatos, elegir en cada paso la opción localmente mejor y **no retractarse**. Esta tarea pide aplicar ese patrón en dos problemas reales de [LeetCode](https://leetcode.com/).

---

## Qué hay que hacer

Resolver **los dos** ejercicios de abajo usando un enfoque **greedy**. Para cada uno:

1. Implementar la solución en LeetCode (el lenguaje es libre: Python, Java, C++, JavaScript, TypeScript, etc.).
2. Hacer **Submit** hasta obtener **Accepted** (éxito: todos los casos de prueba pasan).
3. Subir al **repositorio individual** el código y las **imágenes** que demuestren ese éxito.

Sin captura de **Accepted**, el ejercicio no se considera entregado.

---

## Entrega (repositorio individual)

Monte **todo** en su repositorio individual, en una carpeta clara, por ejemplo:

```text
tarea1/
├── README.md                 ← enlace a cada problema, criterio greedy y complejidad
├── lemonade-change/          ← código del ejercicio 1
├── assign-cookies/           ← código del ejercicio 2
└── evidencias/
    ├── lemonade-change-accepted.png
    └── assign-cookies-accepted.png
```

El nombre de las carpetas puede variar; lo obligatorio es que se identifique **qué archivo es de cuál problema** y que las evidencias estén **dentro del repo** (no solo pegadas en un correo o un chat).

### Imágenes de éxito (obligatorias)

Por **cada** problema incluya al menos **una captura de pantalla** en la que se vea, sin recortar lo esencial:

- el enunciado o el número/título del problema de LeetCode;
- el resultado **Accepted** (o **Success**), en verde;
- que **todos** los test cases pasaron;
- runtime / memoria si LeetCode los muestra;
- **su usuario** de LeetCode visible (o el correo/cuenta con la que resolvió).

No vale una captura solo del editor, ni del Run local, ni de un caso de ejemplo. Tiene que ser el **Submit** aceptado por la plataforma.

Si quiere, puede agregar una segunda imagen con el detalle de *Runtime beats …%* / *Memory beats …%*. Es opcional.

### README de la entrega

En el `README.md` de la carpeta de la tarea, para **cada** ejercicio escriba en pocas líneas:

- enlace al problema;
- cuál es el **criterio greedy** (qué elige en cada paso y por qué);
- complejidad de **tiempo** y de **espacio** (`O(…)`);
- enlace relativo a la(s) imagen(es) de **Accepted**.

Ejemplo de cómo incrustar la evidencia en Markdown:

```markdown
## 860. Lemonade Change

Criterio greedy: …

![Accepted — Lemonade Change](evidencias/lemonade-change-accepted.png)
```

---

## Ejercicio 1 · [860. Lemonade Change](https://leetcode.com/problems/lemonade-change/)

**Dificultad:** Easy  
**Etiqueta:** Greedy

En un puesto de limonada cada vaso cuesta **5**. Los clientes pagan con billetes de **5**, **10** o **20**, en el orden del arreglo `bills`. Hay que devolver el cambio exacto con los billetes ya recibidos (no hay caja inicial). Decidir si se puede atender a **todos**.

Este problema es primo del laboratorio de la **caja / vuelto**: la decisión local es *con qué denominaciones doy el cambio ahora*, sin deshacer ventas anteriores. Piense qué billetes conviene **reservar** (el de 5 suele ser más útil que el de 10).

**Pista de diseño (no es la solución completa):**

- candidatos: el siguiente cliente de la cola;
- criterio: dar el cambio con la combinación que **menos comprometa** los billetes pequeños que quedan;
- factibilidad: si en algún momento no hay cambio, la respuesta es `false`.

Indique en el README la complejidad: con una pasada debería quedar **lineal** en el número de clientes.

---

## Ejercicio 2 · [455. Assign Cookies](https://leetcode.com/problems/assign-cookies/)

**Dificultad:** Easy  
**Etiqueta:** Greedy

Hay `g[i]` (factor de gula del niño `i`) y `s[j]` (tamaño de la galleta `j`). Cada niño recibe **a lo sumo una** galleta. El niño `i` queda satisfecho si `s[j] >= g[i]`. Hay que **maximizar** el número de niños satisfechos.

Aquí el greedy se parece a **asignar el recurso más ajustado** que aún sirve: si desperdicia una galleta grande en un niño fácil de contentar, puede quedarse sin pieza para uno más exigente. Ordenar y luego una pasada (dos punteros) es el patrón esperado.

**Pista de diseño (no es la solución completa):**

- candidatos: niños y galletas;
- criterio: emparejar, de menor a mayor, la galleta **más pequeña que aún satisface** al siguiente niño;
- factibilidad: una galleta demasiado chica se descarta y se prueba la siguiente.

Indique en el README la complejidad. Si ordena, el término dominante suele ser **`O(n log n + m log m)`**.

---

## Qué se evalúa

| Criterio | Qué se espera |
| --- | --- |
| Completitud | Los **dos** problemas en el repositorio individual |
| Éxito en LeetCode | Imagen de **Accepted / Success** por cada uno, legible y asociada al problema |
| Enfoque greedy | Criterio local escrito; no basta “el código pasó” |
| Complejidad | `O` de tiempo y espacio, coherente con el código |
| Organización | Carpetas o nombres claros; el README enlaza código e imágenes |

No se pide copiar una solución de Internet sin entenderla. Si el código es correcto pero no puede explicar el criterio greedy en clase, la tarea queda incompleta.

---

## Recordatorios

- Trabaje en **su** repositorio. Un push al repo del curso **no** cuenta como entrega.
- Haga `git add` de las **imágenes** (`.png` / `.jpg`). Un README que apunta a archivos que nunca se subieron no sirve.
- El veredicto que cuenta es **Accepted** en Submit, no *Run Code* sobre un ejemplo.
- Plazos y forma de avisar el enlace del repo: según lo indicado en clase / aula virtual.
