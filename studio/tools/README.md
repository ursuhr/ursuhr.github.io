# Studio: cómo se arma un reel (guía para quien continúe el trabajo)

Studio es el editor de reels de Úrsula HR (`/studio`, `noindex`). Es 100 % navegador: Canvas 2D + mediabunny (WebCodecs) para exportar MP4. Un reel es una **plantilla JSON** en `studio/projects/` (capas con tiempos) que se carga desde Plantillas ▾. Cada plantilla se genera con un script Python (`studio/tools/make_*.py`, el de referencia más reciente es `make_millon.py`).

## Flujo de un reel
1. Escribir el guion y generar la voz con ElevenLabs (clon `nFvX1GqJpwVJYbJfWReM`). Medir las frases con `ffmpeg -af silencedetect=noise=-38dB:d=0.18` y anotar inicio y fin de cada frase.
2. Escribir el generador (copiar `make_millon.py`): constantes de color, helpers `L/title/pill/halo`, escenas con tiempos de la voz, subtítulos por cláusula (`capAlign='center'`), sonidos (`studio/assets/sfx`, `sfx.json`), música baja.
3. Probar con Playwright: `mf.js` saca fotogramas de la plantilla (`node mf.js '[1,2,3]' tag`), `sheet.py` arma una hoja de contacto, `regr.js` revisa que las 4 plantillas anteriores sigan renderizando. `export.js` exporta el MP4 con la voz (Chromium sin interfaz exporta audio Opus; la usuaria re-exporta en su Chrome del Mac para AAC).
4. Revisar el MP4 con ffprobe/ffmpeg: duración, silencios (pico dB en los huecos), fotogramas clave contra los del editor.
5. Rama propia → commit → PR a `main` → merge squash. La plantilla lleva `template` y `rev`: subir `rev` en cada cambio para que el panel ofrezca la versión nueva.

## Capas y propiedades útiles (engine.js)
- `text` (`*acento*`, `animIn: letters|rise|pop|fade|slide|draw|drop|blur`, `hitAt`, `move`/`scaleKf` con [[t,x,y]]), `shape` (halo, pill, rect, circle, arrow, sparkle, squiggle, key, padlock, line con `dash`, photo), `mockup` (browser/phone con `asset` o `wire`: old/new/panel/editor), `caption` (cápsula estable, `capAlign:'center'`), `sound`, `logo`, `chat`.
- `chat`: burbujas con `msgs` ([{from:'me'|'them', text, at, y, maxW, tag, out, hl, hlAt, dim}] o {kind:'wait'}), cámara interna `cam` [[t,zoom,cy,cx]], todo calculado desde el tiempo.
- Un mockup con `asset` asignado manda sobre el `wire` ilustrado (así se insertan grabaciones de pantalla reales).
- Tiempos en las capas: segundos. `animOut:'fade'` termina en `end`: un texto sale completo antes de que entre el siguiente.

## Reglas del proyecto
- Marca: marfil #F5F1E8, negro #0B0B0B, coral #FF6BA7, amarillo #FFD357, verde #34D399, azul cielo #6EC6FF. Archivo Black (títulos) y Lato (cuerpo). Un solo foco de color intenso por momento; halos tenues (opacity 0.3) y de un color.
- Sin cámara: contenido faceless. Reels alternan oscuro / claro.
- Voz: texto exacto del guion aprobado. Con `eleven_v4` las etiquetas de interpretación funcionan; `eleven_v3` y `multilingual_v2` se van a acento de España en textos largos. El acento chileno de la g y la j se arregla regrabando solo esas frases (Voice Changer) y pegándolas con numpy/ffmpeg.
- Honestidad: no redondear ni inventar datos, anonimizar clientes y desarrolladores, rotular lo recreado.
- No usar `git merge -X ours` si hay otra sesión trabajando: puede pisar cambios del editor. Cambiar `engine.js`/`app.js` solo si hace falta y correr `regr.js` antes.
- Audio de las voces: no se publica en el repositorio.
