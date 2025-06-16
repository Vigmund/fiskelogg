import streamlit as st
import pandas as pd
import os

LOGG_FIL = "loggar.csv"
USERS_FIL = "users.csv"

# --- CSS Styling för färger och typsnitt ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

    html, body, [class*="css"]  {
        background-color: #EDE8D0;
        color: #25523B;
        font-family: 'Roboto', sans-serif;
    }
    .css-1emrehy e16nr0p30 {  /* För Streamlit knappar */
        background-color: #358856;
        color: white;
        font-weight: 600;
    }
    button:hover {
        background-color: #25523B !important;
        color: white !important;
    }
    .stButton>button {
        background-color: #358856;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 8px 16px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #25523B;
        color: white;
    }
    h1, h2, h3, h4, h5 {
        color: #30694B;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Läs in användare ---
if os.path.exists(USERS_FIL):
    users_df = pd.read_csv(USERS_FIL)
else:
    users_df = pd.DataFrame(columns=["username", "password"])

# --- Läs in loggar ---
if os.path.exists(LOGG_FIL):
    df = pd.read_csv(LOGG_FIL)
else:
    df = pd.DataFrame(columns=["username", "Datum", "Art", "Vikt (kg)", "Plats", "Bild"])

# Initiera session_state
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = None
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

def save_users():
    users_df.to_csv(USERS_FIL, index=False)

def save_loggar():
    df.to_csv(LOGG_FIL, index=False)

def login():
    st.title("🎣 Fiskeloggen - Logga in eller registrera dig")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Logga in")
        with st.form("login_form"):
            username = st.text_input("Användarnamn", key="login_user")
            password = st.text_input("Lösenord", type="password", key="login_pass")
            submitted = st.form_submit_button("Logga in")
            if submitted:
                user = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
                if not user.empty:
                    st.session_state.username = username
                    st.session_state.page = "home"
                    st.experimental_rerun()
                else:
                    st.error("Fel användarnamn eller lösenord")

    with col2:
        st.subheader("Registrera nytt konto")
        with st.form("register_form"):
            new_username = st.text_input("Nytt användarnamn", key="reg_user")
            new_password = st.text_input("Nytt lösenord", type="password", key="reg_pass")
            submitted = st.form_submit_button("Registrera")
            if submitted:
                if new_username.strip() == "" or new_password.strip() == "":
                    st.error("Användarnamn och lösenord får inte vara tomma")
                elif new_username in users_df['username'].values:
                    st.error("Användarnamnet är redan taget")
                else:
                    users_df.loc[len(users_df)] = [new_username, new_password]
                    save_users()
                    st.success("Konto skapat! Logga in ovan.")
                    st.experimental_rerun()

def logout():
    st.session_state.username = None
    st.session_state.page = "login"
    st.experimental_rerun()

def visa_mina_fangster():
    st.title(f"🎣 Mina fångster - {st.session_state.username}")

    user_logs = df[df['username'] == st.session_state.username]
    if user_logs.empty:
        st.info("Du har inga fångster ännu.")
    else:
        for i, row in user_logs.iterrows():
            with st.expander(f"{row['Datum']} – {row['Art']}"):
                st.write(f"Plats: {row['Plats']}")
                st.write(f"Vikt: {row['Vikt (kg)']} kg")
                if pd.notna(row['Bild']) and row['Bild'] != "":
                    try:
                        st.image(row['Bild'], width=200)
                    except:
                        st.write("Kunde inte ladda bilden.")

                # Ta bort knapp med bekräftelse
                delete_key = f"delete_{i}"
                if st.session_state.confirm_delete_id == i:
                    st.warning("Är du säker på att du vill slänga tillbaks den här fisken i sjön?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Ja, ta bort", key=f"confirm_yes_{i}"):
                            global df
                            df = df.drop(i)
                            df.reset_index(drop=True, inplace=True)
                            save_loggar()
                            st.success("Logg borttagen.")
                            st.session_state.confirm_delete_id = None
                            st.experimental_rerun()
                    with col_no:
                        if st.button("Nej", key=f"confirm_no_{i}"):
                            st.session_state.confirm_delete_id = None
                            st.experimental_rerun()
                else:
                    if st.button("Ta bort logg", key=delete_key):
                        st.session_state.confirm_delete_id = i
                        st.experimental_rerun()

    if st.button("Tillbaka", key="tillbaka_fangster"):
        st.session_state.page = "home"
        st.experimental_rerun()

def ny_logg():
    st.title("🎣 Ny logg")
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
                os.makedirs("bilder", exist_ok=True)
                bild_path = f"bilder/{bild.name}"
                with open(bild_path, "wb") as f:
                    f.write(bild.getbuffer())

            global df
            ny_rad = {
                "username": st.session_state.username,
                "Datum": datum.strftime("%Y-%m-%d"),
                "Art": art,
                "Vikt (kg)": vikt,
                "Plats": plats,
                "Bild": bild_path
            }
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
            save_loggar()
            st.success("Logg sparad!")
            st.session_state.page = "home"
            st.experimental_rerun()

    if st.button("Tillbaka", key="tillbaka_nylogg"):
        st.session_state.page = "home"
        st.experimental_rerun()

def home():
    st.title("🎣 Fiskeloggen")
    st.write(f"Hej, {st.session_state.username}!")

    # Temporär knapp-layout med kolumner
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Mina fångster", key="btn_fangster"):
            st.session_state.page = "mina_fangster"
            st.experimental_rerun()
    with col2:
        if st.button("Ny logg", key="btn_nylogg"):
            st.session_state.page = "ny_logg"
            st.experimental_rerun()

    if st.button("Logga ut", key="btn_logout"):
        logout()

# --- Main ---
if st.session_state.page == "login":
    login()
elif st.session_state.page == "home":
    home()
elif st.session_state.page == "mina_fangster":
    visa_mina_fangster()
elif st.session_state.page == "ny_logg":
    ny_logg()
