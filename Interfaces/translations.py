# translations.py
TRANSLATIONS = {
    "es": {
        "welcome": "BIENVENIDO AL JUEGO DE EMPRESAS",
        "company_selection": "Selección de Empresa y Período",
        "new_company": "Nombre Nueva Empresa:",
        "create_company": "Crear Empresa",
        "select_existing": "Seleccionar Empresa Existente:",
        "period": "Período:",
        "load_company": "Cargar Empresa y Período",
        "current_company": "Empresa Seleccionada:",
        "current_period": "Período Seleccionado:",
        "menu_title": "Menú de Interfaces",
        "warning": "Advertencia",
        "select_company_first": "Por favor, cree o seleccione una empresa y período primero.",
        "exit_confirm": "¿Está seguro de que desea salir del juego?",
        "company_created": "Empresa '{name}' creada con éxito.",
        "company_empty": "El nombre de la empresa no puede estar vacío.",
        "company_short": "El nombre debe tener al menos 3 caracteres.",
        "company_long": "El nombre no puede exceder los 50 caracteres.",
        "company_invalid_chars": "Solo se permiten caracteres alfanuméricos y espacios.",
        "company_exists": "Ya existe una empresa con el nombre '{name}'.",
        "db_error": "Error de Base de Datos",
        "unexpected_error": "Error Inesperado",
        "company_loaded": "Empresa '{name}' (ID: {id}), Período {period} seleccionados.",
        "company_not_found": "La empresa seleccionada no existe en la base de datos.",
        "initial_period": "0",
        "window_title": "Juego de Empresas - Ingreso de Decisiones",
        "product_home": "NOTEBOOK HOME",
        "product_pro": "NOTEBOOK PROFESSIONAL",
        "company_period": "Empresa y Período",
        "company": "Empresa:",
        "current_period_display": "PERIODO ACTUAL: {}",
        "company_selected": "[Seleccione una empresa]",
        "decisions_title": "INGRESO DE DECISIONES DE LA EMPRESA",
        "save_success": "Decisiones guardadas para el período {period} de {company}.",
        "load_success": "Decisiones cargadas para el período {period}.",
        "load_empty": "No se encontraron decisiones para el período {period}.",
        "save_error": "Error al guardar decisiones: {error}",
        "invalid_period": "El período no es válido",
        "new_company_title": "Nombre de la nueva empresa:",
        "save": "Guardar Decisiones",
        "load": "Cargar Decisiones",
        "back": "Volver al Menú Principal",
        "price_credit": "PRECIOS Y CONDICIÓN DE CRÉDITO",
        "production": "PRODUCCIÓN - TRANSPORTE",
        "plant_purchase": "COMPRA DE PLANTAS DEL PERÍODO",
        "raw_materials": "Control de Materias Primas",
        "sales_points": "PUNTOS DE VENTAS",
        "seller_comp": "Remuneración Variable Vendedores",
        "advertising": "PUBLICIDAD (Frecuencia)",
        "investments": "INVERSIONES - PROMOCIONES SIN PUBLICIDAD"
    },
    "en": {
        "welcome": "WELCOME TO BUSINESS GAME",
        "company_selection": "Company and Period Selection",
        "new_company": "New Company Name:",
        "create_company": "Create Company",
        "select_existing": "Select Existing Company:",
        "period": "Period:",
        "load_company": "Load Company and Period",
        "current_company": "Selected Company:",
        "current_period": "Selected Period:",
        "menu_title": "Interfaces Menu",
        "warning": "Warning",
        "select_company_first": "Please create or select a company and period first.",
        "exit_confirm": "Are you sure you want to exit the game?",
        "company_created": "Company '{name}' created successfully.",
        "company_empty": "Company name cannot be empty.",
        "company_short": "Name must be at least 3 characters long.",
        "company_long": "Name cannot exceed 50 characters.",
        "company_invalid_chars": "Only alphanumeric characters and spaces are allowed.",
        "company_exists": "A company with name '{name}' already exists.",
        "db_error": "Database Error",
        "unexpected_error": "Unexpected Error",
        "company_loaded": "Company '{name}' (ID: {id}), Period {period} selected.",
        "company_not_found": "The selected company was not found in the database.",
        "initial_period": "0"
    }
}

CURRENT_LANGUAGE = "es"

def tr(key: str, **kwargs) -> str:
    """Obtiene la traducción para la clave dada y aplica formato."""
    translation = TRANSLATIONS[CURRENT_LANGUAGE].get(key, key)
    
    if isinstance(translation, str):
        try:
            return translation.format(**kwargs)
        except (KeyError, IndexError):
            return translation
    return str(translation)