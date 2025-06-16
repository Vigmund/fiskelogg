import streamlit as st
import pandas as pd
import os
from datetime import datetime
import hashlib

# Färger
BEIGE_BG = "#EDE8D0"
GRON_FARGER = ["#25523B", "#358856", "#5AAB61", "#62BD69", "#30694B", "#0C3823"]

# Filvägar
USERS_CSV = "users.csv"
LOGS_CSV = "logs.csv"
BILDER_MAPP = "bilder"

# Se till att mappen för bilder finns
os.makedirs(BILDER_MAPP, exist_ok=True)

# Initiera dataframes
if os.path.exists(USERS_CSV):
    users_df = pd.read_csv(USERS_CSV)
else:
    users_df = pd.DataFrame(columns=["username", "password_hash"])

if os.path.exists(LOGS_CSV):
    logs_df = pd.read_csv(LOGS_CSV)
else:
    logs_df = pd.DataFrame(columns=["username", "datum", "art", "vikt", "langd", "plats", "meddelande", "bild_path"])

# Hjälpfunktioner
def hash_losen(losen):
    return hashlib.sha256(losen.encode()).hexdigest()

def spara_users():
    users_df.to_csv(USERS_CSV, index=False)

def spara_logs():
    logs_df.to_csv(LOGS_CSV, index=False)

def login():
    st.title("Logga in")
    with st.form("login_form"):
        username = st.text_input("Användarnamn", key="login_user")
        password = st.text_input("Lösenord", type="password", key="login_pass")
        submitted = st.form_submit_button("Logga in")
    if submitted:
        if username in users_df["username"].values:
            hash_pass = hash_losen(password)
            user_pass_hash = users_df.loc[users_df["username"]==username, "password_hash"].values[0]
            if hash_pass == user_pass_hash:
                st.session_state["username"] = username
                st.session_state["logged_in"] = True
                st.success(f"Välkommen, {username}!")
                st.experimental_rerun()
            else:
                st.error("Fel lösenord")
        else:
            st.error("Användare finns inte")

def register():
    st.title("Registrera nytt konto")
    with st.form("register_form"):
        new_username = st.text_input("Välj användarnamn", key="reg_user")
        new_password = st.text_input("Välj lösenord", type="password", key="reg_pass")
        submitted = st.form_submit_button("Registrera")
    if submitted:
        if new_username.strip() == "" or new_password.strip() == "":
            st.error("Fyll i både användarnamn och lösenord.")
            return
        if new_username in users_df["username"].values:
            st.error("Användarnamn upptaget, välj ett annat.")
            return
        ny_hash = hash_losen(new_password)
        global users_df
        users_df = pd.concat([users_df, pd.DataFrame([{"username":new_username, "password_hash":ny_hash}])], ignore_index=True)
        spara_users()
        st.success("Konto skapat! Logga in nedan.")
        st.experimental_rerun()

def logout():
    st.session_state.clear()
    st.experimental_rerun()

def startsida():
    st.markdown(f"<h1 style='color:{GRON_FARGER[0]};'>Välkommen till Fiskeloggen!</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{GRON_FARGER[1]}; font-size:18px;'>Här kan du enkelt logga dina fångster och hålla koll på din fiskelycka.</p>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/616/616408.png", width=150)  # Du kan byta ut mot din egen bild eller logga

def ny_logg():
    st.header("Ny fångst")

    with st.form("ny_logg_form"):
        datum = st.date_input("Datum")
        art = st.text_input("Art")
        vikt = st.number_input("Vikt (kg)", min_value=0.0, step=0.1, format="%.2f")
        langd = st.number_input("Längd (cm)", min_value=0.0, step=0.1, format="%.1f")
        plats = st.text_input("Plats")
        meddelande = st.text_area("Meddelande (valfritt)")
        bild = st.file_uploader("Ladda upp bild (valfritt)", type=["png","jpg","jpeg"])
        submit = st.form_submit_button("Spara logg")

    if submit:
        if art.strip() == "":
            st.error("Ange art.")
            return

        filnamn = ""
        if bild is not None:
            filnamn = f"{st.session_state['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{bild.name}"
            bild_path = os.path.join(BILDER_MAPP, filnamn)
            with open(bild_path, "wb") as f:
                f.write(bild.getbuffer())
        else:
            bild_path = ""

        ny_rad = {
            "username": st.session_state["username"],
            "datum": datum.strftime("%Y-%m-%d"),
            "art": art,
            "vikt": vikt,
            "langd": langd,
            "plats": plats,
            "meddelande": meddelande,
            "bild_path": bild_path
        }

        global logs_df
        logs_df = pd.concat([logs_df, pd.DataFrame([ny_rad])], ignore_index=True)
        spara_logs()
        st.success("Logg sparad!")

def visa_mina_fangster():
    st.header("Mina fångster")

    user_logs = logs_df[logs_df["username"] == st.session_state["username"]]
    if user_logs.empty:
        st.info("Du har inga fångster sparade.")
        return

    for i, row in user_logs.iterrows():
        color = GRON_FARGER[i % len(GRON_FARGER)]
        st.markdown(f"### <span style='color:{color};'>{row['datum']} - {row['art']}</span>", unsafe_allow_html=True)
        st.write(f"Vikt: {row['vikt']} kg")
        st.write(f"Längd: {row['langd']} cm")
        st.write(f"Plats: {row['plats']}")
        if row['meddelande']:
            st.write(f"Meddelande: {row['meddelande']}")
        if row['bild_path']:
            if os.path.exists(row['bild_path']):
                st.image(row['bild_path'], width=300)
        st.markdown("---")

        # Ta bort knapp med bekräftelse
        ta_bort = st.button(f"Släng tillbaka fisken i sjön (ID: {i})")
        if ta_bort:
            if st.confirm(f"Är du säker på att du vill slänga tillbaka fisken {row['art']} från {row['datum']}?"):
                global logs_df
                logs_df = logs_df.drop(i).reset_index(drop=True)
                spara_logs()
                st.success("Logg borttagen!")
                st.experimental_rerun()

def main():
    st.set_page_config(page_title="Fiskeloggen", page_icon=":fish:", layout="centered")
    st.markdown(
        f"""
        <style>
            .reportview-container {{
                background-color: {BEIGE_BG};
            }}
            .css-1d391kg {{
                background-color: {BEIGE_BG};
            }}
            .stButton>button {{
                background-color: {GRON_FARGER[2]};
                color: white;
            }}
            .stButton>button:hover {{
                background-color: {GRON_FARGER[4]};
                color: white;
            }}
            label, .css-1n76uvr, .css-1r6slb0 {{
                color: {GRON_FARGER[0]} !important;
                font-weight: bold;
            }}
            .stTextInput>div>div>input, .stNumberInput>div>div>input, textarea {{
                color: {GRON_FARGER[0]} !important;
                background-color: #f0f2f6;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        # Visa login eller register
        val = st.sidebar.selectbox("Välj", ["Logga in", "Registrera nytt konto"])
        if val == "Logga in":
            login()
        else:
            register()
        return

    # Inloggad användare - visa meny och startsida
    meny_val = st.sidebar.radio("Meny", ["Startsida", "Ny logg", "Mina fångster", "Logga ut"], index=0)
    if meny_val == "Logga ut":
        logout()
        return
    elif meny_val == "Startsida":
        startsida()
    elif meny_val == "Ny logg":
        ny_logg()
    elif meny_val == "Mina fångster":
        visa_mina_fangster()

if __name__ == "__main__":
    main()
