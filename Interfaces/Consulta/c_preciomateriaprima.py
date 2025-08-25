import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Any

# ────────────────────────────────────────────────────────────────────────────────
#  Configuración y Constantes
# ────────────────────────────────────────────────────────────────────────────────

DB_FILE = Path(__file__).parent.parent.parent / "captop.db"

# Textos para internacionalización
TEXTS = {
    "window_title": "Consulta - Precios de Materias Primas",
    "company_frame": "Empresa y Período",
    "company_label": "Empresa:",
    "period_label": "Período:",
    "home_notebook": "Notebook Home",
    "pro_notebook": "Notebook Professional",
    "other_rates": "Otras Tasas",
    "tax_rates": "Tasa Impuesto Compra-Venta por País",
    "load_btn": "Cargar Datos",
    "back_btn": "Volver al Menú Principal",
    "load_success": "Datos cargados correctamente.",
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
#  Vista - Interfaz de Usuario de Consulta
# ────────────────────────────────────────────────────────────────────────────────

class RawMaterialPriceConsultaUI(tk.Toplevel):
    """Interfaz gráfica de consulta para la sección de Precios de Materias Primas."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name = company_name
        self.period = period
        self.db = DatabaseManager(DB_FILE)
        
        # Configuración inicial de la ventana
        self.title(TEXTS["window_title"])
        self.geometry("900x700")
        self.minsize(800, 600)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configurar estilos
        self._configure_styles()
        
        # Variables de control (solo para mostrar datos)
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
        style.configure('TEntry', fieldbackground='#f0f0f0', borderwidth=1, relief='solid', padding=2)
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
        style.configure('Yellow.TLabel', background='yellow', font=('Inter', 10, 'bold'), anchor='center')
        style.configure('Cyan.TLabel', background='lightskyblue', font=('Inter', 10, 'bold'), anchor='center')
    
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
            text="Consulta - Precios de Materias Primas", 
            font=('Inter', 18, 'bold'), 
            anchor='center'
        ).pack(pady=(10, 20), fill="x")
        
        # Secciones de precios
        self._create_home_notebook_section()
        self._create_pro_notebook_section()
        self._create_other_rates_section()
        self._create_tax_rates_section()
        
        # Botones de acción
        self._create_action_buttons()
    
    def _create_company_info_section(self):
        """Crea la sección que muestra información de la empresa y período."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["company_frame"], padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)
        
        # Mostrar nombre de la empresa (no editable)
        ttk.Label(frame, text=TEXTS["company_label"]).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=self.company_name, font=('Inter', 10, 'bold')).grid(
            row=0, column=1, padx=5, pady=2, sticky='w')
        frame.columnconfigure(1, weight=1)
        
        # Mostrar período (no editable)
        ttk.Label(frame, text=TEXTS["period_label"]).grid(row=0, column=2, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=str(self.period), font=('Inter', 10, 'bold')).grid(
            row=0, column=3, padx=5, pady=2, sticky='w')
    
    def _create_home_notebook_section(self):
        """Crea la sección para Notebook Home."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["home_notebook"], padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=5)
        
        # Cabeceras
        ttk.Label(frame, text="", width=15).grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        ttk.Label(frame, text="60 Días", style='Yellow.TLabel').grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        ttk.Label(frame, text="120 Días", style='Yellow.TLabel').grid(row=0, column=2, padx=5, pady=2, sticky='ew')
        
        # Ítems KIT, PPA
        items_home = ["KIT_home", "PPA_home"]
        for i, item in enumerate(items_home):
            ttk.Label(frame, text=item.split('_')[0] + ":").grid(row=i+1, column=0, padx=5, pady=2, sticky='w')
            self.entry_vars[f"{item}_60_days"] = tk.StringVar()
            entry1 = ttk.Entry(frame, textvariable=self.entry_vars[f"{item}_60_days"], state='readonly')
            entry1.grid(row=i+1, column=1, padx=5, pady=2, sticky='ew')
            self.entry_vars[f"{item}_120_days"] = tk.StringVar()
            entry2 = ttk.Entry(frame, textvariable=self.entry_vars[f"{item}_120_days"], state='readonly')
            entry2.grid(row=i+1, column=2, padx=5, pady=2, sticky='ew')
        
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
    
    def _create_pro_notebook_section(self):
        """Crea la sección para Notebook Professional."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["pro_notebook"], padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=5)
        
        # Cabeceras
        ttk.Label(frame, text="", width=15).grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        ttk.Label(frame, text="60 Días", style='Cyan.TLabel').grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        ttk.Label(frame, text="120 Días", style='Cyan.TLabel').grid(row=0, column=2, padx=5, pady=2, sticky='ew')
        
        # Ítems KIT, PPA
        items_pro = ["KIT_pro", "PPA_pro"]
        for i, item in enumerate(items_pro):
            ttk.Label(frame, text=item.split('_')[0] + ":").grid(row=i+1, column=0, padx=5, pady=2, sticky='w')
            self.entry_vars[f"{item}_60_days"] = tk.StringVar()
            entry1 = ttk.Entry(frame, textvariable=self.entry_vars[f"{item}_60_days"], state='readonly')
            entry1.grid(row=i+1, column=1, padx=5, pady=2, sticky='ew')
            self.entry_vars[f"{item}_120_days"] = tk.StringVar()
            entry2 = ttk.Entry(frame, textvariable=self.entry_vars[f"{item}_120_days"], state='readonly')
            entry2.grid(row=i+1, column=2, padx=5, pady=2, sticky='ew')
        
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
    
    def _create_other_rates_section(self):
        """Crea la sección para otras tasas."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["other_rates"], padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=5)
        frame.columnconfigure(1, weight=1)
        
        other_items = [
            "Tasa Sobregiro(%)",
            "Incobrables definitivos (%)",
            "Morosos (%)",
            "Recargos por protestos (%)"
        ]
        
        for i, item in enumerate(other_items):
            ttk.Label(frame, text=item + ":").grid(row=i, column=0, padx=5, pady=2, sticky='w')
            self.entry_vars[self._clean_key(item)] = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=self.entry_vars[self._clean_key(item)], state='readonly')
            entry.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
    
    def _create_tax_rates_section(self):
        """Crea la sección para tasas de impuestos por país."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["tax_rates"], padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=5)
        
        countries = ["Argentina", "Brasil", "Chile", "Colombia", "Mexico"]
        
        # Cabeceras de países
        for col_idx, country in enumerate(countries):
            ttk.Label(frame, text=country, font=('Inter', 10, 'bold'), anchor='center').grid(
                row=0, column=col_idx, padx=5, pady=2, sticky='ew')
            frame.columnconfigure(col_idx, weight=1)
        
        # Fila para Tasa impuesto Compra_Venta
        row_idx = 1
        for col_idx, country in enumerate(countries):
            key = f"Tasa_impuesto_Compra_Venta_{self._clean_key(country)}"
            self.entry_vars[key] = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=self.entry_vars[key], state='readonly')
            entry.grid(row=row_idx, column=col_idx, padx=5, pady=2, sticky='ew')
    
    def _create_action_buttons(self):
        """Crea los botones de acción en la parte inferior."""
        frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=10)
        
        # Configurar columnas con peso igual
        for i in range(2):
            frame.columnconfigure(i, weight=1)
        
        # Botones
        ttk.Button(
            frame, 
            text=TEXTS["load_btn"], 
            command=self._load_data
        ).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        ttk.Button(
            frame, 
            text=TEXTS["back_btn"], 
            command=self._on_closing
        ).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    
    def _clean_key(self, text: str) -> str:
        """Limpia el texto para usarlo como clave en un diccionario."""
        return text.replace(" ", "_").replace("(", "").replace(")", "").replace("%", "").replace("-", "_")
    
    def _load_data(self):
        """Carga los datos desde la base de datos."""
        data = self.db.load_decision(self.company_id, self.period)
        if not data:
            messagebox.showinfo(TEXTS["no_data"], TEXTS["no_data"])
            self._clear_fields()
            return
        
        loaded_data = data.get("raw_material_prices", {})
        
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

# ────────────────────────────────────────────────────────────────────────────────
#  Función de Apertura
# ────────────────────────────────────────────────────────────────────────────────

def abrir_consulta_preciomateriaprima(parent_app, company_id: int, company_name: str, period: int):
    """Función para abrir la interfaz de consulta de precios de materias primas."""
    window = RawMaterialPriceConsultaUI(parent_app, company_id, company_name, period)
    return window