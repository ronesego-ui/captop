import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Type, Optional
import json
from Interfaces.translations import tr
from Interfaces.investigacionmercado import MarketResearchUI
from Interfaces.controlsistema import abrir_control_sistema
from Interfaces.datosfisicosdeinventario import abrir_datos_fisicos_inventario
from Interfaces.informacionadicionalbalance import abrir_informacion_adicional_balance
from Interfaces.ventasporpais import abrir_ventas_por_pais
from Interfaces.modelohome import abrir_modelo_home
from Interfaces.modeloprofessional import abrir_modelo_professional
from Interfaces.ventaspagadasperiodohome import abrir_ventas_pagadas_home
from Interfaces.ventaspagadasperiodoprofessional import abrir_ventas_pagadas_professional
from Interfaces.Consulta.listadoobservaciones import abrir_listado_observaciones

# ------------------------- Configuración Inicial -------------------------
def setup_logging():
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_filename = log_dir / f"business_game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

# ------------------------- Modelo -------------------------
class CompanyModel:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self._init_schema()
        
    def _init_schema(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    cash_usd REAL NOT NULL DEFAULT 0.0,
                    current_period INTEGER NOT NULL DEFAULT 1,
                    reporting_currency_exchange_rate REAL NOT NULL DEFAULT 950.0
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decision (
                    company_id INTEGER NOT NULL,
                    period INTEGER NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (company_id, period)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_statement (
                    company_id INTEGER NOT NULL,
                    period INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (company_id, period, type)
                );
            """)
            conn.commit()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
        
    def create_company(self, name: str) -> Tuple[bool, str]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO company (name, cash_usd, current_period, reporting_currency_exchange_rate) VALUES (?, ?, ?, ?)",
                    (name, 100000.0, 0, 950.0)
                )
                conn.commit()
                return True, tr("company_created", name=name)
        except sqlite3.IntegrityError:
            return False, tr("company_exists", name=name)
        except sqlite3.Error as e:
            logger.error(f"Database error creating company: {str(e)}")
            return False, f"{tr('db_error')}: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error creating company")
            return False, f"{tr('unexpected_error')}: {str(e)}"
            
    def get_companies(self) -> list:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM company ORDER BY name")
                return [row["name"] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Database error getting companies: {str(e)}")
            messagebox.showerror(tr("db_error"), str(e))
            return []
            
    def get_company_info(self, name: str) -> Optional[dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, current_period FROM company WHERE name = ?", 
                    (name,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Database error getting company info: {str(e)}")
            messagebox.showerror(tr("db_error"), str(e))
            return None

# ------------------------- Controlador -------------------------
class MainController:
    def __init__(self, model: CompanyModel):
        self.model = model
        self.current_company_id = None
        self.current_company_name = ""
        self.current_period = 0
        
    def validate_company_name(self, name: str) -> Tuple[bool, str]:
        name = name.strip()
        if not name:
            return False, tr("company_empty")
        if len(name) < 3:
            return False, tr("company_short")
        if len(name) > 50:
            return False, tr("company_long")
        if not all(c.isalnum() or c.isspace() for c in name):
            return False, tr("company_invalid_chars")
        return True, ""
        
    def create_company(self, name: str) -> Tuple[bool, str]:
        valid, msg = self.validate_company_name(name)
        if not valid:
            return False, msg
            
        return self.model.create_company(name.strip())
        
    def get_companies(self) -> list:
        return self.model.get_companies()
        
    def load_company(self, name: str, period: int) -> Tuple[bool, str]:
        company_info = self.model.get_company_info(name)
        if not company_info:
            return False, tr("company_not_found")
            
        self.current_company_id = company_info["id"]
        self.current_company_name = company_info["name"]
        self.current_period = period
        
        logger.info(f"Loaded company: {self.current_company_name} (ID: {self.current_company_id}), Period: {self.current_period}")
        return True, tr("company_loaded", 
                      name=self.current_company_name,
                      id=self.current_company_id,
                      period=self.current_period)

# ------------------------- Vista -------------------------
class MainMenu(tk.Tk):
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.title("Juego de Empresas - Menú Principal")
        self.geometry("800x700")
        self.resizable(True, True)  # Permitir redimensionamiento
        
        self.current_company_id = None
        self.current_company_name = tk.StringVar()
        self.current_period = tk.IntVar(value=0)
        
        self._create_scrollable_ui()
        self._populate_company_dropdown()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_scrollable_ui(self):
        """Configura la interfaz desplazable principal."""
        # Crear canvas y scrollbar
        self.canvas = tk.Canvas(self, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Frame desplazable
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Empaquetar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Crear widgets dentro del frame desplazable
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets dentro del frame desplazable."""
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text=tr("welcome"), font=('Century Gothic', 18, 'bold')).pack(pady=20)

        company_period_frame = ttk.LabelFrame(main_frame, text=tr("company_selection"), padding="15")
        company_period_frame.pack(fill="x", pady=10)

        ttk.Label(company_period_frame, text=tr("new_company")).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.new_company_name_var = tk.StringVar()
        ttk.Entry(company_period_frame, textvariable=self.new_company_name_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(company_period_frame, text=tr("create_company"), command=self._create_company).grid(row=0, column=2, padx=5, pady=5, sticky='e')

        ttk.Label(company_period_frame, text=tr("select_existing")).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.existing_company_name_var = tk.StringVar()
        self.company_combo = ttk.Combobox(
            company_period_frame, 
            textvariable=self.existing_company_name_var, 
            state="readonly", 
            width=30
        )
        self.company_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.company_combo.bind("<<ComboboxSelected>>", self._on_existing_company_selected)
        
        ttk.Label(company_period_frame, text=tr("period")).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.period_combo = ttk.Combobox(
            company_period_frame, 
            textvariable=self.current_period, 
            state="readonly", 
            values=[i for i in range(0, 8)], 
            width=10
        )
        self.period_combo.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.period_combo.set(0)
        
        ttk.Button(
            company_period_frame, 
            text=tr("load_company"), 
            command=self._select_company_period
        ).grid(row=2, column=2, padx=5, pady=5, sticky='e')

        company_period_frame.grid_columnconfigure(1, weight=1)

        current_selection_frame = ttk.LabelFrame(main_frame, text=tr("current_company"), padding="10")
        current_selection_frame.pack(fill="x", pady=10)
        ttk.Label(current_selection_frame, text=tr("current_company")).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(current_selection_frame, textvariable=self.current_company_name, font=('Helvetica', 10, 'bold')).grid(row=0, column=1, padx=5, pady=2, sticky='w')
        ttk.Label(current_selection_frame, text=tr("current_period")).grid(row=1, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(current_selection_frame, textvariable=self.current_period, font=('Century Gothic', 10, 'bold')).grid(row=1, column=1, padx=5, pady=2, sticky='w')
        current_selection_frame.grid_columnconfigure(1, weight=1)

        menu_frame = ttk.LabelFrame(main_frame, text=tr("menu_title"), padding="15")
        menu_frame.pack(fill="both", expand=True, pady=10)
        
        menu_frame.columnconfigure(0, weight=1)
        menu_frame.columnconfigure(1, weight=1)

        buttons_data = [
            ("Balance Inicial", self._open_balance_inicial),
            ("Balance Final", self._open_final_balance),
            ("Información Adicional Balance", self._open_informacion_adicional_balance),
            ("Estado de Resultados", self._open_estado_resultados),
            ("Control del Sistema", self._open_control_sistema),
            ("Datos Físicos Inventario", self._open_datos_fisicos_inventario),
            ("Estado Caja", self._open_caja),
            ("Productos", self._open_productos),
            ("Datos Período Anterior", self._open_datos_periodo_anterior),
            ("Investigación de Mercado", self._open_investigacion_mercado),
            ("Precio Materia Prima", self._open_precio_materia_prima),
            ("Préstamo", self._open_prestamo),
            ("Publicidad", self._open_publicidad),
            ("Ventas por País", self._open_ventas_por_pais),
            ("Resumen del Juego", self._open_resumen_juego),
            ("Venta Proyectada", self._open_venta_proyectada),
            ("Modelo HOME", self._open_modelo_home),
            ("Modelo PROFESSIONAL", self._open_modelo_professional),
            ("Ventas Pagadas Periodo HOME", self._open_ventas_pagadas_home),
            ("Ventas Pagadas Periodo PROFESSIONAL", self._open_ventas_pagadas_professional),
            ("Listado de Observaciones", self._open_listado_observaciones),
        ]

        for i, (text, command) in enumerate(buttons_data):
            row = i // 2
            col = i % 2
            ttk.Button(
                menu_frame, 
                text=text, 
                command=command, 
                width=30
            ).grid(row=row, column=col, padx=10, pady=5, sticky='ew')
    
    def _populate_company_dropdown(self):
        companies = self.controller.get_companies()
        self.company_combo['values'] = companies
        if companies:
            self.existing_company_name_var.set(companies[0])

    def _on_existing_company_selected(self, event=None):
        company_name = self.existing_company_name_var.get()
        if company_name:
            company_info = self.controller.model.get_company_info(company_name)
            if company_info:
                self.period_combo.set(company_info["current_period"])

    def _create_company(self):
        company_name = self.new_company_name_var.get()
        success, message = self.controller.create_company(company_name)
        
        if success:
            messagebox.showinfo("Éxito", message)
            self.new_company_name_var.set("")
            self._populate_company_dropdown()
            self.existing_company_name_var.set(company_name.strip())
            self.period_combo.set(0)
            self._select_company_period()
        else:
            messagebox.showerror("Error", message)

    def _select_company_period(self):
        company_name = self.existing_company_name_var.get()
        period = self.current_period.get()
        
        if not company_name:
            messagebox.showwarning(tr("warning"), tr("select_company_first"))
            return
        
        success, message = self.controller.load_company(company_name, period)
        if success:
            self.current_company_id = self.controller.current_company_id
            self.current_company_name.set(self.controller.current_company_name)
            self.current_period.set(self.controller.current_period)
            messagebox.showinfo("Cargado", message)
        else:
            messagebox.showerror("Error", message)
            self.current_company_id = None
            self.current_company_name.set("")
            self.current_period.set(0)

    def _open_interface(self, interface_class: Type[tk.Toplevel]):
        """Método genérico para abrir interfaces secundarias"""
        if self.current_company_id is None:
            messagebox.showwarning(tr("warning"), tr("select_company_first"))
            return

        self.withdraw()
        try:
            child_window = interface_class(
                parent_app=self,  # Pasa la instancia principal como parent_app
                company_id=self.current_company_id,
                company_name=self.current_company_name.get(),
                period=self.current_period.get()
            )
            child_window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_closing(child_window))
        except ImportError as e:
            logger.error(f"Error importing interface module: {str(e)}")
            messagebox.showerror("Error", f"No se pudo importar el módulo de la interfaz: {str(e)}")
            self.deiconify()
        except Exception as e:
            logger.error(f"Error opening interface: {str(e)}")
            messagebox.showerror("Error", f"No se pudo abrir la interfaz: {str(e)}")
            self.deiconify()

    def _on_child_closing(self, child_window):
        """Maneja el cierre de ventanas secundarias"""
        child_window.destroy()
        self.deiconify()

    def show_main_menu(self):
        """Muestra el menú principal nuevamente"""
        self.deiconify()

    def _open_productos(self):
        from homeprofessional import ProductsSelectionUI
        self._open_interface(ProductsSelectionUI)

    def _open_balance_inicial(self):
        from Interfaces.balanceinicial import BalanceSheetUI
        self._open_interface(BalanceSheetUI)

    def _open_final_balance(self):
        from Interfaces.balancefinal import FinalBalanceUI
        self._open_interface(FinalBalanceUI)
    
    def _open_estado_resultados(self):
        from Interfaces.estadoderesultado import IncomeStatementUI
        self._open_interface(IncomeStatementUI)

    def _open_caja(self):
        from Interfaces.caja import CashFlowUI
        self._open_interface(CashFlowUI)

    def _open_control_sistema(self):
        abrir_control_sistema(
            self,
            self.current_company_id,
            self.current_company_name.get(),
            self.current_period.get()
        )

    def _open_datos_fisicos_inventario(self):
        abrir_datos_fisicos_inventario(
            self,
            self.current_company_id,
            self.current_company_name.get(),
            self.current_period.get()
        )
    def _open_informacion_adicional_balance(self):
        abrir_informacion_adicional_balance(
            self,
            self.current_company_id,
            self.current_company_name.get(),
            self.current_period.get()
        )
    def _open_datos_periodo_anterior(self):
        from Interfaces.datosperiodoanterior import PreviousPeriodDataUI
        self._open_interface(PreviousPeriodDataUI)

    def _open_investigacion_mercado(self):
        """Abre la ventana de Investigación de Mercado"""
        self._open_interface(MarketResearchUI)

    def _open_precio_materia_prima(self):
        from Interfaces.preciomateriaprima import RawMaterialPriceUI
        self._open_interface(RawMaterialPriceUI)

    def _open_prestamo(self):
        from Interfaces.prestamo import LoanDecisionsUI
        self._open_interface(LoanDecisionsUI)
        
    def _open_publicidad(self):
        from Interfaces.publicidad import AdvertisingUI
        self._open_interface(AdvertisingUI)

    def _open_resumen_juego(self):
        from Interfaces.resumenjuego1 import CompanySummaryUI
        self._open_interface(CompanySummaryUI)
    
    def _open_ventas_por_pais(self):
        abrir_ventas_por_pais(
            self,
            self.current_company_id,
            self.current_company_name.get(),
            self.current_period.get()
        )

    def _open_venta_proyectada(self):
        from Interfaces.ventaproyectada import ProjectedSalesUI
        self._open_interface(ProjectedSalesUI)

    def _open_modelo_home(self):
        abrir_modelo_home(
            self,
            self.current_company_id,
            self.current_company_name.get(),
            self.current_period.get()
    )

    def _open_modelo_professional(self):
        abrir_modelo_professional(
            self,
            self.current_company_id,
            self.current_company_name.get(),
            self.current_period.get()
    )
    def _open_ventas_pagadas_home(self):
        abrir_ventas_pagadas_home(
            self,
            self.current_company_id,
            self.current_company_name.get(),
            self.current_period.get()
    )
    def _open_ventas_pagadas_professional(self):
        abrir_ventas_pagadas_professional(
            self,
            self.current_company_id,
            self.current_company_name.get(),
            self.current_period.get()
    )
    def _open_listado_observaciones(self):
        abrir_listado_observaciones(
            self,
            self.current_company_id,
            self.current_company_name.get(),
            self.current_period.get()
    )
    def _on_closing(self):
        """Maneja el cierre de la aplicación principal"""
        if messagebox.askokcancel("Salir", tr("exit_confirm")):
            self.destroy()

# ------------------------- Punto de Entrada -------------------------
if __name__ == "__main__":
    DB_FILE = Path(__file__).parent.parent / "captop.db"
    
    company_model = CompanyModel(DB_FILE)
    main_controller = MainController(company_model)
    
    app = MainMenu(main_controller)
    app.mainloop()