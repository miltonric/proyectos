# Configuración del sistema de calificación

# Configuración de la página Streamlit
PAGE_CONFIG = {
    "page_title": "Sistema de Calificación - Trabajos de Fin de Asignatura",
    "page_icon": "🏆",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configuración de criterios de calificación
CRITERIOS_CALIFICACION = {
    "innovacion": {
        "nombre": "INNOVACIÓN",
        "peso": 30,
        "descripcion": "¿Qué hace único al proyecto? ¿Es disruptivo?",
        "min_value": 0,
        "max_value": 10,
        "default_value": 5
    },
    "viabilidad": {
        "nombre": "VIABILIDAD",
        "peso": 25,
        "descripcion": "¿Es factible implementarlo? ¿Qué recursos necesita?",
        "min_value": 0,
        "max_value": 10,
        "default_value": 5
    },
    "impacto": {
        "nombre": "IMPACTO",
        "peso": 20,
        "descripcion": "¿A quién beneficia? ¿Qué problema soluciona?",
        "min_value": 0,
        "max_value": 10,
        "default_value": 5
    },
    "ejecucion": {
        "nombre": "EJECUCIÓN",
        "peso": 15,
        "descripcion": "¿Está bien desarrollado? ¿Qué tan profesional es?",
        "min_value": 0,
        "max_value": 10,
        "default_value": 5
    },
    "pitch": {
        "nombre": "PITCH",
        "peso": 10,
        "descripcion": "¿Convencieron al panel? ¿Comunicaron claramente?",
        "min_value": 0,
        "max_value": 10,
        "default_value": 5
    }
}

# Configuración de roles
ROLES = {
    "admin": {
        "nombre": "Administrador",
        "permisos": ["dashboard", "registro_proyecto", "calificacion_proyecto", "ranking", "usuarios", "reportes"]
    },
    "docente": {
        "nombre": "Docente",
        "permisos": ["dashboard_docente", "calificacion_proyecto"]
    }
}

# Configuración de estados de proyectos
ESTADOS_PROYECTO = {
    "pendiente": "Pendiente",
    "calificado": "Ya Calificado",
    "en_horario": "En Horario de Presentación",
    "fuera_horario": "Fuera de Horario"
}

# Configuración de colores para el dashboard
COLORES_DASHBOARD = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# Configuración de archivos
ARCHIVOS = {
    "datos": "datos/data.json",
    "backup": "datos/backup/",
    "logs": "logs/"
}

# Configuración de paginación
PAGINACION = {
    "proyectos_por_pagina": 10,
    "usuarios_por_pagina": 20
}

# Configuración de validaciones
VALIDACIONES = {
    "longitud_minima_password": 6,
    "longitud_maxima_nombre": 100,
    "longitud_maxima_descripcion": 1000,
    "max_estudiantes_por_proyecto": 5
}

# Configuración de notificaciones
NOTIFICACIONES = {
    "mostrar_balloons": True,
    "tiempo_mostrar_mensaje": 5,
    "mostrar_progreso": True
}
