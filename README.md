# 🥦 App de Seguimiento Nutricional con Acompañamiento Profesional

Aplicación web desarrollada en **Streamlit** para que pacientes en tratamiento con una **Licenciada en Nutrición** puedan visualizar su progreso, consultar su plan de alimentación y registrar su adherencia diaria de forma sencilla, visual y amigable.

Esta versión está pensada como demo y base para personalizarla según cada consultorio o profesional de la salud.

---

## ✨ Características principales

- **Dashboard de seguimiento profesional**  
  - Tarjetas con:
    - Peso inicial, peso actual y peso objetivo.
    - IMC estimado.
    - Porcentaje de avance hacia la meta.
    - Días consecutivos cumpliendo el plan.
  - Gráfica de línea con la evolución del peso.
  - Mensaje de la nutrióloga.
  - Recordatorio constante de la **fecha y hora de la próxima cita**.

- **Mi plan de alimentación**  
  - Plan semanal de ejemplo (Lunes a Domingo) organizado por tiempos de comida.
  - Filtro por día de la semana.
  - Visualización en formato **cards** por comida y en **tabla**.
  - Fácilmente editable en el código para pegar el plan real de cada paciente.

- **Registro diario**  
  - Formulario para registrar:
    - Fecha (por defecto, hoy).
    - Checkboxes de cumplimiento por tiempo de comida: Desayuno, Colación 1, Comida, Colación 2, Cena.
    - Estado de ánimo del día: Muy bien, Bien, Regular, Mal.
    - Comentarios breves.
  - Los datos se guardan en un `pandas.DataFrame` en memoria.
  - Tabla con los registros del día o de los últimos 7 días.

- **Progreso**  
  - Cálculo del **porcentaje de adherencia diaria** (comidas cumplidas vs. planificadas).
  - Gráfica de barras con la adherencia en los últimos 7 días.
  - Cálculo de **% de adherencia global** (últimos 7 días).
  - Mensaje automático motivacional según el nivel de adherencia.

- **Contacto con la nutrióloga**  
  - Tarjeta destacada con el nombre de la nutrióloga:
    - **L.N. Brenda López Hernández**
    - Cédula profesional: **11036805**
  - Recomendaciones generales.
  - Área de notas para que el paciente registre dudas para la próxima cita.

- **UX/UI enfocado en salud y nutrición**
  - Paleta de colores suaves (verdes, blancos, tonos pastel).
  - Diseño limpio, con tarjetas (`cards`), columnas y jerarquía de títulos.
  - Emojis discretos para una experiencia más cercana y amigable.

---

## 🧱 Tecnologías utilizadas

- [Streamlit](https://streamlit.io/) – Framework para apps de datos en Python.
- [Pandas](https://pandas.pydata.org/) – Manejo de datos tabulares en memoria.

---

## 🚀 Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/app-seguimiento-nutricional.git
cd app-seguimiento-nutricional
```

### 2. Crear y activar entorno virtual (opcional, pero recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en macOS / Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la app

```bash
streamlit run app.py
```

Streamlit abrirá la app en tu navegador (por defecto en `http://localhost:8501`).

---

## 🛠 Personalización

- **Plan de alimentación:**  
  Edita la función `get_diet_plan_df()` en `app.py` para pegar el plan real de cada paciente o un plan estándar del consultorio.

- **Datos iniciales (peso, altura, meta):**  
  Se pueden ajustar desde el **sidebar** de la app. También se pueden fijar valores por defecto en `init_session_state()`.

- **Texto de la nutrióloga / mensajes motivacionales:**  
  Se pueden modificar en las secciones:
  - `show_dashboard()` → *Mensaje de la nutrióloga*.
  - `show_progress()` → mensajes según nivel de adherencia.

- **Persistencia de datos:**  
  Actualmente los datos se guardan en memoria (mientras la app está activa).  
  El código está organizado para que sea sencillo luego conectar con:
  - Google Sheets
  - Bases de datos (PostgreSQL, MySQL, etc.)
  - CSVs en disco

---

## 🧩 Estructura del código

El archivo principal `app.py` está estructurado en funciones:

- `init_session_state()` – Inicializa valores de sesión.
- `sync_weight_with_today()` – Sincroniza el peso actual con el historial.
- `get_diet_plan_df()` – Devuelve el plan de alimentación de ejemplo.
- `calculate_streak(df)` – Calcula días consecutivos cumpliendo el plan.
- `show_top_summary()` – Muestra peso inicial/actual/meta y próxima cita.
- `show_dashboard()` – Sección **Seguimiento profesional**.
- `show_plan()` – Sección **Mi plan de alimentación**.
- `show_daily_log()` – Sección **Registro diario**.
- `show_progress()` – Sección **Progreso**.
- `show_contact()` – Sección **Contacto**.
- `main()` – Control de navegación y layout general.

---

## 📌 Próximas mejoras posibles

- Autenticación por paciente.
- Persistencia real de datos (Google Sheets / base de datos).
- Exportar reportes en PDF para entregar al paciente.
- Notificaciones de recordatorio de cita.
- Panel de administración para la nutrióloga con vista de múltiples pacientes.

---

## 👩‍⚕️ Créditos

App pensada para acompañar procesos de consulta nutricional con:

**L.N. Brenda López Hernández**  
Cédula profesional: **11036805**
