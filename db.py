# captop/db.py

import sqlite3
from pathlib import Path

# Define la ruta de la base de datos
DB_FILE = Path(__file__).parent.parent / "captop.db"

def get_connection():
    """Establece y devuelve una conexión a la base de datos."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Permite acceder a las columnas por nombre
    return conn

def init_schema():
    """Inicializa el esquema de la base de datos si no existe."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Tabla de Compañías (CORREGIDA: Añadida reporting_currency_exchange_rate)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                cash_usd REAL NOT NULL,
                current_period INTEGER NOT NULL DEFAULT 1,
                reporting_currency_exchange_rate REAL NOT NULL DEFAULT 950.0 -- Valor por defecto inicial, se actualizará
            );
        """)

        # Tabla de Fábricas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS factory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                country TEXT NOT NULL,
                line TEXT NOT NULL,
                built_period INTEGER NOT NULL,
                FOREIGN KEY (company_id) REFERENCES company(id)
            );
        """)

        # Tabla de Inventario (CORREGIDA: Añadida company_id y en la clave primaria)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                company_id INTEGER NOT NULL,
                period INTEGER NOT NULL,
                product_line TEXT NOT NULL,
                country TEXT NOT NULL,
                units REAL NOT NULL,
                PRIMARY KEY (company_id, period, product_line, country),
                FOREIGN KEY (company_id) REFERENCES company(id)
            );
        """)

        # Tabla de Decisiones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decision (
                company_id INTEGER NOT NULL,
                period INTEGER NOT NULL,
                payload TEXT NOT NULL, -- JSON con todas las decisiones del período
                PRIMARY KEY (company_id, period),
                FOREIGN KEY (company_id) REFERENCES company(id)
            );
        """)
        
        # Tabla del Ledger (libro mayor)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                period INTEGER NOT NULL,
                type TEXT NOT NULL, -- Ej: REVENUE, PRODUCTION_COST, MARKETING_COST, TAX_EXPENSE, etc.
                amount REAL NOT NULL,
                currency TEXT NOT NULL, -- <-- Asegura que esta columna exista
                note TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES company(id)
            );
        """)

        # Tabla de Estados Financieros (Balance y Estado de Resultados)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_statement (
                company_id INTEGER NOT NULL,
                period INTEGER NOT NULL,
                type TEXT NOT NULL, -- Ej: BALANCE_SHEET, INCOME_STATEMENT
                data TEXT NOT NULL, -- JSON con los datos del estado financiero
                PRIMARY KEY (company_id, period, type),
                FOREIGN KEY (company_id) REFERENCES company(id)
            );
        """)

        conn.commit()