import streamlit as st
import pandas as pd
import os
import random

# --- Konstanter för färger ---
BEIGE_BG = "#EDE8D0"
GRON_FARGER = ["#25523B", "#358856", "#5AAB61", "#62BD69", "#30694B", "#0C3823"]

# Filnamn för datalagring
USERS_FILE = "users.csv"
LOGG_FILE = "fangster.csv"

# --- Hjälpfunktion för att slumpa grön färg ---
def get_random_green_color(seed=None):
    if seed is not None:
        random.seed(seed)
    return random.choice(GRON_FARGER)

# --- Läs in eller skapa datafiler ---
def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        return pd.DataFrame(columns=["username", "password"])

def load_logs():
    if os.path.exists(LOGG_FILE):
        return pd.read_csv(LOGG_FILE)
    else:
        return pd.DataFrame(columns=["username","datum","art","vikt","langd","plats","meddelande"])

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def save_logs(df):
    df.to_csv(LOGG_FILE, index=False)

# --- Startsida ---
def startsida():
    st.markdown(f"""
        <div style="background-color:{BEIGE_BG}; padding:20px; border-radius:10px;">
            <h1 style="color:{get_random_green_color(0)}; text-align:center;">Välkommen till Fiskeloggen!</h1>
            <p style="color:{get_random_green_color(1)}; text-align:center;">
                Logga in eller skapa nytt konto för att börja logga dina fångster.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Logga in"):
        st.session_state['page'] = "login"
        st.experimental_rerun()
        return

    if st.button("Skapa konto"):
        st.session_state['page'] = "register"
        st.experimental_rerun()
        return

# --- Login-sida ---
def login():
    users_df = load_users()
    st.markdown(f"<h2 style='color:{get_random_green_color(2)}'>Logga in</h2>", unsafe_allow_html=True)
    username = st.text_input("Användarnamn", key="login_username", help="Skriv ditt användarnamn", label_visibility="visible")
    password = st.text_input("Lösenord", type="password", key="login_password", help="Skriv ditt lösenord", label_visibility="visible")

    if st.button("Logga in"):
        if username == "" or password == "":
            st.error("Ange både användarnamn och lösenord.")
        elif username in users_df["username"].values:
            pw = users_df.loc[users_df["username"] == username, "password"].values[0]
            if pw == password:
                st.success(f"Välkommen, {username}!")
                st.session_state['user'] = username
                st.session_state['page'] = "home"
                st.experimental_rerun()
                return
            else:
                st.error("Fel lösenord.")
        else:
            st.error("Användarnamnet finns inte.")

    if st.button("Tillbaka till startsidan"):
        st.session_state['page'] = "start"
        st.experimental_rerun()
        return

# --- Registrera nytt konto ---
def register():
    users_df = load_users()
    st.markdown(f"<h2 style='color:{get_random_green_color(3)}'>Skapa nytt konto</h2>", unsafe_allow_html=True)
    username = st.text_input("Välj användarnamn", key="register_username", help="Välj ett användarnamn", label_visibility="visible")
    password = st.text_input("Välj lösenord", type="password", key="register_password", help="Välj ett lösenord", label_visibility="visible")

    if st.button("Registrera"):
        if username == "" or password == "":
            st.error("Ange både användarnamn och lösenord.")
        elif username in users_df["username"].values:
            st.error("Användarnamnet är redan upptaget.")
        else:
            new_row = pd.DataFrame({"username": [username], "password": [password]})
            users_df = pd.concat([users_df, new_row], ignore_index=True)
            save_users(users_df)
            st.success("Kontot skapat! Logga in med dina uppgifter.")
            st.session_state['page'] = "login"
            st.experimental_rerun()
            return

    if st.button("Tillbaka till startsidan"):
        st.session_state['page'] = "start"
        st.experimental_rerun()
        return

# --- Startsida efter inloggning ---
def home():
    st.markdown(f"<h2 style='color:{get_random_green_color(4)}'>Välkommen {st.session_state['user']}!</h2>", unsafe_allow_html=True)
    if st.button("Ny logg"):
        st.session_state['page'] = "ny_logg"
        st.experimental_rerun()
        return
    if st.button("Mina fångster"):
        st.session_state['page'] = "mina_fangster"
        st.experimental_rerun()
        return
    if st.button("Logga ut"):
        st.session_state.pop('user', None)
        st.session_state['page'] = "start"
        st.experimental_rerun()
        return

# --- Ny fångst-logg ---
def ny_logg():
    logs_df = load_logs()
    st.markdown(f"<h2 style='color:{get_random_green_color(5)}'>Ny fångst</h2>", unsafe_allow_html=True)
    with st.form("fisk_form"):
        datum = st.date_input("Datum")
        art = st.text_input("Art")
        vikt = st.number_input("Vikt (kg)", min_value=0.0, format="%.2f")
        langd = st.number_input("Längd (cm)", min_value=0.0, format="%.1f")
        plats = st.text_input("Plats")
        meddelande = st.text_area("Meddelande (valfritt)")

        submitted = st.form_submit_button("Spara")

        if submitted:
            if art.strip() == "":
                st.error("Ange fiskens art.")
            else:
                new_log = {
                    "username": st.session_state['user'],
                    "datum": datum.strftime("%Y-%m-%d"),
                    "art": art,
                    "vikt": vikt,
                    "langd": langd,
                    "plats": plats,
                    "meddelande": meddelande
                }
                logs_df = pd.concat([logs_df, pd.DataFrame([new_log])], ignore_index=True)
                save_logs(logs_df)
                st.success("Fångsten sparad!")
                st.session_state['page'] = "home"
                st.experimental_rerun()
                return

    if st.button("Tillbaka"):
        st.session_state['page'] = "home"
        st.experimental_rerun()
        return

# --- Visa användarens fångster ---
def visa_mina_fangster():
    logs_df = load_logs()
    st.markdown(f"<h2 style='color:{get_random_green_color(0)}'>Mina fångster</h2>", unsafe_allow_html=True)
    user_logs = logs_df[logs_df["username"] == st.session_state['user']]
    if user_logs.empty:
        st.info("Du har inga loggade fångster än.")
    else:
        st.dataframe(user_logs.drop(columns=["username"]), use_container_width=True)

    if st.button("Tillbaka"):
        st.session_state['page'] = "home"
        st.experimental_rerun()
        return

# --- Huvudfunktion ---
def main():
    st.set_page_config(page_title="Fiskeloggen", page_icon="🎣", layout="centered")

    # CSS för bakgrund och textfärger
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {BEIGE_BG};
            color: {GRON_FARGER[0]} !important;
        }}
        label, h1, h2, h3, h4, h5, h6, p {{
            color: {GRON_FARGER[1]} !important;
        }}
        input[type="text"], input[type="password"], input[type="number"], textarea {{
            color: {GRON_FARGER[2]} !important;
            background-color: #f9f9f9;
        }}
        ::placeholder {{
            color: {GRON_FARGER[3]} !important;
        }}
        div.stButton > button:first-child {{
            background-color: {GRON_FARGER[4]} !important;
            color: {BEIGE_BG} !important;
            font-weight: bold;
        }}
        div.stButton > button:first-child:hover {{
            background-color: {GRON_FARGER[5]} !important;
            color: {BEIGE_BG} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    if 'page' not in st.session_state:
        st.session_state['page'] = "start"

    page = st.session_state['page']

    if page == "start":
        startsida()
    elif page == "login":
        login()
    elif page == "register":
        register()
    elif page == "home":
        if 'user' not in st.session_state:
            st.session_state['page'] = "start"
            st.experimental_rerun()
            return
        home()
    elif page == "ny_logg":
        if 'user' not in st.session_state:
            st.session_state['page'] = "start"
            st.experimental_rerun()
            return
        ny_logg()
    elif page == "mina_fangster":
        if 'user' not in st.session_state:
            st.session_state['page'] = "start"
            st.experimental_rerun()
            return
        visa_mina_fangster()

if __name__ == "__main__":
    main()
