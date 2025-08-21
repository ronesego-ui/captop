# ventaspagadasperiodohome.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class VentasPagadasModel:
    """Modelo para manejar los datos de Ventas Pagadas en el Período HOME."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_ventas_data(self, company_id: int, period: int, data: Dict[str, Any]) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO financial_statement (company_id, period, type, data) VALUES (?, ?, ?, ?)",
                    (company_id, period, "VENTAS_PAGADAS_HOME", json.dumps(data))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving ventas pagadas data: {str(e)}")
            return False
            
    def load_ventas_data(self, company_id: int, period: int) -> Optional[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM financial_statement WHERE company_id = ? AND period = ? AND type = ?",
                    (company_id, period, "VENTAS_PAGADAS_HOME")
                )
                row = cursor.fetchone()
                return json.loads(row["data"]) if row else None
        except Exception as e:
            logger.error(f"Error loading ventas pagadas data: {str(e)}")
            return None

class VentasPagadasUI(tk.Toplevel):
    """Interfaz gráfica para Ventas Pagadas en el Período HOME."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        
        # Configurar modelo
        db_file = Path(__file__).parent.parent / "captop.db"
        self.model = VentasPagadasModel(db_file)
        
        # Inicializar variables
        self.entry_vars = {}
        
        self.title("Ventas Pagadas Período HOME")
        self.geometry("900x700")
        self.resizable(True, True)
        
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_header()
        self._create_table()
        self._create_buttons()
        
    def _configure_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#DCDAD5')
        style.configure('TLabel', background='#DCDAD5', font=('Inter', 10))
        style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 11, 'bold'))
        style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=2, width=8)
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
        style.configure('Header.TLabel', font=('Inter', 14, 'bold'), background='#DCDAD5')
        style.configure('Section.TLabel', font=('Inter', 11, 'bold'), background='#DCDAD5')
        style.configure('Bold.TLabel', font=('Inter', 10, 'bold'))
        style.configure('TableHeader.TLabel', font=('Inter', 10, 'bold'), background='#DCDAD5')
        
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
        
        ttk.Label(header_frame, text="VENTAS PAGADAS EN EL PERÍODO HOME", 
                 style='Header.TLabel').pack(fill="x", pady=(0, 5))
        
        # Información de período y empresa
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill="x", pady=5)
        
        ttk.Label(info_frame, text="Período:", font=('Inter', 10, 'bold')).grid(
            row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text=f"{self.period_int} FUMANCHU", font=('Inter', 10)).grid(
            row=0, column=1, padx=5, pady=2, sticky='w')
            
        ttk.Label(info_frame, text="Empresa:", font=('Inter', 10, 'bold')).grid(
            row=0, column=2, padx=5, pady=2, sticky='w')
        ttk.Label(info_frame, text=self.company_name_str, font=('Inter', 10)).grid(
            row=0, column=3, padx=5, pady=2, sticky='w')
            
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(3, weight=1)
        
    def _create_table(self):
        """Crea la tabla de ventas pagadas."""
        table_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        table_frame.pack(fill="x", padx=10, pady=10)
        
        # Encabezados de columnas
        headers = ["", "Argentina", "Brasil", "Chile", "Colombia", "Mexico"]
        
        # Crear encabezados
        for col, header in enumerate(headers):
            ttk.Label(table_frame, text=header, style='TableHeader.TLabel', 
                     width=12, anchor='center').grid(row=0, column=col, padx=2, pady=2, sticky='nsew')
        
        # Filas de la tabla
        rows = [
            "TDI",
            "CD",
            "CO",
            "TOTAL PAIS",
            "VENTAS METAS",
            "TOTAL ST",
            "TOTAL DL",
            "DATOS PARA EL PRÓXIMO PERÍODO CXC",
            "Total en el Continente",
            "TDI",
            "CD",
            "CO",
            "TOTAL PAIS",
            "VENTAS METAS",
            "TOTAL CXC ST",
            "TOTAL CXC DL",
            "TOTAL CRED. CUENTAS POR COBRAR",
            "COMISION VENDEDORES $ PAIS",
            "COMISION VENDEDORES $ TOTAL",
            "REMUNERACION FIJA VENDEDORES X PAIS",
            "REMUNERACION FIJA VENDEDORES X PAIS",  # Duplicado en la imagen
            "NACREDITO PERÍODO",
            "IVA DEBITO PERÍODO",
            "IVA BALANCE FINAL",
            "Precios Netos KIT",
            "Precios Netos PPA",
            "INVENTARIO FINAL MP $"
        ]
        
        # Crear filas
        for row_idx, row_label in enumerate(rows, start=1):
            # Etiqueta de fila
            ttk.Label(table_frame, text=row_label, 
                     width=30, anchor='w').grid(row=row_idx, column=0, padx=5, pady=2, sticky='w')
            
            # Entradas para cada país
            for col_idx, country in enumerate(headers[1:], start=1):
                # Identificador único para cada celda
                cell_id = f"{row_label.replace(' ', '_')}_{country}"
                
                # Crear entrada
                var = tk.StringVar(value="0")
                entry = ttk.Entry(table_frame, textvariable=var, width=12, justify='right')
                entry.grid(row=row_idx, column=col_idx, padx=2, pady=2)
                
                # Guardar referencia a la variable
                self.entry_vars[cell_id] = var
        
        # Configurar pesos de columnas
        for col in range(len(headers)):
            table_frame.grid_columnconfigure(col, weight=1 if col > 0 else 2)
        
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
        ventas_data = self.model.load_ventas_data(self.company_id, self.period_int)
        
        if ventas_data:
            for cell_id, value in ventas_data.items():
                if cell_id in self.entry_vars:
                    self.entry_vars[cell_id].set(str(value))
    
    def calculate_values(self):
        """Calcula los valores (placeholder)."""
        messagebox.showinfo("Información", "Los cálculos se realizarán según la lógica de negocio específica")
        
    def save_data(self):
        """Guarda los datos en la base de datos."""
        try:
            data = {}
            for cell_id, var in self.entry_vars.items():
                value = var.get()
                try:
                    # Convertir a entero si es posible
                    data[cell_id] = int(value) if value else 0
                except ValueError:
                    # Mantener como cadena si no es convertible
                    data[cell_id] = value

            if self.model.save_ventas_data(self.company_id, self.period_int, data):
                messagebox.showinfo("Éxito", 
                                  f"Datos de Ventas Pagadas guardados para el período {self.period_int}")
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
def abrir_ventas_pagadas_home(parent_app, company_id: int, company_name: str, period: int):
    VentasPagadasUI(parent_app, company_id, company_name, period)