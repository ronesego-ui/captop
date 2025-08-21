# ventasporpais.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# ------------------------- Configuración Inicial -------------------------
logger = logging.getLogger(__name__)

# Mapeo de países
PAISES = {
    "A": "Argentina",
    "B": "Brasil",
    "C": "Chile",
    "D": "Colombia",
    "E": "México"
}

# ------------------------- Modelo -------------------------
class SalesByCountryModel:
    """Modelo para manejar las ventas por país."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_sales_data(self, company_id: int, period: int, model: str, data: Dict[str, Any]) -> bool:
        """Guarda los datos de ventas por país en la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO financial_statement (company_id, period, type, data) VALUES (?, ?, ?, ?)",
                    (company_id, period, f"SALES_{model}", json.dumps(data))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving sales data for {model}: {str(e)}")
            return False
            
    def load_sales_data(self, company_id: int, period: int, model: str) -> Optional[Dict[str, Any]]:
        """Carga los datos de ventas por país desde la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM financial_statement WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, f"SALES_{model}")
                )
                row = cursor.fetchone()
                return json.loads(row["data"]) if row else None
        except Exception as e:
            logger.error(f"Error loading sales data for {model}: {str(e)}")
            return None

# ------------------------- Vista -------------------------
class SalesByCountryUI(tk.Toplevel):
    """Interfaz gráfica para las Ventas por País."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent / "captop.db"
        self.model = SalesByCountryModel(db_file)
        
        # Inicializar variables
        self.entry_vars = {}
        self.current_model = tk.StringVar(value="HOME")
        
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.title("Ventas por País")
        self.geometry("1000x800")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_header()
        self._create_model_selector()
        self._create_sales_sections()
        self._create_additional_info()
        self._create_buttons()
        
    def _configure_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#DCDAD5')
        style.configure('TLabel', background='#DCDAD5', font=('Inter', 9))
        style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 10, 'bold'))
        style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=2, width=8)
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        style.configure('TRadiobutton', font=('Inter', 10, 'bold'))
        style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
        style.configure('Header.TLabel', font=('Inter', 14, 'bold'), background='#DCDAD5')
        style.configure('Section.TLabel', font=('Inter', 11, 'bold'), background='#DCDAD5')
        style.configure('Subsection.TLabel', font=('Inter', 10, 'bold'))
        style.configure('Bold.TLabel', font=('Inter', 9, 'bold'))
        style.configure('Center.TLabel', anchor='center')
        
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
        
        ttk.Label(header_frame, text="JUEGO DE EMPRESAS - COMPUTADORAS", 
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
        
    def _create_model_selector(self):
        """Crea el selector de modelo (HOME/PROFESSIONAL)."""
        selector_frame = ttk.Frame(self.scrollable_frame, padding=(10, 5))
        selector_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(selector_frame, text="Modelo:", font=('Inter', 10, 'bold')).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            selector_frame, text="HOME", 
            variable=self.current_model, value="HOME",
            command=self._switch_model
        ).pack(side="left", padx=10)
        
        ttk.Radiobutton(
            selector_frame, text="PROFESSIONAL", 
            variable=self.current_model, value="PROFESSIONAL",
            command=self._switch_model
        ).pack(side="left", padx=10)
        
    def _create_sales_sections(self):
        """Crea las secciones de ventas por país."""
        # Contenedor principal
        container = ttk.Frame(self.scrollable_frame)
        container.pack(fill="x", padx=10, pady=10)
        
        # Sección de ventas de unidades
        units_frame = ttk.LabelFrame(container, text="VENTAS DE UNIDADES", padding=10)
        units_frame.pack(fill="x", pady=5)
        self._create_country_table(units_frame, "unidades", ["TO", "CO", "CO", "Total por País", "Total del Continente"])
        
        # Sección de ventas en valores
        values_frame = ttk.LabelFrame(container, text="VENTAS EN VALORES (US$)", padding=10)
        values_frame.pack(fill="x", pady=5)
        
        # Subsección de venta bruta
        ttk.Label(values_frame, text="VENTA BRUTA:", font=('Inter', 9, 'bold')).pack(anchor='w', pady=(0, 5))
        self._create_country_table(values_frame, "venta_bruta", ["TO", "CO", "CO", "Total por país", "Total en el Continente"])
        
        # Subsección de venta neta
        ttk.Label(values_frame, text="VENTA NETA:", font=('Inter', 9, 'bold')).pack(anchor='w', pady=(10, 5))
        self._create_country_table(values_frame, "venta_neta", ["TO", "CO", "CO", "Total por país", "Total en el Continente"])
        
        # Sección de impuestos
        taxes_frame = ttk.LabelFrame(container, text="IMPUESTO COMPRA-VENTA", padding=10)
        taxes_frame.pack(fill="x", pady=5)
        self._create_country_table(taxes_frame, "impuesto", ["Total por país", "Total en el Continente"])
        
        # Sección de publicidad
        ads_frame = ttk.LabelFrame(container, text="INVERSIÓN EN PUBLICIDAD (US$)", padding=10)
        ads_frame.pack(fill="x", pady=5)
        self._create_country_table(ads_frame, "publicidad", ["Total por país", "Total del Continente"])
        
    def _create_country_table(self, parent, section_prefix, rows):
        """Crea una tabla para una sección específica con países."""
        # Encabezados de países
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Columna vacía para las etiquetas de fila
        ttk.Label(header_frame, width=20).pack(side="left")
        
        # Encabezados de países
        for pais in ["A", "B", "C", "D", "E"]:
            frame = ttk.Frame(header_frame)
            frame.pack(side="left", padx=5, fill="x", expand=True)
            ttk.Label(frame, text=f"{pais}\n{PAISES[pais]}", 
                     style='Center.TLabel', justify='center').pack()
        
        # Total (si aplica)
        if "Total" in rows[0]:
            frame = ttk.Frame(header_frame)
            frame.pack(side="left", padx=5, fill="x", expand=True)
            ttk.Label(frame, text="Total", style='Center.TLabel').pack()
        
        # Filas de datos
        for i, row_label in enumerate(rows):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill="x", pady=2)
            
            # Etiqueta de fila
            ttk.Label(row_frame, text=row_label, width=20, anchor='w').pack(side="left")
            
            # Campos para cada país
            for pais in ["A", "B", "C", "D", "E"]:
                frame = ttk.Frame(row_frame)
                frame.pack(side="left", padx=5, fill="x", expand=True)
                
                var = tk.StringVar(value="0")
                entry = ttk.Entry(frame, textvariable=var, width=8, justify='center')
                entry.pack(fill="x")
                
                # Almacenar variable con clave única
                key = f"{self.current_model.get()}_{section_prefix}_{row_label}_{pais}"
                self.entry_vars[key] = var
            
            # Campo para total (si aplica)
            if "Total" in rows[0] and "Total" not in row_label:
                frame = ttk.Frame(row_frame)
                frame.pack(side="left", padx=5, fill="x", expand=True)
                
                var = tk.StringVar(value="0")
                ttk.Label(frame, textvariable=var, 
                         background='white', relief='solid', 
                         anchor='center', padding=2).pack(fill="x")
                
                key = f"{self.current_model.get()}_{section_prefix}_{row_label}_total"
                self.entry_vars[key] = var
    
    def _create_additional_info(self):
        """Crea la sección de información adicional."""
        container = ttk.Frame(self.scrollable_frame)
        container.pack(fill="x", padx=10, pady=10)
        
        # Nota
        note_frame = ttk.LabelFrame(container, text="NOTA", padding=10)
        note_frame.pack(fill="x", pady=5)
        
        note_text = "Los gastos de publicidad en medios continentales [radio y cine] se consideran en Alandia, aunque es continental."
        ttk.Label(note_frame, text=note_text, wraplength=800, justify='left').pack(anchor='w')
        
        # Condiciones de crédito
        credit_frame = ttk.LabelFrame(container, text="CONDICIONES DE CRÉDITO", padding=10)
        credit_frame.pack(fill="x", pady=5)
        
        # Encabezados
        header_frame = ttk.Frame(credit_frame)
        header_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(header_frame, width=20).pack(side="left")
        
        for pais in ["A", "B", "C", "D", "E"]:
            frame = ttk.Frame(header_frame)
            frame.pack(side="left", padx=5, fill="x", expand=True)
            ttk.Label(frame, text=f"{pais}\n{PAISES[pais]}", 
                     style='Center.TLabel', justify='center').pack()
        
        # Fila de datos
        row_frame = ttk.Frame(credit_frame)
        row_frame.pack(fill="x", pady=2)
        
        ttk.Label(row_frame, text="Condiciones", width=20, anchor='w').pack(side="left")
        
        for pais in ["A", "B", "C", "D", "E"]:
            frame = ttk.Frame(row_frame)
            frame.pack(side="left", padx=5, fill="x", expand=True)
            
            var = tk.StringVar(value="0")
            entry = ttk.Entry(frame, textvariable=var, width=8, justify='center')
            entry.pack(fill="x")
            
            key = f"{self.current_model.get()}_credito_{pais}"
            self.entry_vars[key] = var
        
    def _create_buttons(self):
        """Crea los botones de acción."""
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 20))
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Calcular Totales", 
                  command=self.calculate_totals).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Guardar", 
                  command=self.save_data).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Volver al Menú Principal", 
                  command=self._on_closing).pack(side="right", padx=5, pady=5)
        
    def _switch_model(self):
        """Cambia entre los modelos HOME y PROFESSIONAL."""
        self._load_initial_data()
        
    def _load_initial_data(self):
        """Carga los datos iniciales para el modelo actual."""
        model = self.current_model.get()
        sales_data = self.model.load_sales_data(self.company_id, self.period_int, model)
        
        if sales_data:
            for key, var in self.entry_vars.items():
                if key.startswith(f"{model}_") and key in sales_data:
                    var.set(str(sales_data[key]))
    
    def calculate_totals(self):
        """Calcula los totales para cada sección (placeholder)."""
        # Esta función sería implementada con la lógica de negocio real
        messagebox.showinfo("Información", "Los cálculos de totales se realizarán según la lógica de negocio específica")
        
    def save_data(self):
        """Guarda los datos en la base de datos."""
        try:
            model = self.current_model.get()
            sales_data = {}
            
            # Recolectar solo los datos relevantes para el modelo actual
            for key, var in self.entry_vars.items():
                if key.startswith(f"{model}_"):
                    try:
                        sales_data[key] = float(var.get() or 0.0)
                    except ValueError:
                        sales_data[key] = var.get()

            # Guardar en la base de datos
            if self.model.save_sales_data(self.company_id, self.period_int, model, sales_data):
                messagebox.showinfo("Éxito", 
                                  f"Datos de {model} guardados para el período {self.period_int}")
            else:
                messagebox.showerror("Error", "Error al guardar los datos en la base de datos")

        except Exception as e:
            logger.error(f"Error inesperado al guardar datos: {str(e)}")
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def _on_closing(self):
        """Maneja el cierre de la ventana para volver al menú principal."""
        self.destroy()
        self.parent_app.show_main_menu()


# Función para abrir esta interfaz desde el menú principal
def abrir_ventas_por_pais(parent_app, company_id: int, company_name: str, period: int):
    SalesByCountryUI(parent_app, company_id, company_name, period)