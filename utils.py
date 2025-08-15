import json
import hashlib
from datetime import datetime
import os

def cargar_datos():
    """Carga los datos desde el archivo JSON"""
    try:
        with open('datos/data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Crear estructura por defecto si no existe
        datos_por_defecto = {
            "usuarios": [
                {
                    "id": "admin_001",
                    "username": "admin",
                    "password": hashlib.sha256("admin123".encode()).hexdigest(),
                    "nombre": "Administrador",
                    "email": "admin@universidad.edu",
                    "rol": "admin",
                    "fecha_registro": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "proyectos": [],
            "calificaciones": [],
            "ranking": {
                "proyectos_ganadores": [],
                "ultima_actualizacion": None
            },
            "configuracion": {
                "pesos_criterios": {
                    "innovacion": 30,
                    "viabilidad": 25,
                    "impacto": 20,
                    "ejecucion": 15,
                    "pitch": 10
                }
            }
        }
        guardar_datos(datos_por_defecto)
        return datos_por_defecto

def guardar_datos(datos):
    """Guarda los datos en el archivo JSON"""
    # Crear directorio si no existe
    os.makedirs('datos', exist_ok=True)
    
    with open('datos/data.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def generar_id(prefix):
    """Genera un ID único con prefijo"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{timestamp}"

def esta_en_horario_presentacion(horas_presentacion):
    """Verifica si la hora actual está dentro del horario de presentación"""
    if not horas_presentacion or horas_presentacion == 'Sin horario asignado':
        return False
    
    try:
        hora_actual = datetime.now().time()
        
        # Parsear horario (formato: "14:00 - 15:00")
        if ' - ' in horas_presentacion:
            inicio_str, fin_str = horas_presentacion.split(' - ')
            inicio = datetime.strptime(inicio_str, '%H:%M').time()
            fin = datetime.strptime(fin_str, '%H:%M').time()
            
            return inicio <= hora_actual <= fin
        else:
            # Si solo hay una hora, considerar 1 hora de presentación
            hora_presentacion = datetime.strptime(horas_presentacion, '%H:%M').time()
            inicio = hora_presentacion
            fin = datetime.strptime(f"{hora_presentacion.hour + 1:02d}:{hora_presentacion.minute:02d}", '%H:%M').time()
            
            return inicio <= hora_actual <= fin
    except:
        return False

def calcular_calificacion_ponderada(criterios, pesos):
    """Calcula la calificación ponderada basada en los criterios y pesos"""
    total = 0
    
    for criterio, calificacion in criterios.items():
        if criterio in pesos:
            total += calificacion * (pesos[criterio] / 100)
    
    return round(total, 2)

def actualizar_ranking(datos):
    """Actualiza el ranking de proyectos"""
    # Obtener proyectos calificados
    proyectos_calificados = [p for p in datos['proyectos'] if p.get('calificacion_final', 0) > 0]
    
    # Ordenar por calificación (descendente)
    proyectos_ordenados = sorted(
        proyectos_calificados, 
        key=lambda x: x['calificacion_final'], 
        reverse=True
    )
    
    # Top 3 ganadores
    top_3 = proyectos_ordenados[:3]
    
    # Crear lista de ganadores con premios
    ganadores = []
    premios = ["🥇 1er Lugar", "🥈 2do Lugar", "🥉 3er Lugar"]
    
    for i, proyecto in enumerate(top_3):
        ganadores.append({
            "id": proyecto['id'],
            "nombre_proyecto": proyecto['nombre'],
            "asignatura": proyecto['asignatura'],
            "carrera": proyecto['carrera'],
            "calificacion_final": proyecto['calificacion_final'],
            "premio": premios[i] if i < len(premios) else f"{i+1}º Lugar"
        })
    
    # Actualizar ranking
    datos['ranking']['proyectos_ganadores'] = ganadores
    datos['ranking']['ultima_actualizacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return datos

def autenticar_usuario(username, password, datos):
    """Autentica un usuario con las credenciales proporcionadas"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    for usuario in datos['usuarios']:
        if usuario['username'] == username and usuario['password'] == password_hash:
            return True
    
    return False

def obtener_usuario_por_username(username, datos):
    """Obtiene un usuario por su nombre de usuario"""
    for usuario in datos['usuarios']:
        if usuario['username'] == username:
            return usuario
    return None
