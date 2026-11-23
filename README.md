# RADAR MX V03 — alimentación automática

Se conserva el diseño V02 y se sustituye el catálogo ficticio por `data/events.json`, generado automáticamente.

## Para activar datos reales

1. Solicita una clave para **Ticketmaster Discovery API** (consulta sus términos, cuotas y permisos de uso).
2. Sube esta carpeta a un repositorio GitHub de tu propiedad.
3. En GitHub → Settings → Secrets and variables → Actions → New repository secret, crea `TICKETMASTER_API_KEY` y pega la clave. **Nunca la incluyas en HTML, JavaScript ni en el repositorio.**
4. En GitHub → Actions, habilita workflows y ejecuta **Actualizar eventos CDMX** → Run workflow para probar. El proceso se programó para una ejecución diaria a las 06:15 hora de CDMX; GitHub puede retrasar tareas programadas.
5. Habilita GitHub Pages desde la rama que contiene `index.html` en la raíz. Comprueba que se publica `data/events.json`.

Sin clave, el proceso **falla sin sobrescribir datos**. No hay eventos inventados en la web. La sección Promos permanecerá vacía hasta integrar una fuente de descuentos con términos y vigencia verificables.

## Probar localmente

En la carpeta del proyecto ejecuta `python -m http.server 8000` y visita `http://localhost:8000`. Abrir `index.html` con `file://` puede bloquear `fetch` del JSON.

## Alcance y límites

- Primera fuente preparada: Ticketmaster Discovery API; no se afirma acceso activo hasta que proporciones la clave.
- Filtra eventos cercanos a CDMX y excluye fechas pasadas, pero los límites geográficos son aproximados.
- Muestra precios mínimos solo cuando la API los proporciona en MXN; no garantiza disponibilidad ni precio final con cargos.
- Las imágenes y descripciones provienen de la API; revisa permisos de uso y atribución antes de publicar.
- GitHub Pages no ejecuta Python: GitHub Actions genera y guarda el JSON en el repositorio.
- No requiere cuentas, base de datos, ni claves públicas en el navegador.
- Para una sección Promos automática real se necesita una fuente específica de promociones verificables; no se infieren descuentos a partir de precios.
