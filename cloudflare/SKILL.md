---
name: publicar-web-cloudflare
description: Publica una web estática del workspace en Cloudflare Pages y guía al alumno durante el primer inicio de sesión. Usar cuando pidan desplegar, subir o publicar una página estática en Cloudflare, aunque no conozcan Wrangler, npm o npx.
---

# Publicar una web estática en Cloudflare

Completa el despliegue de principio a fin. El alumno no necesita conocer `npx`, `npm` ni Wrangler: ejecuta tú los comandos y explica solo las acciones que requieran su participación.

## Objetivo

Publicar los archivos estáticos en Cloudflare Pages y entregar:

1. La URL pública de producción.
2. La URL concreta del despliegue.
3. La confirmación de que la página principal y los recursos esenciales responden correctamente.

No publiques secretos, configuraciones locales, `node_modules`, `.git`, archivos `.env` ni documentos del profesor que no formen parte de la web.

## Flujo

### 1. Identificar lo que se debe publicar

Inspecciona el workspace antes de ejecutar comandos de despliegue.

- Si la raíz contiene `index.html`, publica esa raíz.
- Si existe una carpeta preparada, como `dist`, `build`, `public`, `out` o `site`, y contiene `index.html`, publícala en lugar de la raíz.
- Si el proyecto tiene `package.json`, revisa sus scripts y la documentación breve del proyecto.
- Si hay un script de compilación habitual (`build`), ejecútalo y publica la carpeta generada.
- Si no hay `index.html`, detente y explica qué falta. No inventes una estructura ni publiques el repositorio completo.

Antes de subir, comprueba:

- Que `index.html` existe en la raíz de la carpeta de salida.
- Que las rutas de CSS, JavaScript, imágenes, fuentes y SVG sean correctas.
- Que la carpeta no contenga secretos ni archivos de desarrollo innecesarios.
- Que los recursos referenciados con rutas relativas estén presentes.

Si hay dudas entre dos carpetas de salida, presenta al alumno las opciones de forma breve y pide que confirme cuál es su web.

### 2. Comprobar las herramientas

Ejecuta los comandos con el gestor de paquetes sin requerir una instalación global:

```bash
npx --yes wrangler --version
```

Si `npx` no existe, explica sin tecnicismos que falta Node.js. Para macOS puede usarse el instalador oficial de Node.js; después, abre una terminal nueva y vuelve a solicitar la publicación. No instales herramientas globales sin necesidad.

No pidas al alumno que escriba comandos si puedes ejecutarlos tú.

### 3. Iniciar sesión si hace falta

Comprueba primero la sesión:

```bash
npx --yes wrangler whoami
```

Si Cloudflare indica que no hay sesión iniciada:

1. Explica: "Cloudflare necesita confirmar tu identidad una vez. Se abrirá tu navegador; acepta la conexión y vuelve aquí."
2. Ejecuta:

   ```bash
   npx --yes wrangler login
   ```

3. Espera a que termine el proceso. No pidas contraseñas ni tokens al alumno.
4. Vuelve a ejecutar `npx --yes wrangler whoami` y confirma que la sesión está activa.

Si el navegador no se abre, usa la URL de autorización que muestre Wrangler y ejecuta el flujo normal de OAuth. Nunca solicites que copien aquí cookies, tokens, secretos o contraseñas.

### 4. Elegir el nombre del proyecto

Usa como base el nombre de la carpeta del proyecto, convertido a minúsculas, ASCII, guiones y sin espacios. Los nombres de Cloudflare Pages deben estar formados por minúsculas, números y guiones.

Antes de crear nada, lista los proyectos disponibles:

```bash
npx --yes wrangler pages project list
```

- Si no existe, crea un proyecto con ese nombre.
- Si existe y hay evidencia de que es el proyecto de esta web, úsalo para actualizarla.
- Si existe pero no puedes confirmarlo, muestra su dominio al alumno y pide confirmación antes de sobrescribirlo.
- Si el nombre está ocupado o resulta ambiguo, propone otro nombre corto y pide confirmación antes de publicarlo.

No publiques datos ni elimines proyectos preexistentes.

### 5. Crear y publicar

Crea el proyecto solo si no existe:

```bash
npx --yes wrangler pages project create NOMBRE-DEL-PROYECTO --production-branch main
```

Despliega exclusivamente la carpeta de salida:

```bash
npx --yes wrangler pages deploy CARPETA-DE-SALIDA \
  --project-name=NOMBRE-DEL-PROYECTO \
  --branch=main \
  --commit-dirty=true
```

Si `CARPETA-DE-SALIDA` contiene espacios, ponla entre comillas. No cambies ni borres los archivos del alumno para el despliegue.

### 6. Verificar el resultado

Obtén la URL mostrada por Wrangler. Comprueba también la URL estable:

```text
https://NOMBRE-DEL-PROYECTO.pages.dev/
```

Verifica con peticiones HTTP:

- La página principal devuelve una respuesta correcta.
- El HTML publicado está presente.
- Los recursos importantes mencionados por `index.html` cargan correctamente.
- No aparece una página vacía, un `404`, una pantalla de error ni un recurso principal roto.

Si algo falla:

1. Informa del problema con lenguaje claro.
2. Revisa rutas absolutas, mayúsculas, minúsculas y archivos omitidos.
3. Corrige solo los errores relacionados con la publicación.
4. Vuelve a desplegar y repite la comprobación.

No declares el despliegue terminado únicamente porque el comando haya finalizado.

### 7. Entregar el resultado

Responde de forma breve:

- **Web publicada:** URL estable.
- **Despliegue:** URL concreta de la versión, si Wrangler la devuelve.
- **Proyecto:** nombre utilizado.
- **Verificación:** página principal y recursos comprobados.
- Si fue necesario actualizar archivos, indica cuáles.

Incluye los enlaces como Markdown. No incluyas tokens, identificadores de cuenta ni datos de sesión.

## Repetición del despliegue

Para publicar cambios posteriores:

1. Vuelve a identificar y, si procede, construir la carpeta de salida.
2. Verifica la sesión.
3. Reutiliza el mismo nombre de proyecto.
4. Despliega y comprueba otra vez los recursos.

La experiencia deseada para el alumno es: pide “publica mi web en Cloudflare”, completa el inicio de sesión una sola vez en su navegador y recibe la URL final.
