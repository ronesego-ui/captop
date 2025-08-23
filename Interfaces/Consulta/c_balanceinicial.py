import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# ------------------------- Configuración Inicial -------------------------
# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Internacionalización
TRANSLATIONS = {
    "es": {
        "window_title": "Consulta Balance Inicial de la Empresa",
        "company_period": "Empresa y Período",
        "company": "Empresa:",
        "period": "Período:",
        "activo_circulante": "Activo Circulante",
        "activo_fijo": "Activo Fijo",
        "activo_intangible": "Activos Intangibles",
        "total_activo": "Total Activo",
        "pasivo_circulante": "Pasivo Circulante",
        "deudas_largo_plazo": "Deudas Largo Plazo",
        "patrimonio": "Patrimonio",
        "total_pasivo_patrimonio": "Total Pasivo y Patrimonio",
        "back": "Volver al Menú Principal",
        "load_success": "Balance cargado para el período {period}.",
        "load_empty": "No se encontraron datos de balance para el período {period} de esta empresa. Campos vacíos.",
        "company_not_found": "Empresa no encontrada en la base de datos.",
        "db_error": "Error de Base de Datos",
        "invalid_period": "El período actual no es un número válido."
    }
}

CURRENT_LANGUAGE = "es"

def tr(key: str, **kwargs) -> str:
    """Obtiene la traducción para la clave dada y aplica formato."""
    return TRANSLATIONS[CURRENT_LANGUAGE].get(key, key).format(**kwargs)

# ------------------------- Modelo -------------------------
class BalanceSheetModel:
    """Modelo para manejar los datos del balance inicial."""
    
    def __init__(self, db_file: Path):
        """Inicializa el modelo con la ruta al archivo de base de datos."""
        self.db_file = db_file
    
    def get_connection(self):
        """Establece y devuelve una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def load_balance_sheet(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        """Carga los datos del balance desde la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM financial_statement WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, "BALANCE_SHEET")
                )
                row = cursor.fetchone()
                return json.loads(row["data"]) if row else None
        except Exception as e:
            logger.error(f"Error loading balance sheet: {str(e)}")
            return None

# ------------------------- Vista -------------------------
class BalanceSheetConsultaUI(tk.Toplevel):
    """Interfaz gráfica para la Consulta del Balance Inicial."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        """Inicializa la ventana de Consulta de Balance Inicial."""
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent.parent / "captop.db"
        self.model = BalanceSheetModel(db_file)
        
        # Inicializar variables
        self.label_vars = {}
        self.total_vars = {}
        
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.title(tr("window_title"))
        self.geometry("1000x700")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_company_period_section()
        self._create_balance_sections()
        self._create_buttons()
        
    def _configure_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#DCDAD5')
        style.configure('TLabel', background='#DCDAD5', font=('Inter', 10))
        style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 11, 'bold'))
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        style.configure('TCanvas', background='#DCDAD5')
        style.configure('TScrollbar', background='#DCDAD5')

        style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
        
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

    def _create_balance_sections(self):
        """Crea las secciones del balance."""
        content_frame = ttk.Frame(self.scrollable_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Columna Activo
        activo_frame = ttk.Frame(content_frame)
        activo_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._create_activo_sections(activo_frame)

        # Columna Pasivo/Patrimonio
        pasivo_frame = ttk.Frame(content_frame)
        pasivo_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._create_pasivo_patrimonio_sections(pasivo_frame)

    def _create_activo_sections(self, parent_frame):
        """Crea las secciones de activo."""
        # Activo Circulante
        frame = ttk.LabelFrame(parent_frame, text=tr("activo_circulante"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = [
            "Disponible", "Deposito a plazo/Valores Neg", "Deudores por Venta",
            "Estimac Deudores Incobrable", "Materia Prima", "Productos en Procesos",
            "Productos Transito Maritimo", "Productos Terminados", "Otros Activos Circulante",
            "Cuentas por Cobrar EEs Competid"
        ]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "activo_circulante", i)
        
        self._create_total_row(frame, "Total Activo Circulante", "activo_circulante_total", len(items))

        # Activo Fijo
        frame = ttk.LabelFrame(parent_frame, text=tr("activo_fijo"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = [
            "Edificios Administ/Venta", "Plantas", "Muebles/Maquina/Otros", "Terrenos",
            "Depreciacion del ejercicio", "Acum. periodos Anteriores"

        ]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "activo_fijo", i)
        
        self._create_total_row(frame, "Total Activo Fijo Neto", "activo_fijo_total_neto", len(items))
        self._create_total_row(frame, "Total de Activo Fijo", "total_activo_fijo", len(items)+1)

        # Activos Intangibles
        frame = ttk.LabelFrame(parent_frame, text=tr("activo_intangible"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = ["Intangibles y otros Act Nom"]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "activo_intangible", i)

        # Total Activo
        frame = ttk.LabelFrame(parent_frame, text=tr("total_activo"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        self._create_total_row(frame, "Total Activo", "total_activo_final", 0)

    def _create_pasivo_patrimonio_sections(self, parent_frame):
        """Crea las secciones de pasivo y patrimonio."""
        # Pasivo Circulante
        frame = ttk.LabelFrame(parent_frame, text=tr("pasivo_circulante"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = [
            "Deudas por sobregiro", "Documentos Protestados", "Prestamos de Corto Plazo",
            "Vcto a Corto Plazo/Deudas Largo Plazo", "Dividendos por Pagar", "Intereses por Pagar",
            "Ctas y Dctos por Pagar", "Otras Provisiones", "Impuestos Compra-Venta",
            "Impuesto a la Renta", "Otros Pasivos Circulantes", "Notas de Crédito"
        ]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "pasivo_circulante", i)
        
        self._create_total_row(frame, "Total Pasivos Circulante", "pasivo_circulante_total", len(items))

        # Deudas Largo Plazo
        frame = ttk.LabelFrame(parent_frame, text=tr("deudas_largo_plazo"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = ["Deudas a largo plazo"]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "deudas_largo_plazo", i)
        
        self._create_total_row(frame, "Total Deuda Largo Plazo", "total_deuda_largo_plazo", len(items))

        # Patrimonio
        frame = ttk.LabelFrame(parent_frame, text=tr("patrimonio"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = [
            "Capital Pagado", "Resultado Ejercicio Anterior", "Dividendos Pag Periodo Anterior",
            "Dividendos Declarados Periodo", "Resultado del Ejercicio"
        ]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "patrimonio", i)
        
        self._create_total_row(frame, "Total Patrimonio", "total_patrimonio", len(items))

        # Total Pasivo
        frame = ttk.LabelFrame(parent_frame, text="Total Pasivo", padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        self._create_total_row(frame, "Total Pasivo", "total_pasivo_final", 0)

        # Total Pasivo y Patrimonio
        frame = ttk.LabelFrame(parent_frame, text=tr("total_pasivo_patrimonio"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        self._create_total_row(frame, "Total Pasivo y Patrimonio", "total_pasivo_patrimonio_final", 0)

    def _create_display_row(self, parent, label_text, prefix, row):
        """Crea una fila con etiqueta y campo de solo lectura."""
        # Normalizar el nombre para la variable
        var_name = f"{prefix}_{label_text.replace(' ', '_').replace('/', '_')}"
        
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=2, sticky='w')
        
        # Crear variable y etiqueta para mostrar el valor
        var = tk.StringVar(value="0.00")
        self.label_vars[var_name] = var
        
        # Crear etiqueta para mostrar el valor
        value_label = ttk.Label(parent, textvariable=var, font=('Inter', 10), background='white', relief='solid', padding=(5, 2))
        value_label.grid(row=row, column=1, padx=5, pady=2, sticky='ew')

    def _create_total_row(self, parent, label_text, var_name, row):
        """Crea una fila para mostrar un total."""
        ttk.Label(parent, text=label_text, font=('Inter', 10, 'bold')).grid(
            row=row, column=0, padx=5, pady=2, sticky='w')
        
        var = tk.StringVar(value="0.00")
        self.total_vars[var_name] = var
        
        ttk.Label(parent, textvariable=var, font=('Inter', 10, 'bold'), background='white', relief='solid', padding=(5, 2)).grid(
            row=row, column=1, padx=5, pady=2, sticky='ew')

    def _create_buttons(self):
        """Crea los botones de la interfaz."""
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(
            button_frame, 
            text=tr("back"), 
            command=self._on_closing
        ).pack(side="right", padx=5)

    def _load_initial_data(self):
        """Carga los datos iniciales del balance."""
        balance_data = self.model.load_balance_sheet(self.company_id, self.period_int)
        
        if balance_data:
            logger.info("Datos encontrados en base de datos")
            for key, var in self.label_vars.items():
                if key in balance_data:
                    var.set(str(balance_data[key]))
            
            for key, var in self.total_vars.items():
                if key in balance_data:
                    var.set(f"{float(balance_data[key]):,.2f}")
            
            messagebox.showinfo("Cargar Balance", tr("load_success", period=self.period_int))
        else:
            logger.info("No se encontraron datos en base de datos")
            messagebox.showinfo("Cargar Balance", tr("load_empty", period=self.period_int))

    def _get_float_value(self, key):
        """Obtiene el valor flotante de una variable, con manejo de errores."""
        try:
            if key in self.label_vars:
                return float(self.label_vars[key].get() or 0)
            return 0.0
        except ValueError:
            return 0.0

    def _on_closing(self):
        """Maneja el cierre de la ventana para volver al menú principal."""
        self.destroy()
        self.parent_app.show_main_menu()

# Función para abrir la interfaz desde el menú principal
def abrir_consulta_balance_inicial(parent_app, company_id: int, company_name: str, period: int):
    """Abre la interfaz de consulta de balance inicial."""
    BalanceSheetConsultaUI(parent_app, company_id, company_name, period)