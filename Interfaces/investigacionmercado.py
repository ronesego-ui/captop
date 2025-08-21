import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Any, List

# ────────────────────────────────────────────────────────────────────────────────
#  Configuración y Constantes
# ────────────────────────────────────────────────────────────────────────────────

DB_FILE = Path(__file__).parent.parent / "captop.db"

# Textos para internacionalización
TEXTS = {
    "window_title": "Investigación de Mercado",
    "company_frame": "Empresa y Período",
    "company_label": "Empresa:",
    "period_label": "Período:",
    "research_frame": "Ingreso de Investigación de Mercado",
    "save_btn": "Guardar",
    "load_btn": "Cargar",
    "back_btn": "Volver al Menú Principal",
    "save_success": "Datos guardados correctamente.",
    "invalid_period": "Período inválido.",
    "company_not_found": "Empresa no encontrada.",
    "total_cost_label": "Costo Total de Inversiones",
    "headers": ["", "Home", "Professional", "Precio Unitario", "Costo"],
}

# ────────────────────────────────────────────────────────────────────────────────
#  Modelo - Manejo de Base de Datos
# ────────────────────────────────────────────────────────────────────────────────

class DatabaseManager:
    """Manejador de la base de datos encapsulando todas las operaciones SQL."""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
    
    def get_connection(self):
        """Devuelve una conexión SQLite con filas accesibles por nombre."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_decision(self, company_id: int, period: int, payload: Dict) -> bool:
        """Guarda las decisiones de investigación de mercado."""
        with self.get_connection() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "REPLACE INTO decision (company_id, period, payload) VALUES (?, ?, ?)",
                    (company_id, period, json.dumps(payload))
                )
                conn.commit()
                return True
            except sqlite3.Error:
                return False
    
    def load_decision(self, company_id: int, period: int) -> Optional[Dict]:
        """Carga las decisiones de investigación de mercado."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT payload FROM decision WHERE company_id = ? AND period = ?",
                (company_id, period))
            row = cur.fetchone()
            return json.loads(row["payload"]) if row else None

# ────────────────────────────────────────────────────────────────────────────────
#  Vista - Interfaz de Usuario
# ────────────────────────────────────────────────────────────────────────────────

class MarketResearchUI(tk.Toplevel):
    """Interfaz gráfica para la sección de Investigación de Mercado."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name = company_name
        self.period = period
        self.db = DatabaseManager(DB_FILE)
        
        # Configuración inicial de la ventana
        self.title(TEXTS["window_title"])
        self.geometry("1050x850")
        self.minsize(900, 700)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configurar estilos
        self._configure_styles()
        
        # Variables de control
        self.entry_vars: Dict[str, tk.StringVar] = {}
        self.calculated_vars: Dict[str, tk.StringVar] = {}
        
        # Crear widgets
        self._create_widgets()
        
        # Cargar datos iniciales
        self._load_data()
    
    def _configure_styles(self):
        """Configura los estilos visuales de la aplicación."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#DCDAD5")
        style.configure("TLabel", background="#DCDAD5", font=("Inter", 10))
        style.configure("TLabelFrame", background="#DCDAD5", font=("Inter", 11, "bold"))
        style.configure("TEntry", fieldbackground="white", relief="solid", padding=2)
        style.configure("TButton", font=("Inter", 10, "bold"))
        style.configure("Bold.TLabel", font=("Inter", 10, "bold"))
    
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        # Canvas desplazable
        self.canvas = tk.Canvas(self, bg="#DCDAD5")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Contenedor principal
        self.container = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.container, anchor="nw")
        self.container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Secciones de la interfaz
        self._create_company_info_section()
        self._create_research_table()
        self._create_action_buttons()
    
    def _create_company_info_section(self):
        """Crea la sección que muestra información de la empresa y período."""
        frame = ttk.LabelFrame(self.container, text=TEXTS["company_frame"], padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)
        
        # Mostrar nombre de la empresa (no editable)
        ttk.Label(frame, text=TEXTS["company_label"]).grid(row=0, column=0, padx=4, pady=2, sticky="w")
        ttk.Label(frame, text=self.company_name, font=("Inter", 10, "bold")).grid(
            row=0, column=1, padx=4, pady=2, sticky="w"
        )
        frame.columnconfigure(1, weight=1)
        
        # Mostrar período (no editable)
        ttk.Label(frame, text=TEXTS["period_label"]).grid(row=0, column=2, padx=4, pady=2, sticky="w")
        ttk.Label(frame, text=str(self.period), font=("Inter", 10, "bold")).grid(
            row=0, column=3, padx=4, pady=2, sticky="w"
        )
    
    def _create_research_table(self):
        """Crea la tabla de investigación de mercado."""
        self.research_items = [
            "IM-1a_Potencial Continente para 1 Período",
            "IM-1b_Potencial Continente para 2 Períodos",
            "IM-1c_Potencial Continente para 3 Períodos",
            "IM-2a_Potencial País para 1 Período",
            "IM-2b_Potencial País para 2 Períodos",
            "IM-2c_Potencial País para 3 Período",
            "IM-3a_Potencial Canal para 1 Período",
            "IM-3b_Potencial Canal para 2 Período",
            "IM-3c_Potencial Canal para 3 Período",
            "IM-6_Condiciones de Crédito",
            "IM-7_Total Inversión Publicitaria",
            "IM-9_Participación Unidades por País",
            "IM-10_Participación Unidades por Canal",
            "IM-11_Participación en US$ ventas por País",
            "IM-12_Participación en US$ ventas por Canal",
            "IM-14_Demanda insatisfecha",
            "IM-15_Venta unidades por canal",
            "IM-16_Venta unidades por país",
            "IM-17_Precios reales por canal",
            "IM-18_Total Monto Invertido en Promoción",
            "IM-19_Remuneración Variable Vendedores",
            "IM-20_Mapa Posicionamiento",
            "IM-21_Producción Ordenada",
            "IM-22_Tipo de Medios Publicitarios Utilizados",
            "IM-24_Numero de Vendedores",
            "IM-25_Eficiencia Vendedores",
        ]
        
        frame = ttk.LabelFrame(
            self.container, 
            text=TEXTS["research_frame"], 
            padding=(10, 5)
        )
        frame.pack(fill="x", padx=10, pady=10)
        
        # Encabezados de la tabla
        for col, header in enumerate(TEXTS["headers"]):
            ttk.Label(frame, text=header, style="Bold.TLabel").grid(
                row=0, column=col, padx=4, pady=2
            )
            frame.columnconfigure(col, weight=1 if col else 3)
        
        # Filas de la tabla
        for row, item in enumerate(self.research_items, start=1):
            # Nombre del ítem
            ttk.Label(frame, text=item, anchor="w", wraplength=250).grid(
                row=row, column=0, padx=4, pady=2, sticky="w"
            )
            
            # Campos de entrada
            for idx, col_name in enumerate(TEXTS["headers"][1:-1]):
                key = self._generate_field_key(item, col_name)
                entry = self._create_entry(frame, key)
                entry.grid(row=row, column=idx+1, padx=2, pady=2, sticky="ew")
            
            # Campo de costo calculado
            cost_key = self._generate_field_key(item, "Costo")
            lbl = self._create_calculated_label(frame, cost_key)
            lbl.grid(row=row, column=4, padx=2, pady=2, sticky="ew")
        
        # Total de costos
        ttk.Label(frame, text=TEXTS["total_cost_label"], style="Bold.TLabel").grid(
            row=len(self.research_items)+1, column=0, columnspan=4, padx=4, pady=6, sticky="w"
        )
        self._create_calculated_label(frame, "total_costo_inversiones").grid(
            row=len(self.research_items)+1, column=4, padx=2, pady=6, sticky="ew"
        )
    
    def _create_action_buttons(self):
        """Crea los botones de acción en la parte inferior."""
        frame = ttk.Frame(self.container, padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)
        
        # Configurar columnas con peso igual
        for i in range(3):
            frame.columnconfigure(i, weight=1)
        
        # Botones
        ttk.Button(
            frame, 
            text=TEXTS["save_btn"], 
            command=self._save_data
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Button(
            frame, 
            text=TEXTS["load_btn"], 
            command=self._load_data
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Button(
            frame, 
            text=TEXTS["back_btn"], 
            command=self._on_closing
        ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
    
    def _create_entry(self, parent, key: str) -> ttk.Entry:
        """Crea un campo de entrada y registra su variable."""
        var = tk.StringVar()
        self.entry_vars[key] = var
        var.trace_add("write", lambda *_: self._calculate_costs())
        return ttk.Entry(parent, width=12, textvariable=var)
    
    def _create_calculated_label(self, parent, key: str) -> ttk.Label:
        """Crea una etiqueta para valores calculados."""
        var = tk.StringVar(value="0.00")
        self.calculated_vars[key] = var
        return ttk.Label(
            parent, 
            textvariable=var, 
            style="Bold.TLabel", 
            anchor="e"
        )
    
    # ────────────────────────────────────────────────────────────────────────────────
    #  Lógica de Negocio
    # ────────────────────────────────────────────────────────────────────────────────
    
    def _generate_field_key(self, item: str, field: str) -> str:
        """Genera una clave única para cada campo."""
        return f"mr_{item.replace(' ', '_').replace('.', '').replace('-', '_')}_{field}"
    
    def _calculate_costs(self):
        """Calcula los costos basados en los valores ingresados."""
        total = 0.0
        
        for item in self.research_items:
            try:
                # Obtener claves para los campos relevantes
                key_home = self._generate_field_key(item, "Home")
                key_pro = self._generate_field_key(item, "Professional")
                key_unit = self._generate_field_key(item, "Precio Unitario")
                key_cost = self._generate_field_key(item, "Costo")
                
                # Obtener valores (0 si está vacío o no es número)
                h = float(self.entry_vars[key_home].get() or 0)
                p = float(self.entry_vars[key_pro].get() or 0)
                u = float(self.entry_vars[key_unit].get() or 0)
                
                # Calcular costo y actualizar
                costo = (h * u) + (p * u)
                self.calculated_vars[key_cost].set(f"{costo:,.2f}")
                total += costo
            except ValueError:
                # Manejar errores de conversión
                self.calculated_vars[key_cost].set("Error")
        
        # Actualizar total
        self.calculated_vars["total_costo_inversiones"].set(f"{total:,.2f}")
    
    def _save_data(self):
        """Guarda los datos de investigación de mercado."""
        # Preparar los datos para guardar
        data = {
            "market_research": {
                **{k: v.get() for k, v in self.entry_vars.items()},
                **{k: v.get() for k, v in self.calculated_vars.items()}
            }
        }
        
        # Guardar en la base de datos
        if self.db.save_decision(self.company_id, self.period, data):
            messagebox.showinfo(
                TEXTS["save_success"],
                parent=self
            )
        else:
            messagebox.showerror(
                "Error",
                "No se pudo guardar los datos",
                parent=self
            )
    
    def _load_data(self):
        """Carga los datos de investigación de mercado."""
        data = self.db.load_decision(self.company_id, self.period)
        if not data or "market_research" not in data:
            self._clear_fields()
            return
        
        research_data = data["market_research"]
        
        # Cargar valores en los campos
        for key, var in self.entry_vars.items():
            if key in research_data:
                var.set(research_data[key])
        
        # Cargar valores calculados
        for key, var in self.calculated_vars.items():
            if key in research_data:
                try:
                    value = float(research_data[key].replace(",", "")) if research_data[key] else 0.0
                    var.set(f"{value:,.2f}")
                except (ValueError, AttributeError):
                    var.set(research_data[key])
        
        # Recalcular costos
        self._calculate_costs()
    
    def _clear_fields(self):
        """Limpia todos los campos del formulario."""
        for var in self.entry_vars.values():
            var.set("")
        
        for var in self.calculated_vars.values():
            var.set("0.00")
    
    def _on_closing(self):
        """Maneja el cierre de la ventana."""
        self.destroy()
        self.parent_app.show_main_menu()
