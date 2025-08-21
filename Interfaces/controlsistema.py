# controlsistema.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# ------------------------- Configuración Inicial -------------------------
logger = logging.getLogger(__name__)

# Internacionalización (agregar estas traducciones al diccionario principal)
CONTROL_TRANSLATIONS = {
    "es": {
        "window_title": "Controles del Sistema",
        "inventory_data": "DATOS INVENTARIOS TOTAL",
        "raw_material": "Consumo Materias Primas",
        "kits_ppa": "Inventario Final KITS y PPA",
        "desktop": "Inventario Final Productos Terminados-DESKTOP",
        "notebook": "Inventario Final Productos Terminados-NOTEBOOK",
        "total_inventory": "Total Inventario Final",
        "calculate": "Calcular Totales",
        "save": "Guardar",
        "back": "Volver al Menú Principal",
        "save_success": "Datos guardados para el período {period} de {company}.",
        "save_error": "Error al guardar datos: {error}"
    }
}

# ------------------------- Modelo -------------------------
class ControlSistemaModel:
    """Modelo para manejar los datos de control del sistema."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_control_data(self, company_id: int, period: int, data: Dict[str, Any]) -> bool:
        """Guarda los datos de control en la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO financial_statement (company_id, period, type, data) VALUES (?, ?, ?, ?)",
                    (company_id, period, "CONTROL_SISTEMA", json.dumps(data))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving control data: {str(e)}")
            return False
            
    def load_control_data(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        """Carga los datos de control desde la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM financial_statement WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, "CONTROL_SISTEMA")
                )
                row = cursor.fetchone()
                return json.loads(row["data"]) if row else None
        except Exception as e:
            logger.error(f"Error loading control data: {str(e)}")
            return None

# ------------------------- Vista -------------------------
class ControlSistemaUI(tk.Toplevel):
    """Interfaz gráfica para los Controles del Sistema."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent / "captop.db"
        self.model = ControlSistemaModel(db_file)
        
        # Inicializar variables
        self.entry_vars = {}
        self.total_vars = {}
        
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.title("Controles del Sistema")
        self.geometry("600x500")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_header()
        self._create_inventory_section()
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
        style.configure('Header.TLabel', font=('Inter', 14, 'bold'), background='#DCDAD5')
        style.configure('Section.TLabel', font=('Inter', 12, 'bold'), background='#DCDAD5')
        
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
        
        ttk.Label(header_frame, text="CONTROLES DEL SISTEMA", 
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
        
    def _create_inventory_section(self):
        """Crea la sección de datos de inventario."""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text="DATOS INVENTARIOS TOTAL", 
                                      padding=(10, 10))
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # Campos de entrada
        fields = [
            ("raw_material", "Consumo Materias Primas (US$)"),
            ("kits_ppa", "Inventario Final KITS y PPA (US$)"),
            ("desktop", "Inventario Final Productos Terminados-DESKTOP (US$)"),
            ("notebook", "Inventario Final Productos Terminados-NOTEBOOK (US$)")
        ]
        
        for i, (key, label) in enumerate(fields):
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(row_frame, text=label, width=40, anchor='w').pack(side="left", padx=(0, 10))
            var = tk.StringVar(value="0.00")
            entry = ttk.Entry(row_frame, textvariable=var, width=15)
            entry.pack(side="right")
            
            self.entry_vars[key] = var
            
            # Vincular el cálculo automático cuando se modifiquen los valores
            var.trace_add("write", lambda *args: self.calculate_total())
        
        # Total inventario
        total_frame = ttk.Frame(section_frame)
        total_frame.pack(fill="x", padx=5, pady=(15, 5))
        
        ttk.Label(total_frame, text="Total Inventario Final (US$)", 
                 font=('Inter', 10, 'bold')).pack(side="left", padx=(0, 10))
        
        total_var = tk.StringVar(value="0.00")
        ttk.Label(total_frame, textvariable=total_var, 
                 font=('Inter', 10, 'bold'), width=15, anchor='e').pack(side="right")
        
        self.total_vars["total_inventory"] = total_var
        
    def _create_buttons(self):
        """Crea los botones de acción."""
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 20))
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Calcular Totales", 
                  command=self.calculate_total).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Guardar", 
                  command=self.save_data).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Volver al Menú Principal", 
                  command=self._on_closing).pack(side="right", padx=5, pady=5)
        
    def _load_initial_data(self):
        """Carga los datos iniciales desde la base de datos."""
        control_data = self.model.load_control_data(self.company_id, self.period_int)
        
        if control_data:
            for key, var in self.entry_vars.items():
                if key in control_data:
                    var.set(str(control_data[key]))
            
            if "total_inventory" in control_data:
                self.total_vars["total_inventory"].set(f"{control_data['total_inventory']:,.2f}")
        
        self.calculate_total()
        
    def calculate_total(self):
        """Calcula el total del inventario."""
        try:
            total = 0.0
            # Sumar los valores de los campos relevantes
            for key in ["kits_ppa", "desktop", "notebook"]:
                value = self.entry_vars[key].get()
                total += float(value) if value else 0.0
            
            self.total_vars["total_inventory"].set(f"{total:,.2f}")
        except ValueError:
            self.total_vars["total_inventory"].set("Error")
            logger.error("Error en el cálculo del total - valores no numéricos")
    
    def save_data(self):
        """Guarda los datos en la base de datos."""
        try:
            control_data = {}
            
            # Recolectar datos de entrada
            for key, var in self.entry_vars.items():
                try:
                    control_data[key] = float(var.get() or 0.0)
                except ValueError:
                    control_data[key] = var.get()
            
            # Recolectar totales calculados
            for key, var in self.total_vars.items():
                try:
                    control_data[key] = float(var.get().replace(',', '') or 0.0)
                except ValueError:
                    control_data[key] = var.get()

            # Guardar en la base de datos
            if self.model.save_control_data(self.company_id, self.period_int, control_data):
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
def abrir_control_sistema(parent_app, company_id: int, company_name: str, period: int):
    ControlSistemaUI(parent_app, company_id, company_name, period)