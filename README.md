

    .------------------------------------------------------------------------------.
    |                             .mmMMMMMMMMMMMMMmm.                              |
    |                         .mMMMMMMMMMMMMMMMMMMMMMMMm.                          |
    |                      .mMMMMMMMMMMMMMMMMMMMMMMMMMMMMMm.                       |
    |                    .MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM.                     |
    |                  .MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM.                   |
    |                 MMMMMMMM'  `"MMMMM~~~~~~~MMMM""`  'MMMMMMMM                  |
    |                MMMMMMMMM                           MMMMMMMMM                 |
    |               MMMMMMMMMM:                         :MMMMMMMMMM                |
    |              .MMMMMMMMMM                           MMMMMMMMMM.               |
    |              MMMMMMMMM"                             "MMMMMMMMM               |
    |              MMMMMMMMM                               MMMMMMMMM               |
    |              MMMMMMMMM           REPWRITER           MMMMMMMMM               |
    |              MMMMMMMMMM                             MMMMMMMMMM               |
    |              `MMMMMMMMMM                           MMMMMMMMMM`               |
    |               MMMMMMMMMMMM.                     .MMMMMMMMMMMM                |
    |                MMMMMM  MMMMMMMMMM         MMMMMMMMMMMMMMMMMM                 |
    |                 MMMMMM  'MMMMMMM           MMMMMMMMMMMMMMMM                  |
    |                  `MMMMMM  "MMMMM           MMMMMMMMMMMMMM`                   |
    |                    `MMMMMm                 MMMMMMMMMMMM`                     |
    |                      `"MMMMMMMMM           MMMMMMMMM"`                       |
    |                         `"MMMMMM           MMMMMM"`                          |
    |                             `""M           M""`                              |
    '------------------------------------------------------------------------------'



**RepWritter** es una herramienta versátil escrita en Python diseñada para simplificar la creación, edición y publicación de documentación técnica, tutoriales y reportes directamente en GitHub. Ideal para desarrolladores, ingenieros, educadores y profesionales de diversas áreas, este script te permite estructurar contenido de manera profesional con soporte para títulos, imágenes, descripciones detalladas, archivos adjuntos y subida automática a un repositorio GitHub. Ya sea que estés documentando un proyecto de software, creando guías paso a paso o compartiendo análisis técnicos, RepWritter optimiza el proceso para que puedas enfocarte en el contenido.

## Características Principales

- **Interfaz de Menú Interactiva:** Fácil de usar con opciones numeradas y comandos de tecla única.
- **Soporte Multimedia:** Añade imágenes principales, imágenes en descripciones y archivos adicionales (PDFs, scripts, etc.).
- **Gestión de Contenido:** Edita cualquier sección en cualquier momento, desde títulos hasta archivos adjuntos.
- **Guardado Local:** Guarda el progreso en archivos `.json` para retomar writeups largos en sesiones posteriores.
- **Publicación en GitHub:** Sube automáticamente el writeup como `README.md` en una carpeta con el nombre del título, con imágenes en `img/` y archivos adjuntos en la raíz de la carpeta.
- **Personalización:** Incluye referencias con enlaces en las descripciones y un pie de página con redes sociales.

## Requisitos

- **Python 3.x**
- **Dependencias:**
  - `dotenv` (`pip install python-dotenv`)
  - `shutil`, `subprocess`, `readline` (incluidas en la biblioteca estándar de Python)
- **Git** instalado y configurado en tu sistema.
- **Token de GitHub** para autenticación (almacenado en `~/.Gitenv`).

## Instalación

1. Clona este repositorio o descarga el script:
    ```bash
   git clone https://github.com/imahian/repwritter.git
   cd repwritter
    ```

2. Instala las dependencias:
    ```bash 
    pip install python-dotenv
3. Configura tu token de GitHub:

    Ejecuta el script por primera vez; te pedirá el token si no existe ~/.Gitenv.
    O crea manualmente el archivo ~/.Gitenv con:

    GITHUB_TOKEN=tu_token_aqui

## Modo de uso

1. Iniciar el Script:
```bash
python repwritter.py
```
Verás un banner ASCII y el menú principal:

```bash
===========================
WRITEUP GENERATOR
===========================

Current Writeup:
[Contenido actual]

Options:
  1. Add Title
  2. Add Image
  3. Add Description with Subtitle, One-liner, and/or Image
  4. Add Flag
  5. Add File
  6. Edit Steps
  S. Save Current Writeup
  L. Load Writeup
  F. Finish and Generate Writeup
  Q. Quit without Saving

Select an option:
```

2. Opciones del Menú:

```
    1. Add Title: Define el título del writeup (será el nombre de la carpeta en GitHub).
    2. Add Image: Añade una imagen principal (se guardará en img/).
    3. Add Description...: Crea una sección con subtítulo, descripción multilínea, un one-liner opcional (en formato terminal) y una imagen opcional.
    4. Add Flag: Añade un flag con ofuscación automática (mitad visible, mitad asteriscos).
    5. Add File: Adjunta archivos adicionales (e.g., PDFs, scripts) que se subirán junto al README.md.
    6. Edit Steps: Edita cualquier elemento añadido (título, imágenes, descripciones, flags, archivos).
    S. Save Current Writeup: Guarda el progreso en ~/.repwritter/saved_writeups/<nombre>.json.
    L. Load Writeup: Carga un writeup guardado o desde un README.md existente en ~/writeups/.
    F. Finish and Generate Writeup: Genera el README.md localmente y súbelo a GitHub.
    Q. Quit without Saving: Sal sin guardar (con opción de guardar si hay cambios).
```


<div align="center">
<p>Thanks for reading! Follow me on my socials:</p>
<a href="https://x.com/@imahian"><img src="https://www.vectorlogo.zone/logos/x/x-icon.svg" alt="X" width="40">
</a> <a href="https://discord.gg/grwQeYk7"><img src="https://www.vectorlogo.zone/logos/discord/discord-icon.svg" alt="Discord" width="40"></a>
<a href="https://youtube.com/@imahian"><img src="https://www.vectorlogo.zone/logos/youtube/youtube-icon.svg" alt="YouTube" width="40"></a>
<a href="https://twitch.tv/imahian"><img src="https://www.vectorlogo.zone/logos/twitch/twitch-icon.svg" alt="Twitch" width="40"></a>
</div>
