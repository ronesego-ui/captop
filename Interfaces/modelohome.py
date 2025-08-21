# modelohome.py
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
class ModeloHomeModel:
    """Modelo para manejar los datos del Modelo HOME."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_modelo_data(self, company_id: int, period: int, data: Dict[str, Any]) -> bool:
        """Guarda los datos del modelo HOME en la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO financial_statement (company_id, period, type, data) VALUES (?, ?, ?, ?)",
                    (company_id, period, "MODELO_HOME", json.dumps(data))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving modelo HOME data: {str(e)}")
            return False
            
    def load_modelo_data(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        """Carga los datos del modelo HOME desde la base de datos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM financial_statement WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, "MODELO_HOME")
                )
                row = cursor.fetchone()
                return json.loads(row["data"]) if row else None
        except Exception as e:
            logger.error(f"Error loading modelo HOME data: {str(e)}")
            return None

# ------------------------- Vista -------------------------
class ModeloHomeUI(tk.Toplevel):
    """Interfaz gráfica para el Modelo HOME."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent / "captop.db"
        self.model = ModeloHomeModel(db_file)
        
        # Inicializar variables
        self.entry_vars = {}
        
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self.title("Modelo HOME")
        self.geometry("500x600")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_header()
        self._create_data_section()
        self._create_buttons()
        
    def _configure_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#DCDAD5')
        style.configure('TLabel', background='#DCDAD5', font=('Inter', 10))
        style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 11, 'bold'))
        style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=2, width=12)
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
        style.configure('Header.TLabel', font=('Inter', 14, 'bold'), background='#DCDAD5')
        style.configure('Section.TLabel', font=('Inter', 11, 'bold'), background='#DCDAD5')
        style.configure('Bold.TLabel', font=('Inter', 10, 'bold'))
        
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
        
        ttk.Label(header_frame, text="MODELO HOME", 
                 style='Header.TLabel').pack(fill="x", pady=(0, 5))
        
        # Información de período y empresa
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill="x", pady=5)
        
        ttk.Label(info_frame, text="Período:", font=('Inter', 10, 'bold')).grid(
            row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text=str(self.period_int), font=('Inter', 10)).grid(
            row=0, column=1, padx=5, pady=2, sticky='w')
            
        ttk.Label(info_frame, text="Empresa:", font=('Inter', 10, 'bold')).grid(
            row=0, column=2, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text=self.company_name_str, font=('Inter', 10)).grid(
            row=0, column=3, padx=5, pady=2, sticky='w')
            
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(3, weight=1)
        
    def _create_data_section(self):
        """Crea la sección principal de datos."""
        section_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        section_frame.pack(fill="x", padx=10, pady=10)
        
        # Lista de campos con sus etiquetas
        fields = [
            ("ventas_pagadas", "Ventas Pagadas"),
            ("desideras_ventas", "Desideras por ventas"),
            ("ventas_metas", "Ventas Metas"),
            ("impto_compra_venta", "Impto Compra-Venta"),
            ("publicidad", "Publicidad"),
            ("promociones", "Promociones"),
            ("compras_paradas", "COMPRAS PARADAS"),
            ("compras_por_parar", "COMPRAS POR PARAR"),
            ("stock_final_prod_terminados", "Stock Final Prod Terminados"),
            ("produccion_periodo", "Producción del período"),
            ("stock_trans_marit", "Stock Trans Marit"),
            ("stock_nit_si_home", "Stock NIT Si HOME"),
            ("stock_pfar_home", "Stock PFAR-HOME"),
            ("precid_nit_i_home", "PRECID NIT I HOME"),
            ("precid_nit_z_home", "PRECID NIT Z HOME"),
            ("tasa_sobregiro", "Tasa Sobregiro [%]"),
            ("incobrables_definitivos", "Incobrables definitivos [%]"),
            ("morosos", "Morosos [%]"),
            ("recargo_protesto", "Recargo por protesto [%]"),
        ]
        
        for i, (key, label) in enumerate(fields):
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill="x", padx=5, pady=3)
            
            # Etiqueta
            ttk.Label(row_frame, text=label, width=30, anchor='w').grid(row=0, column=0, sticky='w')
            
            # Entrada
            var = tk.StringVar(value="0")
            entry = ttk.Entry(row_frame, textvariable=var, width=12)
            entry.grid(row=0, column=1, padx=5)
            self.entry_vars[key] = var
            
            # Para los campos con [X], añadir formato especial
            if "[X]" in label:
                ttk.Label(row_frame, text="(proporción)").grid(row=0, column=2, padx=5, sticky='w')
        
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
        modelo_data = self.model.load_modelo_data(self.company_id, self.period_int)
        
        if modelo_data:
            for key, var in self.entry_vars.items():
                if key in modelo_data:
                    var.set(str(modelo_data[key]))
    
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
                try:
                    # Intentar convertir a número si es posible
                    if key in ["tasa_sobregiro", "incobrables_definitivos", "morosos", "recargo_protesto"]:
                        # Convertir proporciones a decimales
                        data[key] = float(value) if value else 0.0
                    else:
                        # Mantener como entero para la mayoría de los campos
                        data[key] = int(value) if value else 0
                except ValueError:
                    data[key] = value  # Mantener como cadena si no es convertible

            if self.model.save_modelo_data(self.company_id, self.period_int, data):
                messagebox.showinfo("Éxito", 
                                  f"Datos del Modelo HOME guardados para el período {self.period_int}")
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
def abrir_modelo_home(parent_app, company_id: int, company_name: str, period: int):
    ModeloHomeUI(parent_app, company_id, company_name, period)