# Volotea Destination Finder

**Enlace a la app:** [[https://...streamlit.app  ](https://v7quiz.streamlit.app/)](https://v7quiz.streamlit.app/)
**Autor/a:** Sara Fernández Carmona

## Pitch

Muchas personas que desean viajar en su tiempo libre recurren a buscadores de vuelos rígidos que exigen aeropuertos de origen concretos y fechas exactas, generando fatiga analítica antes de encontrar inspiración. Volotea Destination Finder resuelve esta barrera mediante un cuestionario interactivo de cuatro preguntas que conecta los deseos del viajero con el catálogo oficial de destinos de la aerolínea. La lógica determinista del sistema puntúa y filtra el catálogo local para sugerir hasta tres recomendaciones personalizadas, respaldadas por imágenes dinámicas de Wikimedia Commons. Tras probar la app, comprobé la importancia de gestionar fallos de red en las peticiones de imagen para que la interfaz nunca pierda estabilidad. Si continuara el proyecto, integraría un mapa interactivo de rutas basadas en los hubs principales de la compañía.

## El problema

Los viajeros que buscan inspiración para una escapada se enfrentan a portales masivos y formularios de aerolíneas que priorizan la logística técnica sobre los deseos del usuario. Tienen que cruzar manualmente sus preferencias de presupuesto, duración y clima con redes de rutas complejas sin saber qué lugares encajan mejor con su mood actual. Merece la pena resolverlo para transformar el descubrimiento de destinos en un proceso lúdico, rápido, visual y completamente alineado con la identidad de marca.

## Qué hace la app

1. **Cuestionario de inspiración:** Un formulario limpio y responsivo donde el usuario indica su ambiente de viaje preferido, el tiempo disponible, la temporada de viaje y su nivel de presupuesto.
2. **Motor de puntuación determinista:** Un algoritmo interno que cruza los datos con el catálogo local (`destinations.csv`) para puntuar y ordenar sin aleatoriedad las mejores opciones de viaje.
3. **Tarjetas de recomendación Volotea:** Presentación visual de hasta tres destinos con códigos IATA, regiones de islas filtradas, narrativas inspiradoras, razones personalizadas de coincidencia y llamadas a la acción comerciales.

## La pieza de IA / Motor de Lógica

- **Qué usa:** Un motor de reglas determinista y estructurado en Python, complementado con la API pública de Wikimedia Commons para la recuperación dinámica de imágenes sin necesidad de claves de API.
- **Por qué esa opción:** Permite un rendimiento inmediato sin latencia de red, garantizando cero costes operativos y total independencia de tokens o suscripciones de pago.
- **Qué pasa si falla:** Si la API de Wikimedia Commons experimenta un fallo o tiempo de espera, la app recupera la estabilidad del diseño mediante un bloque de excepciones que evita la ruptura del layout y muestra la información textual de forma limpia.

## Cómo la he construido

- **Herramientas:** Cursor, Google Colab y VS Code.
- **Fichero de contexto del agente:** [AGENTS.md](./AGENTS.md)
- **Prompts clave:**
  1. *Prompt de estructura inicial:* "Crea una aplicación en Streamlit basada en el catálogo de Volotea que actúe como un quiz de inspiración de viajes sin pedir aeropuertos de origen."
  2. *Prompt de diseño de marca:* "Aplica una hoja de estilos CSS personalizada utilizando estrictamente la paleta de colores corporativa de Volotea: rojo principal (#E10E49) y marrón corporativo (#452325) para títulos."
  3. *Prompt de robustez visual:* "Implementa una función de consulta a la API de Wikimedia Commons con reintentos de consultas limpias de acentos y un sistema de respaldo por si la imagen no está disponible."
- **Qué delegué al agente y qué revisé a mano:** Delegué la estructuración inicial de los componentes visuales de Streamlit y las consultas HTTP a Wikimedia. Revisé y ajusté a mano la lógica de puntuación determinista, los filtros estrictos para regiones de islas y la gestión de la paleta de colores corporativa.

## Prueba y mejora

| Quién la probó | Qué probó | Qué pasó | Qué cambié |
|---|---|---|---|
| Yo como usuaria | Pruebas de selección con filtros muy restrictivos (ej. presupuesto bajo y temporada de invierno en destinos de playa) | El sistema de puntuación no encontraba elementos con score $\ge 4$, mostrando un aviso en blanco o bloqueando la sección de resultados. | Añadí una validación explícita para mostrar un mensaje claro e instructivo invitando al usuario a relajar sus filtros en lugar de renderizar tarjetas vacías. |
| Yo como usuaria | Peticiones a Wikimedia con nombres de ciudades con caracteres especiales o tildes (ej. A Coruña) | La API devolvía listas vacías porque no reconocía los caracteres acentuados en las consultas de búsqueda (`gsrsearch`). | Implementé una función de normalización con `unicodedata` para eliminar acentos de forma segura antes de lanzar las queries de imagen. |

## Ejecutar en local (opcional)

```bash
pip install -r requirements.txt
streamlit run destination_v7.py
