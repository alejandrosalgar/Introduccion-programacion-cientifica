# Taller de grafos · Un problema en la plantilla

Repositorio del curso — periodo **2026-2**.

| Campo | Detalle |
| --- | --- |
| Taller | Grafos |
| Clase en la que se pide el video | **miércoles 18 de noviembre de 2026** |
| Modalidad | individual; se elige **uno** de los diez problemas |
| Plantilla | [`grafos/index.html`](grafos/index.html) |
| Entregables | un solo HTML y un video de **4 a 6 minutos** |

La clase de grafos ya está en un archivo que se abre con doble clic: diapositivas y laboratorios de DFS, BFS y Dijkstra, sin servidor y sin conexión. Este taller pide tomar ese archivo como plantilla y volverlo la exposición de un problema propio.

---

## 1. Qué hay que hacer

1. Copie [`grafos/index.html`](grafos/index.html).
2. Elija **un** problema de la lista.
3. Cambie el grafo, los pesos, los textos de cada paso y la respuesta, hasta que el archivo cuente ese problema.
4. Puede cambiar colores, tipografía y composición. No es obligatorio: el taller es el problema, no la hoja de estilos.

El reproductor se puede reutilizar. Las flechas cambian de diapositiva. En el laboratorio siguen el anterior, el siguiente, la barra y reproducir.

El mapa de la clase (ITM Robledo, El Poblado, la vía rápida) y el relato de S, A, B y H son el ejemplo. El archivo del taller usa otro grafo y otro relato. Cambiar solo la paleta deja el ejemplo de clase.

## 2. Qué se lleva el 18 de noviembre

El video se solicita en esa clase. El medio de envío se confirma ahí. Hay que llegar con las dos piezas hechas: el video se graba sobre el HTML ya terminado.

1. **Un `index.html`.** Un solo archivo. Doble clic, sin instalar nada y sin internet. Las flechas y los controles del laboratorio siguen funcionando.
2. **Un video de cuatro a seis minutos.** Se ve ese archivo en el navegador y se oye la explicación. No hace falta aparecer en cámara.

En el video, en este orden aproximado:

- nombre, número del problema y la pregunta en una oración;
- la lista de vecinos del grafo propio;
- el algoritmo avanzando, señalando la pila, la cola o los pendientes;
- la respuesta: ruta y costo, en las unidades del problema.

Si el enunciado pide dos algoritmos, se ven las dos rutas y se dice por qué no son la misma.

El video y el HTML se entregan juntos. Si el archivo cambia después de grabar, dejan de corresponder.

## 3. Reglas

- El trabajo es individual. El HTML y la voz son de quien entrega.
- Un problema. Si el enunciado pide comparar BFS con Dijkstra, o BFS con un DFS más largo, esa comparación es parte del mismo problema.
- El grafo es propio. Renombrar los vértices del ejemplo, con las mismas conexiones, no cuenta.
- Salvo el laberinto, el grafo tiene **entre 6 y 14 vértices**.
- Los pesos, cuando existen, son positivos y van escritos sobre la arista. El largo del trazo en pantalla no es el peso: el número lo es.
- El algoritmo responde la pregunta anunciada. DFS recorre; no se usa como camino más corto. BFS cuenta aristas; no se usa como menor distancia en metros o en minutos.
- Cada paso habla de los vértices propios.
- Una diapositiva muestra la lista de adyacencia y, si hay pesos, el de cada arista. El dibujo y esa lista son el mismo grafo.
- El texto va en español.
- Si el problema usa personas, los nombres son inventados: sin apellidos de compañeros, sin correos y sin teléfonos.

Si dos personas eligen el mismo enunciado, los grafos tienen que ser distintos.

## 4. Los diez problemas

### 4.1 Pasillos

Un lugar conocido: un piso del ITM, un edificio, un centro comercial. Los vértices son sitios. Las aristas son pasillos o puertas y todas cuestan 1. Hay más de un camino entre el origen y el destino.

- **Pregunta.** ¿Cuál es el menor número de pasillos entre los dos sitios?
- **Algoritmo.** BFS. Al cierre, muestre también un recorrido DFS entre los mismos sitios que use estrictamente más pasillos, y escriba que esa ruta no es la respuesta.
- **Qué se ve.** La cola, la distancia en pasillos y las dos rutas, con sus cantidades.

### 4.2 La avenida larga

Un barrio o un pueblo, distinto del mapa de la clase. Una avenida une dos zonas en un solo tramo y mide más metros que otro camino, de más calles y tramos más cortos.

- **Pregunta.** ¿Qué ruta usa menos calles? ¿Qué ruta suma menos metros?
- **Algoritmo.** BFS para las calles. Dijkstra para los metros.
- **Qué se ve.** Las dos rutas y los dos costos. Las secuencias de vértices son distintas. La avenida larga queda identificada en el dibujo.

### 4.3 Transbordos y minutos

Una red pequeña de bus, metro o cable. Las estaciones son los vértices. Cambiar de línea es seguir una arista. Cada tramo dura unos minutos, siempre un número positivo.

- **Pregunta.** ¿Qué ruta hace menos transbordos? ¿Qué ruta tarda menos minutos?
- **Algoritmo.** BFS para los transbordos. Dijkstra para los minutos.
- **Qué se ve.** Un par origen–destino en el que la ruta de menos transbordos tarda más. Los dos tiempos quedan escritos en minutos.

### 4.4 La cadena más corta

Entre 8 y 12 personas, con nombres inventados. Una arista significa que se conocen. Elija dos que no tengan arista directa y entre las cuales sí exista un camino.

- **Pregunta.** ¿Cuál es la cadena más corta de conocidos entre esas dos personas?
- **Algoritmo.** BFS. La distancia es el número de saltos.
- **Qué se ve.** La cola y, al cierre, la cadena. El relato dice por qué una cadena más larga no mejora la respuesta.

### 4.5 Laberinto

Una cuadrícula de 5×5 a 8×8, con al menos cuatro celdas muro. Cada celda libre es un vértice. Solo se camina arriba, abajo, a la izquierda o a la derecha. El paso vale 1. Existe un camino más largo que el mínimo.

- **Pregunta.** ¿Cuál es el camino más corto, en pasos, desde el ingreso hasta la salida?
- **Algoritmo.** BFS.
- **Qué se ve.** La ola sobre la cuadrícula, los muros y, al cierre, la ruta con el número de pasos. Si el frente entra a un callejón, el texto dice que eso no acorta la ruta.

### 4.6 Dos salidas

Un edificio. Los pasillos cuestan 1. Hay un origen y al menos dos salidas, las dos alcanzables.

- **Pregunta.** ¿Qué salida queda a menos puertas, y a cuántas?
- **Algoritmo.** BFS. Sirve comparar la distancia a cada salida.
- **Qué se ve.** La salida elegida con su número de puertas, y la otra con el suyo. Si empatan, el texto lo dice y muestra las dos.

### 4.7 El tubo que no conviene

Una red de agua, gas o cable. Los vértices son un tanque, válvulas y un destino. Cada tubo tiene una longitud en metros, positiva. Entre algún par de vértices hay un tubo directo más largo que otro camino de dos o más tubos.

- **Pregunta.** ¿Cuál es la menor longitud de tubería desde el tanque hasta el destino?
- **Algoritmo.** Dijkstra.
- **Qué se ve.** Un paso en el que el tubo directo se descarta porque no mejora la marca del vecino. Cada longitud está escrita. Al cierre, la ruta y el total en metros.

### 4.8 La calle cerrada

Un grafo conexo de calles, todas de costo 1. Se elige una arista y se cierra. Al quitarla, el destino deja de ser alcanzable o el mínimo de calles sube.

- **Pregunta.** ¿Cuántas calles hay con la red completa, y qué pasa al cerrar esa arista?
- **Algoritmo.** BFS en los dos momentos.
- **Qué se ve.** El antes y el después, con la arista nombrada. La segunda respuesta es otra ruta, con más calles, o la frase «no hay camino».

### 4.9 Minutos, no cuadras

Un mapa pequeño. El peso es el tiempo en minutos, no el largo del trazo. Alguna cuadra que se ve corta tarda más que un rodeo de varias cuadras.

- **Pregunta.** ¿Cuál es la ruta de menor tiempo?
- **Algoritmo.** Dijkstra, en minutos. BFS entra como contraste: la ruta de menos cuadras.
- **Qué se ve.** Las dos rutas, distintas. El cierre dice los minutos de cada una.

### 4.10 Lo que se confirma y no se usa

Un grafo con pesos positivos. El destino no es el vecino más cercano del origen: hay al menos un vértice estrictamente más cerca del origen que el destino, y ese vértice no está en la ruta óptima.

- **Pregunta.** ¿Cuál es la menor distancia del origen al destino?
- **Algoritmo.** Dijkstra.
- **Qué se ve.** Un paso en el que se confirma un vértice fuera de la ruta final. El relato explica que la búsqueda crece por distancia al origen: ese vértice estaba más cerca que el destino, se confirma antes y no queda en el camino. Al cierre, la ruta, la distancia y la unidad.

## 5. Qué se revisa

| Criterio | Qué se espera |
| --- | --- |
| Problema | Es uno de los diez. La pregunta cabe en una oración y el video la dice |
| Grafo | Propio, del tamaño pedido, distinto del ejemplo. La lista de adyacencia y el dibujo coinciden |
| Algoritmo | Responde la pregunta. Se ve avanzar, con la pila, la cola o los pendientes |
| Respuesta | Ruta y costo al cierre, en las unidades del enunciado, coherentes con los pesos dibujados |
| Comparación | Si el problema la pide, las dos respuestas se ven y se explica por qué difieren |
| Archivo | Un HTML. Abre con doble clic. Los controles siguen sirviendo |
| Video | De cuatro a seis minutos. Se oye la explicación y se ve el laboratorio en marcha |

La evaluación se rige por el **capítulo XII del Reglamento Estudiantil (RE)**.

---

## 6. Recordatorio

El canal del video se confirma en la clase del **18 de noviembre de 2026**. Ese día el `index.html` ya está cerrado: el video muestra ese archivo, no la plantilla del curso.
