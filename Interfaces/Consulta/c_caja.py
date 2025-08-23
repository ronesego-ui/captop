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
        "window_title": "Consulta Caja - Flujo de Efectivo",
        "company_period": "Empresa y Período",
        "company": "Empresa:",
        "period": "Período:",
        "ingresos_confirmados": "Ingresos Confirmados",
        "ingresos_estimados": "INGRESOS ESTIMADOS",
        "total_ingresos": "Total Ingresos",
        "pagos_inversiones": "Por Pagos de inversiones",
        "pagos_pasivos_anteriores": "PAGOS PASIVOS PERIODO ANTERIOR (balance anterior)",
        "pagos_contado_confirmados": "PAGOS AL CONTADO DEL PERIODO, CONFIRMADOS",
        "pagos_estimados": "PAGOS ESTIMADOS DEL PERIODO",
        "total_egresos": "Total Egreso",
        "resumen_caja": "Resumen de Caja",
        "saldo_periodo": "SALDO DEL PERIODO",
        "saldo_inicial": "SALDO INICIAL",
        "saldo_caja_sobregiro": "SALDO CAJA/SOBREGIRO PERIODO",
        "back": "Volver al Menú Principal",
        "load_success": "Datos de caja cargados para el período {period}.",
        "load_empty": "No se encontraron datos de caja para el período {period} de esta empresa. Campos vacíos.",
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
class CashFlowModel:
    """Modelo para manejar los datos de flujo de efectivo."""
    
    def __init__(self, db_file: Path):
        """Inicializa el modelo con la ruta al archivo de base de datos."""
        self.db_file = db_file
        
    def get_connection(self):
        """Establece y devuelve una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def load_cash_flow(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        """Carga los datos de flujo de efectivo desde la base de datos."""
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
                    return payload.get("cash_flow_data", {})
                return None
        except Exception as e:
            logger.error(f"Error loading cash flow: {str(e)}")
            return None
            
    def get_initial_balance(self, company_id: int, period: int) -> float:
        """Obtiene el saldo inicial desde el balance."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM financial_statement WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, "BALANCE_SHEET")
                )
                row = cursor.fetchone()
                if row:
                    balance_data = json.loads(row["data"])
                    disponible_key = "activo_circulante_Disponible"
                    try:
                        return float(balance_data.get(disponible_key, 0.0))
                    except ValueError:
                        return 0.0
                return 0.0
        except Exception as e:
            logger.error(f"Error getting initial balance: {str(e)}")
            return 0.0

# ------------------------- Vista -------------------------
class CashFlowConsultaUI(tk.Toplevel):
    """Interfaz gráfica para la Consulta de Flujo de Efectivo."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        """Inicializa la ventana de Consulta de Flujo de Efectivo."""
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent.parent / "captop.db"
        self.model = CashFlowModel(db_file)
        
        # Inicializar variables
        self.display_vars = {}
        self.calculated_vars = {}
        
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.title(tr("window_title"))
        self.geometry("1200x800")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_company_period_section()
        self._create_cash_flow_sections()
        self._create_buttons()
        
    def _configure_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#DCDAD5')
        style.configure('TLabel', background='#DCDAD5', font=('Inter', 10))
        style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 11, 'bold'))
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
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

        # Mostrar nombre de la empresa (solo lectura)
        ttk.Label(frame, text=tr("company")).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=self.company_name_str, font=('Inter', 10, 'bold')).grid(
            row=0, column=1, padx=5, pady=2, sticky='w')
        
        # Mostrar período (solo lectura)
        ttk.Label(frame, text=tr("period")).grid(row=0, column=2, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=str(self.period_int), font=('Inter', 10, 'bold')).grid(
            row=0, column=3, padx=5, pady=2, sticky='w')
        
        frame.grid_columnconfigure(1, weight=1)

    def _create_cash_flow_sections(self):
        """Crea las secciones del flujo de efectivo."""
        content_frame = ttk.Frame(self.scrollable_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)  # Columna Ingresos
        content_frame.grid_columnconfigure(1, weight=1)  # Columna Egresos

        # Columna Ingresos
        ingresos_frame = ttk.Frame(content_frame)
        ingresos_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._create_ingresos_sections(ingresos_frame)

        # Columna Egresos
        egresos_frame = ttk.Frame(content_frame)
        egresos_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._create_egresos_sections(egresos_frame)

        # Sección Resumen
        self._create_summary_section()

    def _create_ingresos_sections(self, parent_frame):
        """Crea las secciones de ingresos."""
        # Ingresos Confirmados
        frame = ttk.LabelFrame(parent_frame, text=tr("ingresos_confirmados"), padding=(10, 5))
        frame.pack(fill="x", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = [
            "Préstamos de Corto Plazo aprobados", "Préstamos de Largo Plazo aprobados",
            "Aportes de Capital autorizados", "Retiros Depósitos a plazo (capital)",
            "Intereses Depósitos a plazo", "Venta Activos Fijos-Plantas",
            "Venta Activos Fijos-Oficinas", "Ingreso Indemnización de seguros reclamados",
            "Venta Bruta al contado entre empresas competidoras",
            "Cobro Cuentas por cobrar a empresas competidoras"
        ]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "ingresos_conf", i)

        # Ingresos Estimados
        frame = ttk.LabelFrame(parent_frame, text=tr("ingresos_estimados"), padding=(10, 5))
        frame.pack(fill="x", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = ["Ingresos por venta en el período", "Cobranza Cuentas por Cobrar"]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "ingresos_est", i)

        # Total Ingresos
        total_frame = ttk.Frame(parent_frame, padding=(0, 5))
        total_frame.pack(fill="x", padx=5, pady=5)
        total_frame.grid_columnconfigure(1, weight=1)
        self._create_total_row(total_frame, tr("total_ingresos"), "total_ingresos", 0)

    def _create_egresos_sections(self, parent_frame):
        """Crea las secciones de egresos."""
        # Por Pagos de inversiones
        frame = ttk.LabelFrame(parent_frame, text=tr("pagos_inversiones"), padding=(10, 5))
        frame.pack(fill="x", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = ["Plantas", "Muebles Máquinas y otros", "Terrenos", "Intangibles", "Depósitos a Plazo"]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "egresos_inv", i)

        # PAGOS PASIVOS PERIODO ANTERIOR
        frame = ttk.LabelFrame(parent_frame, text=tr("pagos_pasivos_anteriores"), padding=(10, 5))
        frame.pack(fill="x", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = [
            "Documentos Protestados + recargos", "Sobregiros Autorizados", "Banco Préstamos Corto Plazo",
            "Banco Porción del Largo Plazo", "Dividendos", "Intereses sobregiro",
            "Cuentas y Documentos por Pagar (Proveedores)", "Provisiones, multas y castigos",
            "Impuesto Compra-venta", "Impuesto a la Renta", "Otros pasivos circulantes(Pago a empresas Competidoras)",
            "Nota de Crédito"
        ]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "egresos_pasivos_ant", i)

        # PAGOS AL CONTADO DEL PERIODO, CONFIRMADOS
        frame = ttk.LabelFrame(parent_frame, text=tr("pagos_contado_confirmados"), padding=(10, 5))
        frame.pack(fill="x", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = [
            "Compras \"HOME\" a Empresas Competidoras", "Compras \"PROFESSIONAL\" a Empresas Competidoras",
            "Transporte HOME", "Transporte PROFESSIONAL", "Gastos Generales Fijos Producción",
            "Mantención Plantas", "Gastos Generales Fijos Ventas", "Remuneraciones Fijas Vendedores",
            "Publicidad", "Promociones Especiales", "Investigaciones de Mercado",
            "Gastos Generales Fijos Administración", "Remuneraciones Ejecutivos", "Seguros",
            "Multas y Castigos", "Intereses/Comisiones porción Préstamos Corto Plazo",
            "Intereses porción de Préstamos a Largo Plazo", "Costos Adicionales Producción autorizados"
        ]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "egresos_contado_conf", i)

        # PAGOS ESTIMADOS DEL PERIODO
        frame = ttk.LabelFrame(parent_frame, text=tr("pagos_estimados"), padding=(10, 5))
        frame.pack(fill="x", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = [
            "Remuneraciones Variables Producción", "Compras de Kits y PPA del período",
            "Patentes-Royalties", "Bodegaje", "Remuneraciones Variables Vendedores"
        ]
        for i, item in enumerate(items):
            self._create_display_row(frame, item, "egresos_est", i)

        # Total Egresos
        total_frame = ttk.Frame(parent_frame, padding=(0, 5))
        total_frame.pack(fill="x", padx=5, pady=5)
        total_frame.grid_columnconfigure(1, weight=1)
        self._create_total_row(total_frame, tr("total_egresos"), "total_egresos", 0)

    def _create_summary_section(self):
        """Crea la sección de resumen."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=tr("resumen_caja"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)
        frame.grid_columnconfigure(1, weight=1)

        self._create_total_row(frame, tr("saldo_periodo"), "saldo_periodo", 0)
        self._create_total_row(frame, tr("saldo_inicial"), "saldo_inicial", 1)
        self._create_total_row(frame, tr("saldo_caja_sobregiro"), "saldo_caja_sobregiro", 2)

    def _create_display_row(self, parent_frame, label_text, key_prefix, row_num):
        """Crea una fila con etiqueta y campo de solo lectura."""
        ttk.Label(parent_frame, text=label_text, anchor='w').grid(
            row=row_num, column=0, padx=5, pady=2, sticky='w')
        var = tk.StringVar(value="0.00")
        ttk.Label(parent_frame, textvariable=var, anchor='e', background='white', relief='solid', padding=2).grid(
            row=row_num, column=1, padx=5, pady=2, sticky='ew')
        self.display_vars[f"{key_prefix}_{label_text.replace(' ', '_').replace('/', '_').replace('.', '').replace(':', '')}"] = var
        return var

    def _create_total_row(self, parent_frame, label_text, key, row_num, is_bold=True):
        """Crea una fila para un total calculado."""
        font_style = ('Inter', 10, 'bold') if is_bold else ('Inter', 10)
        ttk.Label(parent_frame, text=label_text, font=font_style, anchor='w').grid(
            row=row_num, column=0, padx=5, pady=2, sticky='w')
        var = tk.StringVar(value="0.00")
        ttk.Label(parent_frame, textvariable=var, font=font_style, anchor='e').grid(
            row=row_num, column=1, padx=5, pady=2, sticky='ew')
        self.calculated_vars[key] = var
        return var

    def _create_buttons(self):
        """Crea los botones de acción."""
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        button_frame.pack(fill="x", padx=10, pady=10)
        button_frame.columnconfigure(0, weight=1)

        ttk.Button(button_frame, text=tr("back"), command=self._on_closing).grid(
            row=0, column=0, padx=5, pady=5, sticky='ew')

    def _load_initial_data(self):
        """Carga los datos del flujo de efectivo."""
        cash_flow_data = self.model.load_cash_flow(self.company_id, self.period_int)
        
        if cash_flow_data:
            # Rellenar los campos de visualización
            for key, var in self.display_vars.items():
                if key in cash_flow_data:
                    try:
                        var.set(f"{float(cash_flow_data[key]):,.2f}")
                    except ValueError:
                        var.set(str(cash_flow_data[key]))
            
            # Rellenar los campos calculados
            for key, var in self.calculated_vars.items():
                if key in cash_flow_data:
                    try:
                        var.set(f"{float(cash_flow_data[key]):,.2f}")
                    except ValueError:
                        var.set(str(cash_flow_data[key]))
            
            messagebox.showinfo("Cargar Caja", 
                              tr("load_success", period=self.period_int))
        else:
            messagebox.showinfo("Cargar Caja", 
                              tr("load_empty", period=self.period_int))

    def _on_closing(self):
        """Maneja el cierre de la ventana para volver al menú principal."""
        self.destroy()
        self.parent_app.show_main_menu()

# Función para abrir la interfaz desde el menú principal
def abrir_consulta_caja(parent_app, company_id: int, company_name: str, period: int):
    """Abre la interfaz de consulta de caja."""
    CashFlowConsultaUI(parent_app, company_id, company_name, period)