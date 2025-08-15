import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from streamlit_option_menu import option_menu
import hashlib



# CSS mínimo y simple
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #ffffff;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .form-container {
        background: linear-gradient(135deg, #34495e, #2c3e50);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin: 1rem 0;
        border: 2px solid #3498db;
    }
    
    .ranking-card {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        text-align: center;
        border: 2px solid #f39c12;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .gold-medal {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-color: #FFD700;
    }
    
    .silver-medal {
        background: linear-gradient(135deg, #C0C0C0, #A9A9A9);
        border-color: #C0C0C0;
    }
    
    .bronze-medal {
        background: linear-gradient(135deg, #CD7F32, #B8860B);
        border-color: #CD7F32;
    }
</style>
""", unsafe_allow_html=True)

# Función para cargar datos
def cargar_datos():
    """Carga los datos desde el archivo JSON"""
    try:
        with open('datos/data.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        # Crear estructura inicial si no existe
        datos_iniciales = {
            "usuarios": [
                {
                    "id": "user_001",
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
            "configuracion": {
                "pesos_criterios": {
                    "innovacion": 30,
                    "viabilidad": 25,
                    "impacto": 20,
                    "ejecucion": 15,
                    "pitch": 10
                },
                "max_calificacion": 10,
                "min_calificacion": 0
            },
            "ranking": {
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
                "proyectos_ganadores": []
            }
        }
        
        # Crear directorio si no existe
        os.makedirs('datos', exist_ok=True)
        
        # Guardar datos iniciales
        with open('datos/data.json', 'w', encoding='utf-8') as file:
            json.dump(datos_iniciales, file, indent=2, ensure_ascii=False)
        
        return datos_iniciales

# Función para guardar datos
def guardar_datos(datos):
    """Guarda los datos en el archivo JSON"""
    with open('datos/data.json', 'w', encoding='utf-8') as file:
        json.dump(datos, file, indent=2, ensure_ascii=False)

# Función para autenticar usuarios
def autenticar_usuario(username, password, datos):
    """Autentica un usuario con username y password"""
    for usuario in datos['usuarios']:
        if usuario['username'] == username:
            hash_almacenado = usuario['password']
            return hashlib.sha256(password.encode()).hexdigest() == hash_almacenado
    return False

# Función para generar IDs únicos
def generar_id(prefix):
    """Genera un ID único con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}_{timestamp}"

# Función para calcular calificación ponderada
def calcular_calificacion_ponderada(criterios, pesos):
    """Calcula la calificación ponderada según los criterios y pesos"""
    total = 0
    for criterio, calificacion in criterios.items():
        if criterio in pesos:
            # Convertir el peso de porcentaje a decimal y multiplicar por la calificación
            peso_decimal = pesos[criterio] / 100
            total += calificacion * peso_decimal
    return round(total, 2)

# Función para verificar si está en horario de presentación
def esta_en_horario_presentacion(horas_presentacion):
    """Verifica si la hora actual está dentro del horario de presentación"""
    try:
        if not horas_presentacion or ' - ' not in horas_presentacion:
            return False
        
        hora_inicio_str, hora_fin_str = horas_presentacion.split(' - ')
        hora_actual = datetime.now().strftime("%H:%M")
        
        # Convertir a objetos datetime para comparación
        hora_inicio_time = datetime.strptime(hora_inicio_str, "%H:%M").time()
        hora_fin_time = datetime.strptime(hora_fin_str, "%H:%M").time()
        hora_actual_time = datetime.strptime(hora_actual, "%H:%M").time()
        
        return hora_inicio_time <= hora_actual_time <= hora_fin_time
    except:
        return False

# Función para actualizar ranking
def actualizar_ranking(datos):
    """Actualiza el ranking de proyectos basado en las calificaciones"""
    # Calcular calificación final para cada proyecto
    for proyecto in datos['proyectos']:
        if proyecto['calificaciones']:
            # Obtener todas las calificaciones del proyecto
            calificaciones_proyecto = [
                cal for cal in datos['calificaciones'] 
                if cal['proyecto_id'] == proyecto['id']
            ]
            
            if calificaciones_proyecto:
                # Calcular promedio de calificaciones ponderadas
                calificaciones_ponderadas = [cal['calificacion_ponderada'] for cal in calificaciones_proyecto]
                proyecto['calificacion_final'] = round(sum(calificaciones_ponderadas) / len(calificaciones_ponderadas), 2)
            else:
                proyecto['calificacion_final'] = 0
        else:
            proyecto['calificacion_final'] = 0
    
    # Ordenar proyectos por calificación final
    proyectos_ordenados = sorted(
        [p for p in datos['proyectos'] if p['calificacion_final'] > 0],
        key=lambda x: x['calificacion_final'],
        reverse=True
    )
    
    # Actualizar top 3
    datos['ranking']['proyectos_ganadores'] = []
    premios = ["🥇 Oro", "🥈 Plata", "🥉 Bronce"]
    
    for i, proyecto in enumerate(proyectos_ordenados[:3]):
        datos['ranking']['proyectos_ganadores'].append({
            'premio': premios[i],
            'nombre_proyecto': proyecto['nombre'],
            'calificacion_final': proyecto['calificacion_final']
        })
    
    datos['ranking']['fecha_actualizacion'] = datetime.now().strftime("%Y-%m-%d")
    
    return datos

def main():
    """Función principal de la aplicación"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="Sistema de Calificación",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Ocultar elementos de Streamlit
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    datos = cargar_datos()
    
    # Verificar autenticación
    if 'usuario_actual' not in st.session_state:
        # Página de login
        mostrar_login(datos)
        return
    
    # Usuario autenticado - mostrar sidebar y contenido
    usuario = st.session_state.usuario_actual
    
    # Sidebar con menú
    with st.sidebar:
        st.markdown("##  Sistema de Calificación")
        
        # Mostrar información del usuario y rol
        st.markdown(f"**Usuario:** {usuario['nombre']}")
        st.markdown(f"{usuario['rol'].title()}")
        
        # Mostrar opciones disponibles según el rol
        if usuario['rol'] == 'admin':
            st.markdown("**Acceso:** Todas las funcionalidades")
        else:
            st.markdown("**Acceso:** Solo Dashboard y Calificar Proyecto")
        
        st.markdown("---")
        
        # Menú de opciones dinámico según el rol
        if usuario['rol'] == 'admin':
            # Administradores ven todas las opciones
            selected = option_menu(
                menu_title="Menú Principal",
                options=["Dashboard", "Registrar Proyecto", "Calificar Proyecto", "Ranking", "Usuarios", "Reportes"],
                icons=["house", "file-earmark-plus", "star", "trophy", "people", "graph-up"],
                menu_icon="cast",
                default_index=0,
            )
        else:
            # Docentes solo ven Dashboard y Calificar Proyecto
            selected = option_menu(
                menu_title="Menú Principal",
                options=["Dashboard", "Calificar Proyecto"],
                icons=["house", "star"],
                menu_icon="cast",
                default_index=0,
            )
        
        st.markdown("---")
        
        # Botón de cerrar sesión
        if st.button(" Cerrar Sesión", use_container_width=True):
            del st.session_state.usuario_actual
            st.rerun()
    
    # Mostrar contenido según la selección
    if selected == "Dashboard":
        mostrar_dashboard(datos)
    elif selected == "Calificar Proyecto":
        mostrar_calificacion_proyecto(datos)
    elif selected == "Registrar Proyecto":
        # Solo administradores pueden registrar proyectos
        if usuario['rol'] == 'admin':
            mostrar_registro_proyecto(datos)
        else:
            st.error("❌ Solo los administradores pueden registrar proyectos")
            st.info("👆 Selecciona otra opción del menú")
    elif selected == "Ranking":
        # Solo administradores pueden ver el ranking
        if usuario['rol'] == 'admin':
            mostrar_ranking(datos)
        else:
            st.error("❌ Solo los administradores pueden ver el ranking")
            st.info("👆 Selecciona otra opción del menú")
    elif selected == "Usuarios":
        # Solo administradores pueden gestionar usuarios
        if usuario['rol'] == 'admin':
            mostrar_usuarios(datos)
        else:
            st.error("❌ Solo los administradores pueden gestionar usuarios")
            st.info("👆 Selecciona otra opción del menú")
    elif selected == "Reportes":
        # Solo administradores pueden ver reportes
        if usuario['rol'] == 'admin':
            mostrar_reportes(datos)
        else:
            st.error("❌ Solo los administradores pueden ver reportes")
            st.info("👆 Selecciona otra opción del menú")
    
    # Botón para reabrir sidebar en móviles
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .mobile-menu-btn {
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 999;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 12px;
            font-size: 16px;
            cursor: pointer;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Agregar botón para dispositivos móviles
    col_mobile_menu, col_spacer = st.columns([1, 4])
    with col_mobile_menu:
        if st.button("☰ Menú", key="mobile_menu_btn", help="Abrir menú lateral"):
            st.session_state.sidebar_state = "expanded"
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Sistema de Calificación de Trabajos de Fin de Asignatura | 
        Desarrollado con Streamlit | 
        © 2025 UIDE campus Loja
    </div>
    """, unsafe_allow_html=True)

# Funciones para mostrar cada sección
def mostrar_login(datos):
    """Muestra la página de login"""
    st.markdown('<h1 class="main-header">🔐 Iniciar Sesión</h1>', unsafe_allow_html=True)
    
    with st.form("login"):
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader(" Ingresa tus credenciales")
        
        username = st.text_input("Usuario", placeholder="usuario123")
        password = st.text_input("Contraseña", type="password", placeholder="contraseña123")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True):
                if username and password:
                    if autenticar_usuario(username, password, datos):
                        st.session_state.usuario_actual = next(
                            u for u in datos['usuarios'] if u['username'] == username
                        )
                        st.success("✅ ¡Bienvenido!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                else:
                    st.error("❌ Por favor complete todos los campos")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Información adicional
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666;">
            <h4>📚 Información del Sistema</h4>
            <p>Este sistema permite a los docentes calificar proyectos de estudiantes</p>
            <p>y a los administradores gestionar todo el proceso.</p>
        </div>
        """, unsafe_allow_html=True)

def mostrar_dashboard(datos):
    """Muestra el dashboard principal"""
    st.markdown('<h1 class="main-header">🏠 Dashboard</h1>', unsafe_allow_html=True)
    
    # Mensaje de bienvenida según el rol
    if 'usuario_actual' in st.session_state:
        usuario = st.session_state.usuario_actual
        if usuario['rol'] == 'admin':
            st.success(f"👑 ¡Bienvenido Administrador {usuario['nombre']}! Tienes acceso completo a todas las funcionalidades del sistema.")
        else:
            st.info(f"👨‍🏫 ¡Bienvenido Docente {usuario['nombre']}! Puedes ver el dashboard y calificar proyectos.")
    
    # Hora actual y estado de proyectos
    hora_actual = datetime.now().strftime("%H:%M")
    st.markdown(f"### 🕐 Hora Actual: {hora_actual}")
    
    # Proyectos en horario de presentación
    proyectos_en_horario = []
    for proyecto in datos['proyectos']:
        if esta_en_horario_presentacion(proyecto.get('horas_presentacion', '00:00 - 00:00')):
            proyectos_en_horario.append(proyecto)
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📊 Total Proyectos", len(datos['proyectos']))
    with col2:
        st.metric("⏰ En Horario", len(proyectos_en_horario))
    with col3:
        st.metric("✅ Calificados", len([p for p in datos['proyectos'] if p.get('calificacion_final', 0) > 0]))
    with col4:
        st.metric("📚 Asignaturas", len(set([p.get('asignatura', '') for p in datos['proyectos']])))
    with col5:
        # Botón de descarga del JSON
        # Solo mostrar este botón si el usuario es admin
        if 'usuario_actual' in st.session_state and st.session_state.usuario_actual['rol'] == 'admin':
            if st.button("📥 Descargar Datos", key="descargar_json", use_container_width=True):
                # Crear archivo JSON para descarga
                json_str = json.dumps(datos, indent=2, ensure_ascii=False)
                st.download_button(
                    label="💾 Descargar data.json",
                    data=json_str.encode('utf-8'),
                    file_name=f"datos_proyectos_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    key="download_json"
                )
    
    # Búsqueda rápida
    st.markdown("---")
    st.markdown("#### 🔍 **Búsqueda Rápida**")
    
    # Inicializar historial de búsquedas
    if 'historial_busquedas' not in st.session_state:
        st.session_state.historial_busquedas = []
    
    col_busqueda_rapida, col_buscar_btn, col_sugerencias = st.columns([3, 1, 1])
    
    with col_busqueda_rapida:
        busqueda_rapida = st.text_input(
            "🔍 Buscar proyecto rápidamente...",
            placeholder="Escribe el nombre del proyecto...",
            key="busqueda_rapida"
        )
    
    with col_buscar_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Buscar", key="btn_busqueda_rapida", use_container_width=True):
            if busqueda_rapida and busqueda_rapida.strip():
                # Agregar a historial
                if busqueda_rapida not in st.session_state.historial_busquedas:
                    st.session_state.historial_busquedas.insert(0, busqueda_rapida)
                    if len(st.session_state.historial_busquedas) > 10:  # Mantener solo 10 búsquedas
                        st.session_state.historial_busquedas.pop()
                
                # Buscar proyecto específico
                proyecto_encontrado = None
                proyectos_similares = []
                
                for proyecto in datos['proyectos']:
                    nombre_proyecto = proyecto.get('nombre', '').lower()
                    busqueda_lower = busqueda_rapida.lower()
                    
                    if busqueda_lower in nombre_proyecto:
                        if not proyecto_encontrado:  # Primer match exacto
                            proyecto_encontrado = proyecto
                        else:
                            proyectos_similares.append(proyecto)
                
                if proyecto_encontrado:
                    st.success(f"✅ **Proyecto encontrado:** {proyecto_encontrado['nombre']}")
                    
                    # Mostrar detalles del proyecto
                    col_det1, col_det2 = st.columns(2)
                    with col_det1:
                        st.markdown(f"**📚 Asignatura:** {proyecto_encontrado.get('asignatura', 'N/A')}")
                        st.markdown(f"**🎓 Carrera:** {proyecto_encontrado.get('carrera', 'N/A')}")
                        st.markdown(f"**👥 Estudiantes:** {', '.join(proyecto_encontrado.get('estudiantes', []))}")
                    
                    with col_det2:
                        st.markdown(f"**⏰ Horario:** {proyecto_encontrado.get('horas_presentacion', 'N/A')}")
                        st.markdown(f"**⭐ Calificación:** {proyecto_encontrado.get('calificacion_final', 0):.1f}/10" if proyecto_encontrado.get('calificacion_final', 0) > 0 else "**⭐ Calificación:** Sin calificar")
                        st.markdown(f"**📅 Estado:** {proyecto_encontrado.get('estado', 'N/A')}")
                    
                    # Mostrar proyectos similares si existen
                    if proyectos_similares:
                        st.info(f"🔍 **Proyectos similares encontrados:** {len(proyectos_similares)}")
                        for i, proyecto_sim in enumerate(proyectos_similares[:3]):  # Mostrar solo 3
                            st.markdown(f"• **{proyecto_sim['nombre']}** - {proyecto_sim.get('asignatura', 'N/A')}")
                else:
                    st.warning(f"❌ No se encontró ningún proyecto con '{busqueda_rapida}'")
                    st.info("💡 **Sugerencias:**")
                    st.info("• Verifica la ortografía")
                    st.info("• Intenta con palabras clave más cortas")
                    st.info("• Usa la búsqueda avanzada para más opciones")
            else:
                st.warning("⚠️ Por favor ingresa un término de búsqueda")
    
    with col_sugerencias:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💡 Sugerencias", key="btn_sugerencias", use_container_width=True):
            # Generar sugerencias basadas en nombres de proyectos
            nombres_proyectos = [p.get('nombre', '') for p in datos['proyectos']]
            palabras_clave = []
            for nombre in nombres_proyectos:
                palabras = nombre.split()
                palabras_clave.extend([p.lower() for p in palabras if len(p) > 3])
            
            # Contar frecuencia y mostrar más comunes
            from collections import Counter
            palabras_frecuentes = Counter(palabras_clave).most_common(5)
            
            st.info("🔍 **Palabras clave populares:**")
            for palabra, frecuencia in palabras_frecuentes:
                st.markdown(f"• **{palabra}** ({frecuencia} veces)")
    
    # Mostrar historial de búsquedas recientes
    if st.session_state.historial_busquedas:
        with st.expander("📚 **Búsquedas Recientes**"):
            for i, busqueda in enumerate(st.session_state.historial_busquedas[:5]):
                col_hist, col_btn = st.columns([3, 1])
                with col_hist:
                    st.markdown(f"🔍 **{busqueda}**")
                with col_btn:
                    if st.button(f"🔍", key=f"repetir_busqueda_{i}", help=f"Repetir búsqueda: {busqueda}"):
                        # No modificar session_state directamente, usar rerun
                        st.rerun()
    
    st.markdown("---")
    
    # Tabla de proyectos
    if datos['proyectos']:
        st.markdown("### 📋 Proyectos Registrados")
        
        # Buscador avanzado de proyectos
        st.markdown("#### 🔍 **Búsqueda Avanzada**")
        
        # Filtros de búsqueda
        col_filtros1, col_filtros2, col_filtros3 = st.columns(3)
        
        with col_filtros1:
            # Búsqueda por texto
            busqueda_texto = st.text_input(
                "🔍 Buscar por nombre o descripción", 
                placeholder="Ingresa texto a buscar...",
                key="busqueda_texto"
            )
            
            # Filtro por asignatura
            asignaturas_unicas = sorted(list(set([p.get('asignatura', '') for p in datos['proyectos']])))
            filtro_asignatura = st.selectbox(
                "📚 Filtrar por asignatura",
                ["Todas las asignaturas"] + asignaturas_unicas,
                key="filtro_asignatura"
            )
        
        with col_filtros2:
            # Filtro por carrera
            carreras_unicas = sorted(list(set([p.get('carrera', '') for p in datos['proyectos']])))
            filtro_carrera = st.selectbox(
                "🎓 Filtrar por carrera",
                ["Todas las carreras"] + carreras_unicas,
                key="filtro_carrera"
            )
            
            # Filtro por estado de calificación
            filtro_calificacion = st.selectbox(
                "⭐ Filtrar por calificación",
                ["Todos los proyectos", "Sin calificar", "Calificados"],
                key="filtro_calificacion"
            )
        
        with col_filtros3:
            # Filtro por estado de horario
            filtro_horario = st.selectbox(
                "⏰ Filtrar por horario",
                ["Todos los horarios", "En horario", "Fuera de horario"],
                key="filtro_horario"
            )
            
            # Filtros automáticos inteligentes
            filtro_inteligente = st.selectbox(
                "🧠 Filtros Inteligentes",
                ["Sin filtros automáticos", "Proyectos prioritarios", "Proyectos atrasados", "Mejores calificados"],
                key="filtro_inteligente"
            )
            
            # Botón para limpiar filtros
            if st.button("🗑️ Limpiar Filtros", key="limpiar_filtros", use_container_width=True):
                st.rerun()
        
        # Aplicar filtros
        proyectos_filtrados = datos['proyectos']
        
        # Filtro por texto
        if busqueda_texto and busqueda_texto.strip():
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if (busqueda_texto.lower() in p.get('nombre', '').lower() or
                    busqueda_texto.lower() in p.get('asignatura', '').lower() or
                    busqueda_texto.lower() in p.get('carrera', '').lower())
            ]
        
        # Filtro por asignatura
        if filtro_asignatura != "Todas las asignaturas":
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if p.get('asignatura', '') == filtro_asignatura
            ]
        
        # Filtro por carrera
        if filtro_carrera != "Todas las carreras":
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if p.get('carrera', '') == filtro_carrera
            ]
        
        # Filtro por calificación
        if filtro_calificacion == "Sin calificar":
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if p.get('calificacion_final', 0) == 0
            ]
        elif filtro_calificacion == "Calificados":
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if p.get('calificacion_final', 0) > 0
            ]
        
        # Filtro por horario
        if filtro_horario == "En horario":
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if esta_en_horario_presentacion(p.get('horas_presentacion', ''))
            ]
        elif filtro_horario == "Fuera de horario":
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if not esta_en_horario_presentacion(p.get('horas_presentacion', ''))
            ]
        
        # Filtros inteligentes automáticos
        if filtro_inteligente == "Proyectos prioritarios":
            # Proyectos sin calificar que están en horario
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if p.get('calificacion_final', 0) == 0 and esta_en_horario_presentacion(p.get('horas_presentacion', ''))
            ]
        elif filtro_inteligente == "Proyectos atrasados":
            # Proyectos sin calificar que están fuera de horario
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if p.get('calificacion_final', 0) == 0 and not esta_en_horario_presentacion(p.get('horas_presentacion', ''))
            ]
        elif filtro_inteligente == "Mejores calificados":
            # Proyectos con calificación >= 8.0
            proyectos_filtrados = [
                p for p in proyectos_filtrados 
                if p.get('calificacion_final', 0) >= 8.0
            ]
        
        # Mostrar resumen de filtros aplicados
        filtros_activos = []
        if busqueda_texto and busqueda_texto.strip():
            filtros_activos.append(f"Texto: '{busqueda_texto}'")
        if filtro_asignatura != "Todas las asignaturas":
            filtros_activos.append(f"Asignatura: {filtro_asignatura}")
        if filtro_carrera != "Todas las carreras":
            filtros_activos.append(f"Carrera: {filtro_carrera}")
        if filtro_calificacion != "Todos los proyectos":
            filtros_activos.append(f"Calificación: {filtro_calificacion}")
        if filtro_horario != "Todos los horarios":
            filtros_activos.append(f"Horario: {filtro_horario}")
        if filtro_inteligente != "Sin filtros automáticos":
            filtros_activos.append(f"Inteligente: {filtro_inteligente}")
        
        if filtros_activos:
            st.success(f"🔍 **Filtros activos:** {', '.join(filtros_activos)}")
            st.info(f"📊 Mostrando **{len(proyectos_filtrados)}** de **{len(datos['proyectos'])}** proyectos")
            
            # Análisis inteligente de filtros
            with st.expander("🧠 **Análisis Inteligente de Filtros**"):
                col_analisis1, col_analisis2 = st.columns(2)
                
                with col_analisis1:
                    # Distribución por asignatura
                    if filtro_asignatura == "Todas las asignaturas":
                        asignaturas_filtradas = [p.get('asignatura', '') for p in proyectos_filtrados]
                        asignaturas_count = pd.Series(asignaturas_filtradas).value_counts()
                        if len(asignaturas_count) > 0:
                            st.markdown("**📚 Distribución por Asignatura:**")
                            for asignatura, count in asignaturas_count.head(5).items():
                                st.markdown(f"• {asignatura}: {count} proyectos")
                
                with col_analisis2:
                    # Distribución por carrera
                    if filtro_carrera == "Todas las carreras":
                        carreras_filtradas = [p.get('carrera', '') for p in proyectos_filtrados]
                        carreras_count = pd.Series(carreras_filtradas).value_counts()
                        if len(carreras_count) > 0:
                            st.markdown("**🎓 Distribución por Carrera:**")
                            for carrera, count in carreras_count.head(5).items():
                                st.markdown(f"• {carrera}: {count} proyectos")
                
                # Análisis de calificaciones
                calificaciones_filtradas = [p.get('calificacion_final', 0) for p in proyectos_filtrados if p.get('calificacion_final', 0) > 0]
                if calificaciones_filtradas:
                    st.markdown("**⭐ Análisis de Calificaciones:**")
                    try:
                        promedio = sum(calificaciones_filtradas) / len(calificaciones_filtradas)
                        st.markdown(f"• **Promedio:** {promedio:.2f}/10")
                    except:
                        st.markdown("• **Promedio:** N/A")
                    
                    try:
                        st.markdown(f"• **Máxima:** {max(calificaciones_filtradas):.1f}/10")
                        st.markdown(f"• **Mínima:** {min(calificaciones_filtradas):.1f}/10")
                    except:
                        st.markdown("• **Máxima:** N/A")
                        st.markdown("• **Mínima:** N/A")
                    
                    st.markdown(f"• **Total calificados:** {len(calificaciones_filtradas)}")
        else:
            st.info(f"📊 Mostrando todos los **{len(proyectos_filtrados)}** proyectos")
        
        if proyectos_filtrados:
            # Crear DataFrame
            proyectos_df = pd.DataFrame(proyectos_filtrados)
            proyectos_df['Estado Horario'] = proyectos_df['horas_presentacion'].apply(
                lambda x: '🟢 En Horario' if esta_en_horario_presentacion(x) else '🔴 Fuera de Horario'
            )
            
            # Agregar columna de calificación formateada
            proyectos_df['Calificación'] = proyectos_df['calificacion_final'].apply(
                lambda x: f"{x:.1f}/10" if x > 0 else "Sin calificar"
            )
            
            # Opciones de ordenamiento
            st.markdown("#### 📊 **Opciones de Visualización**")
            col_orden, col_export = st.columns([2, 1])
            
            with col_orden:
                ordenar_por = st.selectbox(
                    "🔄 Ordenar por:",
                    ["Nombre", "Asignatura", "Carrera", "Calificación", "Estado Horario"],
                    key="ordenar_por"
                )
                
                # Mapear nombres de columnas
                mapeo_orden = {
                    "Nombre": "nombre",
                    "Asignatura": "asignatura", 
                    "Carrera": "carrera",
                    "Calificación": "calificacion_final",
                    "Estado Horario": "Estado Horario"
                }
                
                # Aplicar ordenamiento
                if ordenar_por in mapeo_orden:
                    columna_orden = mapeo_orden[ordenar_por]
                    if columna_orden == "Estado Horario":
                        # Ordenar por estado de horario (En Horario primero)
                        try:
                            proyectos_df = proyectos_df.sort_values(
                                by="Estado Horario", 
                                key=lambda x: x.map({'🟢 En Horario': 0, '🔴 Fuera de Horario': 1})
                            )
                        except:
                            # Si falla el ordenamiento, ordenar alfabéticamente
                            proyectos_df = proyectos_df.sort_values("Estado Horario")
                    else:
                        try:
                            proyectos_df = proyectos_df.sort_values(columna_orden)
                        except:
                            # Si falla el ordenamiento, no hacer nada
                            pass
            
            with col_export:
                # Botón de exportación
                if st.button("📥 Exportar CSV", key="exportar_csv", use_container_width=True):
                    csv_data = proyectos_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="💾 Descargar CSV",
                        data=csv_data,
                        file_name=f"proyectos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        key="download_csv"
                    )
            
            # Mostrar columnas relevantes
            columnas_mostrar = ['nombre', 'asignatura', 'carrera', 'horas_presentacion', 'Estado Horario', 'Calificación']
            proyectos_df_display = proyectos_df[columnas_mostrar].copy()
            proyectos_df_display.columns = ['Nombre', 'Asignatura', 'Carrera', 'Horario', 'Estado Horario', 'Calificación']
            
            # Mostrar tabla con paginación
            st.markdown("#### 📋 **Resultados de la Búsqueda**")
            
            # Paginación
            items_por_pagina = st.selectbox("📄 Proyectos por página:", [10, 25, 50, 100], key="items_por_pagina")
            total_paginas = (len(proyectos_df_display) + items_por_pagina - 1) // items_por_pagina
            
            if total_paginas > 1:
                pagina_actual = st.selectbox(f"📖 Página (de {total_paginas}):", 
                                           range(1, total_paginas + 1), 
                                           key="pagina_actual")
                inicio = (pagina_actual - 1) * items_por_pagina
                fin = inicio + items_por_pagina
                proyectos_pagina = proyectos_df_display.iloc[inicio:fin]
                
                st.info(f"📄 Mostrando proyectos {inicio + 1} a {min(fin, len(proyectos_df_display))} de {len(proyectos_df_display)}")
            else:
                proyectos_pagina = proyectos_df_display
            
            # Mostrar tabla
            st.dataframe(proyectos_pagina, use_container_width=True)
            
            # Estadísticas de la búsqueda
            if filtros_activos:
                st.markdown("#### 📈 **Estadísticas de la Búsqueda**")
                col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                
                with col_stats1:
                    st.metric("🔍 Proyectos Encontrados", len(proyectos_filtrados))
                with col_stats2:
                    calificados = len([p for p in proyectos_filtrados if p.get('calificacion_final', 0) > 0])
                    st.metric("⭐ Proyectos Calificados", calificados)
                with col_stats3:
                    en_horario = len([p for p in proyectos_filtrados if esta_en_horario_presentacion(p.get('horas_presentacion', ''))])
                    st.metric("⏰ En Horario", en_horario)
                with col_stats4:
                    if len(proyectos_filtrados) > 0:
                        try:
                            promedio_cal = sum([p.get('calificacion_final', 0) for p in proyectos_filtrados]) / len(proyectos_filtrados)
                            st.metric("📊 Promedio Calificación", f"{promedio_cal:.1f}/10")
                        except:
                            st.metric("📊 Promedio Calificación", "N/A")
                    else:
                        st.metric("📊 Promedio Calificación", "N/A")
        else:
            if filtros_activos:
                st.warning(f"❌ No se encontraron proyectos con los filtros aplicados")
                st.info("💡 **Sugerencias:**")
                st.info("• Intenta relajar algunos filtros")
                st.info("• Verifica la ortografía en la búsqueda de texto")
                st.info("• Usa el botón 'Limpiar Filtros' para empezar de nuevo")
            else:
                st.info("No hay proyectos registrados aún")
    else:
        st.info("No hay proyectos registrados aún")
        
def mostrar_registro_proyecto(datos):
    """Muestra el formulario de registro de proyectos"""
    st.markdown('<h1 class="main-header">📝 Registrar Nuevo Proyecto</h1>', unsafe_allow_html=True)
    
    with st.form("registro_proyecto"):
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader("📋 Información del Proyecto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del Proyecto", placeholder="Mi Proyecto Innovador")
            asignatura = st.text_input("Asignatura", placeholder="Programación Avanzada")
            carrera = st.text_input("Carrera", placeholder="Ingeniería en Sistemas")
        
        with col2:
            semestre = st.text_input("Semestre/Ciclo", placeholder="8vo Semestre")
            docente = st.text_input("Docente", placeholder="Dr. Juan Pérez")
            horas_presentacion = st.text_input("Horario de Presentación", placeholder="14:00 - 15:00")
        
        # Estudiantes
        st.markdown("### 👥 Estudiantes del Proyecto")
        num_estudiantes = st.number_input("Número de Estudiantes", min_value=1, max_value=5, value=1)
        
        estudiantes = []
        for i in range(num_estudiantes):
            estudiante = st.text_input(f"Estudiante {i+1}", placeholder=f"Nombre del estudiante {i+1}")
            if estudiante:
                estudiantes.append(estudiante)
        
        # Descripción
        descripcion = st.text_area("Descripción del Proyecto", placeholder="Describe brevemente tu proyecto...")
        
        if st.form_submit_button("💾 Registrar Proyecto", use_container_width=True):
            if nombre and asignatura and carrera and estudiantes:
                nuevo_proyecto = {
                    "id": generar_id("proj"),
                    "nombre": nombre,
                    "asignatura": asignatura,
                    "carrera": carrera,
                    "semestre": semestre,
                    "docente": docente,
                    "horas_presentacion": horas_presentacion,
                    "estudiantes": estudiantes,
                    "descripcion": descripcion,
                    "fecha_registro": datetime.now().strftime("%Y-%m-%d"),
                    "calificaciones": [],
                    "calificacion_final": 0
                }
                
                datos["proyectos"].append(nuevo_proyecto)
                guardar_datos(datos)
                
                st.success("✅ Proyecto registrado exitosamente!")
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
def mostrar_calificacion_proyecto(datos):
    """Muestra la sección de calificación de proyectos"""
    # colocamos un boton que lleve al dashboard
    if st.button("🔙 Volver al Dashboard", use_container_width=True):
        mostrar_dashboard(datos)
        st.stop()





    st.markdown('<h1 class="main-header"> Area de Calificación de Proyectos</h1>', unsafe_allow_html=True)
    
    # Mensaje informativo según el rol
    if 'usuario_actual' in st.session_state:
        usuario = st.session_state.usuario_actual
        if usuario['rol'] == 'docente':
            st.info(" **Panel de Calificación para Docentes** - Aquí puedes evaluar los proyectos de tus estudiantes según los criterios establecidos.")
        else:
            st.success(" **Panel de Calificación para Administradores** - Puedes calificar cualquier proyecto del sistema.")
    
    # Verificar si hay un proyecto seleccionado
    if 'proyecto_seleccionado' in st.session_state:
        # Buscar el proyecto seleccionado
        proyecto_seleccionado = next(
            (p for p in datos['proyectos'] if p['id'] == st.session_state.proyecto_seleccionado), 
            None
        )
        
        if proyecto_seleccionado:
            # Header del proyecto seleccionado
            st.markdown('<div style="background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 1rem; border-radius: 1rem; text-align: center; border: 2px solid #3498db; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">', unsafe_allow_html=True)
            st.markdown(f"### 🎯 Calificando Proyecto")
            st.markdown(f"**Proyecto:** {proyecto_seleccionado['nombre']}")
            st.markdown(f"**Asignatura:** {proyecto_seleccionado['asignatura']}")
            st.markdown(f"**Carrera:** {proyecto_seleccionado['carrera']}")
            st.markdown(f"**Estudiantes:** {', '.join(proyecto_seleccionado['estudiantes'])}")
            st.markdown(f"**Horario:** {proyecto_seleccionado.get('horas_presentacion', 'Sin horario asignado')}")
            st.markdown(f"**Estado:** {'🟢 En Horario de Presentación' if esta_en_horario_presentacion(proyecto_seleccionado.get('horas_presentacion', '00:00 - 00:00')) else '🔴 Fuera de Horario'}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Botón para volver a la tabla
            col_volver1, col_volver2, col_volver3 = st.columns([1, 2, 1])
            with col_volver2:
                if st.button("⬅️ Volver a la Tabla", use_container_width=True):
                    del st.session_state.proyecto_seleccionado
                    st.rerun()
            
            st.markdown("---")
            
            # Criterios de calificación (fuera del formulario para actualización en tiempo real)
            st.markdown('<div >', unsafe_allow_html=True)

            
            st.markdown("---")
            st.markdown("### Calificaciones por Criterio")
            
            # Criterios según la rúbrica
            criterios = {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### INNOVACIÓN (30%)")
                criterios['innovacion'] = st.slider(
                    "Calificación Innovación", 
                    min_value=0, 
                    max_value=10, 
                    value=0,
                    key="innovacion"
                )
                
                st.markdown("#### VIABILIDAD (25%)")
                criterios['viabilidad'] = st.slider(
                    "Calificación Viabilidad", 
                    min_value=0, 
                    max_value=10, 
                    value=0,
                    key="viabilidad"
                )
                
                st.markdown("#### IMPACTO (20%)")
                criterios['impacto'] = st.slider(
                    "Calificación Impacto", 
                    min_value=0, 
                    max_value=10, 
                    value=0,
                    key="impacto"
                )
            
            with col2:
                st.markdown("#### EJECUCIÓN (15%)")
                criterios['ejecucion'] = st.slider(
                    "Calificación Ejecución", 
                    min_value=0, 
                    max_value=10, 
                    value=0,
                    key="ejecucion"
                )
                
                st.markdown("#### PITCH (10%)")
                criterios['pitch'] = st.slider(
                    "Calificación Pitch", 
                    min_value=0, 
                    max_value=10, 
                    value=0,
                    key="pitch"
                )
            
            # Mostrar calificación ponderada en tiempo real
            calificacion_ponderada = calcular_calificacion_ponderada(
                criterios, 
                datos['configuracion']['pesos_criterios']
            )
            
            st.markdown("---")
            st.markdown(f"### Calificación Ponderada: **{calificacion_ponderada}/10**")
            
            # Mostrar desglose del cálculo
            
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Formulario de calificación (solo comentarios y envío)
            with st.form("calificacion_proyecto"):
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                st.markdown("### Comentarios y Envío")
                
                # Comentarios
                comentarios = st.text_area("Comentarios adicionales", placeholder="Escriba sus comentarios sobre el proyecto...")
                
                # Botón de envío
                col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
                with col_submit2:
                    if st.form_submit_button("Enviar Calificación", use_container_width=True):
                        nueva_calificacion = {
                            "id": generar_id("cal"),
                            "proyecto_id": proyecto_seleccionado['id'],
                            "docente_id": st.session_state.usuario_actual['id'],
                            "fecha_calificacion": datetime.now().strftime("%Y-%m-%d"),
                            "criterios": criterios,
                            "calificacion_ponderada": calificacion_ponderada,
                            "comentarios": comentarios
                        }
                        
                        datos["calificaciones"].append(nueva_calificacion)
                        
                        # Actualizar proyecto
                        proyecto_seleccionado["calificaciones"].append(nueva_calificacion["id"])
                        
                        # Actualizar ranking
                        datos = actualizar_ranking(datos)
                        
                        guardar_datos(datos)
                        
                        st.success("Calificación enviada exitosamente!")
                        # Limpiar selección y volver a la tabla
                        del st.session_state.proyecto_seleccionado
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.error("Proyecto no encontrado")
            del st.session_state.proyecto_seleccionado
            st.rerun()
    
    else:
        # Mostrar tabla de proyectos
        st.markdown("### Tabla de Proyectos para Calificar")
        
        # Buscador de proyectos para calificar
        col_search_cal, col_clear_cal = st.columns([3, 1])
        with col_search_cal:
            busqueda_calificar = st.text_input(
                "🔍 Buscar proyecto por nombre", 
                placeholder="Ingresa el nombre del proyecto...",
                key="busqueda_calificar"
            )
        with col_clear_cal:
            st.markdown("<br>", unsafe_allow_html=True)  # Espaciado vertical
            if st.button("🗑️ Limpiar", key="clear_calificar"):
                # No modificar session_state directamente, usar rerun
                st.rerun()
        
        # Filtrar proyectos según búsqueda
        proyectos_para_filtrar = datos['proyectos']
        if busqueda_calificar and busqueda_calificar.strip():
            proyectos_para_filtrar = [
                p for p in datos['proyectos'] 
                if busqueda_calificar.lower() in p['nombre'].lower()
            ]
        
        # Crear DataFrame para la tabla
        proyectos_tabla = []
        for proyecto in proyectos_para_filtrar:
            # Verificar si ya fue calificado por este usuario
            ya_calificado = any(
                cal['docente_id'] == st.session_state.usuario_actual['id'] and 
                cal['proyecto_id'] == proyecto['id']
                for cal in datos['calificaciones']
            )
            
            proyectos_tabla.append({
                'Hora de Exposición': proyecto.get('horas_presentacion', 'Sin horario asignado'),
                'Nombre del Proyecto': proyecto['nombre'],
                'Asignatura': proyecto['asignatura'],
                'Carrera': proyecto['carrera'],
                'Estado': 'Ya Calificado' if ya_calificado else 'Pendiente',
                'Acción': '' if ya_calificado else 'Calificar'
            })
        
        # Mostrar resultados de búsqueda
        if busqueda_calificar and busqueda_calificar.strip():
            st.info(f"🔍 Mostrando {len(proyectos_tabla)} proyecto(s) que contiene(n) '{busqueda_calificar}'")
        
        # Ordenar por hora de exposición
        def ordenar_por_hora(proyecto):
            try:
                hora = proyecto['Hora de Exposición']
                if ' - ' in hora and hora != 'Sin horario asignado':
                    return datetime.strptime(hora.split(' - ')[0], '%H:%M')
                else:
                    return datetime.max
            except:
                return datetime.max
        
        proyectos_tabla.sort(key=ordenar_por_hora)
        
        # Mostrar tabla
        if proyectos_tabla:
            # Crear columnas para la tabla
            col_hora, col_nombre, col_asignatura, col_carrera, col_estado, col_accion = st.columns([1, 2, 1, 1, 1, 1])
            
            # Header de la tabla
            with col_hora:
                st.markdown("**Hora de Exposición**")
            with col_nombre:
                st.markdown("**Nombre del Proyecto**")
            with col_asignatura:
                st.markdown("**Asignatura**")
            with col_carrera:
                st.markdown("**Carrera**")
            with col_estado:
                st.markdown("**Estado**")
            with col_accion:
                st.markdown("**Acción**")
            
            st.markdown("---")
            
            # Filas de la tabla
            for i, proyecto in enumerate(proyectos_tabla):
                col_hora, col_nombre, col_asignatura, col_carrera, col_estado, col_accion = st.columns([1, 2, 1, 1, 1, 1])
                
                with col_hora:
                    st.write(proyecto['Hora de Exposición'])
                with col_nombre:
                    st.write(proyecto['Nombre del Proyecto'])
                with col_asignatura:
                    st.write(proyecto['Asignatura'])
                with col_carrera:
                    st.write(proyecto['Carrera'])
                with col_estado:
                    if proyecto['Estado'] == 'Ya Calificado':
                        st.success(proyecto['Estado'])
                    else:
                        st.info(proyecto['Estado'])
                with col_accion:
                    if proyecto['Acción'] == 'Calificar':
                        # Buscar el proyecto original para obtener el ID
                        proyecto_original = next((p for p in datos['proyectos'] if p['nombre'] == proyecto['Nombre del Proyecto']), None)
                        if proyecto_original and 'id' in proyecto_original:
                            if st.button("⭐ Calificar", key=f"calificar_{proyecto_original['id']}_{i}", use_container_width=True):
                                st.session_state.proyecto_seleccionado = proyecto_original['id']
                                st.rerun()
                        else:
                            st.warning("⚠️ ID del proyecto no encontrado")
                    else:
                        st.write("")
                
                # Separador entre filas
                if i < len(proyectos_tabla) - 1:
                    st.markdown("---")
            
            # Estadísticas
            st.markdown("---")
            proyectos_calificados = len([p for p in proyectos_tabla if p['Estado'] == 'Ya Calificado'])
            proyectos_pendientes = len([p for p in proyectos_tabla if p['Estado'] == 'Pendiente'])
            
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("Total Proyectos", len(proyectos_tabla))
            with col_stats2:
                st.metric("Ya Calificados", proyectos_calificados)
            with col_stats3:
                st.metric("Pendientes", proyectos_pendientes)
            
            if proyectos_pendientes == 0:
                st.success("¡Has calificado todos los proyectos!")
        else:
            if busqueda_calificar and busqueda_calificar.strip():
                st.warning(f"❌ No se encontraron proyectos que contengan '{busqueda_calificar}'")
            else:
                st.info("No hay proyectos registrados para mostrar")

def mostrar_ranking(datos):
    """Muestra el ranking de proyectos"""
    st.markdown('<h1 class="main-header">Ranking de Proyectos</h1>', unsafe_allow_html=True)
    
    # Actualizar ranking
    datos = actualizar_ranking(datos)
    guardar_datos(datos)
    
    if datos['ranking']['proyectos_ganadores']:
        st.markdown("### Podium de Ganadores")
        
        # Top 3 con medallas
        for i, ganador in enumerate(datos['ranking']['proyectos_ganadores']):
            if i == 0:  # Oro
                st.markdown(f"""
                <div class="ranking-card gold-medal">
                    <h2>{ganador['premio']}</h2>
                    <h3>{ganador['nombre_proyecto']}</h3>
                    <h1>Calificación: {ganador['calificacion_final']}/10</h1>
                </div>
                """, unsafe_allow_html=True)
            elif i == 1:  # Plata
                st.markdown(f"""
                <div class="ranking-card silver-medal">
                    <h2>{ganador['premio']}</h2>
                    <h3>{ganador['nombre_proyecto']}</h3>
                    <h1>Calificación: {ganador['calificacion_final']}/10</h1>
                </div>
                """, unsafe_allow_html=True)
            else:  # Bronce
                st.markdown(f"""
                <div class="ranking-card bronze-medal">
                    <h2>{ganador['premio']}</h2>
                    <h3>{ganador['nombre_proyecto']}</h3>
                    <h1>Calificación: {ganador['calificacion_final']}/10</h1>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabla completa de ranking
        st.markdown("### Ranking Completo")
        
        # Buscador para ranking
        col_search_rank, col_clear_rank = st.columns([3, 1])
        with col_search_rank:
            busqueda_ranking = st.text_input(
                "🔍 Buscar proyecto en ranking por nombre", 
                placeholder="Ingresa el nombre del proyecto...",
                key="busqueda_ranking"
            )
        with col_clear_rank:
            st.markdown("<br>", unsafe_allow_html=True)  # Espaciado vertical
            if st.button("🗑️ Limpiar", key="clear_ranking"):
                # No modificar session_state directamente, usar rerun
                st.rerun()
        
        proyectos_ordenados = sorted(
            [p for p in datos['proyectos'] if p['calificacion_final'] > 0],
            key=lambda x: x['calificacion_final'],
            reverse=True
        )
        
        # Filtrar proyectos según búsqueda
        if busqueda_ranking and busqueda_ranking.strip():
            proyectos_ordenados = [
                p for p in proyectos_ordenados 
                if busqueda_ranking.lower() in p['nombre'].lower()
            ]
        
        # Mostrar resultados de búsqueda
        if busqueda_ranking and busqueda_ranking.strip():
            st.info(f"🔍 Mostrando {len(proyectos_ordenados)} proyecto(s) que contiene(n) '{busqueda_ranking}'")
        
        if proyectos_ordenados:
            ranking_df = pd.DataFrame(proyectos_ordenados)
            ranking_df['Posición'] = range(1, len(proyectos_ordenados) + 1)
            ranking_df = ranking_df[['Posición', 'nombre', 'asignatura', 'carrera', 'calificacion_final']]
            ranking_df.columns = ['Posición', 'Proyecto', 'Asignatura', 'Carrera', 'Calificación Final']
            
            st.dataframe(ranking_df, use_container_width=True)
        else:
            if busqueda_ranking and busqueda_ranking.strip():
                st.warning(f"❌ No se encontraron proyectos que contengan '{busqueda_ranking}' en el ranking")
            else:
                st.info("No hay proyectos calificados aún")
    else:
        st.info("No hay proyectos calificados aún para mostrar el ranking")
    
def mostrar_usuarios(datos):
    """Muestra la gestión de usuarios"""
    st.markdown('<h1 class="main-header">Gestión de Usuarios</h1>', unsafe_allow_html=True)
    
    # Botón de descarga de datos (solo para administradores)
    if st.session_state.usuario_actual['rol'] == 'admin':
        col_descarga, col_spacer = st.columns([1, 3])
        with col_descarga:
            if st.button("📥 Descargar Datos Completos", key="descargar_datos_completos", use_container_width=True):
                # Crear archivo JSON para descarga
                json_str = json.dumps(datos, indent=2, ensure_ascii=False)
                st.download_button(
                    label="💾 Descargar data.json",
                    data=json_str.encode('utf-8'),
                    file_name=f"datos_completos_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    key="download_datos_completos"
                )
    
    st.markdown("---")
    
    if st.session_state.usuario_actual['rol'] == 'admin':
        with st.form("registro_usuario"):
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.subheader("Registrar Nuevo Usuario")
            
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Usuario", placeholder="usuario123")
                password = st.text_input("Contraseña", type="password", placeholder="contraseña123")
                nombre = st.text_input("Nombre Completo", placeholder="Juan Pérez")
            
            with col2:
                email = st.text_input("Email", placeholder="juan@universidad.edu")
                rol = st.selectbox("Rol", ["docente", "admin"])
            
            if st.form_submit_button("Registrar Usuario", use_container_width=True):
                if username and password and nombre and email:
                    # Verificar si el usuario ya existe
                    if any(u['username'] == username for u in datos['usuarios']):
                        st.error("El usuario ya existe")
                    else:
                        nuevo_usuario = {
                            "id": generar_id("user"),
                            "username": username,
                            "password": hashlib.sha256(password.encode()).hexdigest(),
                            "nombre": nombre,
                            "email": email,
                            "rol": rol,
                            "fecha_registro": datetime.now().strftime("%Y-%m-%d")
                        }
                        
                        datos["usuarios"].append(nuevo_usuario)
                        guardar_datos(datos)
                        
                        st.success("Usuario registrado exitosamente!")
                        st.rerun()
                else:
                    st.error("Por favor complete todos los campos")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Lista de usuarios
        st.markdown("### Usuarios Registrados")
        usuarios_df = pd.DataFrame(datos['usuarios'])
        usuarios_df = usuarios_df[['username', 'nombre', 'email', 'rol', 'fecha_registro']]
        usuarios_df.columns = ['Usuario', 'Nombre', 'Email', 'Rol', 'Fecha Registro']
        
        st.dataframe(usuarios_df, use_container_width=True)
    else:
        st.warning("⚠️ Solo los administradores pueden gestionar usuarios")
    
def mostrar_reportes(datos):
    """Muestra los reportes y estadísticas"""
    st.markdown('<h1 class="main-header">Reportes y Estadísticas</h1>', unsafe_allow_html=True)
    
    # Estadísticas generales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Estadísticas Generales")
        
        # Proyectos por asignatura
        if datos['proyectos']:
            asignaturas = {}
            for proyecto in datos['proyectos']:
                asignatura = proyecto['asignatura']
                asignaturas[asignatura] = asignaturas.get(asignatura, 0) + 1
            
            st.markdown("**Proyectos por Asignatura:**")
            for asignatura, cantidad in asignaturas.items():
                st.markdown(f"- {asignatura}: {cantidad}")
        
        # Proyectos por carrera
        if datos['proyectos']:
            carreras = {}
            for proyecto in datos['proyectos']:
                carrera = proyecto['carrera']
                carreras[carrera] = carreras.get(carrera, 0) + 1
            
            st.markdown("**Proyectos por Carrera:**")
            for carrera, cantidad in carreras.items():
                st.markdown(f"- {carrera}: {cantidad}")
    
    with col2:
        st.markdown("### Análisis de Calificaciones")
        
        if datos['calificaciones']:
            # Promedio por criterio
            promedios_criterios = {
                'innovacion': [],
                'viabilidad': [],
                'impacto': [],
                'ejecucion': [],
                'pitch': []
            }
            
            for cal in datos['calificaciones']:
                for criterio, valor in cal['criterios'].items():
                    promedios_criterios[criterio].append(valor)
            
            st.markdown("**Promedio por Criterio:**")
            for criterio, valores in promedios_criterios.items():
                if valores:
                    promedio = sum(valores) / len(valores)
                    peso = datos['configuracion']['pesos_criterios'][criterio]
                    st.markdown(f"- {criterio.title()} ({peso}%): {promedio:.2f}/10")
            
            # Calificaciones totales
            calificaciones_totales = [cal['calificacion_ponderada'] for cal in datos['calificaciones']]
            if calificaciones_totales:
                promedio_general = sum(calificaciones_totales) / len(calificaciones_totales)
                st.markdown(f"**Promedio General:** {promedio_general:.2f}/10")
    
    # Gráficos (si hay datos)
    if datos['proyectos'] and datos['calificaciones']:
        st.markdown("### Visualizaciones")
        
        # DataFrame para análisis
        proyectos_df = pd.DataFrame(datos['proyectos'])
        calificaciones_df = pd.DataFrame(datos['calificaciones'])
        
        # Mostrar datos en tablas
        st.markdown("**Proyectos y Calificaciones:**")
        st.dataframe(proyectos_df[['nombre', 'asignatura', 'carrera', 'calificacion_final']], use_container_width=True)
        
        st.markdown("**Detalle de Calificaciones:**")
        st.dataframe(calificaciones_df[['proyecto_id', 'calificacion_ponderada', 'fecha_calificacion']], use_container_width=True)

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
