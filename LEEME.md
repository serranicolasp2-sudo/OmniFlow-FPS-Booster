# OmniFlow FPS Booster — Acelerador e Interpolador de Fotogramas HFR (Universal)

> **Multiplicador de fluidez cinematográfica y generación de fotogramas intermedios de alta tasa.**  
> Desarrollado con el diseño visual oficial de **Tu Tiendita IA** (Sitio web oficial: [tutiendita-ia.store](https://tutiendita-ia.store)).

---

## 🎨 Identidad Visual y Diseño de Marca: "Tu Tiendita IA"

La interfaz gráfica de **OmniFlow FPS Booster** sigue las especificaciones de diseño oficiales de la suite creativa de **Tu Tiendita IA** ([tutiendita-ia.store](https://tutiendita-ia.store)).

Implementa el sistema estético **"Noche Tinta Studio"**:
- **Azul Birome (`#1E3C96` / `#2A4FC0`)**: Acciones primarias y botones interactivos.
- **Azul Tinta Profundo (`#16205A` / `#0A1024`)**: Fondo inmersivo y paneles de control.
- **Rosa Malvón (`#E0435C`)**: Badges de alerta, acentos de estado y botones de detención.
- **Amarillo Yema (`#FFD23F`)**: Barra de progreso de interpolación y notificaciones de completado.
- **Tipografía Fluent Segoe UI**: Legibilidad clara, indicadores de tiempo y métricas en vivo.

---

## 📖 Descripción General

¿Alguna vez notaste que tus videos de 24 o 30 cuadros por segundo se ven con tirones ("judder"), especialmente en paneos de cámara o escenas de acción rápida?

**OmniFlow FPS Booster** es una herramienta especializada en **interpolación temporal de fotogramas**. Implementa motores inteligentes de mezcla adaptativa con corte de escenas (*scene-cut detection*) y estimación de movimiento vectorial para sintetizar fotogramas intermedios de forma veloz, estable y sin los molestos artefactos de distorsión plástica (*warping*) típicos de los algoritmos lentos.

El resultado es un video con una fluidez sedosa a **60 FPS** o **120 FPS**, ideal para:
- Videos generados con herramientas de IA (Runway, Kling, Luma, Pika, Sora) que suelen renderizarse a 24 o 25 fps.
- Secuencias de animación 3D y videojuegos.
- Animación 2D tradicional y anime.
- Tomas de cámaras reales, entrevistas y vlogs.
- Creación de tomas en cámara lenta extrema (*slow-motion*) a 120 FPS.

Todo funciona de forma **100% offline y local en tu equipo**, sin límites de archivos ni suscripciones a servicios en la nube.

---

## ⚡ Características Principales y Algoritmos

### 1. Métodos de Interpolación Adaptativos
- **Universal Adaptativo (Cine, Video Real, 3D — Recomendado)**: Mezcla temporal adaptativa basada en `framerate` con detección inteligente de cortes de plano (umbral de cambio de escena al 8.2%). Es la opción predilecta por su altísima velocidad, estabilidad y ausencia total de deformaciones ("efecto gelatina").
- **Anime & Animación 2D (Cortes limpios y anti-morphing)**: Diseñado para animación tradicional en "2s" o "3s". Aplica un umbral de corte de escena al 5.0% y rango de mezcla estricto para preservar las líneas de entintado sin mezclar fotogramas entre planos distintos.
- **Motion Blend / Shutter Suave (Elimina tirones en paneos)**: Aplica una fusión temporal continua (`minterpolate` en modo `blend`) que emula el ángulo de obturación cinematográfico (*shutter angle*), suavizando paneos rápidos de cámara.
- **Cadencia Pura / Pulldown Exacto**: Duplica y distribuye los fotogramas de forma matemáticamente exacta (`fps`) sin alterar un solo píxel del cuadro original.
- **Estimación de Movimiento Vectorial (MCI / Flujo Óptico — Lento)**: Algoritmo avanzado de estimación de vectores de movimiento bidireccionales por bloques cruzados (`minterpolate` en modo `mci:bidir`). Reconstruye la trayectoria espacial de cada bloque entre cuadros (mayor demanda de tiempo de render).

### 2. Tasas de Fotogramas Destino
- **60 FPS (Estándar recomendado — Ultra suave)**: El estándar universal para YouTube, Instagram Reels, TikTok y televisores modernos. Multiplica por 2 o por 2.5 la fluidez sin aumentar desmedidamente el peso del archivo.
- **120 FPS (Ultra HFR / Slow-motion extremo)**: Fluidez absoluta para pantallas de 120 Hz / 144 Hz o para reproducir el clip a velocidad reducida en tu editor de video (cámara lenta de calidad cinematográfica).
- **50 FPS**: Estándar para transmisiones televisivas PAL / broadcast europeo.
- **48 FPS (Doble cine HFR)**: La frecuencia exacta utilizada en grandes producciones cinematográficas HFR (como *El Hobbit* o *Avatar*).

### 3. Ajuste de Calidad CRF (Constant Rate Factor)
- **CRF 16 — Master (Sin pérdida perceptible)**: Máxima fidelidad visual, recomendado para archivar másters o para reutilizar en edición profesional.
- **CRF 18 — Balance óptimo de producción**: La mejor relación entre calidad impecable y tamaño de archivo moderado.
- **CRF 20 — Archivo ligero**: Genera archivos compactos ideales para compartir por mensajería o redes sociales.

### 4. Soporte Total de Orientaciones y Formatos
OmniFlow detecta automáticamente la geometría del video:
- Horizontal tradicional (`16:9`, `21:9`).
- Vertical móvil (`9:16` para TikTok, Reels y Shorts).
- Formato cuadrado (`1:1` para feeds de Instagram).  
No recorta, no agrega barras negras forzadas y no distorsiona el aspecto original.

### 5. Aceleración por Placa de Video
- **NVIDIA GeForce RTX (NVENC p7 + Spatial/Temporal AQ)**: Render ultrarrápido aprovechando los chips NVENC de arquitectura Turing, Ampere y Ada Lovelace.
- **NVIDIA GeForce RTX HEVC / H.265**: Calidad superior con menor ancho de banda.
- **AMD Radeon AMF Hardware**: Compatible con tarjetas gráficas AMD Radeon RX.
- **CPU / Software Universal (libx264)**: Máxima compatibilidad para cualquier procesador moderno.

---

## 🚀 Guía de Uso Paso a Paso

### Modo Video Individual
1. Ejecutá **OmniFlow FPS Booster**.
2. En la pestaña **"Archivo Único"**, hacé clic en **"Examinar..."** y seleccioná el video a procesar. La aplicación te mostrará de inmediato los FPS originales y la resolución.
3. En **"Tasa de Fotogramas Destino"**, seleccioná **60 FPS** (o 120 FPS si deseás alta tasa de refresco).
4. En **"Tipo de Contenido / Método"**, dejá *Universal Adaptativo* (o seleccioná *Anime 2D* si es animación tradicional).
5. Seleccioná la calidad CRF deseada (por defecto CRF 18).
6. Elegí tu acelerador por GPU o CPU.
7. Presioná el botón **"Elevar FPS"**.
8. Observá el progreso en tiempo real. Cuando termine, el video se guardará automáticamente en la subcarpeta `Videos_60fps/` (o `Videos_120fps/`) con el sufijo `_60fps` o `_120fps` en contenedor `.mp4` con audio sincronizado intacto.

### Modo Procesamiento por Lote (Carpeta Completa)
1. Pasá a la pestaña **"Carpeta Completa / Lote"**.
2. Seleccioná la carpeta que contiene tus videos.
3. Marcá o desmarcá la opción de incluir subcarpetas.
4. Presioná **"Procesar Carpeta"**. La herramienta procesará ordenadamente toda la cola de videos.

---

## 📁 Formatos Admitidos

- **Entrada**: `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`, `.flv`, `.ts`, `.m4v`, `.mpg`, `.mpeg`, `.wmv`.
- **Salida**: Contenedor `.mp4` optimizado (H.264 o H.265 / HEVC) o formato de origen compatible, con pista de audio copiada intacta (`-c:a copy`) garantizando sincronización labial absoluta.

---

## 📦 Variantes de Instalación

1. **Instalador Oficial (`OmniFlow FPS Booster Instalador 1.0.exe`)**:
   - Asistente de instalación estándar en Windows.
   - Crea iconos en el Escritorio y Menú Inicio.
   - Lanzador nativo `.exe` silencioso.
2. **Versión Portable (`OmniFlow FPS Booster Portable.zip`)**:
   - Descomprimí y ejecutá directamente `OmniFlow FPS Booster.exe`.
   - Listo para usar desde un pendrive o unidad externa sin instalar librerías adicionales.

---

## 💻 Requisitos del Sistema

- **Sistema Operativo**: Windows 10 u 11 (64 bits).
- **Procesador**: 4 núcleos o más (Intel i5/i7 o AMD Ryzen 5/7 recomendado para interpolación por software).
- **Memoria RAM**: 8 GB mínimo (16 GB recomendado para 4K a 60/120 fps).
- **GPU Recomendada**: NVIDIA GeForce GTX 1660 / RTX 2060 / 3060 / 4060 o AMD Radeon RX 6600 o superior.

---

*Desarrollado para la suite creativa de **Tu Tiendita IA** · [https://tutiendita-ia.store](https://tutiendita-ia.store)*
