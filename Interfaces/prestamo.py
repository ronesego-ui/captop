import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Any

# ────────────────────────────────────────────────────────────────────────────────
#  Configuración y Constantes
# ────────────────────────────────────────────────────────────────────────────────

DB_FILE = Path(__file__).parent.parent / "captop.db"

# Textos para internacionalización
TEXTS = {
    "window_title": "Decisiones de Financiamiento",
    "company_frame": "Empresa y Período",
    "company_label": "Empresa:",
    "period_label": "Período:",
    "long_term": "Largo Plazo",
    "short_term": "Corto Plazo",
    "credit_line": "Línea de Crédito",
    "amount_label": "Monto:",
    "term_label": "Plazo (años):",
    "grace_label": "Periodo Gracia:",
    "save_btn": "Guardar Decisiones",
    "load_btn": "Cargar Decisiones",
    "back_btn": "Volver al Menú Principal",
    "save_success": "Decisiones guardadas correctamente.",
    "load_success": "Decisiones cargadas correctamente.",
    "no_data": "No se encontraron datos para este período.",
    "error": "Error",
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
        """Guarda las decisiones en la base de datos."""
        with self.get_connection() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "REPLACE INTO decision (company_id, period, payload) VALUES (?, ?, ?)",
                    (company_id, period, json.dumps(payload))
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                messagebox.showerror(TEXTS["error"], f"Error de base de datos: {str(e)}")
                return False
    
    def load_decision(self, company_id: int, period: int) -> Optional[Dict]:
        """Carga las decisiones desde la base de datos."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT payload FROM decision WHERE company_id = ? AND period = ?",
                (company_id, period)
            )
            row = cur.fetchone()
            return json.loads(row["payload"]) if row else None

# ────────────────────────────────────────────────────────────────────────────────
#  Vista - Interfaz de Usuario
# ────────────────────────────────────────────────────────────────────────────────

class LoanDecisionsUI(tk.Toplevel):
    """Interfaz gráfica para la sección de Decisiones de Financiamiento."""
    
    def __init__(self, parent_app, company_id: int, company_name: str, period: int):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name = company_name
        self.period = period
        self.db = DatabaseManager(DB_FILE)
        
        # Configuración inicial de la ventana
        self.title(TEXTS["window_title"])
        self.geometry("800x650")
        self.minsize(700, 550)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configurar estilos
        self._configure_styles()
        
        # Variables de control
        self.entry_vars: Dict[str, tk.StringVar] = {}
        self.combo_vars: Dict[str, tk.StringVar] = {}
        
        # Crear widgets
        self._create_widgets()
        
        # Cargar datos iniciales
        self._load_data()
    
    def _configure_styles(self):
        """Configura los estilos visuales de la aplicación."""
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
        style.configure('Centered.TLabel', anchor='center', font=('Inter', 12, 'bold'))
    
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        # Canvas desplazable
        self.canvas = tk.Canvas(self, bg='#DCDAD5')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Sección de información de empresa y período
        self._create_company_info_section()
        
        # Título Principal
        ttk.Label(
            self.scrollable_frame, 
            text="Decisiones de Financiamiento", 
            font=('Inter', 18, 'bold'), 
            anchor='center'
        ).pack(pady=(10, 20), fill="x")
        
        # Secciones de financiamiento
        self._create_long_term_section()
        self._create_short_term_section()
        self._create_credit_line_section()
        
        # Botones de acción
        self._create_action_buttons()
    
    def _create_company_info_section(self):
        """Crea la sección que muestra información de la empresa y período."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["company_frame"], padding=(10, 5))
        frame.pack(fill="x", padx=10, pady=10)
        
        # Mostrar nombre de la empresa (no editable)
        ttk.Label(frame, text=TEXTS["company_label"]).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=self.company_name, font=('Inter', 10, 'bold')).grid(
            row=0, column=1, padx=5, pady=2, sticky='w'
        )
        frame.columnconfigure(1, weight=1)
        
        # Mostrar período (no editable)
        ttk.Label(frame, text=TEXTS["period_label"]).grid(row=0, column=2, padx=5, pady=2, sticky='w')
        ttk.Label(frame, text=str(self.period), font=('Inter', 10, 'bold')).grid(
            row=0, column=3, padx=5, pady=2, sticky='w'
        )
    
    def _create_long_term_section(self):
        """Crea la sección para préstamos a largo plazo."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["long_term"], padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=5)
        frame.columnconfigure(1, weight=1)
        
        # Monto Largo Plazo
        ttk.Label(frame, text=TEXTS["amount_label"]).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.entry_vars["long_term_amount"] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.entry_vars["long_term_amount"]).grid(
            row=0, column=1, padx=5, pady=2, sticky='ew'
        )
        
        # Plazo (años)
        ttk.Label(frame, text=TEXTS["term_label"]).grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.combo_vars["loan_term"] = tk.StringVar()
        loan_term_options = [str(i) for i in range(2, 9)]  # 2 a 8 años
        ttk.Combobox(
            frame, 
            textvariable=self.combo_vars["loan_term"],
            values=loan_term_options, 
            state="readonly"
        ).grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        
        # Periodo Gracia
        ttk.Label(frame, text=TEXTS["grace_label"]).grid(row=2, column=0, padx=5, pady=2, sticky='w')
        self.combo_vars["grace_period"] = tk.StringVar()
        grace_period_options = ["0", "1", "2"]
        ttk.Combobox(
            frame, 
            textvariable=self.combo_vars["grace_period"],
            values=grace_period_options, 
            state="readonly"
        ).grid(row=2, column=1, padx=5, pady=2, sticky='ew')
    
    def _create_short_term_section(self):
        """Crea la sección para préstamos a corto plazo."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["short_term"], padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=5)
        frame.columnconfigure(1, weight=1)
        
        # Monto Corto Plazo
        ttk.Label(frame, text=TEXTS["amount_label"]).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.entry_vars["short_term_amount"] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.entry_vars["short_term_amount"]).grid(
            row=0, column=1, padx=5, pady=2, sticky='ew'
        )
    
    def _create_credit_line_section(self):
        """Crea la sección para línea de crédito."""
        frame = ttk.LabelFrame(self.scrollable_frame, text=TEXTS["credit_line"], padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=5)
        frame.columnconfigure(1, weight=1)
        
        # Monto Línea de Crédito
        ttk.Label(frame, text=TEXTS["amount_label"]).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.entry_vars["credit_line_amount"] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.entry_vars["credit_line_amount"]).grid(
            row=0, column=1, padx=5, pady=2, sticky='ew'
        )
    
    def _create_action_buttons(self):
        """Crea los botones de acción en la parte inferior."""
        frame = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        frame.pack(fill="x", padx=10, pady=10)
        
        # Configurar columnas con peso igual
        for i in range(3):
            frame.columnconfigure(i, weight=1)
        
        # Botones
        ttk.Button(
            frame, 
            text=TEXTS["save_btn"], 
            command=self._save_data
        ).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        ttk.Button(
            frame, 
            text=TEXTS["load_btn"], 
            command=self._load_data
        ).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Button(
            frame, 
            text=TEXTS["back_btn"], 
            command=self._on_closing
        ).grid(row=0, column=2, padx=5, pady=5, sticky='ew')
    
    def _get_numeric_value(self, value_str: str) -> Optional[float]:
        """Convierte el valor a float o devuelve None si no es válido."""
        if not value_str:
            return None
        try:
            return float(value_str.replace(',', ''))
        except ValueError:
            return None
    
    def _save_data(self):
        """Guarda los datos en la base de datos."""
        # Recopilar todos los datos de entrada
        loan_decisions_data = {
            "long_term_amount": self._get_numeric_value(self.entry_vars["long_term_amount"].get()),
            "loan_term": self._get_numeric_value(self.combo_vars["loan_term"].get()),
            "grace_period": self._get_numeric_value(self.combo_vars["grace_period"].get()),
            "short_term_amount": self._get_numeric_value(self.entry_vars["short_term_amount"].get()),
            "credit_line_amount": self._get_numeric_value(self.entry_vars["credit_line_amount"].get()),
        }
        
        # Cargar el payload existente para el período y actualizar solo las decisiones de préstamo
        existing_data = self.db.load_decision(self.company_id, self.period) or {}
        existing_data["loan_decisions"] = loan_decisions_data
        
        if self.db.save_decision(self.company_id, self.period, existing_data):
            messagebox.showinfo(TEXTS["save_success"], TEXTS["save_success"])
        else:
            messagebox.showerror(TEXTS["error"], "No se pudieron guardar los datos.")
    
    def _load_data(self):
        """Carga los datos desde la base de datos."""
        data = self.db.load_decision(self.company_id, self.period)
        if not data:
            messagebox.showinfo(TEXTS["no_data"], TEXTS["no_data"])
            self._clear_fields()
            return
        
        loaded_data = data.get("loan_decisions", {})
        
        # Rellenar los campos de entrada
        if "long_term_amount" in loaded_data:
            self.entry_vars["long_term_amount"].set(str(loaded_data["long_term_amount"] or ""))
        
        if "loan_term" in loaded_data:
            self.combo_vars["loan_term"].set(str(loaded_data["loan_term"] or ""))
        
        if "grace_period" in loaded_data:
            self.combo_vars["grace_period"].set(str(loaded_data["grace_period"] or ""))
        
        if "short_term_amount" in loaded_data:
            self.entry_vars["short_term_amount"].set(str(loaded_data["short_term_amount"] or ""))
        
        if "credit_line_amount" in loaded_data:
            self.entry_vars["credit_line_amount"].set(str(loaded_data["credit_line_amount"] or ""))
        
        messagebox.showinfo(TEXTS["load_success"], TEXTS["load_success"])
    
    def _clear_fields(self):
        """Limpia todos los campos del formulario."""
        for var in self.entry_vars.values():
            var.set("")
        for var in self.combo_vars.values():
            var.set("")
    
    def _on_closing(self):
        """Maneja el cierre de la ventana."""
        self.destroy()
        self.parent_app.show_main_menu()
