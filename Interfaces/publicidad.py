import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Any, List

# ────────────────────────────────────────────────────────────────────────────────
#  Configuración y Constantes
# ────────────────────────────────────────────────────────────────────────────────

DB_FILE = Path(__file__).parent.parent / "captop.db"

# Textos para internacionalización
TEXTS = {
    "window_title": "Ingreso de Publicidad",
    "company_frame": "Empresa y Período",
    "company_label": "Empresa:",
    "period_label": "Período:",
    "advertising_frame": "Ingreso de Publicidad",
    "save_btn": "Guardar Publicidad",
    "load_btn": "Cargar Publicidad",
    "back_btn": "Volver al Menú Principal",
    "save_success": "Publicidad guardada correctamente.",
    "load_success": "Publicidad cargada correctamente.",
    "no_data": "No se encontraron datos para este período.",
    "error": "Error",
}

# ────────────────────────────────────────────────────────────────────────────────
#  Modelo - Manejo de Base de Datos
# ────────────────────────────────────────────────────────────────────────────────

class DatabaseManager:
    """Manejador de la base de datos encapsulando todas las operaciones SQL."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
    
    def get_connection(self):
        """Devuelve una conexión SQLite con filas accesibles por nombre."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_decision(self, company_id: int, period: int, payload: Dict) -> bool:
        """Guarda las decisiones en la base de datos."""
        with self.get_connection() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "REPLACE INTO decision (company_id, period, payload) VALUES (?, ?, ?)",
                    (company_id, period, json.dumps(payload)))
                conn.commit()
                return True
            except sqlite3.Error as e:
                messagebox.showerror(TEXTS["error"], f"Error de base de datos: {str(e)}")
                return False
    
    def load_decision(self, company_id: int, period: int) -> Optional[Dict]:
        """Carga las decisiones desde la base de datos."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT payload FROM decision WHERE company_id = ? AND period = ?",
                (company_id, period))
            row = cur.fetchone()
            return json.loads(row["payload"]) if row else None

# ────────────────────────────────────────────────────────────────────────────────
#  Vista - Interfaz de Usuario
# ────────────────────────────────────────────────────────────────────────────────

class AdvertisingUI(tk.Toplevel):
    """Interfaz gráfica para la sección de Publicidad."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name = company_name
        self.period = period
        self.db = DatabaseManager(DB_FILE)
        
        # Configuración inicial de la ventana
        self.title(TEXTS["window_title"])
        self.geometry("1200x700")
        self.minsize(1000, 600)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configurar estilos
        self._configure_styles()
        
        # Variables de control
        self.entry_vars: Dict[str, tk.StringVar] = {}
        
        # Crear widgets
        self._create_widgets()
        
        # Cargar datos iniciales
        self._load_data()
    
    def _configure_styles(self):
        """Configura los estilos visuales de la aplicación."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#DCDAD5')
        style.configure('TLabel', background='#DCDAD5', font=('Inter', 10))
        style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 11, 'bold'))
        style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=2)
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
    
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        # Canvas desplazable
        self.canvas = tk.Canvas(self, bg='#DCDAD5')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Sección de información de empresa y período
        self._create_company_info_section()
        
        # Título Principal
        ttk.Label(
            self.scrollable_frame, 
            text="Ingreso de Publicidad", 
            font=('Inter', 18, 'bold'), 
            anchor='center'
        ).pack(pady=(10, 20), fill="x")
        
        # Sección de publicidad
        self._create_advertising_section()
        
        # Botones de acción
        self._create_action_buttons()
    
    def _create_company_info_section(self):
        """Crea la sección que muestra información de la empresa y período."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["company_frame"], padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)
        
        # Mostrar nombre de la empresa (no editable)
        ttk.Label(frame, text=TEXTS["company_label"]).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=self.company_name, font=('Inter', 10, 'bold')).grid(
            row=0, column=1, padx=5, pady=2, sticky='w'
        )
        frame.columnconfigure(1, weight=1)
        
        # Mostrar período (no editable)
        ttk.Label(frame, text=TEXTS["period_label"]).grid(row=0, column=2, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=str(self.period), font=('Inter', 10, 'bold')).grid(
            row=0, column=3, padx=5, pady=2, sticky='w'
        )
    
    def _create_advertising_section(self):
        """Crea la sección para ingreso de publicidad por país y medio."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["advertising_frame"], padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        countries = ["Argentina", "Brasil", "Chile", "Colombia", "Mexico"]
        media_types = [
            "Revista PC Actualidad", "Revista Multitiendas", "Diario Negocios y Economía",
            "Diario Sensacionalista", "Televisión Abierta", "Televisión Pagada",
            "Circuito ABC1", "Circuito C2C3", "Radio Adulto Joven", "Radio Noticias",
            "Portal Tipo TERRA", "Portal Diario Electrónico"
        ]
        
        frame.grid_columnconfigure(0, weight=1)  # Columna para los nombres de los medios
        for i in range(1, len(countries) + 1):
            frame.grid_columnconfigure(i, weight=1)

        # Encabezados de columna (Países)
        ttk.Label(frame, text="").grid(row=0, column=0, padx=5, pady=2)
        for i, country in enumerate(countries):
            ttk.Label(frame, text=country, font=('Inter', 10, 'bold')).grid(
                row=0, column=1 + i, padx=5, pady=2
            )

        # Filas de entrada para cada tipo de medio
        for r_idx, media in enumerate(media_types):
            ttk.Label(frame, text=media, anchor='w', wraplength=120, justify='left').grid(
                row=1 + r_idx, column=0, padx=5, pady=2, sticky='w'
            )
            for c_idx, country in enumerate(countries):
                # Generar una clave única para cada campo de entrada
                key = f"advertising_{media.replace(' ', '_').replace('.', '').replace('/', '_')}_{country}"
                self.entry_vars[key] = tk.StringVar()
                ttk.Entry(frame, textvariable=self.entry_vars[key]).grid(
                    row=1 + r_idx, column=1 + c_idx, padx=2, pady=2, sticky='ew'
                )
    
    def _create_action_buttons(self):
        """Crea los botones de acción en la parte inferior."""
        frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=10)
        
        # Configurar columnas con peso igual
        for i in range(3):
            frame.columnconfigure(i, weight=1)
        
        # Botones
        ttk.Button(
            frame, 
            text=TEXTS["save_btn"], 
            command=self._save_data
        ).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        ttk.Button(
            frame, 
            text=TEXTS["load_btn"], 
            command=self._load_data
        ).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Button(
            frame, 
            text=TEXTS["back_btn"], 
            command=self._on_closing
        ).grid(row=0, column=2, padx=5, pady=5, sticky='ew')
    
    def _get_numeric_value(self, value_str: str) -> Optional[float]:
        """Convierte el valor a float o devuelve None si no es válido."""
        if not value_str:
            return None
        try:
            return float(value_str.replace(',', ''))
        except ValueError:
            return None
    
    def _save_data(self):
        """Guarda los datos en la base de datos."""
        # Recopilar todos los datos de entrada
        advertising_data = {}
        for key, var in self.entry_vars.items():
            advertising_data[key] = self._get_numeric_value(var.get())
        
        # Cargar el payload existente para el período y actualizar solo las decisiones de publicidad
        existing_data = self.db.load_decision(self.company_id, self.period) or {}
        existing_data["advertising_decisions"] = advertising_data
        
        if self.db.save_decision(self.company_id, self.period, existing_data):
            messagebox.showinfo(TEXTS["save_success"], TEXTS["save_success"])
        else:
            messagebox.showerror(TEXTS["error"], "No se pudieron guardar los datos.")
    
    def _load_data(self):
        """Carga los datos desde la base de datos."""
        data = self.db.load_decision(self.company_id, self.period)
        if not data:
            messagebox.showinfo(TEXTS["no_data"], TEXTS["no_data"])
            self._clear_fields()
            return
        
        loaded_data = data.get("advertising_decisions", {})
        
        # Rellenar los campos de entrada
        for key, var in self.entry_vars.items():
            if key in loaded_data and loaded_data[key] is not None:
                var.set(str(loaded_data[key]))
            else:
                var.set("")
        
        messagebox.showinfo(TEXTS["load_success"], TEXTS["load_success"])
    
    def _clear_fields(self):
        """Limpia todos los campos del formulario."""
        for var in self.entry_vars.values():
            var.set("")
    
    def _on_closing(self):
        """Maneja el cierre de la ventana."""
        self.destroy()
        self.parent_app.show_main_menu()

