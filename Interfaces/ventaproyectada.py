import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class ProjectedSalesUI(tk.Toplevel):
    def __init__(self, parent_app, company_id, company_name, period, engine):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name_str = company_name
        self.period_int = period
        self.engine = engine

        self.title(f"Venta Proyectada - {self.company_name_str} (Período {self.period_int})")
        self.geometry("1200x800")
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
        self.style.configure('Total.TLabel', font=('Inter', 10, 'bold'), background='#DCDAD5', anchor='e')

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
        self.calculated_vars = {}
        self.stock_anterior_values = {}

        self._create_widgets()
        self._load_data()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        # --- Información de Empresa y Período ---
        info_frame = ttk.Frame(self.scrollable_frame, padding=(10, 5))
        info_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(info_frame, text=f"Empresa: {self.company_name_str}", font=('Inter', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(info_frame, text=f"Período: {self.period_int}", font=('Inter', 11, 'bold')).grid(row=0, column=1, sticky='e', padx=5, pady=2)
        info_frame.columnconfigure(1, weight=1)

        # --- Título Principal ---
        title_label = ttk.Label(self.scrollable_frame, text="Venta Proyectada", font=('Inter', 18, 'bold'), anchor='center')
        title_label.pack(pady=(20, 10), fill="x")

        countries = ["Argentina", "Brasil", "Chile", "Colombia", "Mexico"]
        sales_channels = {
            "Tiendas de Departamento (TD)": "td",
            "Tienda por Especialistas (ES)": "es"
        }

        # --- Producto Modelo Home ---
        home_frame = ttk.LabelFrame(self.scrollable_frame, text="Venta Proyectada HOME", padding=(10, 10))
        home_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(home_frame, text="", width=25).grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        for col_idx, country in enumerate(countries):
            ttk.Label(home_frame, text=country, style='Header.TLabel').grid(row=0, column=col_idx + 1, padx=5, pady=2, sticky='ew')
            home_frame.grid_columnconfigure(col_idx + 1, weight=1)

        row_offset = 1
        for label_text, var_prefix in sales_channels.items():
            ttk.Label(home_frame, text=label_text + ":").grid(row=row_offset, column=0, padx=5, pady=2, sticky='w')
            for col_idx, country in enumerate(countries):
                key = f"home_{var_prefix}_{self._clean_key(country)}"
                self.entry_vars[key] = tk.StringVar()
                ttk.Entry(home_frame, textvariable=self.entry_vars[key]).grid(row=row_offset, column=col_idx + 1, padx=5, pady=2, sticky='ew')
                self.entry_vars[key].trace_add("write", lambda name, index, mode, p="home", c=country: self.calculate_total_pais(p, c))
            row_offset += 1
        
        ttk.Label(home_frame, text="Total País (incluye Outlet):", font=('Inter', 10, 'bold')).grid(row=row_offset, column=0, padx=5, pady=5, sticky='w')
        for col_idx, country in enumerate(countries):
            key = f"home_total_pais_{self._clean_key(country)}"
            self.calculated_vars[key] = tk.StringVar(value="0.00")
            ttk.Label(home_frame, textvariable=self.calculated_vars[key], style='Total.TLabel').grid(row=row_offset, column=col_idx + 1, padx=5, pady=5, sticky='ew')

        # --- Separador ---
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', padx=10, pady=15)

        # --- Producto Modelo Professional ---
        pro_frame = ttk.LabelFrame(self.scrollable_frame, text="Venta Proyectada PROFESSIONAL", padding=(10, 10))
        pro_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(pro_frame, text="", width=25).grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        for col_idx, country in enumerate(countries):
            ttk.Label(pro_frame, text=country, style='Header.TLabel').grid(row=0, column=col_idx + 1, padx=5, pady=2, sticky='ew')
            pro_frame.grid_columnconfigure(col_idx + 1, weight=1)

        row_offset = 1
        for label_text, var_prefix in sales_channels.items():
            ttk.Label(pro_frame, text=label_text + ":").grid(row=row_offset, column=0, padx=5, pady=2, sticky='w')
            for col_idx, country in enumerate(countries):
                key = f"pro_{var_prefix}_{self._clean_key(country)}"
                self.entry_vars[key] = tk.StringVar()
                ttk.Entry(pro_frame, textvariable=self.entry_vars[key]).grid(row=row_offset, column=col_idx + 1, padx=5, pady=2, sticky='ew')
                self.entry_vars[key].trace_add("write", lambda name, index, mode, p="pro", c=country: self.calculate_total_pais(p, c))
            row_offset += 1
        
        ttk.Label(pro_frame, text="Total País (incluye Outlet):", font=('Inter', 10, 'bold')).grid(row=row_offset, column=0, padx=5, pady=5, sticky='w')
        for col_idx, country in enumerate(countries):
            key = f"pro_total_pais_{self._clean_key(country)}"
            self.calculated_vars[key] = tk.StringVar(value="0.00")
            ttk.Label(pro_frame, textvariable=self.calculated_vars[key], style='Total.TLabel').grid(row=row_offset, column=col_idx + 1, padx=5, pady=5, sticky='ew')

        # --- Botones ---
        button_frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        button_frame.pack(fill="x", padx=10, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Guardar Decisiones", command=self._save_data).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Cargar Decisiones", command=self._load_data).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="Volver al Menú Principal", command=self._on_closing).grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    def calculate_total_pais(self, product_type, country, *args):
        """Calcula el Total País para un tipo de producto y país específicos."""
        td_key = f"{product_type}_td_{self._clean_key(country)}"
        es_key = f"{product_type}_es_{self._clean_key(country)}"
        total_key = f"{product_type}_total_pais_{self._clean_key(country)}"
        stock_anterior_key = f"{product_type}_Stock_Período_Anterior_{self._clean_key(country)}"

        td_value = self._get_numeric_value(self.entry_vars.get(td_key, tk.StringVar()).get())
        es_value = self._get_numeric_value(self.entry_vars.get(es_key, tk.StringVar()).get())
        stock_anterior_value = self.stock_anterior_values.get(stock_anterior_key, 0.0)

        total_pais = sum(filter(None, [td_value, es_value, stock_anterior_value]))
        self.calculated_vars[total_key].set(f"{total_pais:,.2f}")

    def _save_data(self):
        """Guarda los datos de venta proyectada usando el motor del juego."""
        projected_sales_data = {}
        for key, var in self.entry_vars.items():
            projected_sales_data[key] = self._get_numeric_value(var.get())
        
        # También guardamos los valores calculados y el stock para referencia
        for key, var in self.calculated_vars.items():
            projected_sales_data[key] = self._get_numeric_value(var.get())
        projected_sales_data["stock_anterior_values"] = self.stock_anterior_values

        success = self.engine.save_decision(
            company_id=self.company_id,
            period=self.period_int,
            decision_type='projected_sales',
            data=projected_sales_data
        )

        if success:
            messagebox.showinfo("Guardar Decisiones", f"Venta proyectada guardada para el período {self.period_int}.")
        else:
            messagebox.showerror("Error al Guardar", "No se pudo guardar la decisión de venta proyectada.")

    def _load_data(self):
        """Carga los datos de venta proyectada del período y rellena la UI."""
        self.clear_all_fields()

        try:
            # Cargar Stock Período Anterior (asumiendo que viene de una decisión 'summary')
            summary_data = self.engine.load_decision(self.company_id, self.period_int, 'summary')
            if summary_data:
                loaded_summary_data = summary_data.get("summary_data", {})
                countries = ["Argentina", "Brasil", "Chile", "Colombia", "Mexico"]
                item_stock_key_base = "Stock_Período_Anterior"
                for product_type in ["home", "pro"]:
                    for country in countries:
                        db_key = f"{product_type}_{item_stock_key_base}_{self._clean_key(country)}"
                        stock_value = loaded_summary_data.get(db_key)
                        self.stock_anterior_values[db_key] = self._get_numeric_value(str(stock_value)) if stock_value is not None else 0.0
            
            # Cargar las ventas proyectadas para el período actual
            projected_sales_data = self.engine.load_decision(self.company_id, self.period_int, 'projected_sales')

            if projected_sales_data:
                for key, var in self.entry_vars.items():
                    if key in projected_sales_data and projected_sales_data[key] is not None:
                        var.set(str(projected_sales_data[key]))
                
                # Cargar valores calculados también, si existen
                for key, var in self.calculated_vars.items():
                    if key in projected_sales_data and projected_sales_data[key] is not None:
                        var.set(f"{float(projected_sales_data[key]):,.2f}")
                
                # Cargar stock anterior si estaba guardado
                if "stock_anterior_values" in projected_sales_data:
                    self.stock_anterior_values = projected_sales_data["stock_anterior_values"]

                messagebox.showinfo("Cargar Venta Proyectada", f"Venta proyectada cargada para el período {self.period_int}.")
            else:
                messagebox.showinfo("Cargar Venta Proyectada", f"No se encontraron datos de venta proyectada para el período {self.period_int}.")

            # Recalcular totales después de cargar todos los datos
            for product_type in ["home", "pro"]:
                for country in ["Argentina", "Brasil", "Chile", "Colombia", "Mexico"]:
                    self.calculate_total_pais(product_type, country)

        except Exception as e:
            messagebox.showerror("Error al Cargar", f"Error al cargar la venta proyectada: {e}")

    def clear_all_fields(self):
        """Limpia todos los campos de entrada y los calculados."""
        for var in self.entry_vars.values():
            var.set("")
        for var in self.calculated_vars.values():
            var.set("0.00")
        self.stock_anterior_values = {}

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