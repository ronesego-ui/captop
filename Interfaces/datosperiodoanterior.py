import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# ------------------------- Configuración Inicial -------------------------
# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('previous_period.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Internacionalización
TRANSLATIONS = {
    "es": {
        "window_title": "Datos del Período Anterior",
        "company_period": "Empresa y Período",
        "company": "Empresa:",
        "period": "Período:",
        "save_success": "Datos guardados para el período {period} de {company}.",
        "load_success": "Datos cargados para el período {period}.",
        "load_empty": "No se encontraron datos para el período {period} de esta empresa. Campos vacíos.",
        "company_not_found": "Empresa no encontrada en la base de datos.",
        "save_error": "Error al guardar datos: {error}",
        "db_error": "Error de Base de Datos",
        "invalid_period": "El período actual no es un número válido.",
        "title": "Saldo Final",
        "notebook_home": "Notebook Home",
        "notebook_pro": "Notebook Professional",
        "save": "Guardar Datos",
        "load": "Cargar Datos",
        "back": "Volver al Menú Principal"
    }
}

CURRENT_LANGUAGE = "es"

def tr(key: str, **kwargs) -> str:
    """Obtiene la traducción para la clave dada y aplica formato."""
    return TRANSLATIONS[CURRENT_LANGUAGE].get(key, key).format(**kwargs)

# ------------------------- Modelo -------------------------
class PreviousPeriodModel:
    """Modelo para manejar los datos del período anterior."""
    
    def __init__(self, db_file: Path):
        """Inicializa el modelo con la ruta al archivo de base de datos."""
        self.db_file = db_file
        
    def get_connection(self):
        """Establece y devuelve una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_previous_period_data(self, company_id: int, period: int, data: Dict[str, Any]) -> bool:
        """Guarda los datos del período anterior en la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Cargar el payload existente para el período y actualizar solo los datos del período anterior
                cursor.execute(
                    "SELECT payload FROM decision WHERE company_id = ? AND period = ?",
                    (company_id, period)
                )
                existing_row = cursor.fetchone()
                
                full_payload = existing_row["payload"] if existing_row else "{}"
                full_payload = json.loads(full_payload)
                full_payload["previous_period_data"] = data
                
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO decision (company_id, period, payload)
                    VALUES (?, ?, ?)
                    """,
                    (company_id, period, json.dumps(full_payload))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving previous period data: {str(e)}")
            return False
            
    def load_previous_period_data(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        """Carga los datos del período anterior desde la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT payload FROM decision WHERE company_id = ? AND period = ?",
                    (company_id, period)
                )
                row = cursor.fetchone()
                if row:
                    payload = json.loads(row["payload"])
                    return payload.get("previous_period_data")
                return None
        except Exception as e:
            logger.error(f"Error loading previous period data: {str(e)}")
            return None

    def get_companies(self) -> list:
        """Obtiene la lista de empresas disponibles."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM company")
                return [(row["id"], row["name"]) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting companies: {str(e)}")
            return []

    def get_company_period(self, company_id: int) -> int:
        """Obtiene el período actual de una empresa."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT current_period FROM company WHERE id = ?",
                    (company_id,)
                )
                row = cursor.fetchone()
                return row["current_period"] if row else 1
        except Exception as e:
            logger.error(f"Error getting company period: {str(e)}")
            return 1

# ------------------------- Vista -------------------------
class PreviousPeriodDataUI(tk.Toplevel):
    """Interfaz gráfica para los datos del período anterior."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        """Inicializa la ventana de datos del período anterior."""
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent / "captop.db"
        self.model = PreviousPeriodModel(db_file)
        
        # Inicializar variables
        self.entry_vars = {}
        self.countries = ["Argentina", "Brasil", "Chile", "Colombia", "Mexico"]
        self.items = ["Productos Terminados", "Producc_Ordenada", "Desp_Matir(Destino)", "Plásticos", "Aluminio"]
        
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.title(tr("window_title"))
        self.geometry("1000x800")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_company_period_section()
        self._create_notebook_sections()
        self._create_buttons()
        
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
        style.configure('Header.TLabel', font=('Inter', 10, 'bold'), anchor='center')
        
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
        self.company_name_var = tk.StringVar(value=self.company_name_str)
        ttk.Label(frame, textvariable=self.company_name_var, font=('Inter', 10, 'bold')).grid(
            row=0, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(frame, text=tr("period")).grid(row=0, column=2, padx=5, pady=2, sticky='w')
        self.period_var = tk.StringVar(value=str(self.period_int))
        ttk.Label(frame, textvariable=self.period_var, font=('Inter', 10, 'bold')).grid(
            row=0, column=3, padx=5, pady=2, sticky='w')
        
        frame.grid_columnconfigure(1, weight=1)

    def _create_notebook_sections(self):
        """Crea las secciones de notebooks."""
        # --- Título Principal ---
        title_label = ttk.Label(self.scrollable_frame, text=tr("title"), font=('Inter', 18, 'bold'), anchor='center')
        title_label.pack(pady=(20, 10), fill="x")

        # --- Notebook Home ---
        self._create_notebook_section(tr("notebook_home"), "home")

        # --- Notebook Professional ---
        self._create_notebook_section(tr("notebook_pro"), "pro")

    def _create_notebook_section(self, section_name: str, prefix: str):
        """Crea una sección de notebook (home o pro)."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=section_name, padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=5)
        
        # Cabeceras de países
        ttk.Label(frame, text="", width=20).grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        for col_idx, country in enumerate(self.countries):
            ttk.Label(frame, text=country, style='Header.TLabel').grid(
                row=0, column=col_idx + 1, padx=5, pady=2, sticky='ew')
            frame.grid_columnconfigure(col_idx + 1, weight=1)

        # Ítems y entradas
        for row_idx, item in enumerate(self.items):
            ttk.Label(frame, text=item + ":").grid(row=row_idx + 1, column=0, padx=5, pady=2, sticky='w')
            for col_idx, country in enumerate(self.countries):
                key = f"{prefix}_{self._normalize_key(item)}_{self._normalize_key(country)}"
                self.entry_vars[key] = tk.StringVar()
                ttk.Entry(frame, textvariable=self.entry_vars[key]).grid(
                    row=row_idx + 1, column=col_idx + 1, padx=5, pady=2, sticky='ew')

    def _create_buttons(self):
        """Crea los botones de acción."""
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        button_frame.pack(fill="x", padx=10, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text=tr("save"), command=self.save_data).grid(
            row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text=tr("load"), command=self.load_data).grid(
            row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text=tr("back"), command=self._on_closing).grid(
            row=0, column=2, padx=5, pady=5, sticky='ew')

    def _normalize_key(self, key: str) -> str:
        """Normaliza una clave para que coincida con nuestra convención de nombres."""
        return (key.replace(' ', '_')
                  .replace('/', '_')
                  .replace('.', '_')
                  .replace(':', '')
                  .replace('-', '_')
                  .replace('"', '')
                  .replace("'", "")
                  .replace("ó", "o")
                  .replace("é", "e")
                  .replace("á", "a")
                  .replace("í", "i")
                  .replace("ú", "u")
                  .replace("ñ", "n")
                  .replace("(", "")
                  .replace(")", "")
                  .lower())

    def _get_numeric_value(self, value_str: str) -> Optional[float]:
        """Intenta convertir el valor a float; si falla o es vacío, devuelve None."""
        if not value_str:
            return None
        try:
            # Reemplazar comas por puntos para asegurar la conversión a float en Python
            return float(value_str.replace(',', '.'))
        except ValueError:
            return None

    def _load_initial_data(self):
        """Carga los datos iniciales del período anterior."""
        previous_period_data = self.model.load_previous_period_data(self.company_id, self.period_int)
        
        if previous_period_data:
            for key, var in self.entry_vars.items():
                if key in previous_period_data and previous_period_data[key] is not None:
                    var.set(str(previous_period_data[key]))
            
            messagebox.showinfo("Cargar Datos", tr("load_success", period=self.period_int))
        else:
            messagebox.showinfo("Cargar Datos", tr("load_empty", period=self.period_int))

    def save_data(self):
        """Guarda los datos del período anterior en la base de datos."""
        try:
            # Recopilar todos los datos de entrada
            previous_period_data = {}
            for key, var in self.entry_vars.items():
                previous_period_data[key] = self._get_numeric_value(var.get())
            
            if self.model.save_previous_period_data(self.company_id, self.period_int, previous_period_data):
                messagebox.showinfo("Éxito", 
                                  tr("save_success", 
                                     period=self.period_int, 
                                     company=self.company_name_str))
            else:
                messagebox.showerror("Error", 
                                   tr("save_error", 
                                      error="Error al conectar con la base de datos"))

        except Exception as e:
            logger.error(f"Error inesperado al guardar datos: {str(e)}")
            messagebox.showerror("Error", 
                               tr("save_error", error=str(e)))

    def load_data(self):
        """Carga los datos del período anterior desde la base de datos."""
        previous_period_data = self.model.load_previous_period_data(self.company_id, self.period_int)
        
        if previous_period_data:
            for key, var in self.entry_vars.items():
                if key in previous_period_data and previous_period_data[key] is not None:
                    var.set(str(previous_period_data[key]))
                else:
                    var.set("")
            
            messagebox.showinfo("Cargar Datos", tr("load_success", period=self.period_int))
        else:
            messagebox.showinfo("Cargar Datos", tr("load_empty", period=self.period_int))

    def _on_closing(self):
        """Maneja el cierre de la ventana para volver al menú principal."""
        self.destroy()
        self.parent_app.show_main_menu()