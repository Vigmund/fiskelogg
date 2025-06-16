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

def get_random_green_color(idx=0):
    return GRON_FARGER[idx % len(GRON_FARGER)]

def save_users():
    global users_df
    users_df.to_csv(USERS_CSV, index=False)

def save_logs():
    global logs_df
    logs_df.to_csv(LOGS_CSV, index=False)

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
            # Korrekt sätt att lägga till rad i pandas utan append()
            new_row = pd.DataFrame([{"username": username, "password": password}])
            users_df = pd.concat([users_df, new_row], ignore_index=True)
            save_users()
            st.success("Kontot skapat! Logga in med dina uppgifter.")
            st.session_state['page'] = "login"
            st.experimental_rerun()
    if st.button("Tillbaka"):
        st.session_state['page'] = "start"
        st.experimental_rerun()

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

def logout():
    st.session_state.pop('user', None)
    st.session_state['page'] = "start"
    st.experimental_rerun()

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
        logs_df = pd.concat([logs_df, pd.DataFrame([ny_rad])], ignore_index=True)
        save_logs()
        st.success("Logg sparad!")
        if st.button("Till startsidan"):
            st.session_state['page'] = "home"
            st.experimental_rerun()

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
            if row["bild"]:
                if os.path.exists(row["bild"]):
                    st.image(row["bild"], width=300)
            if st.button(f"Ta bort fångst {idx}"):
                logs_df.drop(idx, inplace=True)
                save_logs()
                st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Till startsidan"):
        st.session_state['page'] = "home"
        st.experimental_rerun()

def home():
    st.markdown(f"<h2 style='color:{get_random_green_color(0)}'>Välkommen, {st.session_state['user']}!</h2>", unsafe_allow_html=True)
    if st.button("Ny fångst"):
        st.session_state['page'] = "ny_logg"
        st.experimental_rerun()
    if st.button("Mina fångster"):
        st.session_state['page'] = "mina_fangster"
        st.experimental_rerun()
    if st.button("Logga ut"):
        logout()

def main():
    st.set_page_config(page_title="Fiskeloggen", page_icon="🎣", layout="centered")
    st.markdown(f"""
    <style>
        /* Bakgrund och textfärger */
        .stApp {{
            background-color: {BEIGE_BG};
            color: {GRON_FARGER[0]};
        }}
        /* All text som är label eller rubrik i form */
        label, h1, h2, h3, h4, h5, h6 {{
            color: {GRON_FARGER[1]} !important;
        }}
        /* Inputfältens text och placeholders */
        input[type="text"], input[type="password"], input[type="number"], textarea {{
            color: {GRON_FARGER[2]} !important;
        }}
        ::placeholder {{
            color: {GRON_FARGER[3]} !important;
        }}
        /* Buttons färg */
        div.stButton > button:first-child {{
            background-color: {GRON_FARGER[4]};
            color: {BEIGE_BG};
            font-weight: bold;
        }}
        div.stButton > button:first-child:hover {{
            background-color: {GRON_FARGER[5]};
            color: {BEIGE_BG};
        }}
    </style>
    """, unsafe_allow_html=True)

    if 'page' not in st.session_state:
        st.session_state['page'] = "start"

    if st.session_state['page'] == "start":
        startsida()
    elif st.session_state['page'] == "login":
        login()
    elif st.session_state['page'] == "register":
        register()
    elif st.session_state['page'] == "home":
        if 'user' not in st.session_state:
            st.session_state['page'] = "start"
            st.experimental_rerun()
        else:
            home()
    elif st.session_state['page'] == "ny_logg":
        if 'user' not in st.session_state:
            st.session_state['page'] = "start"
            st.experimental_rerun()
        else:
            ny_logg()
    elif st.session_state['page'] == "mina_fangster":
        if 'user' not in st.session_state:
            st.session_state['page'] = "start"
            st.experimental_rerun()
        else:
            visa_mina_fangster()

if __name__ == "__main__":
    main()
