"""
page_login.py — Page de connexion et d'inscription pour le CEM Generator.

Affiche une interface professionnelle de connexion/inscription avec un
design premium intégré au thème sombre de l'application.
"""
import streamlit as st
from backend.services.auth_service import authenticate, create_user
from frontend.translations import t


def _inject_login_css():
    """Injecte le CSS premium pour la page de connexion."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* Font Global override within the login context */
    .login-wrapper {
        font-family: 'Outfit', sans-serif !important;
        animation: fadeInBox 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        opacity: 0;
        transform: translateY(20px);
    }

    @keyframes fadeInBox {
        to { opacity: 1; transform: translateY(0); }
    }

    /* Arrière-plan dynamique (si besoin d'être global, on cible div[data-testid="stApp"]) 
       On se contente ici de sublimer le conteneur lui-même. */
       
    .login-container {
        max-width: 420px;
        margin: 4rem auto;
        padding: 3rem 2.5rem;
        background: rgba(15, 15, 25, 0.65);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 40px 100px -20px rgba(0, 0, 0, 0.8),
                    inset 0 1px 1px rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .login-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 45px 120px -20px rgba(0, 0, 0, 0.9),
                    inset 0 1px 1px rgba(255, 255, 255, 0.15),
                    0 0 40px rgba(79, 139, 249, 0.15);
    }

    /* Lueur de fond animée (Glow) */
    .login-container::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at 50% 0%, rgba(79, 139, 249, 0.15), transparent 40%),
                    radial-gradient(circle at 100% 100%, rgba(0, 191, 165, 0.1), transparent 40%);
        pointer-events: none;
        z-index: 0;
        animation: rotateGlow 20s linear infinite;
    }

    @keyframes rotateGlow {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .login-header, .login-form-content {
        position: relative;
        z-index: 1; /* Par-dessus le glow */
    }

    .login-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }

    .login-header .logo-icon {
        font-size: 3.5rem;
        display: inline-block;
        margin-bottom: 1rem;
        filter: drop-shadow(0 4px 12px rgba(79, 139, 249, 0.4));
        animation: floatIcon 3s ease-in-out infinite;
    }

    @keyframes floatIcon {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .login-header h1 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #a5c3ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }

    .login-header p {
        color: #8892b0;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* Streamlit Input Overrides */
    /* On vise les inputs cachés derrière les classes Streamlit */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    div[data-baseweb="input"]:focus-within {
        background-color: rgba(255, 255, 255, 0.06) !important;
        border-color: #4F8BF9 !important;
        box-shadow: 0 0 0 3px rgba(79, 139, 249, 0.2) !important;
    }

    div[data-baseweb="input"] input {
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif !important;
        padding: 0.8rem 1rem !important;
    }

    label[data-testid="stWidgetLabel"] p {
        font-family: 'Outfit', sans-serif !important;
        color: #a0aec0 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        margin-bottom: 0.2rem !important;
    }

    /* Streamlit Primary Button Override */
    button[kind="primary"] {
        background: linear-gradient(135deg, #4F8BF9 0%, #3a70cb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 8px 20px -6px rgba(79, 139, 249, 0.6) !important;
        transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
        text-transform: uppercase !important;
        margin-top: 1rem !important;
    }

    button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 12px 25px -6px rgba(79, 139, 249, 0.8) !important;
        background: linear-gradient(135deg, #5c94fa 0%, #427cde 100%) !important;
    }
    
    button[kind="primary"]:active {
        transform: translateY(1px) scale(0.98) !important;
        box-shadow: 0 4px 10px -2px rgba(79, 139, 249, 0.5) !important;
    }

    /* Streamlit Secondary Button Override (Links) */
    button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #8892b0 !important;
        border-radius: 12px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    .login-divider {
        display: flex;
        align-items: center;
        margin: 2rem 0;
        gap: 15px;
    }

    .login-divider::before,
    .login-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
    }

    .login-divider span {
        color: #64748b;
        font-size: 0.8rem;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .admin-hint {
        background: rgba(79, 139, 249, 0.05);
        border: 1px dashed rgba(79, 139, 249, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .admin-hint:hover {
        background: rgba(79, 139, 249, 0.08);
        border-color: rgba(79, 139, 249, 0.4);
    }

    .admin-hint p {
        color: #8892b0;
        font-size: 0.8rem;
        font-family: 'Outfit', sans-serif;
        margin: 0;
        text-align: center;
    }

    .admin-hint code {
        background: rgba(79, 139, 249, 0.15);
        padding: 3px 8px;
        border-radius: 6px;
        color: #4F8BF9;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(79, 139, 249, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)


def render_page_login():
    """Affiche la page de connexion/inscription."""
    _inject_login_css()
    
    # Initialiser le mode (login/register)
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"
    
    # Container principal
    st.markdown('<div class="login-wrapper"><div class="login-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="login-header">
        <span class="logo-icon">📚</span>
        <h1>{t("app_title")}</h1>
        <p>{t("login_subtitle")}</p>
    </div>
    <div class="login-form-content">
    """, unsafe_allow_html=True)
    
    if st.session_state["auth_mode"] == "login":
        _render_login_form()
    else:
        _render_register_form()
    
    st.markdown('</div></div></div>', unsafe_allow_html=True)


def _render_login_form():
    """Formulaire de connexion."""
    st.markdown(f"""
    <div class="login-divider">
        <span>{t("login_title")}</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            t("login_username"),
            placeholder=t("login_username_ph"),
            key="login_user_input"
        )
        password = st.text_input(
            t("login_password"),
            type="password",
            placeholder="••••••••",
            key="login_pass_input"
        )
        
        submitted = st.form_submit_button(
            t("login_btn"),
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            success, message = authenticate(username, password)
            if success:
                st.rerun()
            else:
                st.error(message)
    
    # Lien vers inscription
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(t("login_no_account"), use_container_width=True):
            st.session_state["auth_mode"] = "register"
            st.rerun()
    
    # Hint admin
    st.markdown(f"""
    <div class="admin-hint">
        <p>🔑 {t("login_admin_hint")}: <code>admin</code> / <code>admin123</code></p>
    </div>
    """, unsafe_allow_html=True)


def _render_register_form():
    """Formulaire d'inscription."""
    st.markdown(f"""
    <div class="login-divider">
        <span>{t("register_title")}</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("register_form", clear_on_submit=False):
        full_name = st.text_input(
            t("register_fullname"),
            placeholder=t("register_fullname_ph"),
            key="reg_name_input"
        )
        username = st.text_input(
            t("login_username"),
            placeholder=t("register_username_ph"),
            key="reg_user_input"
        )
        password = st.text_input(
            t("login_password"),
            type="password",
            placeholder="••••••••",
            key="reg_pass_input"
        )
        password_confirm = st.text_input(
            t("register_confirm_password"),
            type="password",
            placeholder="••••••••",
            key="reg_pass_confirm_input"
        )
        
        submitted = st.form_submit_button(
            t("register_btn"),
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if password != password_confirm:
                st.error(t("register_password_mismatch"))
            else:
                success, message = create_user(username, password, full_name)
                if success:
                    st.success(message)
                    st.info(t("register_success_hint"))
                else:
                    st.error(message)
    
    # Lien vers connexion
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(t("register_has_account"), use_container_width=True):
            st.session_state["auth_mode"] = "login"
            st.rerun()
