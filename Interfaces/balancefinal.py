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
        logging.FileHandler('balance_final.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Internacionalización
TRANSLATIONS = {
    "es": {
        "window_title": "Balance Final de la Empresa",
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
        "calculate": "Calcular Totales",
        "save": "Guardar Balance",
        "back": "Volver al Menú Principal",
        "save_success": "Balance final guardado para el período {period} de {company}.",
        "load_success": "Balance final cargado para el período {period}.",
        "load_empty": "No se encontraron datos de balance final para el período {period} de esta empresa. Campos vacíos.",
        "company_not_found": "Empresa no encontrada en la base de datos.",
        "save_error": "Error al guardar balance final: {error}",
        "db_error": "Error de Base de Datos",
        "invalid_period": "El período actual no es un número válido."
    }
}

CURRENT_LANGUAGE = "es"

def tr(key: str, **kwargs) -> str:
    """Obtiene la traducción para la clave dada y aplica formato."""
    return TRANSLATIONS[CURRENT_LANGUAGE].get(key, key).format(**kwargs)

# ------------------------- Modelo -------------------------
class FinalBalanceModel:
    """Modelo para manejar los datos del balance final."""
    
    def __init__(self, db_file: Path):
        """Inicializa el modelo con la ruta al archivo de base de datos."""
        self.db_file = db_file
        
    def get_connection(self):
        """Establece y devuelve una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_final_balance(self, company_id: int, period: int, data: Dict[str, Any]) -> bool:
        """Guarda los datos del balance final en la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO financial_statement (company_id, period, type, data) VALUES (?, ?, ?, ?)",
                    (company_id, period, "BALANCE_FINAL", json.dumps(data))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving final balance: {str(e)}")
            return False
            
    def load_final_balance(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        """Carga los datos del balance final desde la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM financial_statement WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, "BALANCE_FINAL")
                )
                row = cursor.fetchone()
                return json.loads(row["data"]) if row else None
        except Exception as e:
            logger.error(f"Error loading final balance: {str(e)}")
            return None

# ------------------------- Vista -------------------------
class FinalBalanceUI(tk.Toplevel):
    """Interfaz gráfica para el Balance Final."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        """Inicializa la ventana de Balance Final."""
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent / "captop.db"
        self.model = FinalBalanceModel(db_file)
        
        # Inicializar variables
        self.entry_vars = {}
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
        style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=2)
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
            self._create_input_row(frame, item, "activo_circulante", i)
        
        self._create_total_row(frame, "Total Activo Circulante", "activo_circulante_total", len(items))

        # Activo Fijo
        frame = ttk.LabelFrame(parent_frame, text=tr("activo_fijo"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = [
            "Edificios Administ/Venta", "Plantas", "Muebles/Maquina/Otros", "Terrenos",
            "Depreciacion del ejercicio", "Acum. pendiente Anteriores"
        ]
        for i, item in enumerate(items):
            self._create_input_row(frame, item, "activo_fijo", i)
        
        self._create_total_row(frame, "Total Activo Fijo Neto", "activo_fijo_total_neto", len(items))
        self._create_total_row(frame, "Total de Activo Fijo", "total_activo_fijo", len(items)+1)

        # Activos Intangibles
        frame = ttk.LabelFrame(parent_frame, text=tr("activo_intangible"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = ["Intangibles y otros Act Nom"]
        for i, item in enumerate(items):
            self._create_input_row(frame, item, "activo_intangible", i)

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
            self._create_input_row(frame, item, "pasivo_circulante", i)
        
        self._create_total_row(frame, "Total Pasivos Circulante", "pasivo_circulante_total", len(items))

        # Deudas Largo Plazo
        frame = ttk.LabelFrame(parent_frame, text=tr("deudas_largo_plazo"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        items = ["Deudas a largo plazo"]
        for i, item in enumerate(items):
            self._create_input_row(frame, item, "deudas_largo_plazo", i)
        
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
            self._create_input_row(frame, item, "patrimonio", i)
        
        self._create_total_row(frame, "Total Patrimonio", "total_patrimonio", len(items))

        # Total Pasivo y Patrimonio
        frame = ttk.LabelFrame(parent_frame, text=tr("total_pasivo_patrimonio"), padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        self._create_total_row(frame, "Total Pasivo", "total_pasivo_final", 0)
        self._create_total_row(frame, "Total Pasivo y Patrimonio", "total_pasivo_patrimonio_final", 1)

    def _create_input_row(self, parent_frame, label_text, key_prefix, row_num):
        """Crea una fila con etiqueta y campo de entrada."""
        normalized_label = self._normalize_key(label_text)
        
        ttk.Label(parent_frame, text=label_text, anchor='w').grid(
            row=row_num, column=0, padx=5, pady=2, sticky='w')
        var = tk.StringVar(value="")
        entry = ttk.Entry(parent_frame, textvariable=var, width=20)
        entry.grid(row=row_num, column=1, padx=5, pady=2, sticky='ew')
        
        key = f"{key_prefix}_{normalized_label}"
        self.entry_vars[key] = var
        return var

    def _create_total_row(self, parent_frame, label_text, key, row_num, is_bold=True):
        """Crea una fila para un total calculado."""
        font_style = ('Inter', 10, 'bold') if is_bold else ('Inter', 10)
        ttk.Label(parent_frame, text=label_text, font=font_style, anchor='w').grid(
            row=row_num, column=0, padx=5, pady=2, sticky='w')
        var = tk.StringVar(value="0.00")
        ttk.Label(parent_frame, textvariable=var, font=font_style, anchor='e').grid(
            row=row_num, column=1, padx=5, pady=2, sticky='ew')
        self.total_vars[key] = var
        return var

    def _create_buttons(self):
        """Crea los botones de acción."""
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        button_frame.pack(fill="x", padx=10, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text=tr("calculate"), command=self.calculate_totals).grid(
            row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text=tr("save"), command=self.save_final_balance).grid(
            row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text=tr("back"), command=self._on_closing).grid(
            row=0, column=2, padx=5, pady=5, sticky='ew')

    def _normalize_key(self, key: str) -> str:
        """Normalize a key to match our naming convention."""
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
                  .lower())

    def _get_float_value(self, key: str) -> float:
        """Obtiene el valor float de una variable de entrada con verificación robusta."""
        try:
            normalized_key = self._normalize_key(key)
            
            # First try exact match
            if normalized_key in self.entry_vars:
                value = self.entry_vars[normalized_key].get()
                return float(value) if value else 0.0
            elif normalized_key in self.total_vars:
                value = self.total_vars[normalized_key].get()
                return float(value.replace(',', '')) if value else 0.0
            
            # Try common variations for the specific missing keys
            key_variations = {
                'activo_fijo_acum_periodos_anteriores': [
                    'activo_fijo_acumulado_anteriores',
                    'activo_fijo_depreciacion_acumulada',
                    'activo_fijo_depreciacion_anteriores'
                ],
                'pasivo_circulante_notas_de_credito': [
                    'pasivo_circulante_notas_credito',
                    'pasivo_circulante_creditos',
                    'pasivo_circulante_notas'
                ]
            }
            
            if normalized_key in key_variations:
                for variation in key_variations[normalized_key]:
                    if variation in self.entry_vars:
                        value = self.entry_vars[variation].get()
                        return float(value) if value else 0.0
                    elif variation in self.total_vars:
                        value = self.total_vars[variation].get()
                        return float(value.replace(',', '')) if value else 0.0
            
            # Try partial match as last resort
            for existing_key in self.entry_vars:
                if normalized_key in existing_key or existing_key in normalized_key:
                    value = self.entry_vars[existing_key].get()
                    return float(value) if value else 0.0
                    
            for existing_key in self.total_vars:
                if normalized_key in existing_key or existing_key in normalized_key:
                    value = self.total_vars[existing_key].get()
                    return float(value.replace(',', '')) if value else 0.0
            
            logger.debug(f"Clave no encontrada: {normalized_key} (no se pudo encontrar alternativa)")
            return 0.0
            
        except ValueError as e:
            logger.debug(f"Error al convertir valor para clave {normalized_key}: {str(e)}")
            return 0.0

    def _load_initial_data(self):
        """Carga los datos iniciales del balance final."""
        balance_data = self.model.load_final_balance(self.company_id, self.period_int)
        
        if balance_data:
            for key, var in self.entry_vars.items():
                if key in balance_data:
                    var.set(str(balance_data[key]))
            
            for key, var in self.total_vars.items():
                if key in balance_data:
                    var.set(f"{float(balance_data[key]):,.2f}")
            
            messagebox.showinfo("Cargar Balance Final", tr("load_success", period=self.period_int))
        else:
            messagebox.showinfo("Cargar Balance Final", tr("load_empty", period=self.period_int))
        
        self.calculate_totals()

    def calculate_totals(self):
        """Calcula los totales del balance final con validación robusta."""
        try:
            # --- Activo Circulante ---
            total_ac = sum(self._get_float_value(key) for key in [
                "activo_circulante_Disponible", 
                "activo_circulante_Deposito_a_plazo_Valores_Neg",
                "activo_circulante_Deudores_por_Venta", 
                "activo_circulante_Estimac_Deudores_Incobrable",
                "activo_circulante_Materia_Prima", 
                "activo_circulante_Productos_en_Procesos",
                "activo_circulante_Productos_Transito_Maritimo", 
                "activo_circulante_Productos_Terminados",
                "activo_circulante_Otros_Activos_Circulante", 
                "activo_circulante_Cuentas_por_Cobrar_EEs_Competid"
            ])
            self.total_vars["activo_circulante_total"].set(f"{total_ac:,.2f}")

            # --- Activo Fijo Neto ---
            total_af_neto = sum(self._get_float_value(key) for key in [
                "activo_fijo_Edificios_Administ_Venta", 
                "activo_fijo_Plantas",
                "activo_fijo_Muebles_Maquina_Otros", 
                "activo_fijo_Terrenos"
            ])
            
            depreciacion = self._get_float_value("activo_fijo_Depreciacion_del_ejercicio")
            acum_depreciacion = self._get_float_value("activo_fijo_Acum_periodos_Anteriores")
            total_af_neto -= (depreciacion + acum_depreciacion)
            self.total_vars["activo_fijo_total_neto"].set(f"{total_af_neto:,.2f}")

            # --- Total Activo Fijo (incluye intangibles) ---
            intangibles = self._get_float_value("activo_intangible_Intangibles_y_otros_Act_Nom")
            total_activo_fijo_final = total_af_neto + intangibles
            self.total_vars["total_activo_fijo"].set(f"{total_activo_fijo_final:,.2f}")

            # --- Total Activo Final (circulante + fijo) ---
            total_activo_final = total_ac + total_activo_fijo_final
            self.total_vars["total_activo_final"].set(f"{total_activo_final:,.2f}")

            # --- Pasivo Circulante ---
            total_pc = sum(self._get_float_value(key) for key in [
                "pasivo_circulante_Deudas_por_sobregiro", 
                "pasivo_circulante_Documentos_Protestados",
                "pasivo_circulante_Prestamos_de_Corto_Plazo", 
                "pasivo_circulante_Vcto_a_Corto_Plazo_Deudas_Largo_Plazo",
                "pasivo_circulante_Dividendos_por_Pagar", 
                "pasivo_circulante_Intereses_por_Pagar",
                "pasivo_circulante_Ctas_y_Dctos_por_Pagar", 
                "pasivo_circulante_Otras_Provisiones",
                "pasivo_circulante_Impuestos_Compra_Venta", 
                "pasivo_circulante_Impuesto_a_la_Renta",
                "pasivo_circulante_Otros_Pasivos_Circulantes", 
                "pasivo_circulante_Notas_de_Credito"
            ])
            self.total_vars["pasivo_circulante_total"].set(f"{total_pc:,.2f}")

            # --- Deudas Largo Plazo ---
            total_dlp = self._get_float_value("deudas_largo_plazo_Deudas_a_largo_plazo")
            self.total_vars["total_deuda_largo_plazo"].set(f"{total_dlp:,.2f}")

            # --- Patrimonio ---
            total_patrimonio = sum(self._get_float_value(key) for key in [
                "patrimonio_Capital_Pagado", 
                "patrimonio_Resultado_Ejercicio_Anterior",
                "patrimonio_Dividendos_Pag_Periodo_Anterior", 
                "patrimonio_Dividendos_Declarados_Periodo",
                "patrimonio_Resultado_del_Ejercicio"
            ])
            self.total_vars["total_patrimonio"].set(f"{total_patrimonio:,.2f}")

            # --- Total Pasivo (Circulante + Largo Plazo) ---
            total_pasivo = total_pc + total_dlp
            self.total_vars["total_pasivo_final"].set(f"{total_pasivo:,.2f}")

            # --- Total Pasivo y Patrimonio ---
            total_pasivo_y_patrimonio = total_pasivo + total_patrimonio
            self.total_vars["total_pasivo_patrimonio_final"].set(f"{total_pasivo_y_patrimonio:,.2f}")

        except Exception as e:
            logger.error(f"Error al calcular totales: {str(e)}")
            messagebox.showerror("Error", f"Error al calcular totales: {str(e)}")

    def save_final_balance(self):
        """Guarda los datos del balance final en la base de datos."""
        try:
            balance_data = {}
            
            # Recolectar datos de entrada
            for key, var in self.entry_vars.items():
                try:
                    balance_data[key] = float(var.get() or 0.0)
                except ValueError:
                    balance_data[key] = var.get()
            
            # Recolectar datos de totales calculados
            for key, var in self.total_vars.items():
                try:
                    balance_data[key] = float(var.get().replace(',', '') or 0.0)
                except ValueError:
                    balance_data[key] = var.get()

            # Guardar en la base de datos
            if self.model.save_final_balance(self.company_id, self.period_int, balance_data):
                messagebox.showinfo("Éxito", 
                                  tr("save_success", 
                                     period=self.period_int, 
                                     company=self.company_name_str))
            else:
                messagebox.showerror("Error", 
                                   tr("save_error", 
                                      error="Error al conectar con la base de datos"))

        except Exception as e:
            logger.error(f"Error inesperado al guardar balance final: {str(e)}")
            messagebox.showerror("Error", 
                               tr("save_error", error=str(e)))

    def _on_closing(self):
        """Maneja el cierre de la ventana para volver al menú principal."""
        self.destroy()
        self.parent_app.show_main_menu()