import streamlit as st
import pandas as pd
import os
import hashlib

LOGG_FIL = "loggar.csv"
USER_FIL = "users.csv"

# Funktion för att hasha lösenord
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Läs in användare
if os.path.exists(USER_FIL):
    users_df = pd.read_csv(USER_FIL)
else:
    users_df = pd.DataFrame(columns=["username", "password_hash"])

# Läs in loggar, med kolumn för användare
if os.path.exists(LOGG_FIL):
    df = pd.read_csv(LOGG_FIL)
else:
    df = pd.DataFrame(columns=["Användare", "Datum", "Art", "Vikt (kg)", "Plats", "Bild"])

# Initiera sidan i session_state om inte satt
if "page" not in st.session_state:
    st.session_state.page = "login"  # start på inloggningssidan
if "username" not in st.session_state:
    st.session_state.username = None

def register():
    st.title("Registrera nytt konto")
    new_user = st.text_input("Användarnamn")
    new_password = st.text_input("Lösenord", type="password")
    if st.button("Registrera"):
        if new_user == "" or new_password == "":
            st.error("Fyll i både användarnamn och lösenord")
        elif new_user in users_df['username'].values:
            st.error("Användarnamnet är redan taget")
        else:
            global users_df
            users_df = users_df.append({
                "username": new_user,
                "password_hash": hash_password(new_password)
            }, ignore_index=True)
            users_df.to_csv(USER_FIL, index=False)
            st.success("Registrering lyckades! Logga in nu.")
            st.session_state.page = "login"

def login():
    st.title("Logga in")
    username = st.text_input("Användarnamn")
    password = st.text_input("Lösenord", type="password")
    if st.button("Logga in"):
        if username in users_df['username'].values:
            saved_hash = users_df.loc[users_df['username'] == username, 'password_hash'].values[0]
            if hash_password(password) == saved_hash:
                st.success(f"Inloggad som {username}")
                st.session_state.username = username
                st.session_state.page = "home"
            else:
                st.error("Fel lösenord")
        else:
            st.error("Användaren finns inte")
    if st.button("Registrera nytt konto"):
        st.session_state.page = "register"

def home():
    st.title(f"🎣 Fiskeloggen - Välkommen {st.session_state.username}")
    if st.button("Mina fångster"):
        st.session_state.page = "mina_fangster"
    if st.button("Ny logg"):
        st.session_state.page = "ny_logg"
    if st.button("Logga ut"):
        st.session_state.username = None
        st.session_state.page = "login"

# Anpassa mina fångster och ny_logg för att filtrera på st.session_state.username också

def visa_mina_fangster():
    st.title("Mina fångster")
    user_logs = df[df['Användare'] == st.session_state.username]
    if user_logs.empty:
        st.info("Du har inga fångster ännu.")
    else:
        for i, row in user_logs.iterrows():
            with st.expander(f"{row['Datum']} – {row['Art']}"):
                st.write(f"Plats: {row['Plats']}")
                st.write(f"Vikt: {row['Vikt (kg)']} kg")
                if pd.notna(row['Bild']):
                    st.image(row['Bild'], width=200)
    if st.button("Tillbaka", key="tillbaka_fangster"):
        st.session_state.page = "home"

def ny_logg():
    st.title("Ny logg")
    with st.form("form_ny_logg"):
        datum = st.date_input("Datum")
        art = st.text_input("Art")
        vikt = st.number_input("Vikt (kg)", min_value=0.0, format="%.2f")
        plats = st.text_input("Plats")
        bild = st.file_uploader("Ladda upp bild", type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("Spara logg")
        if submitted:
            bild_path = ""
            if bild is not None:
                if not os.path.exists("bilder"):
                    os.makedirs("bilder")
                bild_path = f"bilder/{bild.name}"
                with open(bild_path, "wb") as f:
                    f.write(bild.getbuffer())
            global df
            ny_rad = {
                "Användare": st.session_state.username,
                "Datum": datum.strftime("%Y-%m-%d"),
                "Art": art,
                "Vikt (kg)": vikt,
                "Plats": plats,
                "Bild": bild_path
            }
            df = df.append(ny_rad, ignore_index=True)
            df.to_csv(LOGG_FIL, index=False)
            st.success("Logg sparad!")
            st.session_state.page = "home"

    if st.button("Tillbaka", key="tillbaka_nylogg"):
        st.session_state.page = "home"

# Main page routing
if st.session_state.page == "login":
    login()
elif st.session_state.page == "register":
    register()
elif st.session_state.page == "home":
    if st.session_state.username:
        home()
    else:
        st.session_state.page = "login"
elif st.session_state.page == "mina_fangster":
    if st.session_state.username:
        visa_mina_fangster()
    else:
        st.session_state.page = "login"
elif st.session_state.page == "ny_logg":
    if st.session_state.username:
        ny_logg()
    else:
        st.session_state.page = "login"
