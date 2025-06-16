import streamlit as st
import pandas as pd
import os

# Färger
BEIGE_BG = "#EDE8D0"
GRON_FARGER = ["#25523B", "#358856", "#5AAB61", "#62BD69", "#30694B", "#0C3823"]

# Datafiler
USERS_CSV = "users.csv"
LOGS_CSV = "logs.csv"
IMAGES_FOLDER = "images"

# Initiera dataframes globalt
if os.path.exists(USERS_CSV):
    users_df = pd.read_csv(USERS_CSV)
else:
    users_df = pd.DataFrame(columns=["username", "password"])

if os.path.exists(LOGS_CSV):
    logs_df = pd.read_csv(LOGS_CSV)
else:
    logs_df = pd.DataFrame(columns=["username", "datum", "art", "vikt", "langd", "plats", "meddelande", "bild"])

if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)

# Funktion för att hämta en grön färg från listan (varierar per anrop)
def get_random_green_color(idx=0):
    return GRON_FARGER[idx % len(GRON_FARGER)]

# Spara dataframes till filer
def save_users():
    global users_df
    users_df.to_csv(USERS_CSV, index=False)

def save_logs():
    global logs_df
    logs_df.to_csv(LOGS_CSV, index=False)

# Startsida
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
    if st.button("Skapa konto"):
        st.session_state['page'] = "register"

# Registrera nytt konto
def register():
    global users_df
    st.markdown(f"<h2 style='color:{get_random_green_color(2)}'>Registrera nytt konto</h2>", unsafe_allow_html=True)
    with st.form("register_form"):
        username = st.text_input("Välj användarnamn", max_chars=20)
        password = st.text_input("Välj lösenord", type="password", max_chars=20)
        submitted = st.form_submit_button("Registrera")
    if submitted:
        if username.strip() == "" or password.strip() == "":
            st.error("Användarnamn och lösenord får inte vara tomma.")
            return
        if username in users_df['username'].values:
            st.error("Användarnamnet är upptaget. Välj ett annat.")
        else:
            users_df = users_df.append({"username": username, "password": password}, ignore_index=True)
            save_users()
            st.success("Kontot skapat! Logga in med dina uppgifter.")
            st.session_state['page'] = "login"
            st.experimental_rerun()
    if st.button("Tillbaka"):
        st.session_state['page'] = "start"
        st.experimental_rerun()

# Logga in
def login():
    global users_df
    st.markdown(f"<h2 style='color:{get_random_green_color(3)}'>Logga in</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Användarnamn")
        password = st.text_input("Lösenord", type="password")
        submitted = st.form_submit_button("Logga in")
    if submitted:
        user_row = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
        if not user_row.empty:
            st.session_state['user'] = username
            st.session_state['page'] = "home"
            st.experimental_rerun()
        else:
            st.error("Fel användarnamn eller lösenord.")
    if st.button("Tillbaka"):
        st.session_state['page'] = "start"
        st.experimental_rerun()

# Logga ut
def logout():
    st.session_state.pop('user', None)
    st.session_state['page'] = "start"
    st.experimental_rerun()

# Ny fisklogg
def ny_logg():
    global logs_df
    st.markdown(f"<h2 style='color:{get_random_green_color(4)}'>Ny fångst</h2>", unsafe_allow_html=True)
    with st.form("ny_logg_form"):
        datum = st.date_input("Datum")
        art = st.text_input("Art")
        vikt = st.number_input("Vikt (kg)", min_value=0.0, step=0.01, format="%.2f")
        langd = st.number_input("Längd (cm)", min_value=0.0, step=0.1, format="%.1f")
        plats = st.text_input("Plats")
        meddelande = st.text_area("Meddelande (valfritt)")
        bild = st.file_uploader("Ladda upp bild", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Spara logg")
    if submitted:
        bild_path = ""
        if bild is not None:
            bild_namn = f"{st.session_state['user']}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}_{bild.name}"
            bild_path = os.path.join(IMAGES_FOLDER, bild_namn)
            with open(bild_path, "wb") as f:
                f.write(bild.getbuffer())
        ny_rad = {
            "username": st.session_state['user'],
            "datum": datum,
            "art": art,
            "vikt": vikt,
            "langd": langd,
            "plats": plats,
            "meddelande": meddelande,
            "bild": bild_path
        }
        logs_df = logs_df.append(ny_rad, ignore_index=True)
        save_logs()
        st.success("Logg sparad!")
        if st.button("Till startsidan"):
            st.session_state['page'] = "home"
            st.experimental_rerun()

# Visa fångster för inloggad användare
def visa_mina_fangster():
    global logs_df
    st.markdown(f"<h2 style='color:{get_random_green_color(5)}'>Mina fångster</h2>", unsafe_allow_html=True)
    mina_logs = logs_df[logs_df['username'] == st.session_state['user']]
    if mina_logs.empty:
        st.info("Du har inga fångster sparade ännu.")
    else:
        for idx, row in mina_logs.iterrows():
            st.markdown(f"""
                <div style="background-color:#FFFFFF; padding:10px; margin-bottom:10px; border-radius:8px;">
                <b style="color:{get_random_green_color(idx)}">Datum:</b> {row['datum']}<br>
                <b style="color:{get_random_green_color(idx+1)}">Art:</b> {row['art']}<br>
                <b style="color:{get_random_green_color(idx+2)}">Vikt (kg):</b> {row['vikt']}<br>
                <b style="color:{get_random_green_color(idx+3)}">Längd (cm):</b> {row['langd']}<br>
                <b style="color:{get_random_green_color(idx+4)}">Plats:</b> {row['plats']}<br>
                <b style="color:{get_random_green_color(idx+5)}">Meddelande:</b> {row['meddelande']}<br>
            """, unsafe_allow_html=True)
            if row['bild']:
                try:
                    st.image(row['bild'], width=300)
                except:
                    st.text("Bild kunde inte visas.")
            if st.button(f"Ta bort logg #{idx}", key=f"del_{idx}"):
                if st.checkbox(f"Är du säker på att du vill slänga tillbaks den här fisken i sjön? (logg #{idx})", key=f"confirm_{idx}"):
                    logs_df = logs_df.drop(idx)
                    save_logs()
                    st.success("Logg borttagen!")
                    st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Till startsidan"):
        st.session_state['page'] = "home"
        st.experimental_rerun()

# Huvudsida efter login
def home():
    st.markdown(f"""
    <div style="background-color:{BEIGE_BG}; padding:15px; border-radius:10px; margin-bottom:10px;">
        <h2 style="color:{get_random_green_color(0)}">Välkommen, {st.session_state['user']}!</h2>
        <button onclick="window.location.href='#';" id="nylogg_btn">Ny fångst</button>
        <button onclick="window.location.href='#';" id="mina_fangster_btn">Mina fångster</button>
        <button onclick="window.location.href='#';" id="logga_ut_btn">Logga ut</button>
    </div>
    """, unsafe_allow_html=True)

    # Simple knappar med Streamlit istället för HTML-knappar för bättre kontroll
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Ny fångst"):
            st.session_state['page'] = "ny_logg"
            st.experimental_rerun()
    with col2:
        if st.button("Mina fångster"):
            st.session_state['page'] = "mina_fangster"
            st.experimental_rerun()
    with col3:
        if st.button("Logga ut"):
            logout()

# Main controller
def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = "start"
    if 'user' not in st.session_state:
        st.session_state['user'] = None

    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {BEIGE_BG};
        }}
        .css-1d391kg {{
            color: {get_random_green_color(0)};
        }}
        label {{
            color: {get_random_green_color(1)};
            font-weight: bold;
        }}
        input, textarea {{
            color: {get_random_green_color(5)};
            background-color: #F9F9F9;
        }}
        .stButton>button {{
            background-color: {get_random_green_color(2)};
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
        }}
        .stButton>button:hover {{
            background-color: {get_random_green_color(3)};
        }}
    </style>
    """, unsafe_allow_html=True)

    if st.session_state['user'] is None:
        if st.session_state['page'] == "start":
            startsida()
        elif st.session_state['page'] == "login":
            login()
        elif st.session_state['page'] == "register":
            register()
    else:
        if st.session_state['page'] == "home":
            home()
        elif st.session_state['page'] == "ny_logg":
            ny_logg()
        elif st.session_state['page'] == "mina_fangster":
            visa_mina_fangster()
        else:
            st.session_state['page'] = "home"
            st.experimental_rerun()

if __name__ == "__main__":
    main()
