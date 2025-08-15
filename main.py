import streamlit as st
import sys
import os

# Agregar el directorio actual al path para importar las funciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import cargar_datos, autenticar_usuario, obtener_usuario_por_username
from config import PAGE_CONFIG

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Calificación",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ocultar la navegación automática de páginas
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# CSS principal
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 1rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.form-container {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 1rem;
    border: 2px solid #e9ecef;
    margin: 1rem 0;
}

.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 2rem;
    background: white;
    border-radius: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.3s;
    width: 100%;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.sidebar-menu {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.menu-item {
    padding: 0.5rem 1rem;
    margin: 0.25rem 0;
    border-radius: 0.25rem;
    cursor: pointer;
    transition: all 0.3s;
}

.menu-item:hover {
    background: #e9ecef;
}

.menu-item.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.logout-btn {
    background: #dc3545;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    cursor: pointer;
    width: 100%;
    margin-top: 1rem;
}

.logout-btn:hover {
    background: #c82333;
}
</style>
""", unsafe_allow_html=True)

def main():
    """Función principal que controla la navegación según el rol"""
    
    # Verificar autenticación
    if 'usuario_actual' not in st.session_state:
        mostrar_login()
    else:
        usuario = st.session_state.usuario_actual
        
        # Mostrar sidebar con navegación según el rol
        mostrar_sidebar(usuario)
        
        # Mostrar contenido según la página seleccionada
        if 'pagina_actual' not in st.session_state:
            if usuario['rol'] == 'admin':
                st.session_state.pagina_actual = 'admin_dashboard'
            else:
                st.session_state.pagina_actual = 'docente_dashboard'
        
        mostrar_contenido(usuario)

def mostrar_sidebar(usuario):
    """Muestra el sidebar con navegación según el rol"""
    
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-menu">
            <h3>👤 {usuario['nombre']}</h3>
            <p><strong>Rol:</strong> {usuario['rol'].title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menú según el rol
        if usuario['rol'] == 'admin':
            st.markdown("### 🎯 Navegación")
            
            # Opciones para administradores
            opciones_admin = [
                ('admin_dashboard', '🏠 Dashboard Admin', 'Panel principal de administración'),
                ('concurso', '📚 Sistema Original', 'Acceso al sistema original concurso.py')
            ]
            
            for pagina_id, titulo, descripcion in opciones_admin:
                is_active = st.session_state.pagina_actual == pagina_id
                if st.button(
                    titulo, 
                    key=f"menu_{pagina_id}",
                    use_container_width=True,
                    help=descripcion
                ):
                    st.session_state.pagina_actual = pagina_id
                    st.rerun()
        
        elif usuario['rol'] == 'docente':
            st.markdown("### 🎯 Navegación")
            
            # Solo una opción para docentes
            if st.button(
                '👨‍🏫 Dashboard Docente', 
                key="menu_docente_dashboard",
                use_container_width=True,
                help="Panel de calificación para docentes"
            ):
                st.session_state.pagina_actual = 'docente_dashboard'
                st.rerun()
        
        st.markdown("---")
        
        # Botón de logout
        if st.button("🚪 Cerrar Sesión", key="logout", use_container_width=True):
            del st.session_state.usuario_actual
            if 'pagina_actual' in st.session_state:
                del st.session_state.pagina_actual
            st.rerun()

def mostrar_contenido(usuario):
    """Muestra el contenido según la página seleccionada"""
    
    pagina = st.session_state.pagina_actual
    
    if usuario['rol'] == 'admin':
        if pagina == 'admin_dashboard':
            mostrar_dashboard_admin()
        elif pagina == 'concurso':
            mostrar_sistema_original()
        else:
            st.error("❌ Página no válida")
            st.session_state.pagina_actual = 'admin_dashboard'
            st.rerun()
    
    elif usuario['rol'] == 'docente':
        if pagina == 'docente_dashboard':
            mostrar_dashboard_docente()
        else:
            st.error("❌ Página no válida")
            st.session_state.pagina_actual = 'docente_dashboard'
            st.rerun()

def mostrar_dashboard_admin():
    """Muestra el dashboard de administradores"""
    
    # Importar y ejecutar el dashboard de administradores
    from pages.admin_dashboard import main as admin_main
    admin_main()

def mostrar_dashboard_docente():
    """Muestra el dashboard de docentes"""
    
    # Importar y ejecutar el dashboard de docentes
    from pages.docente_dashboard import main as docente_main
    docente_main()

def mostrar_sistema_original():
    """Muestra el sistema original concurso.py"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📚 Sistema Original - Concurso</h1>
        <h3>Acceso al sistema completo de calificación</h3>
        <p>Esta es la versión original del sistema con todas las funcionalidades</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Importar y ejecutar el sistema original
    try:
        from concurso import main as concurso_main
        concurso_main()
    except Exception as e:
        st.error(f"❌ Error al cargar el sistema original: {str(e)}")
        st.info("💡 Asegúrate de que el archivo concurso.py esté disponible")

def mostrar_login():
    """Muestra la página de login"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🏆 Sistema de Calificación</h1>
        <h3>Trabajos de Fin de Asignatura</h3>
        <p>Inicia sesión para acceder al sistema</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Centrar el formulario de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        with st.form("login_principal"):
            st.markdown("### 🔐 Iniciar Sesión")
            
            username = st.text_input("Usuario", placeholder="usuario123")
            password = st.text_input("Contraseña", type="password", placeholder="contraseña123")
            
            if st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True):
                if username and password:
                    # Cargar datos
                    datos = cargar_datos()
                    
                    # Autenticar usuario
                    if autenticar_usuario(username, password, datos):
                        # Obtener información completa del usuario
                        usuario = obtener_usuario_por_username(username, datos)
                        if usuario:
                            st.session_state.usuario_actual = usuario
                            st.success("✅ ¡Bienvenido!")
                            st.rerun()
                        else:
                            st.error("❌ Error al obtener información del usuario")
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

if __name__ == "__main__":
    main()
