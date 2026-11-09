# Studio UrsulaHR

Panel para editar reels 9:16 en el navegador (usar Google Chrome). Todo se procesa en el computador, no se sube ningún archivo.

- `index.html`, `app.js`: interfaz (lienzo, capas, línea de tiempo, exportación a MP4).
- `engine.js`: motor de render (se usa igual en la vista previa y al exportar).
- `projects/*.json`: plantillas de reels. `proceso.json` sale del guion "Cómo trabajo" de Notion.
- `fonts/`, `vendor/`, `assets/`: tipografías del manual de marca, librería de exportación (mediabunny) y logo.

Flujo: elegir plantilla, cargar la voz en "Voz / audio" (ofrece escalar los tiempos), arrastrar grabaciones sobre los mockups, ajustar títulos en el lienzo y exportar.
