import tkinter as tk
from tkinter import ttk, messagebox
import bcchapi as bcch
import pandas as pd
import logging
from datetime import datetime
import sqlite3

logger = logging.getLogger(__name__)

class UFDataUI(tk.Toplevel):
    def __init__(self, parent_app, company_id, company_name, period, model):
        super().__init__()
        self.parent_app = parent_app
        self.company_id = company_id
        self.company_name = company_name
        self.period = period
        self.model = model
        
        self.title(f"Datos UF - {company_name} (Período {period})")
        self.geometry("800x500")
        self.resizable(True, True)
        
        self._create_widgets()
        self._load_existing_data()
        
        # Configurar el protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Cabecera
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(header_frame, text="Datos Mensuales de la UF", 
                 font=('Century Gothic', 14, 'bold')).pack(side="left")
        
        # Botones de acción
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        ttk.Button(btn_frame, text="Consultar BCCh", 
                  command=self._fetch_bcch_data, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Guardar", 
                  command=self._save_data, width=10).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atrás", 
                  command=self._on_closing, width=10).pack(side="left", padx=5)
        
        # Área de datos
        data_frame = ttk.LabelFrame(main_frame, text="Datos UF", padding="10")
        data_frame.pack(fill="both", expand=True)
        
        # Treeview para mostrar datos
        columns = ("fecha", "valor")
        self.tree = ttk.Treeview(data_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configurar columnas
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("valor", text="Valor UF")
        self.tree.column("fecha", width=150, anchor="center")
        self.tree.column("valor", width=150, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Estado
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief="sunken", anchor="w")
        status_bar.pack(fill="x", pady=(10, 0))
        self.status_var.set("Listo")
    
    def _fetch_bcch_data(self):
        try:
            self.status_var.set("Consultando BCCh...")
            self.update_idletasks()
            
            # Consultar datos al BCCh
            siete = bcch.Siete("ronesego@outlook.com", "24052Mil6")
            uf_mensual = siete.cuadro(
                series=["F073.UFF.PRE.Z.D"],
                nombres=["UF"],
                desde="2025-01-01",
                hasta=datetime.now().strftime("%Y-%m-%d"),
                variacion=0,
                frecuencia="ME",
                observado={"UF": "last"}
            )
            
            # Procesar datos
            df = uf_mensual.reset_index()
            df.columns = ['Fecha', 'Valor_UF']
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.strftime('%Y-%m-%d')
            df['Valor_UF'] = df['Valor_UF'].astype(float)
            
            # Actualizar treeview
            self._update_treeview(df)
            self.status_var.set(f"Datos obtenidos: {len(df)} registros")
            
        except Exception as e:
            logger.error(f"Error consultando BCCh: {str(e)}")
            self.status_var.set("Error en la consulta")
            messagebox.showerror("Error", f"No se pudieron obtener datos del BCCh: {str(e)}")
    
    def _update_treeview(self, df):
        # Limpiar datos existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar nuevos datos
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(
                row['Fecha'],
                f"{row['Valor_UF']:,.0f}".replace(',', '.')  # Formatear con separadores
            ))
    
    def _save_data(self):
        try:
            # Recoger datos del treeview
            data_to_save = []
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                fecha = values[0]
                #valor = float(values[1].replace('.', ''))  # Convertir a float
                valor_str = values[1].replace('.', '')
                valor = float(valor_str)
                data_to_save.append((fecha, valor))
            
            # Guardar en la base de datos
            count = 0
            for fecha, valor in data_to_save:
                if self.model.save_uf_data(fecha, valor):
                    count += 1
            
            self.status_var.set(f"Datos guardados: {count} registros")
            messagebox.showinfo("Éxito", f"Se guardaron {count} registros de UF en la base de datos")
            
        except Exception as e:
            logger.error(f"Error guardando datos UF: {str(e)}")
            self.status_var.set("Error al guardar")
            messagebox.showerror("Error", f"No se pudieron guardar los datos: {str(e)}")
    
    def _load_existing_data(self):
        try:
            uf_data = self.model.get_uf_data()
            if uf_data:
                # Limpiar treeview
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Insertar datos existentes
                for fecha, valor in uf_data:
                    self.tree.insert("", "end", values=(
                        fecha,
                        f"{valor:,.0f}".replace(',', '.')  # Formatear con separadores
                    ))
                self.status_var.set(f"Datos cargados: {len(uf_data)} registros")
            else:
                self.status_var.set("No hay datos UF almacenados")
                
        except Exception as e:
            logger.error(f"Error cargando datos UF: {str(e)}")
            self.status_var.set("Error al cargar datos")
    
    def _on_closing(self):
        """Maneja el cierre de la ventana"""
        self.destroy()
        self.parent_app.show_main_menu()