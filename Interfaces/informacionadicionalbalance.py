# informacionadicionalbalance.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# ------------------------- Configuración Inicial -------------------------
logger = logging.getLogger(__name__)

# ------------------------- Modelo -------------------------
class AdditionalBalanceInfoModel:
    """Modelo para manejar la información adicional del balance."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_additional_info(self, company_id: int, period: int, data: Dict[str, Any]) -> bool:
        """Guarda los datos de información adicional en la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO financial_statement (company_id, period, type, data) VALUES (?, ?, ?, ?)",
                    (company_id, period, "ADDITIONAL_BALANCE_INFO", json.dumps(data))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving additional balance info: {str(e)}")
            return False
            
    def load_additional_info(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        """Carga los datos de información adicional desde la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM financial_statement WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, "ADDITIONAL_BALANCE_INFO")
                )
                row = cursor.fetchone()
                return json.loads(row["data"]) if row else None
        except Exception as e:
            logger.error(f"Error loading additional balance info: {str(e)}")
            return None

# ------------------------- Vista -------------------------
class AdditionalBalanceInfoUI(tk.Toplevel):
    """Interfaz gráfica para la Información Adicional del Balance."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent / "captop.db"
        self.model = AdditionalBalanceInfoModel(db_file)
        
        # Inicializar variables
        self.entry_vars = {}
        
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.title("Información Adicional del Balance")
        self.geometry("800x700")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_header()
        self._create_info_section()
        self._create_market_section()
        self._create_financial_section()
        self._create_buttons()
        
    def _configure_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#DCDAD5')
        style.configure('TLabel', background='#DCDAD5', font=('Inter', 9))
        style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 10, 'bold'))
        style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=2, width=15)
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
        style.configure('Header.TLabel', font=('Inter', 14, 'bold'), background='#DCDAD5')
        style.configure('Section.TLabel', font=('Inter', 11, 'bold'), background='#DCDAD5')
        style.configure('Bold.TLabel', font=('Inter', 9, 'bold'))
        style.configure('Right.TLabel', anchor='e')
        
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
        
    def _create_header(self):
        """Crea el encabezado con información de empresa y período."""
        header_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(header_frame, text="INFORMACION ADICIONAL BALANCE", 
                 style='Header.TLabel').pack(fill="x", pady=(0, 10))
        
        # Empresa y período
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill="x", pady=5)
        
        ttk.Label(info_frame, text="Empresa:", font=('Inter', 10, 'bold')).grid(
            row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text=self.company_name_str, font=('Inter', 10)).grid(
            row=0, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(info_frame, text="Período:", font=('Inter', 10, 'bold')).grid(
            row=0, column=2, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text=str(self.period_int), font=('Inter', 10)).grid(
            row=0, column=3, padx=5, pady=2, sticky='w')
            
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(3, weight=1)
        
    def _create_info_section(self):
        """Crea la sección principal de información adicional."""
        section_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # Lista de campos con sus etiquetas y unidades
        fields = [
            ("reclamos_notas_credito", "Reclamos de Notas de Crédito del Período", ""),
            ("linea_sobregiro", "Línea de Sobregiro Autorizada por el Banco", ""),
            ("traspaso_corto_plazo", "Traspaso a Corto Plazo de la Deuda Largo Plazo", ""),
            ("plantas_vida_util", "Plantas que Terminan Su Vida Util en el Período (Valor)", ""),
            ("muebles_vida_util", "Muebles que Terminan Su Vida Util en el Período (Valor)", ""),
            ("traspaso_activo_intangible", "Traspaso a Activo Fijo como Intangible", ""),
            ("amortizaciones_intangible", "Amortizaciones Intangible", ""),
            ("reclamo_seguro_mercaderias", "Reclamo Seguro Mercaderías", ""),
            ("reclamo_seguro_edificios", "Reclamo Seguro Edificios", ""),
            ("reclamo_seguro_plantas", "Reclamo Seguro Plantas", ""),
            ("intereses_ganados", "Intereses Ganados Devengados en el período", ""),
            ("dividendos_declarados", "Dividendos Declarados del período", ""),
            ("provisiones_adicionales", "Provisiones adicionales período [pasivo/pérdida]", ""),
            ("venta_bruta_credito_empresas", "Venta Bruta al crédito entre empresas competidoras", ""),
            ("impuesto_ventas_empresas", "Impuesto por ventas e empresas competidoras", ""),
            ("ajuste_impuesto_plena", "Ajuste Impuesto a la Plena períodos anteriores (+/-)", ""),
            ("compra_bruta_home_credito", "Compra Bruta 'HOME' al Crédito Empresas Competidoras", ""),
            ("compra_bruta_pro_credito", "Compra Bruta 'PROFESSIONAL' al Crédito Empresas Competidoras", ""),
            ("perdidas_tributarias", "Pérdidas Tributarias acumuladas", ""),
            ("remuneracion_variable", "Remuneraciones variable promedio unitario Producción", "US$"),
            ("costo_variable_home", "Costo Variable unitario Producción del Período HOME", "US$"),
            ("costo_variable_pro", "Costo Variable unitario Producción del Período PROFESSIONAL", "US$"),
            ("costo_variable_terminado_home", "Costo Variable unitario Productos Terminados HOME", "US$"),
            ("costo_variable_terminado_pro", "Costo Variable unitario Productos Terminados PROFESSIONAL", "US$"),
            ("tasa_impuesto_renta", "Tasa Impuesto a la Renta", "%"),
            ("tasa_dividendos", "Tasa distribución de Dividendos", "%"),
        ]
        
        for i, (key, label, unit) in enumerate(fields):
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=2)
            
            # Etiqueta
            ttk.Label(row_frame, text=label, width=60, anchor='w').grid(row=0, column=0, sticky='w')
            
            # Entrada
            var = tk.StringVar(value="")
            entry = ttk.Entry(row_frame, textvariable=var, width=15)
            entry.grid(row=0, column=1, padx=(10, 5))
            self.entry_vars[key] = var
            
            # Unidad
            if unit:
                ttk.Label(row_frame, text=unit).grid(row=0, column=2, sticky='w')
            
            row_frame.columnconfigure(0, weight=1)
        
    def _create_market_section(self):
        """Crea la sección de participación de mercado."""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text="PARTICIPACIÓN DE MERCADO", 
                                      padding=(10, 10))
        section_frame.pack(fill="x", padx=10, pady=10)
        
        fields = [
            ("participacion_mercado_usd_home", "Participación de Mercado en US$ + HOME", ""),
            ("participacion_mercado_usd_pro", "Participación de Mercado en US$ - PROFESSIONAL", ""),
            ("participacion_mercado_ud_home", "Participación de Mercado en Unidades + HOME", ""),
            ("participacion_mercado_ud_pro", "Participación de Mercado en Unidades - PROFESSIONAL", ""),
            ("rendimiento", "Rendimiento", "%"),
        ]
        
        for i, (key, label, unit) in enumerate(fields):
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row_frame, text=label, width=50, anchor='w').grid(row=0, column=0, sticky='w')
            
            var = tk.StringVar(value="")
            entry = ttk.Entry(row_frame, textvariable=var, width=15)
            entry.grid(row=0, column=1, padx=(10, 5))
            self.entry_vars[key] = var
            
            if unit:
                ttk.Label(row_frame, text=unit).grid(row=0, column=2, sticky='w')
            
            row_frame.columnconfigure(0, weight=1)
        
    def _create_financial_section(self):
        """Crea la sección de información financiera final."""
        section_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        section_frame.pack(fill="x", padx=10, pady=10)
        
        fields = [
            ("ventas_totales", "Ventas Totales del período", ""),
            ("resultado_periodo", "Resultado del período", ""),
            ("situacion_tesoreria", "Situación de Tesorería", ""),
            ("disponible", "Disponible", ""),
        ]
        
        for i, (key, label, unit) in enumerate(fields):
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row_frame, text=label, width=40, anchor='w', style='Bold.TLabel').grid(row=0, column=0, sticky='w')
            
            var = tk.StringVar(value="")
            entry = ttk.Entry(row_frame, textvariable=var, width=15)
            entry.grid(row=0, column=1, padx=(10, 5))
            self.entry_vars[key] = var
            
            if unit:
                ttk.Label(row_frame, text=unit).grid(row=0, column=2, sticky='w')
            
            row_frame.columnconfigure(0, weight=1)
        
        # Campos finales especiales
        special_fields = [
            ("sobregiro_estimado", "Sobregiro Estimado", ""),
            ("prestamos_estimados", "Préstamos Estimados", ""),
        ]
        
        for key, label, unit in special_fields:
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(row_frame, text=label, font=('Inter', 10, 'bold'), width=30, anchor='w').grid(row=0, column=0, sticky='w')
            
            var = tk.StringVar(value="")
            entry = ttk.Entry(row_frame, textvariable=var, width=15)
            entry.grid(row=0, column=1, padx=(10, 5))
            self.entry_vars[key] = var
            
            if unit:
                ttk.Label(row_frame, text=unit).grid(row=0, column=2, sticky='w')
        
    def _create_buttons(self):
        """Crea los botones de acción."""
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 20))
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Calcular", 
                  command=self.calculate_values).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Guardar", 
                  command=self.save_data).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Volver al Menú Principal", 
                  command=self._on_closing).pack(side="right", padx=5, pady=5)
        
    def _load_initial_data(self):
        """Carga los datos iniciales desde la base de datos."""
        additional_info = self.model.load_additional_info(self.company_id, self.period_int)
        
        if additional_info:
            for key, var in self.entry_vars.items():
                if key in additional_info:
                    var.set(str(additional_info[key]))
    
    def calculate_values(self):
        """Calcula los valores (placeholder)."""
        # Esta función sería implementada con la lógica de negocio real
        messagebox.showinfo("Información", "Los cálculos se realizarán según la lógica de negocio específica")
        
    def save_data(self):
        """Guarda los datos en la base de datos."""
        try:
            data = {}
            for key, var in self.entry_vars.items():
                value = var.get()
                # Intentar convertir a número si es posible
                try:
                    data[key] = float(value) if value else 0.0
                except ValueError:
                    data[key] = value  # Guardar como cadena si no es convertible

            if self.model.save_additional_info(self.company_id, self.period_int, data):
                messagebox.showinfo("Éxito", 
                                  f"Datos guardados para el período {self.period_int} de {self.company_name_str}")
            else:
                messagebox.showerror("Error", "Error al guardar los datos en la base de datos")
        except Exception as e:
            logger.error(f"Error inesperado al guardar: {str(e)}")
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def _on_closing(self):
        """Maneja el cierre de la ventana para volver al menú principal."""
        self.destroy()
        self.parent_app.show_main_menu()


# Función para abrir esta interfaz desde el menú principal
def abrir_informacion_adicional_balance(parent_app, company_id: int, company_name: str, period: int):
    AdditionalBalanceInfoUI(parent_app, company_id, company_name, period)