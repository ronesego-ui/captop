# datosfisicosdeinventario.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# ------------------------- Configuración Inicial -------------------------
logger = logging.getLogger(__name__)

# Internacionalización
INVENTORY_TRANSLATIONS = {
    "es": {
        "window_title": "Datos Físicos de Inventarios",
        "raw_materials": "MATERIAS PRIMAS",
        "home": "HOME",
        "professional": "PROFESSIONAL",
        "kits_inventory": "Inventario Final Kits (Unidades)",
        "ppa_inventory": "Inventario Final PPA (Unidades)",
        "desktop_model": "MODELO DESKTOP",
        "notebook_model": "MODELO NOTEBOOK",
        "period_assembly": "Ensamblaje del Período",
        "period_assembly_units": "Ensamblaje del Período (Unidades)",
        "finished_inventory": "Inventario Final Productos Terminados",
        "finished_inventory_units": "Inventario Final Productos Terminados (Unidades)",
        "economic_indices": "INDICES ECONOMICOS FINANCIEROS",
        "working_capital": "Capital de Trabajo Contable",
        "net_working_capital": "Capital Trabajo Funcional Neto",
        "working_fund": "Fondo de Maniobra",
        "treasury_situation": "Situación de Tesorería",
        "operation_funds": "Fondos Proveniente Operaciones",
        "liquidity": "Liquidez",
        "functional_liquidity": "Liquidez funcional",
        "acid_test": "Prueba acida",
        "inventory_permanence": "Permanencia de: Inventarios",
        "sales_debtors": "deudores por ventas",
        "spontaneous_credits": "creditos espontáneos",
        "maturation_cycle": "ciclo de maduración",
        "long_term_debt_ratio": "Deuda largo plazo/Patrimonio",
        "total_debt_ratio": "Deuda total/Patrimonio",
        "working_capital_ratio": "Fondo Maniobra/Capitales permanentes",
        "company_yield": "Rendimiento empresa",
        "operational_yield": "Rendimiento operacional",
        "operation_cashflow_yield": "Rendimiento Flujos de operación",
        "contribution_margin": "Margen de contribución",
        "fixed_costs_ratio": "Costos fijos/ventas",
        "shareholder_profitability": "Rentabilidad accionista",
        "equity_capital_ratio": "Patrimonio/Capital",
        "days": "días",
        "percentage": "%",
        "calculate": "Calcular",
        "save": "Guardar",
        "back": "Volver al Menú Principal",
        "save_success": "Datos guardados para el período {period} de {company}.",
        "save_error": "Error al guardar datos: {error}"
    }
}

# ------------------------- Modelo -------------------------
class PhysicalInventoryModel:
    """Modelo para manejar los datos físicos de inventarios."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_inventory_data(self, company_id: int, period: int, data: Dict[str, Any]) -> bool:
        """Guarda los datos de inventario en la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO financial_statement (company_id, period, type, data) VALUES (?, ?, ?, ?)",
                    (company_id, period, "PHYSICAL_INVENTORY", json.dumps(data))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving physical inventory data: {str(e)}")
            return False
            
    def load_inventory_data(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        """Carga los datos de inventario desde la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM financial_statement WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, "PHYSICAL_INVENTORY")
                )
                row = cursor.fetchone()
                return json.loads(row["data"]) if row else None
        except Exception as e:
            logger.error(f"Error loading physical inventory data: {str(e)}")
            return None

# ------------------------- Vista -------------------------
class PhysicalInventoryUI(tk.Toplevel):
    """Interfaz gráfica para los Datos Físicos de Inventarios."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent / "captop.db"
        self.model = PhysicalInventoryModel(db_file)
        
        # Inicializar variables
        self.entry_vars = {}
        self.label_vars = {}
        
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.title("Datos Físicos de Inventarios")
        self.geometry("900x700")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_header()
        self._create_raw_materials_section()
        self._create_desktop_section()
        self._create_notebook_section()
        self._create_economic_indices_section()
        self._create_buttons()
        
    def _configure_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#DCDAD5')
        style.configure('TLabel', background='#DCDAD5', font=('Inter', 9))
        style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 10, 'bold'))
        style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=2, width=10)
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
        style.configure('Header.TLabel', font=('Inter', 14, 'bold'), background='#d0d0d0')
        style.configure('Section.TLabel', font=('Inter', 11, 'bold'), background='#e0e0e0')
        style.configure('Subsection.TLabel', font=('Inter', 10, 'bold'))
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
        
        ttk.Label(header_frame, text="DATOS FISICOS DE INVENTARIOS TOTAL CONTINENTE", 
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
        
    def _create_raw_materials_section(self):
        """Crea la sección de materias primas."""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text="MATERIAS PRIMAS", 
                                      padding=(10, 10))
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # Encabezados de columnas
        header_frame = ttk.Frame(section_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="", width=30).pack(side="left")
        ttk.Label(header_frame, text="HOME", style='Subsection.TLabel').pack(side="left", padx=20)
        ttk.Label(header_frame, text="PROFESSIONAL", style='Subsection.TLabel').pack(side="left", padx=20)
        
        # Campos de entrada
        fields = [
            ("kits_inventory", "Inventario Final Kits (Unidades)"),
            ("ppa_inventory", "Inventario Final PPA (Unidades)"),
        ]
        
        for key, label in fields:
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(row_frame, text=label, width=30, anchor='w').pack(side="left")
            
            # Campo para HOME
            home_frame = ttk.Frame(row_frame)
            home_frame.pack(side="left", padx=20)
            home_var = tk.StringVar(value="0")
            ttk.Entry(home_frame, textvariable=home_var, width=10).pack()
            self.entry_vars[f"{key}_home"] = home_var
            
            # Campo para PROFESSIONAL
            professional_frame = ttk.Frame(row_frame)
            professional_frame.pack(side="left", padx=20)
            professional_var = tk.StringVar(value="0")
            ttk.Entry(professional_frame, textvariable=professional_var, width=10).pack()
            self.entry_vars[f"{key}_professional"] = professional_var
        
    def _create_desktop_section(self):
        """Crea la sección para el modelo Desktop."""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text="MODELO DESKTOP", 
                                      padding=(10, 10))
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # Campos de entrada
        fields = [
            ("period_assembly", "Ensamblaje del Período"),
            ("finished_inventory", "Inventario Final Productos Terminados"),
        ]
        
        for key, label in fields:
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(row_frame, text=label, width=40, anchor='w').pack(side="left")
            var = tk.StringVar(value="0")
            ttk.Entry(row_frame, textvariable=var, width=15).pack(side="right")
            self.entry_vars[f"desktop_{key}"] = var
        
    def _create_notebook_section(self):
        """Crea la sección para el modelo Notebook."""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text="MODELO NOTEBOOK", 
                                      padding=(10, 10))
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # Campos de entrada
        fields = [
            ("period_assembly_units", "Ensamblaje del Período (Unidades)"),
            ("finished_inventory_units", "Inventario Final Productos Terminados (Unidades)"),
        ]
        
        for key, label in fields:
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(row_frame, text=label, width=40, anchor='w').pack(side="left")
            var = tk.StringVar(value="0")
            ttk.Entry(row_frame, textvariable=var, width=15).pack(side="right")
            self.entry_vars[f"notebook_{key}"] = var
        
    def _create_economic_indices_section(self):
        """Crea la sección de índices económicos financieros."""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text="INDICES ECONOMICOS FINANCIEROS", 
                                      padding=(10, 10))
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # Índices financieros
        indices = [
            ("working_capital", "Capital de Trabajo Contable", "US$"),
            ("net_working_capital", "Capital Trabajo Funcional Neto", "US$"),
            ("working_fund", "Fondo de Maniobra", "US$"),
            ("treasury_situation", "Situación de Tesorería", "US$"),
            ("operation_funds", "Fondos Proveniente Operaciones", "US$"),
            ("liquidity", "Liquidez", ""),
            ("functional_liquidity", "Liquidez funcional", ""),
            ("acid_test", "Prueba acida", ""),
            ("inventory_permanence", "Permanencia de: Inventarios", "días"),
            ("sales_debtors", "deudores por ventas", "días"),
            ("spontaneous_credits", "creditos espontáneos", "días"),
            ("maturation_cycle", "ciclo de maduración", "días"),
            ("long_term_debt_ratio", "Deuda largo plazo/Patrimonio", ""),
            ("total_debt_ratio", "Deuda total/Patrimonio", ""),
            ("working_capital_ratio", "Fondo Maniobra/Capitales permanentes", ""),
            ("company_yield", "Rendimiento empresa", "%"),
            ("operational_yield", "Rendimiento operacional", "%"),
            ("operation_cashflow_yield", "Rendimiento Flujos de operación", "%"),
            ("contribution_margin", "Margen de contribución", "%"),
            ("fixed_costs_ratio", "Costos fijos/ventas", "%"),
            ("shareholder_profitability", "Rentabilidad accionista", "%"),
            ("equity_capital_ratio", "Patrimonio/Capital", ""),
        ]
        
        for i, (key, label, unit) in enumerate(indices):
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=2)
            
            # Etiqueta del índice
            ttk.Label(row_frame, text=label, width=40, anchor='w', style='Bold.TLabel').grid(row=0, column=0, sticky='w')
            
            # Campo de entrada
            var = tk.StringVar(value="0.00")
            entry = ttk.Entry(row_frame, textvariable=var, width=10)
            entry.grid(row=0, column=1, padx=(10, 5))
            self.entry_vars[key] = var
            
            # Unidad de medida
            if unit:
                ttk.Label(row_frame, text=unit).grid(row=0, column=2, sticky='w')
            
            row_frame.columnconfigure(0, weight=1)
        
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
        inventory_data = self.model.load_inventory_data(self.company_id, self.period_int)
        
        if inventory_data:
            for key, var in self.entry_vars.items():
                if key in inventory_data:
                    var.set(str(inventory_data[key]))
    
    def calculate_values(self):
        """Calcula los valores de los índices económicos (placeholder)."""
        # Esta función sería implementada con la lógica de negocio real
        messagebox.showinfo("Información", "Los cálculos se realizarán según la lógica de negocio específica")
        
    def save_data(self):
        """Guarda los datos en la base de datos."""
        try:
            inventory_data = {}
            
            # Recolectar datos de entrada
            for key, var in self.entry_vars.items():
                try:
                    # Intentar convertir a float si es numérico
                    inventory_data[key] = float(var.get() or 0.0)
                except ValueError:
                    # Mantener como cadena si no es numérico
                    inventory_data[key] = var.get()

            # Guardar en la base de datos
            if self.model.save_inventory_data(self.company_id, self.period_int, inventory_data):
                messagebox.showinfo("Éxito", 
                                  f"Datos guardados para el período {self.period_int} de {self.company_name_str}")
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
def abrir_datos_fisicos_inventario(parent_app, company_id: int, company_name: str, period: int):
    PhysicalInventoryUI(parent_app, company_id, company_name, period)