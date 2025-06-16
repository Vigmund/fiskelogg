import streamlit as st
import pandas as pd
from datetime import datetime

USERS_FILE = "users.csv"
LOGS_FILE = "logs.csv"

GRONA_FARGER = ["#25523B", "#358856", "#5AAB61", "#62BD69", "#30694B", "#0C3823"]

def load_users():
    try:
        return pd.read_csv(USERS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "password"])

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def load_logs():
    try:
        return pd.read_csv(LOGS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "Datum", "Art", "Vikt (kg)", "Längd (cm)", "Plats", "Meddelande", "Bild"])

def save_logs(df):
    df.to_csv(LOGS_FILE, index=False)

if "users_df" not in st.session_state:
    st.session_state.users_df = load_users()
if "logs_df" not in st.session_state:
    st.session_state.logs_df = load_logs()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = ""
if "register_success" not in st.session_state:
    st.session_state.register_success = False

def set_custom_theme():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #EDE8D0;
            color: #25523B;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        }}
        h1, h2, h3, h4, h5 {{
            color: #30694B !important;
            font-weight: 700 !important;
        }}
        label, .streamlit-expanderHeader, .st-bx {{
            font-weight: 600;
            color: #30694B !important;
        }}
        /* Knappar */
        .stButton > button {{
            background-color: #5AAB61 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 18px !important;
            font-weight: 700 !important;
            border: none !important;
            cursor: pointer !important;
        }}
        .stButton > button:hover {{
            background-color: #62BD69 !important;
            color: white !important;
        }}
        /* Inputs */
        input, textarea {{
            background-color: white !important;
            color: #25523B !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            border: 1px solid #358856 !important;
            border-radius: 6px !important;
            padding: 6px !important;
        }}
        input::placeholder, textarea::placeholder {{
            color: #30694B !important;
            opacity: 0.8 !important;
        }}
        /* Ta bort vit text i allt */
        * {{
            color: unset !important;
        }}
        /* Tvinga grön färg på text */
        .label-text {{
            color: #25523B !important;
            font-weight: 700 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def colored_label(text, idx=0):
    farg = GRONA_FARGER[idx % len(GRONA_FARGER)]
    return f"<span style='color:{farg}; font-weight:700;'>{text}</span>"

def login():
    st.markdown("<h2>Logga in</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Användarnamn", key="login_username")
        password = st.text_input("Lösenord", type="password", key="login_password")
        submitted = st.form_submit_button("Logga in")
        if submitted:
            df = st.session_state.users_df
            if ((df["username"] == username) & (df["password"] == password)).any():
                st.session_state.logged_in = True
                st.session_state.logged_in_user = username
                st.success(f"Välkommen tillbaka, {username}!")
                st.experimental_rerun()
            else:
                st.error("Fel användarnamn eller lösenord")

def register():
    st.markdown("<h2>Registrera nytt konto</h2>", unsafe_allow_html=True)
    with st.form("register_form"):
        username = st.text_input("Välj användarnamn", key="register_username")
        password = st.text_input("Välj lösenord", type="password", key="register_password")
        submitted = st.form_submit_button("Registrera")
        if submitted:
            df = st.session_state.users_df
            if username in df["username"].values:
                st.error("Användarnamnet är redan taget, välj ett annat.")
            elif username.strip() == "" or password.strip() == "":
                st.error("Användarnamn och lösenord får inte vara tomma.")
            else:
                new_user = {"username": username, "password": password}
                st.session_state.users_df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
                save_users(st.session_state.users_df)
                st.success("Konto skapat! Logga in ovan.")
                # Flagga så vi kan reruna UTAN att ställa om värden i formuläret
                st.session_state.register_success = True

def logout():
    st.session_state.logged_in = False
    st.session_state.logged_in_user = ""
    st.experimental_rerun()

def ny_logg():
    st.markdown("<h1>Ny logg</h1>", unsafe_allow_html=True)
    df = st.session_state.logs_df

    with st.form("form_ny_logg"):
        st.markdown(colored_label("Datum", 0), unsafe_allow_html=True)
        datum = st.date_input("", key="datum_input")
        st.markdown(colored_label("Art", 1), unsafe_allow_html=True)
        art = st.text_input("", key="art_input")
        st.markdown(colored_label("Vikt (kg)", 2), unsafe_allow_html=True)
        vikt = st.number_input("", min_value=0.0, format="%.2f", key="vikt_input")
        st.markdown(colored_label("Längd (cm)", 3), unsafe_allow_html=True)
        langd = st.number_input("", min_value=0, format="%d", key="langd_input")
        st.markdown(colored_label("Plats", 4), unsafe_allow_html=True)
        plats = st.text_input("", key="plats_input")
        st.markdown(colored_label("Meddelande", 5), unsafe_allow_html=True)
        meddelande = st.text_area("", key="meddelande_input")
        st.markdown(colored_label("Bild (URL)", 0), unsafe_allow_html=True)
        bild = st.text_input("", key="bild_input")

        submitted = st.form_submit_button("Spara logg")

        if submitted:
            ny_rad = {
                "username": st.session_state.logged_in_user,
                "Datum": datum.strftime("%Y-%m-%d"),
                "Art": art,
                "Vikt (kg)": vikt,
                "Längd (cm)": langd,
                "Plats": plats,
                "Meddelande": meddelande,
                "Bild": bild,
            }
            st.session_state.logs_df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
            save_logs(st.session_state.logs_df)
            st.success("Logg sparad!")
            st.experimental_rerun()

def visa_mina_fangster():
    st.markdown("<h1>Mina fångster</h1>", unsafe_allow_html=True)
    df = st.session_state.logs_df
    user = st.session_state.logged_in_user

    mina_fangster = df[df["username"] == user]

    if mina_fangster.empty:
        st.info("Du har inga sparade fångster än.")
        return

    for idx, rad in mina_fangster.iterrows():
        st.markdown(f"### {rad['Datum']} - {rad['Art']}")
        st.write(f"Vikt: {rad['Vikt (kg)']} kg")
        st.write(f"Längd: {rad['Längd (cm)']} cm")
        st.write(f"Plats: {rad['Plats']}")
        st.write(f"Meddelande: {rad['Meddelande']}")
        if rad["Bild"]:
            st.image(rad["Bild"], use_column_width=True)
        st.markdown("---")

def main():
    set_custom_theme()
    st.title("Fiskeloggen")

    if not st.session_state.logged_in:
        col1, col2 = st.columns(2)
        with col1:
            login()
        with col2:
            register()
        # Efter registrering, visa knapp för att logga in
        if st.session_state.register_success:
            st.info("Registrering lyckades, logga in med ditt nya konto.")
    else:
        st.markdown(f"<h2 style='color:#0C3823;'>Välkommen, {st.session_state.logged_in_user}!</h2>", unsafe_allow_html=True)
        meny = st.sidebar.radio("Meny", ["Ny logg", "Mina fångster", "Logga ut"])

        if meny == "Ny logg":
            ny_logg()
        elif meny == "Mina fångster":
            visa_mina_fangster()
        elif meny == "Logga ut":
            logout()

if __name__ == "__main__":
    main()
