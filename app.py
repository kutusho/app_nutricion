# app.py
# -------------------------------------------------------------
# App de Seguimiento Nutricional con Acompañamiento Profesional
# Desarrollada para pacientes en régimen con L.N. en Nutrición
# -------------------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta

# -------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA APP
# -------------------------------------------------------------
st.set_page_config(
    page_title="App de Seguimiento Nutricional",
    page_icon="🥦",
    layout="wide",
)

# -------------------------------------------------------------
# ESTILOS PERSONALIZADOS (UX/UI)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Fuente base y colores suaves */
    html, body, [class*="css"]  {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .main-title {
        font-weight: 700;
        font-size: 2.1rem;
        margin-bottom: 0.25rem;
        color: #154c3f;
    }

    .subtitle {
        color: #4c6b5f;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    .card {
        background-color: #f6fff8;
        border-radius: 16px;
        padding: 1rem 1.25rem;
        border: 1px solid #e0f2e9;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 1rem;
    }

    .card-soft {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        border: 1px solid #e4f0ea;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        margin-bottom: 0.75rem;
    }

    .card-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #165c48;
        margin-bottom: 0.35rem;
    }

    .metric-highlight {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f766e;
        margin-bottom: 0.15rem;
    }

    .metric-caption {
        font-size: 0.8rem;
        color: #64748b;
    }

    .tag-pill {
        display: inline-block;
        padding: 0.1rem 0.6rem;
        border-radius: 999px;
        background-color: #dcfce7;
        color: #166534;
        font-size: 0.7rem;
        font-weight: 600;
    }

    .meal-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: #14532d;
        margin-bottom: 0.1rem;
    }

    .meal-text {
        font-size: 0.85rem;
        color: #475569;
        margin-bottom: 0.1rem;
    }

    .contact-card {
        background: linear-gradient(135deg, #e0f7f1, #f5fdf9);
        border-radius: 18px;
        padding: 1.25rem 1.4rem;
        border: 1px solid #bae6fd33;
        box-shadow: 0 8px 18px rgba(15,118,110,0.12);
    }

    .contact-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #115e59;
        margin-bottom: 0.1rem;
    }

    .contact-role {
        font-size: 0.9rem;
        color: #0f766e;
        margin-bottom: 0.4rem;
    }

    .small-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #6b7280;
        margin-bottom: 0.15rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# INICIALIZACIÓN DE ESTADO DE SESIÓN
# -------------------------------------------------------------
def init_session_state():
    """Crea datos por defecto la primera vez que se abre la app."""
    today = date.today()

    # ---- Estado de autenticación ----
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

    # ---- Datos de seguimiento ----
    if "initial_weight" not in st.session_state:
        st.session_state["initial_weight"] = 80.0  # kg (ejemplo)
    if "current_weight" not in st.session_state:
        st.session_state["current_weight"] = 74.0  # kg (ejemplo)
    if "goal_weight" not in st.session_state:
        st.session_state["goal_weight"] = 68.0  # kg (ejemplo)
    if "height_m" not in st.session_state:
        st.session_state["height_m"] = 1.65  # metros (ejemplo)

    if "next_appointment_date" not in st.session_state:
        st.session_state["next_appointment_date"] = today + timedelta(days=7)
    if "next_appointment_time" not in st.session_state:
        now_time = datetime.now().time().replace(second=0, microsecond=0)
        st.session_state["next_appointment_time"] = now_time

    # Historial de peso
    if "weight_df" not in st.session_state:
        days = [today - timedelta(days=i) for i in range(9, -1, -1)]  # últimos 10 días
        start = st.session_state["initial_weight"]
        end = st.session_state["current_weight"]
        steps = len(days) - 1 if len(days) > 1 else 1
        step = (end - start) / steps
        weights = [round(start + step * i, 1) for i in range(len(days))]
        st.session_state["weight_df"] = pd.DataFrame(
            {"date": days, "weight": weights}
        )

    # Registros diarios simulados
    if "daily_logs_df" not in st.session_state:
        registros = []
        for i in range(6, -1, -1):  # últimos 7 días
            d = today - timedelta(days=i)
            # patrón sencillo de cumplimiento
            cumplidas = 5 - (i % 3)
            valores = [True] * cumplidas + [False] * (5 - cumplidas)
            registros.append(
                {
                    "date": d,
                    "desayuno": valores[0],
                    "colacion1": valores[1],
                    "comida": valores[2],
                    "colacion2": valores[3],
                    "cena": valores[4],
                    "mood": "Bien",
                    "comentarios": "Registro simulado.",
                }
            )
        st.session_state["daily_logs_df"] = pd.DataFrame(registros)


def sync_weight_with_today():
    """Sincroniza el peso actual con un registro para el día de hoy en el historial."""
    df = st.session_state["weight_df"].copy()
    today = date.today()
    current_w = st.session_state["current_weight"]

    if today in df["date"].values:
        df.loc[df["date"] == today, "weight"] = current_w
    else:
        df = pd.concat(
            [df, pd.DataFrame({"date": [today], "weight": [current_w]})],
            ignore_index=True,
        )
        df = df.sort_values("date")

    st.session_state["weight_df"] = df


def get_diet_plan_df():
    """Devuelve un DataFrame con un plan de alimentación base (ejemplo)."""
    data = [
        # Lunes
        ("Lunes", "Desayuno", "Avena con leche descremada, 1/2 plátano y 1 cda de nueces."),
        ("Lunes", "Colación 1", "1 manzana + 10 almendras."),
        ("Lunes", "Comida", "Pechuga de pollo a la plancha, ensalada verde y 2 tortillas de maíz."),
        ("Lunes", "Colación 2", "1 yogur natural sin azúcar."),
        ("Lunes", "Cena", "Tostadas de atún con jitomate y pepino."),
        # Martes
        ("Martes", "Desayuno", "2 huevos revueltos con espinacas y 1 tortilla de maíz."),
        ("Martes", "Colación 1", "1 pera + 1 puñado pequeño de cacahuates naturales."),
        ("Martes", "Comida", "Filete de pescado al horno, arroz integral y ensalada mixta."),
        ("Martes", "Colación 2", "Palitos de zanahoria y pepino con hummus."),
        ("Martes", "Cena", "Ensalada de pollo con lechuga, jitomate y aguacate."),
        # Miércoles
        ("Miércoles", "Desayuno", "Smoothie de frutos rojos con yogur natural y avena."),
        ("Miércoles", "Colación 1", "1 naranja + 8 nueces."),
        ("Miércoles", "Comida", "Carne magra guisada con verduras y 2 tortillas."),
        ("Miércoles", "Colación 2", "Queso panela a la plancha con jitomate."),
        ("Miércoles", "Cena", "Sopa de verduras + tostadas horneadas."),
        # Jueves
        ("Jueves", "Desayuno", "Pan integral con aguacate y huevo cocido."),
        ("Jueves", "Colación 1", "Yogur natural con semillas de chía."),
        ("Jueves", "Comida", "Ensalada de atún con garbanzos y verduras."),
        ("Jueves", "Colación 2", "1 manzana o fruta de temporada."),
        ("Jueves", "Cena", "Crema de calabaza (baja en grasa) + pollo deshebrado."),
        # Viernes
        ("Viernes", "Desayuno", "Omelette de claras con champiñones y jitomate."),
        ("Viernes", "Colación 1", "1 plátano pequeño."),
        ("Viernes", "Comida", "Tacos de pescado a la plancha en tortillas de maíz + ensalada."),
        ("Viernes", "Colación 2", "Gelatina light."),
        ("Viernes", "Cena", "Ensalada de nopales con queso fresco."),
        # Sábado
        ("Sábado", "Desayuno", "Chilaquiles horneados con pollo y poca crema."),
        ("Sábado", "Colación 1", "Fruta picada (papaya, piña, melón)."),
        ("Sábado", "Comida", "Pollo asado, arroz integral y ensalada de col."),
        ("Sábado", "Colación 2", "Yogur griego natural."),
        ("Sábado", "Cena", "Tostadas de tinga de pollo (al horno)."),
        # Domingo
        ("Domingo", "Desayuno", "Hot cakes integrales con miel natural ligera."),
        ("Domingo", "Colación 1", "Uvas o frutos rojos."),
        ("Domingo", "Comida", "Carne asada magra, guacamole y nopales."),
        ("Domingo", "Colación 2", "Palomitas naturales (sin mantequilla)."),
        ("Domingo", "Cena", "Sándwich integral de pavo con vegetales."),
    ]

    df = pd.DataFrame(data, columns=["Día", "Tiempo de comida", "Descripción"])
    return df


def calculate_streak(df):
    """Calcula días consecutivos cumpliendo todos los tiempos de comida."""
    if df.empty:
        return 0

    df_sorted = df.sort_values("date")
    # Se cumple el día si todos los tiempos son True
    meal_cols = ["desayuno", "colacion1", "comida", "colacion2", "cena"]
    df_sorted["cumplido_dia"] = df_sorted[meal_cols].all(axis=1)

    cumplidos = df_sorted[df_sorted["cumplido_dia"]]
    if cumplidos.empty:
        return 0

    fechas = sorted(cumplidos["date"].unique(), reverse=True)
    streak = 0
    esperada = fechas[0]

    for f in fechas:
        if f == esperada:
            streak += 1
            esperada = esperada - timedelta(days=1)
        else:
            break

    return streak


def show_top_summary():
    """Resumen siempre visible: pesos y próxima cita."""
    iw = st.session_state["initial_weight"]
    cw = st.session_state["current_weight"]
    gw = st.session_state["goal_weight"]
    ap_date = st.session_state["next_appointment_date"]
    ap_time = st.session_state["next_appointment_time"]
    ap_dt = datetime.combine(ap_date, ap_time)
    ap_str = ap_dt.strftime("%d/%m/%Y %H:%M")

    st.markdown(
        f"""
        <div class="card" style="background-color:#e8f8f2; margin-bottom:1.4rem;">
            <div class="card-title">Resumen de tu proceso</div>
            <p style="margin-bottom:0.25rem;">
                <strong>Peso inicial:</strong> {iw:.1f} kg · 
                <strong>Peso actual:</strong> {cw:.1f} kg · 
                <strong>Peso objetivo:</strong> {gw:.1f} kg
            </p>
            <p style="margin-bottom:0;">
                💬 Próxima cita: <strong>{ap_str}</strong> con la L.N. Brenda López Hernández.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------
# SECCIÓN LOGIN
# -------------------------------------------------------------
def show_login():
    """
    Sección de iniciar sesión.
    Por ahora usa credenciales de ejemplo:
    usuario: 'paciente', contraseña: 'nutri123'
    """
    st.markdown('<div class="main-title">🔐 Iniciar sesión</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Accede a tu panel de seguimiento nutricional con tu usuario asignado.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Entrar")

        if submit:
            # Credenciales de ejemplo. Aquí luego se puede conectar a DB, Google Sheets, etc.
            if username == "paciente" and password == "nutri123":
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Bienvenido a tu App de Seguimiento Nutricional 🥦")
            else:
                st.error("Usuario o contraseña incorrectos. Intenta de nuevo.")

    with col2:
        st.markdown(
            """
            <div class="card-soft">
                <div class="card-title">¿Qué es esta app?</div>
                <p style="font-size:0.88rem; color:#374151;">
                    Esta plataforma te permite ver tu peso inicial, peso actual, 
                    tu peso objetivo y la fecha de tu próxima cita, además de 
                    registrar si estás cumpliendo con tu plan de alimentación.
                </p>
                <p style="font-size:0.85rem; color:#4b5563;">
                    Las credenciales de acceso son asignadas por tu nutrióloga. 
                    Si tienes dudas, contáctala directamente.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.get("logged_in", False)

# -------------------------------------------------------------
# SECCIÓN 1: SEGUIMIENTO PROFESIONAL (DASHBOARD)
# -------------------------------------------------------------
def show_dashboard():
    st.markdown('<div class="main-title">🥦 Seguimiento profesional</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Visualiza tu avance general con el acompañamiento de la L.N. Brenda López Hernández.</div>',
        unsafe_allow_html=True,
    )

    show_top_summary()

    weight_df = st.session_state["weight_df"].copy()
    daily_df = st.session_state["daily_logs_df"].copy()

    iw = st.session_state["initial_weight"]
    cw = st.session_state["current_weight"]
    gw = st.session_state["goal_weight"]
    h = st.session_state["height_m"]

    # Cálculos clave
    bmi = cw / (h ** 2) if h > 0 else None
    # Progreso hacia la meta (pérdida de peso)
    progress_pct = 0.0
    if iw != gw:
        if iw > gw:  # meta bajar de peso
            progress_pct = (iw - cw) / (iw - gw)
        else:        # meta subir de peso
            progress_pct = (cw - iw) / (gw - iw)
        progress_pct = max(0.0, min(progress_pct, 1.0))

    streak = calculate_streak(daily_df)

    # Métricas principales en tarjetas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="card-soft">
                <div class="card-title">Peso actual</div>
                <div class="metric-highlight">{cw:.1f} kg</div>
                <div class="metric-caption">Meta: {gw:.1f} kg</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if bmi:
            st.markdown(
                f"""
                <div class="card-soft">
                    <div class="card-title">IMC estimado</div>
                    <div class="metric-highlight">{bmi:.1f}</div>
                    <div class="metric-caption">Altura: {h:.2f} m</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="card-soft">
                    <div class="card-title">IMC estimado</div>
                    <div class="metric-highlight">-</div>
                    <div class="metric-caption">Agrega tu altura en el panel lateral.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col3:
        st.markdown(
            f"""
            <div class="card-soft">
                <div class="card-title">Progreso hacia la meta</div>
                <div class="metric-highlight">{progress_pct*100:.0f}%</div>
                <div class="metric-caption">Con base en peso inicial y objetivo.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="card-soft">
                <div class="card-title">Días consecutivos cumpliendo</div>
                <div class="metric-highlight">{streak}</div>
                <div class="metric-caption">Todos los tiempos de comida cumplidos.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Gráfica de evolución de peso
    st.subheader("📉 Evolución de tu peso")
    if not weight_df.empty:
        chart_df = weight_df.set_index("date")[["weight"]]
        chart_df.index.name = "Fecha"
        st.line_chart(chart_df)
    else:
        st.info("Aún no hay historial de peso. Agrega tu peso actual en el panel lateral.")

    # Mensaje de la nutrióloga (simulado)
    st.markdown("")
    st.subheader("💚 Mensaje de la nutrióloga")
    mensaje = (
        "¡Vas haciendo un gran trabajo! Recuerda mantener una buena hidratación, "
        "respetar tus horarios de comida y dormir adecuadamente. Si notas cambios "
        "importantes en tu apetito, energía o estado de ánimo, coméntalo en tu próxima cita."
    )
    st.markdown(
        f"""
        <div class="card">
            <div class="small-label">Nota</div>
            <p style="font-size:0.9rem; color:#1f2937; margin-bottom:0;">{mensaje}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------
# SECCIÓN 2: MI PLAN DE ALIMENTACIÓN
# -------------------------------------------------------------
def show_plan():
    st.markdown('<div class="main-title">📋 Mi plan de alimentación</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Consulta de forma clara qué te corresponde en cada tiempo de comida.</div>',
        unsafe_allow_html=True,
    )

    show_top_summary()

    dieta_df = get_diet_plan_df()

    # Filtro por día
    dias = dieta_df["Día"].unique().tolist()
    dia_seleccionado = st.selectbox("Selecciona el día de la semana:", dias, index=0)

    filtro_df = dieta_df[dieta_df["Día"] == dia_seleccionado].copy()

    st.markdown("### 🍽️ Comidas del día seleccionado")

    # Mostrar en formato "cards" por tiempo de comida
    for _, row in filtro_df.iterrows():
        st.markdown(
            f"""
            <div class="card-soft">
                <div class="meal-title">{row['Tiempo de comida']}</div>
                <div class="meal-text">{row['Descripción']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 📊 Vista en tabla (puedes filtrar y ordenar)")
    st.dataframe(
        filtro_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
        > 💡 *Recuerda:* Este plan es un ejemplo. La L.N. puede personalizar tu dieta. 
        > Puedes modificar directamente el código de esta sección para adaptar tu propio plan.
        """
    )

# -------------------------------------------------------------
# SECCIÓN 3: REGISTRO DIARIO
# -------------------------------------------------------------
def show_daily_log():
    st.markdown('<div class="main-title">📝 Registro diario</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Marca si cumpliste tu plan y cómo te sentiste el día de hoy.</div>',
        unsafe_allow_html=True,
    )

    show_top_summary()

    daily_df = st.session_state["daily_logs_df"].copy()

    st.subheader("Registrar mi día de hoy")

    today = date.today()

    with st.form("registro_diario_form"):
        fecha = st.date_input("Fecha", value=today)
        st.markdown("#### Tiempos de comida cumplidos")
        c1, c2, c3 = st.columns(3)
        with c1:
            desayuno = st.checkbox("Desayuno")
            colacion1 = st.checkbox("Colación 1")
        with c2:
            comida = st.checkbox("Comida")
            colacion2 = st.checkbox("Colación 2")
        with c3:
            cena = st.checkbox("Cena")

        st.markdown("#### ¿Cómo me sentí hoy?")
        mood = st.selectbox(
            "Selecciona una opción:",
            ["Muy bien", "Bien", "Regular", "Mal"],
            index=1,
        )

        comentarios = st.text_area(
            "Comentarios (opcional)",
            placeholder="Ejemplo: Me sentí con más energía por la mañana...",
        )

        enviado = st.form_submit_button("Guardar registro")

    if enviado:
        nuevo_registro = {
            "date": fecha,
            "desayuno": desayuno,
            "colacion1": colacion1,
            "comida": comida,
            "colacion2": colacion2,
            "cena": cena,
            "mood": mood,
            "comentarios": comentarios,
        }

        # Si ya existe registro para la fecha, lo reemplazamos
        daily_df = daily_df[daily_df["date"] != fecha]
        daily_df = pd.concat(
            [daily_df, pd.DataFrame([nuevo_registro])],
            ignore_index=True,
        )
        daily_df = daily_df.sort_values("date")

        st.session_state["daily_logs_df"] = daily_df

        st.success("✅ Registro guardado correctamente.")

    st.markdown("---")
    st.subheader("Mis registros recientes")

    if daily_df.empty:
        st.info("Aún no hay registros cargados.")
        return

    filtro = st.radio(
        "¿Qué quieres ver?",
        ("Hoy", "Últimos 7 días"),
        horizontal=True,
    )

    if filtro == "Hoy":
        df_mostrar = daily_df[daily_df["date"] == today]
    else:
        hace_7 = today - timedelta(days=7)
        df_mostrar = daily_df[daily_df["date"] >= hace_7]

    if df_mostrar.empty:
        st.info("No hay registros en el rango seleccionado.")
    else:
        df_print = df_mostrar.copy().sort_values("date", ascending=False)
        df_print["date"] = df_print["date"].astype(str)
        st.dataframe(
            df_print.reset_index(drop=True),
            use_container_width=True,
        )

# -------------------------------------------------------------
# SECCIÓN 4: PROGRESO
# -------------------------------------------------------------
def show_progress():
    st.markdown('<div class="main-title">📈 Progreso</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Revisa tu nivel de adherencia al plan en los últimos días.</div>',
        unsafe_allow_html=True,
    )

    show_top_summary()

    daily_df = st.session_state["daily_logs_df"].copy()

    if daily_df.empty:
        st.info("Aún no hay datos para mostrar el progreso.")
        return

    meal_cols = ["desayuno", "colacion1", "comida", "colacion2", "cena"]

    # Convertir booleanos a enteros para cálculo
    for c in meal_cols:
        daily_df[c] = daily_df[c].astype(int)

    # Adherencia diaria: promedio de tiempos cumplidos
    daily_df["adherencia"] = daily_df[meal_cols].sum(axis=1) / len(meal_cols)

    # Agrupar por fecha
    resumen = (
        daily_df.groupby("date")["adherencia"]
        .mean()
        .reset_index()
        .sort_values("date")
    )

    today = date.today()
    hace_7 = today - timedelta(days=6)
    resumen_7 = resumen[resumen["date"] >= hace_7]

    st.subheader("📊 Adherencia por día")

    if resumen_7.empty:
        st.info("No hay registros suficientes para los últimos 7 días.")
        return

    chart_df = resumen_7.set_index("date")[["adherencia"]]
    chart_df["% adherencia"] = chart_df["adherencia"] * 100

    st.bar_chart(chart_df[["% adherencia"]])

    adherencia_media = chart_df["adherencia"].mean()
    adherencia_pct = adherencia_media * 100

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="card-soft">
                <div class="card-title">% de adherencia (últimos 7 días)</div>
                <div class="metric-highlight">{adherencia_pct:.0f}%</div>
                <div class="metric-caption">Promedio de comidas cumplidas por día.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Mensaje dinámico según nivel de adherencia
    if adherencia_pct >= 80:
        mensaje = "¡Vas excelente! 🥳 Mantén este ritmo, tu constancia está haciendo la diferencia."
    elif adherencia_pct >= 60:
        mensaje = "¡Muy bien! 💪 Estás en buen camino, pequeños ajustes te acercarán aún más a tu meta."
    elif adherencia_pct >= 40:
        mensaje = "Vas avanzando, poco a poco. 🌱 Revisa en qué tiempos de comida te cuesta más cumplir."
    else:
        mensaje = "No te desanimes. 💚 Cada día es una nueva oportunidad para mejorar tu adherencia."

    with col2:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">Mensaje según tu nivel de adherencia</div>
                <p style="font-size:0.9rem; color:#111827; margin-bottom:0;">{mensaje}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------------------------------------
# SECCIÓN 5: CONTACTO CON LA NUTRIÓLOGA
# -------------------------------------------------------------
def show_contact():
    st.markdown('<div class="main-title">📞 Contacto</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Información de contacto de tu nutrióloga y espacio para anotar dudas.</div>',
        unsafe_allow_html=True,
    )

    show_top_summary()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            <div class="contact-card">
                <div class="contact-name">L.N. Brenda López Hernández</div>
                <div class="contact-role">Licenciada en Nutrición · Cédula profesional 11036805</div>
                <p style="font-size:0.9rem; color:#1f2937;">
                    Esta app está diseñada para acompañar tu tratamiento nutricional profesional.
                    Ante cualquier duda importante sobre tu plan, ajustes de porciones o síntomas,
                    es fundamental que te comuniques directamente con tu nutrióloga.
                </p>
                <p style="font-size:0.86rem; color:#4b5563; margin-bottom:0.4rem;">
                    <strong>Sugerencia:</strong> Puedes anotar aquí los puntos que quieras comentar en tu próxima cita.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        notas = st.text_area(
            "Notas para mi próxima consulta",
            placeholder="Ejemplo: Preguntar sobre colaciones para los días con más actividad física...",
        )
        if notas:
            st.info("Tus notas se guardan temporalmente mientras esta sesión esté activa.")

    with col2:
        st.markdown(
            """
            <div class="card-soft">
                <div class="card-title">Recomendaciones generales</div>
                <ul style="padding-left:1.1rem; margin-bottom:0; font-size:0.85rem; color:#374151;">
                    <li>No realices cambios bruscos en tu plan sin consultarlo.</li>
                    <li>Mantén un registro honesto de lo que comes y cómo te sientes.</li>
                    <li>Si presentas malestar importante, suspende el plan y repórtalo.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------------
def main():
    # Inicializar estado
    init_session_state()

    # Si NO está logueado, mostrar únicamente pantalla de login
    if not st.session_state["logged_in"]:
        # Sidebar mínimo cuando no está autenticado
        with st.sidebar:
            st.markdown("### 🥗 App de Seguimiento Nutricional")
            st.markdown(
                """
                <span class="small-label">Acompañamiento profesional</span><br>
                L.N. <strong>Brenda López Hernández</strong><br>
                <span style="font-size:0.8rem;">Cédula profesional 11036805</span>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("---")
            st.info("Por favor inicia sesión para acceder a tu panel.")
        show_login()
        return

    # ---- SIDEBAR COMPLETO CUANDO YA INICIÓ SESIÓN ----
    with st.sidebar:
        st.markdown("### 🥗 App de Seguimiento Nutricional")
        st.markdown(
            """
            <span class="small-label">Acompañamiento profesional</span><br>
            L.N. <strong>Brenda López Hernández</strong><br>
            <span style="font-size:0.8rem;">Cédula profesional 11036805</span>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.get("username"):
            st.markdown(
                f"👤 <span style='font-size:0.9rem;'>Sesión iniciada como <strong>{st.session_state['username']}</strong></span>",
                unsafe_allow_html=True,
            )

        # Botón para cerrar sesión
        if st.button("Cerrar sesión"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.experimental_rerun()

        st.markdown("---")
        st.markdown("#### ⚖️ Mis datos")
        st.session_state["initial_weight"] = st.number_input(
            "Peso inicial (kg)",
            min_value=30.0,
            max_value=300.0,
            value=float(st.session_state["initial_weight"]),
            step=0.1,
        )
        st.session_state["current_weight"] = st.number_input(
            "Peso actual (kg)",
            min_value=30.0,
            max_value=300.0,
            value=float(st.session_state["current_weight"]),
            step=0.1,
        )
        st.session_state["goal_weight"] = st.number_input(
            "Peso objetivo (kg)",
            min_value=30.0,
            max_value=300.0,
            value=float(st.session_state["goal_weight"]),
            step=0.1,
        )
        st.session_state["height_m"] = st.number_input(
            "Altura (m)",
            min_value=1.20,
            max_value=2.10,
            value=float(st.session_state["height_m"]),
            step=0.01,
        )

        st.markdown("---")
        st.markdown("#### 📅 Próxima cita")
        st.session_state["next_appointment_date"] = st.date_input(
            "Fecha de la cita",
            value=st.session_state["next_appointment_date"],
        )
        st.session_state["next_appointment_time"] = st.time_input(
            "Hora de la cita",
            value=st.session_state["next_appointment_time"],
        )

        st.markdown("---")
        st.markdown("#### 🔍 Navegación")
        menu = st.radio(
            "Ir a:",
            (
                "Seguimiento profesional",
                "Mi plan de alimentación",
                "Registro diario",
                "Progreso",
                "Contacto",
            ),
        )

    # Actualizar historial de peso con el valor de hoy
    sync_weight_with_today()

    # Contenido principal por sección
    if menu == "Seguimiento profesional":
        show_dashboard()
    elif menu == "Mi plan de alimentación":
        show_plan()
    elif menu == "Registro diario":
        show_daily_log()
    elif menu == "Progreso":
        show_progress()
    elif menu == "Contacto":
        show_contact()


if __name__ == "__main__":
    main()
