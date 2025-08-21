import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import sqlite3
from pathlib import Path

# --- Configuración de la Base de Datos ---
DB_FILE = Path(__file__).parent.parent / "captop.db"

def get_connection():
    """Establece y devuelve una conexión a la base de datos."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_schema():
    """Inicializa el esquema de la base de datos si no existe."""
    with get_connection() as conn:
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

# Asegurarse de que el esquema se inicialice al inicio
init_schema()

class CompanySummaryUI(tk.Toplevel):
    def __init__(self, parent_app, company_id, company_name, period):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period

        self.title(f"Resumen del Juego - {self.company_name_str} (Período {self.period_int})")
        self.geometry("1000x800")
        self.resizable(True, True)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#DCDAD5')
        self.style.configure('TLabel', background='#DCDAD5', font=('Inter', 10))
        self.style.configure('TLabelFrame', background='#DCDAD5', font=('Inter', 11, 'bold'))
        self.style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=2)
        self.style.configure('TButton', font=('Inter', 10, 'bold'), padding=5)
        self.style.map('TButton',
            background=[('active', '#e0e0e0')],
            foreground=[('active', 'black')]
        )
        self.style.configure('Header.TLabel', font=('Inter', 10, 'bold'), anchor='center')
        self.style.configure('Readonly.TLabel', background='#DCDAD5', foreground='black', font=('Inter', 10), borderwidth=1, relief='solid', padding=2)

        self.main_canvas = tk.Canvas(self, bg=self.style.lookup('TFrame', 'background'))
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

        self.entry_vars = {}
        self.display_vars = {}

        self._create_widgets()
        self.load_decisions_from_db(self.company_id, self.period_int)

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        # --- Información de Empresa y Período ---
        info_frame = ttk.Frame(self.scrollable_frame, padding=(10, 5))
        info_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(info_frame, text=f"Empresa: {self.company_name_str}", font=('Inter', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(info_frame, text=f"Período: {self.period_int}", font=('Inter', 11, 'bold')).grid(row=0, column=1, sticky='e', padx=5, pady=2)
        info_frame.columnconfigure(1, weight=1)

        # --- Título Principal ---
        title_label = ttk.Label(self.scrollable_frame, text="Juego de Empresa", font=('Inter', 18, 'bold'), anchor='center')
        title_label.pack(pady=(20, 10), fill="x")

        countries = ["Argentina", "Brasil", "Chile", "Colombia", "Mexico"]

        # --- Producto Modelo Home ---
        home_frame = ttk.LabelFrame(self.scrollable_frame, text="Producto Modelo Home", padding=(10, 10))
        home_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(home_frame, text="Período Actual:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.home_period_display = ttk.Label(home_frame, text=str(self.period_int), style='Readonly.TLabel')
        self.home_period_display.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky='ew')

        ttk.Label(home_frame, text="Empresa:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.home_company_display = ttk.Label(home_frame, text=self.company_name_str, style='Readonly.TLabel')
        self.home_company_display.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky='ew')

        ttk.Label(home_frame, text="Ingreso de Decisiones de la Empresa", font=('Inter', 11, 'bold')).grid(row=2, column=0, columnspan=len(countries) + 1, pady=(10, 5), sticky='w')

        ttk.Label(home_frame, text="", width=20).grid(row=3, column=0, padx=5, pady=2, sticky='ew')
        for col_idx, country in enumerate(countries):
            ttk.Label(home_frame, text=country, style='Header.TLabel').grid(row=3, column=col_idx + 1, padx=5, pady=2, sticky='ew')
            home_frame.grid_columnconfigure(col_idx + 1, weight=1)

        row_offset = 4
        item_stock = "Stock Período Anterior"
        ttk.Label(home_frame, text=item_stock + ":").grid(row=row_offset, column=0, padx=5, pady=2, sticky='w')
        for col_idx, country in enumerate(countries):
            key = f"home_{self._clean_key(item_stock)}_{self._clean_key(country)}"
            self.display_vars[key] = tk.StringVar(value="0")
            ttk.Label(home_frame, textvariable=self.display_vars[key], style='Readonly.TLabel').grid(row=row_offset, column=col_idx + 1, padx=5, pady=2, sticky='ew')

        item_ou = "OU"
        ttk.Label(home_frame, text=item_ou + ":").grid(row=row_offset + 1, column=0, padx=5, pady=2, sticky='w')
        for col_idx, country in enumerate(countries):
            key = f"home_{self._clean_key(item_ou)}_{self._clean_key(country)}"
            self.entry_vars[key] = tk.StringVar()
            ttk.Entry(home_frame, textvariable=self.entry_vars[key]).grid(row=row_offset + 1, column=col_idx + 1, padx=5, pady=2, sticky='ew')

        # --- Producto Modelo Professional ---
        pro_frame = ttk.LabelFrame(self.scrollable_frame, text="Producto Modelo Professional", padding=(10, 10))
        pro_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(pro_frame, text="Período Actual:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.pro_period_display = ttk.Label(pro_frame, text=str(self.period_int), style='Readonly.TLabel')
        self.pro_period_display.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky='ew')

        ttk.Label(pro_frame, text="Empresa:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.pro_company_display = ttk.Label(pro_frame, text=self.company_name_str, style='Readonly.TLabel')
        self.pro_company_display.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky='ew')

        ttk.Label(pro_frame, text="Ingreso de Decisiones de la Empresa", font=('Inter', 11, 'bold')).grid(row=2, column=0, columnspan=len(countries) + 1, pady=(10, 5), sticky='w')

        ttk.Label(pro_frame, text="", width=20).grid(row=3, column=0, padx=5, pady=2, sticky='ew')
        for col_idx, country in enumerate(countries):
            ttk.Label(pro_frame, text=country, style='Header.TLabel').grid(row=3, column=col_idx + 1, padx=5, pady=2, sticky='ew')
            pro_frame.grid_columnconfigure(col_idx + 1, weight=1)

        row_offset = 4
        item_stock = "Stock Período Anterior"
        ttk.Label(pro_frame, text=item_stock + ":").grid(row=row_offset, column=0, padx=5, pady=2, sticky='w')
        for col_idx, country in enumerate(countries):
            key = f"pro_{self._clean_key(item_stock)}_{self._clean_key(country)}"
            self.display_vars[key] = tk.StringVar(value="0")
            ttk.Label(pro_frame, textvariable=self.display_vars[key], style='Readonly.TLabel').grid(row=row_offset, column=col_idx + 1, padx=5, pady=2, sticky='ew')

        item_ou = "OU"
        ttk.Label(pro_frame, text=item_ou + ":").grid(row=row_offset + 1, column=0, padx=5, pady=2, sticky='w')
        for col_idx, country in enumerate(countries):
            key = f"pro_{self._clean_key(item_ou)}_{self._clean_key(country)}"
            self.entry_vars[key] = tk.StringVar()
            ttk.Entry(pro_frame, textvariable=self.entry_vars[key]).grid(row=row_offset + 1, column=col_idx + 1, padx=5, pady=2, sticky='ew')

        # --- Botones ---
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        button_frame.pack(fill="x", padx=10, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Guardar Decisiones", command=self.save_decisions).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Cargar Decisiones", command=lambda: self.load_decisions_from_db(self.company_id, self.period_int)).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Volver al Menú Principal", command=self._on_closing).grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    def save_decisions(self):
        """Guarda las decisiones de OU y los datos de stock del período anterior en la base de datos."""
        summary_data = {}
        
        for key, var in self.entry_vars.items():
            summary_data[key] = self._get_numeric_value(var.get())
        
        for key, var in self.display_vars.items():
            summary_data[key] = self._get_numeric_value(var.get())

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT payload FROM decision WHERE company_id = ? AND period = ?",
                    (self.company_id, self.period_int)
                )
                existing_row = cursor.fetchone()
                
                full_payload = {}
                if existing_row:
                    full_payload = json.loads(existing_row["payload"])
                
                full_payload["summary_data"] = summary_data
                
                json_payload = json.dumps(full_payload)

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO decision (company_id, period, payload)
                    VALUES (?, ?, ?)
                    """,
                    (self.company_id, self.period_int, json_payload)
                )
                conn.commit()
                messagebox.showinfo("Guardar Decisiones", f"Decisiones guardadas para el período {self.period_int} de {self.company_name_str}.")
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"Error al guardar las decisiones: {e}")

    def load_decisions_from_db(self, company_id, current_period):
        """Carga los datos de stock del período anterior y las decisiones de OU del período actual."""
        self.clear_all_fields()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Cargar Stock Período Anterior
                previous_period = current_period - 1
                
                if previous_period >= 0:  # Cambiado para permitir período 0
                    cursor.execute(
                        "SELECT payload FROM decision WHERE company_id = ? AND period = ?",
                        (company_id, previous_period)
                    )
                    prev_period_row = cursor.fetchone()
                    
                    if prev_period_row:
                        prev_payload = json.loads(prev_period_row["payload"])
                        loaded_prev_data = prev_payload.get("previous_period_data", {})
                        
                        countries = ["Argentina", "Brasil", "Chile", "Colombia", "Mexico"]
                        item_stock_key = "Productos_Terminados"

                        for product_type in ["home", "pro"]:
                            for country in countries:
                                ui_key = f"{product_type}_Stock_Período_Anterior_{self._clean_key(country)}"
                                db_key = f"{product_type}_{item_stock_key}_{self._clean_key(country)}"
                                if db_key in loaded_prev_data and loaded_prev_data[db_key] is not None:
                                    self.display_vars[ui_key].set(str(loaded_prev_data[db_key]))
                                else:
                                    self.display_vars[ui_key].set("0")
                    else:
                        # Si no hay datos del período anterior, establecer todos los stocks a 0
                        for product_type in ["home", "pro"]:
                            for country in countries:
                                ui_key = f"{product_type}_Stock_Período_Anterior_{self._clean_key(country)}"
                                self.display_vars[ui_key].set("0")
                    
                # Cargar decisiones del período actual
                cursor.execute(
                    "SELECT payload FROM decision WHERE company_id = ? AND period = ?",
                    (company_id, current_period)
                )
                current_period_row = cursor.fetchone()

                if current_period_row:
                    current_payload = json.loads(current_period_row["payload"])
                    loaded_summary_data = current_payload.get("summary_data", {})
                    
                    for key, var in self.entry_vars.items():
                        if key in loaded_summary_data and loaded_summary_data[key] is not None:
                            var.set(str(loaded_summary_data[key]))
                    
                    for key, var in self.display_vars.items():
                        if key in loaded_summary_data and loaded_summary_data[key] is not None:
                            var.set(str(loaded_summary_data[key]))

                    messagebox.showinfo("Cargar Decisiones", f"Decisiones cargadas para el período {current_period}.")
                else:
                    messagebox.showinfo("Cargar Decisiones", f"No se encontraron decisiones para el período {current_period}.")
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"Error al cargar los datos: {e}")

    def clear_all_fields(self):
        """Limpia todos los campos de entrada y los de visualización."""
        for var in self.entry_vars.values():
            var.set("")
        for var in self.display_vars.values():
            var.set("0")

    def _get_numeric_value(self, value_str):
        """Intenta convertir el valor a float; si falla o es vacío, devuelve None."""
        if not value_str:
            return None
        try:
            return float(value_str.replace(',', '.'))
        except ValueError:
            return None

    def _clean_key(self, text):
        """Limpia el texto para usarlo como clave en un diccionario."""
        return text.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")

    def _on_closing(self):
        """Maneja el cierre de la ventana secundaria para volver al menú principal."""
        self.destroy()
        self.parent_app.show_main_menu()