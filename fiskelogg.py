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

def set_custom_theme():
    grona_css = ""
    for i, farg in enumerate(GRONA_FARGER):
        grona_css += f".gron{i} {{color: {farg}; font-weight: 600;}}\n"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #EDE8D0;
            color: #25523B;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        }}
        .css-1v3fvcr h1 {{
            color: #30694B;
        }}
        .stButton > button {{
            background-color: #5AAB61;
            color: white;
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 600;
            border: none;
            margin-top: 10px;
            cursor: pointer;
        }}
        .stButton > button:hover {{
            background-color: #62BD69;
            color: white;
        }}
        input, textarea {{
            border-radius: 6px;
            border: 1px solid #358856;
            padding: 6px;
            background-color: white;
            color: #25523B !important;
            font-weight: 600;
            font-size: 16px;
        }}
        input::placeholder, textarea::placeholder {{
            color: #30694B;
            opacity: 0.7;
        }}
        /* Göm inbyggda input-labels men visa våra egna */
        div[data-baseweb="input"] > label,
        textarea[data-baseweb="textarea"] > label {{
            display: none !important;
        }}
        .streamlit-expanderHeader {{
            color: #0C3823;
            font-weight: 600;
        }}
        {grona_css}
        </style>
        """,
        unsafe_allow_html=True,
    )

def colored_label(text):
    from random import choice
    farg = choice(GRONA_FARGER)
    return f"<span style='color:{farg}; font-weight:600;'>{text}</span>"

def login():
    st.markdown("<h2 class='gron0'>Logga in</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Användarnamn", key="login_username")
        password = st.text_input("Lösenord", type="password", key="login_password")
        submitted = st.form_submit_button("Logga in")
        if submitted:
            df = st.session_state.users_df
            user_row = df[(df["username"] == username) & (df["password"] == password)]
            if not user_row.empty:
                st.session_state.logged_in = True
                st.session_state.logged_in_user = username
                st.success(f"Välkommen tillbaka, {username}!")
                st.experimental_rerun()
            else:
                st.error("Fel användarnamn eller lösenord")

def register():
    st.markdown("<h2 class='gron1'>Registrera nytt konto</h2>", unsafe_allow_html=True)
    with st.form("register_form"):
        username = st.text_input("Välj användarnamn", key="register_username")
        password = st.text_input("Välj lösenord", type="password", key="register_password")
        submitted = st.form_submit_button("Registrera")
        if submitted:
            df = st.session_state.users_df
            if username in df["username"].values:
                st.error("Användarnamnet är redan taget, välj ett annat.")
            elif username == "" or password == "":
                st.error("Användarnamn och lösenord får inte vara tomma.")
            else:
                new_user = {"username": username, "password": password}
                st.session_state.users_df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
                save_users(st.session_state.users_df)
                st.success("Konto skapat! Logga in ovan.")
                st.experimental_rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.logged_in_user = ""
    st.experimental_rerun()

def ny_logg():
    st.markdown(f"<h1 class='gron2'>Ny logg</h1>", unsafe_allow_html=True)
    df = st.session_state.logs_df

    with st.form("form_ny_logg"):
        st.markdown(colored_label("Datum"))
        datum = st.date_input("", key="datum_input")
        st.markdown(colored_label("Art"))
        art = st.text_input("", key="art_input")
        st.markdown(colored_label("Vikt (kg)"))
        vikt = st.number_input("", min_value=0.0, format="%.2f", key="vikt_input")
        st.markdown(colored_label("Längd (cm)"))
        langd = st.number_input("", min_value=0, format="%d", key="langd_input")
        st.markdown(colored_label("Plats"))
        plats = st.text_input("", key="plats_input")
        st.markdown(colored_label("Meddelande"))
        meddelande = st.text_area("", key="meddelande_input")
        st.markdown(colored_label("Bild (URL)"))
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
    st.markdown(f"<h1 class='gron3'>Mina fångster</h1>", unsafe_allow_html=True)
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
        if rad['Bild']:
            st.image(rad['Bild'], use_column_width=True)

        if st.button(f"Ta bort logg #{idx}", key=f"ta_bort_{idx}"):
            confirm = st.radio(
                "Är du säker på att du vill slänga tillbaks den här fisken i sjön?",
                ("Nej", "Ja"),
                key=f"confirm_{idx}",
            )
            if confirm == "Ja":
                st.session_state.logs_df = df.drop(idx).reset_index(drop=True)
                save_logs(st.session_state.logs_df)
                st.success("Logg borttagen!")
                st.experimental_rerun()

def main():
    set_custom_theme()

    if not st.session_state.logged_in:
        st.title("Fiskeloggen")
        st.write("Vänligen logga in eller registrera dig.")
        col1, col2 = st.columns(2)
        with col1:
            login()
        with col2:
            register()
    else:
        st.markdown(f"<h2>Välkommen, {st.session_state.logged_in_user}!</h2>", unsafe_allow_html=True)
        meny = st.sidebar.radio("Meny", ["Ny logg", "Mina fångster", "Logga ut"])

        if meny == "Ny logg":
            ny_logg()
        elif meny == "Mina fångster":
            visa_mina_fangster()
        elif meny == "Logga ut":
            logout()

if __name__ == "__main__":
    main()
