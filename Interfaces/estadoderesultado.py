import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path
import json
import logging
from typing import Dict, Any, Optional

# ------------------------- Configuración Inicial -------------------------
# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('datos_fisicos_inventario.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Internacionalización
TRANSLATIONS = {
    "es": {
        "window_title": "Datos Físicos de Inventarios Total Continente",
        "company_period": "Empresa y Período",
        "company": "Empresa:",
        "period": "Período:",
        "raw_materials": "MATERIAS PRIMAS:",
        "kits_units": "Inventario Final Kits (Unidades)",
        "ppa_units": "Inventario Final PPA (Unidades)",
        "desktop_model": "MODELO DESKTOP:",
        "assembly_period": "Ensamblaje del Período",
        "finished_products": "Inventario Final Productos Terminados",
        "notebook_model": "MODELO NOTEBOOK:",
        "notebook_assembly": "Ensamblaje del Período (Unidades)",
        "notebook_finished": "Inventario Final Productos Terminados (Unidades)",
        "save": "Guardar",
        "update": "Actualizar",
        "clean": "Limpiar",
        "close": "Cerrar",
        "save_success": "Datos físicos guardados para el período {period}.",
        "load_success": "Datos físicos cargados para el período {period}.",
        "load_empty": "No se encontraron datos para el período {period}.",
        "save_error": "Error al guardar datos: {error}"
    }
}

CURRENT_LANGUAGE = "es"

def tr(key: str, **kwargs) -> str:
    """Obtiene la traducción para la clave dada y aplica formato."""
    return TRANSLATIONS[CURRENT_LANGUAGE].get(key, key).format(**kwargs)

# ------------------------- Modelo -------------------------
class DatosFisicosInventarioModel:
    """Modelo para manejar los datos de inventarios físicos."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
        self._initialize_database()
        
    def _initialize_database(self):
        """Crea la tabla si no existe."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_control (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER,
                        period INTEGER,
                        type TEXT,
                        data TEXT,
                        UNIQUE(company_id, period, type))
                    """)
                conn.commit()
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
        
    def get_connection(self):
        """Establece y devuelve una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_inventory_data(self, company_id: int, period: int, data: Dict[str, Any]) -> bool:
        """Guarda los datos de inventario físico en la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO system_control (company_id, period, type, data) VALUES (?, ?, ?, ?)",
                    (company_id, period, "DATOS_FISICOS_INVENTARIO", json.dumps(data))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving inventory data: {str(e)}")
            return False
            
    def load_inventory_data(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        """Carga los datos de inventario físico desde la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM system_control WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, "DATOS_FISICOS_INVENTARIO"))
                row = cursor.fetchone()
                return json.loads(row["data"]) if row else None
        except Exception as e:
            logger.error(f"Error loading inventory data: {str(e)}")
            return None

# ------------------------- Vista -------------------------
class DatosFisicosInventarioUI(tk.Toplevel):
    """Interfaz gráfica para Datos Físicos de Inventarios."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent / "captop.db"
        self.model = DatosFisicosInventarioModel(db_file)
        
        # Inicializar variables
        self.entry_vars = {}
        
        self._setup_ui()
        self._load_initial_data()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.title(tr("window_title"))
        self.geometry("650x550")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_company_period_section()
        self._create_inventory_sections()
        self._create_buttons()
        self._create_footer()
        
    def _configure_styles(self):
        """Configura los estilos de la interfaz."""
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
        
        # Estilos personalizados para botones
        style.configure('Green.TButton', background='#4CAF50', foreground='white')
        style.configure('Blue.TButton', background='#2196F3', foreground='white')
        style.configure('Orange.TButton', background='#FF9800', foreground='white')
        style.configure('Red.TButton', background='#F44336', foreground='white')
        
    def _create_scrollable_frame(self):
        """Crea el área desplazable principal."""
        self.main_canvas = tk.Canvas(self, bg='#DCDAD5')
        self.main_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")
        
    def _create_company_period_section(self):
        """Crea la sección de información de empresa y período."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=tr("company_period"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text=tr("company")).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=self.company_name_str, font=('Inter', 10, 'bold')).grid(
            row=0, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(frame, text=tr("period")).grid(row=0, column=2, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=str(self.period_int), font=('Inter', 10, 'bold')).grid(
            row=0, column=3, padx=5, pady=2, sticky='w')
        
        frame.grid_columnconfigure(1, weight=1)

    def _create_inventory_sections(self):
        """Crea las secciones de datos de inventarios."""
        # Materias Primas
        frame = ttk.LabelFrame(self.scrollable_frame, text=tr("raw_materials"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)
        
        self._create_input_row(frame, tr("kits_units"), "kits_units", 0)
        self._create_input_row(frame, tr("ppa_units"), "ppa_units", 1)

        # Modelo Desktop
        frame = ttk.LabelFrame(self.scrollable_frame, text=tr("desktop_model"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)
        
        self._create_input_row(frame, tr("assembly_period"), "desktop_assembly", 0)
        self._create_input_row(frame, tr("finished_products"), "desktop_finished", 1)

        # Modelo Notebook
        frame = ttk.LabelFrame(self.scrollable_frame, text=tr("notebook_model"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)
        
        self._create_input_row(frame, tr("notebook_assembly"), "notebook_assembly", 0)
        self._create_input_row(frame, tr("notebook_finished"), "notebook_finished", 1)
        
    def _create_input_row(self, parent_frame, label_text, key, row_num):
        """Crea una fila con etiqueta y campo de entrada."""
        row_frame = ttk.Frame(parent_frame)
        row_frame.grid(row=row_num, column=0, sticky="ew", pady=5)
        parent_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(row_frame, text=label_text, width=40, anchor="w").pack(side=tk.LEFT, padx=5)
        
        var = tk.StringVar(value="0")
        entry = ttk.Entry(row_frame, textvariable=var, width=15, justify="right")
        entry.pack(side=tk.RIGHT, padx=5)
        self.entry_vars[key] = var

    def _create_buttons(self):
        """Crea los botones de acción."""
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 20))
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Configurar columnas con peso igual
        for i in range(4):
            button_frame.columnconfigure(i, weight=1)
        
        botones = [
            (tr("save"), 'Green.TButton', self.guardar),
            (tr("update"), 'Blue.TButton', self.actualizar),
            (tr("clean"), 'Orange.TButton', self.limpiar),
            (tr("close"), 'Red.TButton', self._on_closing)
        ]
        
        for i, (texto, estilo, comando) in enumerate(botones):
            btn = ttk.Button(
                button_frame, 
                text=texto, 
                style=estilo,
                command=comando
            )
            btn.grid(row=0, column=i, padx=5, sticky='ew')

    def _create_footer(self):
        """Crea el pie de página."""
        footer_frame = ttk.Frame(self.scrollable_frame)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        ttk.Label(footer_frame, text="Sistema de Gestión FUMANCHU v1.0", 
                 font=('Inter', 9), foreground="#777777").pack(side=tk.LEFT, padx=10)
        
        ttk.Label(footer_frame, text="© 2023 Todos los derechos reservados", 
                 font=('Inter', 9), foreground="#777777").pack(side=tk.RIGHT, padx=10)

    def _load_initial_data(self):
        """Carga los datos iniciales del inventario físico."""
        inventory_data = self.model.load_inventory_data(self.company_id, self.period_int)
        
        if inventory_data:
            for key, var in self.entry_vars.items():
                if key in inventory_data:
                    var.set(inventory_data[key])
            
            messagebox.showinfo("Cargar Datos", tr("load_success", period=self.period_int))
        else:
            messagebox.showinfo("Cargar Datos", tr("load_empty", period=self.period_int))

    def guardar(self):
        """Guarda los datos del inventario físico en la base de datos."""
        try:
            inventory_data = {}
            for key, var in self.entry_vars.items():
                inventory_data[key] = var.get()
            
            if self.model.save_inventory_data(self.company_id, self.period_int, inventory_data):
                messagebox.showinfo("Éxito", tr("save_success", period=self.period_int))
            else:
                messagebox.showerror("Error", tr("save_error", error="Error de base de datos"))
        except Exception as e:
            logger.error(f"Error al guardar datos: {str(e)}")
            messagebox.showerror("Error", tr("save_error", error=str(e)))
    
    def actualizar(self):
        """Actualiza los datos desde la base de datos."""
        self._load_initial_data()
        messagebox.showinfo("Actualizado", "Datos actualizados correctamente")
    
    def limpiar(self):
        """Limpia todos los campos."""
        for var in self.entry_vars.values():
            var.set("0")
        messagebox.showinfo("Campos Limpiados", "Todos los campos han sido restablecidos")
    
    def _on_closing(self):
        """Maneja el cierre de la ventana."""
        self.destroy()
        self.parent_app.show_main_menu()

# Función para abrir desde main.py
def abrir_datos_fisicos_inventario(parent_app, company_id: int, company_name: str, period: int):
    ventana = DatosFisicosInventarioUI(parent_app, company_id, company_name, period)
    ventana.grab_set()