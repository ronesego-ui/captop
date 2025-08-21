import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from Interfaces.translations import tr

class BusinessGameModel:
    """Modelo para manejar los datos del juego de empresas."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_schema(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    cash_usd REAL NOT NULL DEFAULT 0.0,
                    current_period INTEGER NOT NULL DEFAULT 0,
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
            conn.commit()
            
    def get_companies(self) -> list:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM company ORDER BY name")
            return [(row["id"], row["name"]) for row in cursor.fetchall()]
    
    def get_company_info(self, company_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM company WHERE id = ?", (company_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_company(self, name: str) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()                
                cursor.execute(
                    "INSERT INTO company (name, cash_usd, current_period, reporting_currency_exchange_rate) VALUES (?, ?, ?, ?)",
                    (name, 1000000.0, int(tr("initial_period")), 950.0))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            logger.error(f"Empresa ya existe: {name}")
            return False
        except Exception as e:
            logger.error(f"Error al crear empresa: {str(e)}")
            return False
    
    def save_decisions(self, company_id: int, period: int, data: Dict) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO decision (company_id, period, payload) VALUES (?, ?, ?)",
                    (company_id, period, json.dumps(data))
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error al guardar decisiones: {str(e)}")
            return False
    
    def load_decisions(self, company_id: int, period: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT payload FROM decision WHERE company_id = ? AND period = ?",
                (company_id, period)
            )
            row = cursor.fetchone()
            return json.loads(row["payload"]) if row else None

    def increment_period(self, company_id: int) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE company SET current_period = current_period + 1 WHERE id = ?",
                    (company_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error al incrementar período: {str(e)}")
            return False

class ProductUI(tk.Toplevel):
    """Interfaz base para productos."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int, product_type: str):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name = company_name
        self.period = period
        self.product_type = product_type
        
        self.model = BusinessGameModel(Path(__file__).parent.parent / "captop.db")
        self.model.init_schema()
        
        self.entry_vars = {}
        self.countries = ["Argentina", "Brasil", "Chile", "Colombia", "Mexico"]
        
        self._setup_ui()
        self._load_initial_data()
    
    def _setup_ui(self):
        self.title(f"Juego de Empresas - {self.product_type.upper()}")
        self.geometry("1100x900")
        self.resizable(True, True)
        
        self._configure_styles()
        self._create_scrollable_frame()
        self._create_header()
        self._create_company_selector()
        self._create_main_sections()
        self._create_action_buttons()
    
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#DCDAD5')
        style.configure('TLabel', background='#DCDAD5', font=('Inter', 10))
        style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 11, 'bold'))
        style.configure('TEntry', fieldbackground='#f0f0f0', borderwidth=1, relief='solid', padding=2)
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        style.configure('TCombobox', fieldbackground='#DCDAD5', background='#DCDAD5')
        style.configure('TScrollbar', fieldbackground='#DCDAD5', background='#DCDAD5') 
        style.configure('TNotebook', background='#DCDAD5')
        style.configure('TNotebook.Tab', background='#DCDAD5')
        style.map('TNotebook.Tab', background=[('selected', '#DCDAD5')])
        style.configure('TNotebook.Tab', font=('Inter', 10, 'bold'))



  

        style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
    
    def _create_scrollable_frame(self):
        self.main_canvas = tk.Canvas(self, bg='#DCDAD5')

        self.main_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")
    
    def _create_header(self):
        header_frame = ttk.Frame(self.scrollable_frame, padding=(15, 10))
        header_frame.pack(fill="x", pady=10)
        header_frame.columnconfigure(0, weight=1)

        ttk.Label(header_frame, text="JUEGO DE EMPRESAS", font=('Inter', 20, 'bold'), foreground='green').grid(row=0, column=0, pady=5)
        ttk.Label(header_frame, text=f"PRODUCTO MODELO: NOTEBOOK {self.product_type.upper()}", font=('Inter', 12)).grid(row=1, column=0, pady=2)
        
        self.display_period_var = tk.StringVar(value=f"PERIODO ACTUAL: {self.period}")
        ttk.Label(header_frame, textvariable=self.display_period_var, font=('Inter', 12)).grid(row=2, column=0, pady=2)
    
    def _create_company_selector(self):
        company_period_frame = ttk.LabelFrame(self.scrollable_frame, text="Empresa y Período", padding=(10, 5))
        company_period_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(company_period_frame, text="Empresa:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.company_var = tk.StringVar()
        self.company_combo = ttk.Combobox(company_period_frame, textvariable=self.company_var, state="readonly")
        self.company_combo.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        self.company_combo.bind("<<ComboboxSelected>>", self._on_company_selected)
        
        ttk.Label(company_period_frame, text="Período:").grid(row=0, column=2, padx=5, pady=2, sticky='w')
        self.period_var = tk.StringVar(value=str(self.period))
        ttk.Label(company_period_frame, textvariable=self.period_var).grid(row=0, column=3, padx=5, pady=2, sticky='w')
        
        company_period_frame.grid_columnconfigure(1, weight=1)
    
    def _create_main_sections(self):
        self.create_price_credit_section()
        self.create_production_transport_section()
        self.create_plant_purchase_section()
        self.create_raw_materials_section()
        self.create_sales_points_section()
        self.create_seller_compensation_section()
        self.create_advertising_section()
        self.create_investments_section()
    
    def _create_action_buttons(self):
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        button_frame.pack(fill="x", padx=10, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Guardar Decisiones", command=self._save_data).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Cargar Decisiones", command=self._load_data).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Volver al Menú Principal", command=self._on_closing).grid(row=0, column=2, padx=5, pady=5, sticky='ew')
    
    def _load_initial_data(self):
        companies = self.model.get_companies()
        self.company_combo['values'] = [name for _, name in companies]
        
        if companies:
            for c_id, name in companies:
                if c_id == self.company_id:
                    self.company_combo.set(name)
                    self.company_var.set(name)
                    self.period_var.set(str(self.period))
                    break
            
            if self.company_combo.get():
                self._load_data()
    
    def _on_company_selected(self, event=None):
        company_name = self.company_var.get()
        if not company_name:
            return
        
        companies = self.model.get_companies()
        for c_id, name in companies:
            if name == company_name:
                self.company_id = c_id
                break
        
        company_info = self.model.get_company_info(self.company_id)
        if company_info:
            self.period = company_info['current_period']
            self.period_var.set(str(self.period))
            self.display_period_var.set(f"PERIODO ACTUAL: {self.period}")
        
        self._load_data()
    
    def _save_data(self):
        if not self.company_combo.get():
            messagebox.showwarning("Guardar", "Seleccione una empresa primero")
            return
        
        data = {}
        for key, var in self.entry_vars.items():
            value = var.get()
            try:
                data[key] = float(value) if value else 0.0
            except ValueError:
                data[key] = value
        
        if self.model.save_decisions(self.company_id, int(self.period_var.get()), data):
            if self.model.increment_period(self.company_id):
                self.period = int(self.period_var.get()) + 1
                self.period_var.set(str(self.period))
                self.display_period_var.set(f"PERIODO ACTUAL: {self.period}")
                messagebox.showinfo("Éxito", "Decisiones guardadas y período actualizado")
            else:
                messagebox.showerror("Error", "Decisiones guardadas pero no se pudo actualizar el período")
        else:
            messagebox.showerror("Error", "Error al guardar decisiones")
    
    def _load_data(self):
        decisions = self.model.load_decisions(self.company_id, int(self.period_var.get()))
        if decisions:
            for key, value in decisions.items():
                if key in self.entry_vars:
                    self.entry_vars[key].set(str(value))
    
    def _on_closing(self):
        self.destroy()
        self.parent_app.show_main_menu()

    def create_price_credit_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="PRECIOS Y CONDICIÓN DE CRÉDITO", padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        countries = self.countries
        sub_headers = ["TD", "ES"]
        conditions = ["Condición Crédito 1", "Condición Crédito 2", "Condición Crédito 3"]

        frame.grid_columnconfigure(0, weight=1)
        for i in range(1, len(countries) * len(sub_headers) + 1):
            frame.grid_columnconfigure(i, weight=1)

        ttk.Label(frame, text="").grid(row=0, column=0, padx=5, pady=2)
        for i, country in enumerate(countries):
            ttk.Label(frame, text=country, font=('Inter', 10, 'bold')).grid(row=0, column=1 + i * 2, columnspan=2, padx=5, pady=2)

        ttk.Label(frame, text="").grid(row=1, column=0, padx=5, pady=2)
        for i in range(len(countries)):
            for j, sub_header in enumerate(sub_headers):
                ttk.Label(frame, text=sub_header, font=('Inter', 9)).grid(row=1, column=1 + i * 2 + j, padx=5, pady=2)

        for r, condition in enumerate(conditions):
            ttk.Label(frame, text=condition, anchor='w').grid(row=2 + r, column=0, padx=5, pady=2, sticky='w')
            for c_idx, country in enumerate(countries):
                for s_idx, sub_h in enumerate(sub_headers):
                    key = f"price_credit_cond{r+1}_{country}_{sub_h}"
                    var = tk.StringVar()
                    entry = ttk.Entry(frame, width=12, textvariable=var)
                    entry.grid(row=2 + r, column=1 + c_idx * 2 + s_idx, padx=2, pady=2, sticky='ew')
                    self.entry_vars[key] = var

    def create_production_transport_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="PRODUCCIÓN - TRANSPORTE", padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        countries = self.countries
        rows = ["Produc. Ordenada en el per", "Compras/vtas/castigos", "Stock Disponible para Venta", 
                "Despacho Aéreo: Origen", "Despacho Aéreo: Destino"]

        frame.grid_columnconfigure(0, weight=1)
        for i in range(1, len(countries) + 1):
            frame.grid_columnconfigure(i, weight=1)

        ttk.Label(frame, text="").grid(row=0, column=0, padx=5, pady=2)
        for i, country in enumerate(countries):
            ttk.Label(frame, text=country, font=('Inter', 10, 'bold')).grid(row=0, column=1 + i, padx=5, pady=2)

        for r, row_label in enumerate(rows):
            ttk.Label(frame, text=row_label, anchor='w').grid(row=1 + r, column=0, padx=5, pady=2, sticky='w')
            for c_idx, country in enumerate(countries):
                key = f"prod_trans_{row_label.replace(' ', '_').replace('/', '_').replace('.', '')}_{country}"
                var = tk.StringVar()
                entry = ttk.Entry(frame, width=12, textvariable=var)
                entry.grid(row=1 + r, column=1 + c_idx, padx=2, pady=2, sticky='ew')
                self.entry_vars[key] = var

    def create_plant_purchase_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="COMPRA DE PLANTAS DEL PERÍODO", padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        countries = self.countries
        
        frame.grid_columnconfigure(0, weight=1)
        for i in range(1, len(countries) + 1):
            frame.grid_columnconfigure(i, weight=1)

        ttk.Label(frame, text="").grid(row=0, column=0, padx=5, pady=2)
        for i, country in enumerate(countries):
            header_cell = ttk.Frame(frame, relief='solid', borderwidth=1)
            header_cell.grid(row=0, column=1 + i, padx=2, pady=2, sticky='nsew')
            ttk.Label(header_cell, text=country, font=('Inter', 10, 'bold')).pack(fill='both', expand=True)

        ttk.Label(frame, text="Condicion de Compra", anchor='w').grid(row=1, column=0, padx=5, pady=2, sticky='w')
        for c_idx, country in enumerate(countries):
            key = f"plant_purchase_condition_{country}"
            var = tk.StringVar()
            entry = ttk.Entry(frame, width=12, textvariable=var)
            entry.grid(row=1, column=1 + c_idx, padx=2, pady=2, sticky='ew')
            self.entry_vars[key] = var

    def create_raw_materials_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Control de Materias Primas", padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        countries = self.countries
        rows = ["KITS - Consumo en Unidades", "Compra en Unidades", "PPA - Consumo en Unidades", 
                "Compra en Unidades", "Condicion de compra"]
        
        frame.grid_columnconfigure(0, weight=1)
        for i in range(1, len(countries) + 1):
            frame.grid_columnconfigure(i, weight=1)

        ttk.Label(frame, text="").grid(row=0, column=0, padx=5, pady=2)
        for i, country in enumerate(countries):
            ttk.Label(frame, text=country, font=('Inter', 10, 'bold')).grid(row=0, column=1 + i, padx=5, pady=2)

        for r, row_label in enumerate(rows):
            ttk.Label(frame, text=row_label, anchor='w').grid(row=1 + r, column=0, padx=5, pady=2, sticky='w')
            for c_idx, country in enumerate(countries):
                key = f"raw_materials_{row_label.replace(' ', '_').replace('/', '_').replace('.', '').replace(':', '')}_{country}"
                var = tk.StringVar()
                entry = ttk.Entry(frame, width=12, textvariable=var)
                entry.grid(row=1 + r, column=1 + c_idx, padx=2, pady=2, sticky='ew')
                self.entry_vars[key] = var

    def create_sales_points_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="PUNTOS DE VENTAS", padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        countries = self.countries
        rows = ["N° Puntos Venta a Atender TD", "N° Puntos Venta a Atender ES", 
                "N° Vendedores Contratados", "N° Vendedores en Funciones"]

        frame.grid_columnconfigure(0, weight=1)
        for i in range(1, len(countries) + 1):
            frame.grid_columnconfigure(i, weight=1)

        ttk.Label(frame, text="").grid(row=0, column=0, padx=5, pady=2)
        for i, country in enumerate(countries):
            ttk.Label(frame, text=country, font=('Inter', 10, 'bold')).grid(row=0, column=1 + i, padx=5, pady=2)

        for r, row_label in enumerate(rows):
            ttk.Label(frame, text=row_label, anchor='w').grid(row=1 + r, column=0, padx=5, pady=2, sticky='w')
            for c_idx, country in enumerate(countries):
                key = f"sales_points_{row_label.replace(' ', '_').replace('°', 'N').replace('.', '')}_{country}"
                var = tk.StringVar()
                entry = ttk.Entry(frame, width=12, textvariable=var)
                entry.grid(row=1 + r, column=1 + c_idx, padx=2, pady=2, sticky='ew')
                self.entry_vars[key] = var

    def create_seller_compensation_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Remuneración Variable Vendedores", padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        countries = self.countries
        rows = ["Remuneración variable vendedores (%)"]
        
        frame.grid_columnconfigure(0, weight=1)
        for i in range(1, len(countries) + 1):
            frame.grid_columnconfigure(i, weight=1)

        ttk.Label(frame, text="").grid(row=0, column=0, padx=5, pady=2)
        for i, country in enumerate(countries):
            ttk.Label(frame, text=country, font=('Inter', 10, 'bold')).grid(row=0, column=1 + i, padx=5, pady=2)

        for r, row_label in enumerate(rows):
            ttk.Label(frame, text=row_label, anchor='w').grid(row=1 + r, column=0, padx=5, pady=2, sticky='w')
            for c_idx, country in enumerate(countries):
                key = f"variable_comp_{row_label.replace(' ', '_').replace('%', 'perc')}_{country}"
                var = tk.StringVar()
                entry = ttk.Entry(frame, width=12, textvariable=var)
                entry.grid(row=1 + r, column=1 + c_idx, padx=2, pady=2, sticky='ew')
                self.entry_vars[key] = var

    def create_advertising_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="PUBLICIDAD (Frecuencia)", padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        countries = self.countries
        media_types = [
            "Revista PC Actualidad", "Diario Negocios y Economía", "Diario Sensacionalista",
            "Televisión Abierta", "Televisión Cable", "Circuito ABC1", "Circuito C2C3",
            "Radio Adulto Joven", "Radio Noticias", "Radio La TIERRA", "Portal Diario Electrónico"
        ]
        
        frame.grid_columnconfigure(0, weight=1)
        for i in range(1, len(countries) + 1):
            frame.grid_columnconfigure(i, weight=1)

        ttk.Label(frame, text="").grid(row=0, column=0, padx=5, pady=2)
        for i, country in enumerate(countries):
            ttk.Label(frame, text=country, font=('Inter', 10, 'bold')).grid(row=0, column=1 + i, padx=5, pady=2)

        for r_idx, media in enumerate(media_types):
            ttk.Label(frame, text=media, anchor='w', wraplength=100, justify='left').grid(row=1 + r_idx, column=0, padx=5, pady=2, sticky='w')
            for c_idx, country in enumerate(countries):
                key = f"advertising_freq_{media.replace(' ', '_').replace('.', '')}_{country}"
                var = tk.StringVar()
                entry = ttk.Entry(frame, width=12, textvariable=var)
                entry.grid(row=1 + r_idx, column=1 + c_idx, padx=2, pady=2, sticky='ew')
                self.entry_vars[key] = var

    def create_investments_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="INVERSIONES - PROMOCIONES SIN PUBLICIDAD", padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)

        countries = self.countries
        
        frame.grid_columnconfigure(0, weight=1)
        for i in range(1, len(countries) + 1):
            frame.grid_columnconfigure(i, weight=1)

        ttk.Label(frame, text="").grid(row=0, column=0, padx=5, pady=2)
        for i, country in enumerate(countries):
            header_cell = ttk.Frame(frame, relief='solid', borderwidth=1)
            header_cell.grid(row=0, column=1 + i, padx=2, pady=2, sticky='nsew')
            ttk.Label(header_cell, text=country, font=('Inter', 10, 'bold')).pack(fill='both', expand=True)

        ttk.Label(frame, text="Condicion de Compra", anchor='w').grid(row=1, column=0, padx=5, pady=2, sticky='w')
        for c_idx, country in enumerate(countries):
            key = f"investment_condition_{country}"
            var = tk.StringVar()
            entry = ttk.Entry(frame, width=12, textvariable=var)
            entry.grid(row=1, column=1 + c_idx, padx=2, pady=2, sticky='ew')
            self.entry_vars[key] = var

class ProductsSelectionUI(tk.Toplevel):
    """Interfaz para seleccionar entre productos HOME y PROFESSIONAL."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name = company_name
        self.period = period
        
        self.title("Selección de Productos")
        self.geometry("400x300")
        self.resizable(False, False)
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="SELECCIONE EL PRODUCTO", font=('Helvetica', 14, 'bold')).pack(pady=20)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(button_frame, text="NOTEBOOK HOME", 
                  command=lambda: self._open_product_ui("home")).pack(pady=10, fill="x")
        ttk.Button(button_frame, text="NOTEBOOK PROFESSIONAL", 
                  command=lambda: self._open_product_ui("pro")).pack(pady=10, fill="x")
        
        ttk.Button(main_frame, text="Volver", command=self._on_closing).pack(pady=10)
    
    def _open_product_ui(self, product_type: str):
        self.withdraw()
        ProductUI(self.parent_app, self.company_id, self.company_name, self.period, product_type)
    
    def _on_closing(self):
        self.destroy()
        self.parent_app.show_main_menu()