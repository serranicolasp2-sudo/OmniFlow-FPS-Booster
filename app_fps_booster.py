"""
OmniFlow FPS Booster — Acelerador e Interpolador de Fotogramas HFR (Universal)
Diseño: Premium Minimalista "Tu Tiendita IA"
Colores oficiales de marca: Birome (#1E3C96), Tinta (#16205A), Malvón (#E0435C),
Yema (#FFD23F), Cinta (#1A1712), Papel (#F6F7FA), Plata (#8B97B0)
Bordes redondeados, estética editorial de alta gama.
"""

import os
import sys
import subprocess
import threading
import queue
import re
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.scrolledtext as scrolledtext

# Asegurar acceso a Herramientas para importar ui_theme
CURRENT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = CURRENT_DIR.parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

# Asegurar ffmpeg/ffprobe en PATH para funcionamiento 100% offline y portable
_bundle_dir = Path(getattr(sys, "_MEIPASS", CURRENT_DIR))
for _cand in [_bundle_dir, _bundle_dir / "bin", Path(sys.executable).parent / "bin", Path(sys.executable).parent]:
    if (_cand / "ffmpeg.exe").exists():
        os.environ["PATH"] = str(_cand) + os.pathsep + os.environ.get("PATH", "")
        break

from ui_theme import (
    COLOR_BIROME, COLOR_BIROME_HOVER, COLOR_TINTA, COLOR_MALVON, COLOR_MALVON_HOVER,
    COLOR_YEMA, COLOR_CINTA, COLOR_PAPEL, COLOR_PLATA, COLOR_PERIWINKLE,
    BG_APP, BG_CARD, CHIP_BG, CHIP_BORDER, BG_CARD_BORDER, BG_INPUT, BG_INPUT_BORDER, BG_CONSOLE, BG_CONSOLE_BORDER,
    TEXT_MAIN, TEXT_MUTED, TEXT_DIM,
    FONT_HERO, FONT_TITLE, FONT_SUB, FONT_LABEL, FONT_BODY, FONT_MONO, FONT_BTN, FONT_BADGE,
    setup_app_theme, PillBadge, PillButton, RoundedCard, SegmentedSwitch, create_header, prompt_rename_dialog,
    ModernSlider, ConsoleText
)


class FPSBoosterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OmniFlow FPS Booster — Acelerador de Fotogramas Universal")
        self.root.geometry("860x830")
        self.root.minsize(760, 700)
        self.root.configure(bg=BG_APP)

        self.process = None
        self.is_running = False
        self.cancel_requested = False
        self.msg_queue = queue.Queue()
        self.last_output_dir = ""
        self.current_tab_idx = 0

        setup_app_theme(self.root, app_icon="omniflow")
        self._build_ui()
        self.root.after(100, self._process_queue)

    def _build_ui(self):
        # 1. Encabezado con insignias oficiales
        create_header(
            self.root,
            title="OmniFlow FPS Booster",
            subtitle="Interpolación de fotogramas HFR a 48, 50, 60 y 120 FPS sin artefactos ni tirones.",
            badge_text="IA",
            rtx_text="RTX P7 ACTIVE",
            icon="omniflow"
        )

        # 2. Selector segmentado de modo (Pills modernas)
        switch_frame = tk.Frame(self.root, bg=BG_APP)
        switch_frame.pack(fill="x", padx=22, pady=(2, 6))

        self.segmented_switch = SegmentedSwitch(
            switch_frame,
            options=["  🎬 Video Individual  ", "  📁 Carpeta en Lote  "],
            on_change=self._on_switch_tab
        )
        self.segmented_switch.pack(anchor="w")

        # 3. Contenedor de origen/destino (Tarjeta redondeada)
        self.card_io = RoundedCard(self.root, radius=14, pad=16, auto_height=True)
        self.card_io.pack(fill="x", padx=22, pady=4)

        self.io_single_frame = tk.Frame(self.card_io.body, bg=BG_CARD)
        self.io_batch_frame = tk.Frame(self.card_io.body, bg=BG_CARD)

        self._build_single_io_content()
        self._build_batch_io_content()
        self.io_single_frame.pack(fill="x")

        # 4. Tarjeta de Parámetros (Tarjeta redondeada)
        self.card_opts = RoundedCard(self.root, radius=14, pad=16, auto_height=True)
        self.card_opts.pack(fill="x", padx=22, pady=4)
        self._build_options_content()

        # 5. Panel de Control y Progreso (Inferior)
        self._build_progress_card()

    def _on_switch_tab(self, idx):
        self.current_tab_idx = idx
        if idx == 0:
            self.io_batch_frame.pack_forget()
            self.io_single_frame.pack(fill="x")
        else:
            self.io_single_frame.pack_forget()
            self.io_batch_frame.pack(fill="x")

    def _build_single_io_content(self):
        f = self.io_single_frame

        tk.Label(f, text="Selecciona el video (.mp4, .mov, .mkv, etc.) que deseas interpolar:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(0, 4))

        in_row = tk.Frame(f, bg=BG_CARD)
        in_row.pack(fill="x", pady=(0, 6))

        in_well = tk.Frame(in_row, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        in_well.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.single_input_var = tk.StringVar()
        self.single_input_entry = tk.Entry(in_well, textvariable=self.single_input_var, bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief="flat", font=FONT_BODY)
        self.single_input_entry.pack(fill="x", ipady=6, padx=8)

        btn_browse = PillButton(in_row, text="Examinar...", style="secondary", width=120, command=self._browse_single_input)
        btn_browse.pack(side="right")

        self.single_info_var = tk.StringVar(value="Esperando selección de video...")
        lbl_info = tk.Label(f, textvariable=self.single_info_var, bg=BG_CARD, fg=COLOR_PERIWINKLE, font=FONT_SUB)
        lbl_info.pack(anchor="w", pady=(0, 6))

        tk.Label(f, text="Archivo de destino generado:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(2, 4))

        out_row = tk.Frame(f, bg=BG_CARD)
        out_row.pack(fill="x")

        out_well = tk.Frame(out_row, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        out_well.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.single_out_var = tk.StringVar()
        self.single_out_entry = tk.Entry(out_well, textvariable=self.single_out_var, bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief="flat", font=FONT_BODY)
        self.single_out_entry.pack(fill="x", ipady=6, padx=8)

        btn_browse_out = PillButton(out_row, text="Guardar en...", style="secondary", width=120, command=self._browse_single_output)
        btn_browse_out.pack(side="right")

    def _build_batch_io_content(self):
        f = self.io_batch_frame

        tk.Label(f, text="Carpeta de origen con los videos a convertir:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(0, 4))

        in_row = tk.Frame(f, bg=BG_CARD)
        in_row.pack(fill="x", pady=(0, 6))

        in_well = tk.Frame(in_row, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        in_well.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.batch_input_var = tk.StringVar()
        self.batch_input_entry = tk.Entry(in_well, textvariable=self.batch_input_var, bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief="flat", font=FONT_BODY)
        self.batch_input_entry.pack(fill="x", ipady=6, padx=8)

        btn_browse = PillButton(in_row, text="Elegir Carpeta...", style="secondary", width=130, command=self._browse_batch_input)
        btn_browse.pack(side="right")

        tk.Label(f, text="Carpeta de salida:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).pack(anchor="w", pady=(2, 4))

        out_row = tk.Frame(f, bg=BG_CARD)
        out_row.pack(fill="x", pady=(0, 6))

        out_well = tk.Frame(out_row, bg=BG_INPUT, highlightbackground=BG_INPUT_BORDER, highlightthickness=1)
        out_well.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.batch_out_var = tk.StringVar()
        self.batch_out_entry = tk.Entry(out_well, textvariable=self.batch_out_var, bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, relief="flat", font=FONT_BODY)
        self.batch_out_entry.pack(fill="x", ipady=6, padx=8)

        btn_browse_out = PillButton(out_row, text="Guardar en...", style="secondary", width=130, command=self._browse_batch_output)
        btn_browse_out.pack(side="right")

        self.batch_recursive_var = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(f, text="Buscar recursivamente en subcarpetas", variable=self.batch_recursive_var, style="TCheckbutton")
        chk.pack(anchor="w", pady=(2, 0))

    def _build_options_content(self):
        opts = self.card_opts.body
        opts.grid_columnconfigure(1, weight=1)

        top_bar = tk.Frame(opts, bg=BG_CARD)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        tk.Label(top_bar, text="Parámetros de Interpolación y Cadencia", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(side="left")
        PillBadge(top_bar, text="HFR", bg_color=CHIP_BG, fg_color=COLOR_PERIWINKLE, border_color=CHIP_BORDER).pack(side="left", padx=8)

        # Tasa de cuadros destino
        tk.Label(opts, text="Tasa de Fotogramas Destino:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=4)
        self.fps_target_var = tk.StringVar(value="60 FPS (Estándar recomendado — Ultra suave)")
        self.fps_cb = ttk.Combobox(opts, textvariable=self.fps_target_var, state="readonly", width=52)
        self.fps_cb['values'] = (
            "60 FPS (Estándar recomendado — Ultra suave)",
            "120 FPS (Ultra HFR / Slow-motion extremo)",
            "50 FPS (Estándar PAL broadcast)",
            "48 FPS (Doble cine HFR)"
        )
        self.fps_cb.grid(row=1, column=1, sticky="ew", pady=4)
        self.fps_cb.bind("<<ComboboxSelected>>", self._on_fps_change)

        # Algoritmo de interpolación
        tk.Label(opts, text="Tipo de Contenido / Método:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=4)
        self.method_var = tk.StringVar(value="Universal Adaptativo (Cine, Video Real, 3D — Recomendado)")
        method_cb = ttk.Combobox(opts, textvariable=self.method_var, state="readonly", width=52)
        method_cb['values'] = (
            "Universal Adaptativo (Cine, Video Real, 3D — Recomendado)",
            "Anime & Animación 2D (Cortes limpios y anti-morphing)",
            "Motion Blend / Shutter Suave (Elimina tirones y judder en paneos)",
            "Cadencia Pura / Pulldown Exacto (Duplicación matemática sin modificar imagen)"
        )
        method_cb.grid(row=2, column=1, sticky="ew", pady=4)

        # Calidad CRF
        tk.Label(opts, text="Calidad de Exportación:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).grid(row=3, column=0, sticky="w", padx=(0, 10), pady=4)
        self.crf_var = tk.StringVar(value="CRF 16 — Master (Sin pérdida perceptible)")
        crf_cb = ttk.Combobox(opts, textvariable=self.crf_var, state="readonly", width=52)
        crf_cb['values'] = (
            "CRF 16 — Master (Sin pérdida perceptible)",
            "CRF 18 — Balance óptimo de producción",
            "CRF 20 — Archivo ligero"
        )
        crf_cb.grid(row=3, column=1, sticky="ew", pady=4)

        # Aceleración GPU / Motor RTX
        tk.Label(opts, text="Aceleración GPU / Motor:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_LABEL).grid(row=4, column=0, sticky="w", padx=(0, 10), pady=4)
        self.hw_var = tk.StringVar(value="NVIDIA GeForce RTX (NVENC p7 + Spatial/Temporal AQ)")
        self.hw_cb = ttk.Combobox(opts, textvariable=self.hw_var, state="readonly", width=52)
        self.hw_cb['values'] = (
            "NVIDIA GeForce RTX (NVENC p7 + Spatial/Temporal AQ)",
            "NVIDIA GeForce RTX — HEVC / H.265 (Ultra Calidad 4K)",
            "AMD Radeon — AMF Hardware (RX 6000 / 7000 Series)",
            "CPU / Software Universal (libx264 — Máxima compatibilidad)"
        )
        self.hw_cb.grid(row=4, column=1, sticky="ew", pady=4)

    def _build_progress_card(self):
        bot = tk.Frame(self.root, bg=BG_APP, padx=22, pady=4)
        bot.pack(fill="both", expand=True)

        btn_box = tk.Frame(bot, bg=BG_APP)
        btn_box.pack(fill="x", pady=(0, 8))

        self.btn_start = PillButton(btn_box, text="INICIAR GENERACIÓN A 60 FPS", style="primary", height=42, command=self._start_processing)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_cancel = PillButton(btn_box, text="Cancelar", style="danger", height=42, width=105, command=self._cancel)
        self.btn_cancel.configure_state("disabled")
        self.btn_cancel.pack(side="left", padx=(0, 8))

        self.btn_open_folder = PillButton(btn_box, text="Abrir Carpeta Destino", style="secondary", height=42, command=self._open_output_dir)
        self.btn_open_folder.pack(side="right")

        # Barra y Estado
        status_box = tk.Frame(bot, bg=BG_APP)
        status_box.pack(fill="x", pady=(2, 4))

        self.status_var = tk.StringVar(value="Listo para iniciar.")
        self.lbl_status = tk.Label(status_box, textvariable=self.status_var, bg=BG_APP, fg=TEXT_MAIN, font=FONT_LABEL)
        self.lbl_status.pack(side="left")

        self.prog_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(bot, variable=self.prog_var, maximum=100, style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", pady=(0, 8))

        # Consola de registro con borde redondeado
        self.card_log = RoundedCard(bot, bg_app=BG_APP, card_bg=BG_CONSOLE, border_color=BG_CONSOLE_BORDER, radius=10, pad=10, auto_height=False)
        self.card_log.pack(fill="both", expand=True)

        self.log_area = ConsoleText(self.card_log.body, bg=BG_CONSOLE, fg="#A5B4CD", insertbackground=TEXT_MAIN, relief="flat", font=FONT_MONO)
        self.log_area.pack(fill="both", expand=True)
        self.log_area.insert(tk.END, "OmniFlow FPS Booster iniciado con el tema visual oficial de Tu Tiendita IA (sitio web: tutiendita-ia.store).\nElige un clip o lote para elevar su fluidez a 48, 50, 60 o 120 FPS.\n")
        self.log_area.configure(state="disabled")

    def _browse_single_input(self):
        f = filedialog.askopenfilename(
            title="Seleccionar Video",
            filetypes=[("Archivos de Video", "*.mp4;*.mov;*.mkv;*.avi;*.webm"), ("Todos los archivos", "*.*")]
        )
        if f:
            self.single_input_var.set(os.path.normpath(f))
            p = Path(f)
            target_fps = self._get_target_fps()
            out_name = f"{p.stem}_{target_fps}fps{p.suffix}"
            out_path = p.parent / f"Videos_{target_fps}fps" / out_name
            self.single_out_var.set(os.path.normpath(str(out_path)))

            info = self._probe_video(f)
            if info:
                w, h = info.get('width', 0), info.get('height', 0)
                try:
                    w_int, h_int = int(w), int(h)
                    orient = "Vertical 9:16" if h_int > w_int else ("Cuadrado 1:1" if w_int == h_int else "Horizontal 16:9")
                except Exception:
                    orient = "Video"
                self.single_info_var.set(f"Video: {w}x{h} ({orient}) | {info['fps']} fps originales | {info['duration']}s")
            else:
                self.single_info_var.set("Archivo de video seleccionado.")

    def _browse_single_output(self):
        f = filedialog.asksaveasfilename(
            title="Guardar video como",
            defaultextension=".mp4",
            filetypes=[("Video MP4", "*.mp4"), ("Todos los archivos", "*.*")]
        )
        if f:
            self.single_out_var.set(os.path.normpath(f))

    def _browse_batch_input(self):
        d = filedialog.askdirectory(title="Seleccionar Carpeta con Videos")
        if d:
            target_fps = self._get_target_fps()
            self.batch_input_var.set(os.path.normpath(d))
            self.batch_out_var.set(os.path.normpath(os.path.join(d, f"Videos_{target_fps}fps")))

    def _on_fps_change(self, event=None):
        target_fps = self._get_target_fps()
        self.btn_start.configure_text(f"INICIAR GENERACIÓN A {target_fps} FPS")

        inp = self.single_input_var.get().strip()
        if inp:
            p = Path(inp)
            out_name = f"{p.stem}_{target_fps}fps{p.suffix}"
            out_path = p.parent / f"Videos_{target_fps}fps" / out_name
            self.single_out_var.set(os.path.normpath(str(out_path)))

        batch_in = self.batch_input_var.get().strip()
        if batch_in:
            self.batch_out_var.set(os.path.normpath(os.path.join(batch_in, f"Videos_{target_fps}fps")))

    def _browse_batch_output(self):
        d = filedialog.askdirectory(title="Seleccionar Carpeta Destino")
        if d:
            self.batch_out_var.set(os.path.normpath(d))

    def _open_output_dir(self):
        target = self.last_output_dir
        if not target or not os.path.exists(target):
            if self.current_tab_idx == 0:
                p = self.single_out_var.get().strip()
                target = os.path.dirname(p) if p else ""
            else:
                target = self.batch_out_var.get().strip()

        if target and os.path.exists(target):
            os.startfile(target)
        else:
            messagebox.showinfo("Aviso", "Aún no se ha generado una carpeta de destino válida.")

    def _log(self, text):
        self.msg_queue.put(("log", text))

    def _set_status(self, text, progress=None):
        self.msg_queue.put(("status", (text, progress)))

    def _process_queue(self):
        try:
            while True:
                msg_type, data = self.msg_queue.get_nowait()
                if msg_type == "log":
                    self.log_area.configure(state="normal")
                    self.log_area.insert(tk.END, data + "\n")
                    self.log_area.see(tk.END)
                    self.log_area.configure(state="disabled")
                elif msg_type == "status":
                    txt, prog = data
                    self.status_var.set(txt)
                    if prog is not None:
                        self.prog_var.set(prog)
                elif msg_type == "finished":
                    self._on_finished(data)
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(100, self._process_queue)

    def _probe_video(self, file_path):
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,duration",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1",
                file_path
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            lines = res.stdout.strip().splitlines()
            data = {}
            for l in lines:
                if "=" in l:
                    k, v = l.split("=", 1)
                    data[k] = v

            width = data.get("width", "?")
            height = data.get("height", "?")
            r_fps = data.get("r_frame_rate", "24/1")
            if "/" in r_fps:
                num, den = r_fps.split("/")
                fps_val = round(float(num) / float(den), 2)
            else:
                fps_val = round(float(r_fps), 2)

            duration = round(float(data.get("duration", 0)), 2)
            return {"width": width, "height": height, "fps": fps_val, "duration": duration}
        except Exception:
            return None

    def _get_target_fps(self):
        v = self.fps_target_var.get()
        if "120" in v:
            return 120
        elif "50" in v:
            return 50
        elif "48" in v:
            return 48
        return 60

    def _build_vf_filter(self, target_fps, method_str):
        if "Anime" in method_str:
            return f"framerate=fps={target_fps}:interp_start=5:interp_end=250:scene=5.0"
        elif "Motion Blend" in method_str:
            return f"minterpolate=fps={target_fps}:mi_mode=blend"
        elif "Cadencia Pura" in method_str:
            return f"fps={target_fps}"
        else:
            return f"framerate=fps={target_fps}:interp_start=15:interp_end=240:scene=8.2"

    def _start_processing(self):
        if self.is_running:
            return

        target_fps = self._get_target_fps()
        folder = f"Videos_{target_fps}fps"

        is_single = (self.current_tab_idx == 0)

        if is_single:
            inp = self.single_input_var.get().strip()
            out = self.single_out_var.get().strip()
            if not inp or not os.path.exists(inp):
                messagebox.showerror("Error", "Selecciona un video de entrada válido.")
                return
            p = Path(inp)
            default_name = Path(out).name if out else f"{p.stem}_{target_fps}fps{p.suffix}"
            out_folder = Path(out).parent if out else (p.parent / folder)

            chosen_name = prompt_rename_dialog(
                self.root,
                title="Confirmar / Renombrar Salida",
                prompt=f"¿Qué nombre deseas asignarle al video a {target_fps} FPS?",
                default_val=default_name,
                subtext=f"Origen: {p.name}  |  Carpeta destino: {out_folder}"
            )
            if not chosen_name:
                return

            if not os.path.splitext(chosen_name)[1]:
                chosen_name += p.suffix

            out = str(out_folder / chosen_name)
            self.single_out_var.set(out)
            targets = [(inp, out)]
            self.last_output_dir = str(out_folder)
        else:
            in_dir = self.batch_input_var.get().strip()
            out_dir = self.batch_out_var.get().strip()
            if not in_dir or not os.path.exists(in_dir):
                messagebox.showerror("Error", "Selecciona una carpeta de origen válida.")
                return
            if not out_dir:
                out_dir = os.path.join(in_dir, folder)
                self.batch_out_var.set(out_dir)

            self.last_output_dir = out_dir
            raw_targets = self._find_batch_videos(in_dir, out_dir, self.batch_recursive_var.get(), target_fps)
            if not raw_targets:
                messagebox.showwarning("Atención", "No se encontraron videos compatibles (.mp4, .mov, etc.) en la carpeta.")
                return

            sample_file = Path(raw_targets[0][0])
            chosen_suffix = prompt_rename_dialog(
                self.root,
                title=f"Asignar Sufijo ({target_fps} FPS)",
                prompt=f"Se procesarán {len(raw_targets)} videos.\n¿Qué sufijo deseas agregar al nombre de los videos procesados?",
                default_val=f"_{target_fps}fps",
                subtext=f"Ejemplo: '{sample_file.name}' -> '{sample_file.stem}_{target_fps}fps{sample_file.suffix}'"
            )
            if chosen_suffix is None:
                return

            targets = []
            for src, dst in raw_targets:
                p_src = Path(src)
                d_dst = Path(dst).parent
                new_fname = f"{p_src.stem}{chosen_suffix}{p_src.suffix}"
                targets.append((src, str(d_dst / new_fname)))

        method_str = self.method_var.get()
        crf_str = self.crf_var.get()
        crf_val = "16" if "16" in crf_str else ("18" if "18" in crf_str else "20")

        self.is_running = True
        self.cancel_requested = False
        self.btn_start.configure_state("disabled")
        self.btn_cancel.configure_state("normal")
        self.prog_var.set(0)

        self._log(f"\n🚀 Iniciando interpolación: {len(targets)} video(s) -> {target_fps} FPS")
        self._log(f"Método: {method_str} | CRF {crf_val}")
        self._log(f"Acelerador: {self.hw_var.get()}")

        t = threading.Thread(target=self._worker_thread, args=(targets, target_fps, method_str, crf_val), daemon=True)
        t.start()

    def _find_batch_videos(self, in_dir, out_dir, recursive, target_fps=60):
        exts = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
        targets = []
        in_path = Path(in_dir)

        iterator = in_path.rglob("*") if recursive else in_path.glob("*")

        for p in iterator:
            if p.is_file() and p.suffix.lower() in exts:
                if f"videos_{target_fps}fps" in str(p).lower() or f"_{target_fps}fps" in p.name.lower():
                    continue
                rel = p.relative_to(in_path)
                dest = Path(out_dir) / rel.parent / f"{p.stem}_{target_fps}fps{p.suffix}"
                targets.append((str(p), str(dest)))

        return targets

    def _cancel(self):
        if self.is_running:
            self.cancel_requested = True
            if self.process:
                try:
                    self.process.terminate()
                except Exception:
                    pass
            self._log("⚠️ Cancelación solicitada por el usuario.")
            self._set_status("Cancelando proceso...")

    def _get_encoder_args(self, hw_choice, crf_val):
        if "NVIDIA" in hw_choice:
            codec = "hevc_nvenc" if "HEVC" in hw_choice else "h264_nvenc"
            return [
                "-c:v", codec,
                "-preset", "p7",
                "-tune", "hq",
                "-multipass", "fullres",
                "-rc", "vbr",
                "-cq", crf_val,
                "-b:v", "0",
                "-spatial-aq", "1",
                "-temporal-aq", "1",
                "-pix_fmt", "yuv420p"
            ]
        elif "AMD Radeon" in hw_choice:
            codec = "h264_amf"
            return [
                "-c:v", codec,
                "-quality", "quality",
                "-rc", "cqp",
                "-qp_i", crf_val,
                "-qp_p", crf_val,
                "-pix_fmt", "yuv420p"
            ]
        else:
            return [
                "-c:v", "libx264",
                "-crf", crf_val,
                "-preset", "slow",
                "-pix_fmt", "yuv420p"
            ]

    def _worker_thread(self, targets, target_fps, method_str, crf_val):
        total = len(targets)
        vf = self._build_vf_filter(target_fps, method_str)
        success_count = 0
        start_time = time.time()
        hw_choice = self.hw_var.get()

        for idx, (inp_path, out_path) in enumerate(targets, 1):
            if self.cancel_requested:
                break

            fname = os.path.basename(inp_path)
            self._set_status(f"Interpolando [{idx}/{total}]: {fname} a {target_fps} FPS", progress=((idx - 1) / total) * 100)
            self._log(f"\n▶ [{idx}/{total}] Procesando: {fname} -> {target_fps} fps")

            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            info = self._probe_video(inp_path)
            duration = info["duration"] if info else 0
            if info and "width" in info and "height" in info:
                try:
                    w_int, h_int = int(info["width"]), int(info["height"])
                    orient_tag = "📱 Vertical (9:16)" if h_int > w_int else ("⏹ Cuadrado (1:1)" if w_int == h_int else "🖥 Horizontal (16:9)")
                    self._log(f"  Geometría origen: {w_int}x{h_int} [{orient_tag}]")
                except Exception:
                    pass
            enc_args = self._get_encoder_args(hw_choice, crf_val)

            cmd = [
                "ffmpeg", "-y", "-hide_banner",
                "-i", inp_path,
                "-vf", vf
            ] + enc_args + [
                "-map", "0:v:0",
                "-map", "0:a?",
                "-c:a", "copy",
                out_path
            ]

            try:
                creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True, creationflags=creation_flags)

                time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

                while True:
                    line = self.process.stderr.readline()
                    if not line and self.process.poll() is not None:
                        break
                    if line and duration > 0:
                        m = time_pattern.search(line)
                        if m:
                            hours, mins, secs = float(m.group(1)), float(m.group(2)), float(m.group(3))
                            curr_time = hours * 3600 + mins * 60 + secs
                            clip_pct = min(curr_time / duration, 1.0)
                            overall_pct = ((idx - 1 + clip_pct) / total) * 100
                            self._set_status(f"Interpolando [{idx}/{total}]: {fname} ({int(clip_pct*100)}%)", progress=overall_pct)

                self.process.wait()
                if self.process.returncode == 0:
                    success_count += 1
                    self._log(f"  ✓ Guardado: {os.path.basename(out_path)} ({target_fps} FPS)")
                else:
                    if not self.cancel_requested and ("NVIDIA" in hw_choice or "AMD" in hw_choice):
                        self._log("  ⚠️ Hardware GPU no compatible en este sistema. Reintentando con CPU de alta fidelidad...")
                        fallback_cmd = [
                            "ffmpeg", "-y", "-hide_banner",
                            "-i", inp_path,
                            "-vf", vf,
                            "-c:v", "libx264",
                            "-crf", crf_val,
                            "-preset", "slow",
                            "-pix_fmt", "yuv420p",
                            "-map", "0:v:0",
                            "-map", "0:a?",
                            "-c:a", "copy",
                            out_path
                        ]
                        self.process = subprocess.Popen(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True, creationflags=creation_flags)
                        while True:
                            line = self.process.stderr.readline()
                            if not line and self.process.poll() is not None:
                                break
                        self.process.wait()
                        if self.process.returncode == 0:
                            success_count += 1
                            self._log(f"  ✓ Guardado (CPU): {os.path.basename(out_path)} ({target_fps} FPS)")
                        else:
                            self._log(f"  ✗ Error al procesar {fname}")
                    else:
                        if not self.cancel_requested:
                            self._log(f"  ✗ Error al procesar {fname}")
            except Exception as e:
                self._log(f"  ✗ Excepción: {e}")

        total_time = round(time.time() - start_time, 1)
        self.msg_queue.put(("finished", (success_count, total, total_time, self.cancel_requested, target_fps)))

    def _on_finished(self, data):
        success_count, total, total_time, was_cancelled, target_fps = data
        self.is_running = False
        self.btn_start.configure_state("normal")
        self.btn_cancel.configure_state("disabled")

        if was_cancelled:
            self._set_status("Operación cancelada.", progress=0)
            self._log(f"\n⚠️ Proceso interrumpido. Completados: {success_count} de {total}.")
        else:
            self.prog_var.set(100)
            self._set_status(f"¡Completado! {success_count}/{total} videos generados a {target_fps} FPS en {total_time}s.", progress=100)
            self._log(f"\n✨ ¡Finalizado con éxito! {success_count} video(s) elevados a {target_fps} FPS en {total_time} segundos.")
            messagebox.showinfo("Proceso Completado", f"Se interpolaron {success_count} de {total} videos con éxito a {target_fps} FPS.\n\nTiempo total: {total_time}s")


if __name__ == "__main__":
    root = tk.Tk()
    app = FPSBoosterApp(root)
    root.mainloop()
