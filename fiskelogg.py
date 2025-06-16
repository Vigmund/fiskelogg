import streamlit as st
import pandas as pd
import os

# --- Färgpalett ---
BEIGE = "#EDE8D0"
GREENS = ["#25523B", "#358856", "#5AAB61", "#62BD69", "#30694B", "#0C3823"]
BLACK = "#000000"

st.set_page_config(page_title="Fiskeloggen", page_icon="🎣", layout="centered")

# --- Initiera/ Läs in datafiler ---

if not os.path.exists("users.csv"):
    users_df = pd.DataFrame(columns=["username", "password"])
    users_df.to_csv("users.csv", index=False)
else:
    users_df = pd.read_csv("users.csv")

if not os.path.exists("fangster.csv"):
    df = pd.DataFrame(columns=["username", "datum", "art", "vikt", "langd", "plats", "meddelande"])
    df.to_csv("fangster.csv", index=False)
else:
    df = pd.read_csv("fangster.csv")


# --- Hjälpfunktion för färg (för att variera textfärg) ---
import random
def random_green():
    return random.choice(GREENS)


# --- Startsida ---
def startsida():
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BEIGE};
        color: {BLACK};
    }}
    </style>
    """, unsafe_allow_html=True)
    st.title("🎣 Välkommen till Fiskeloggen")
    st.markdown(f'<h3 style="color:{random_green()};">Logga in eller skapa ett konto för att börja</h3>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Logga in", use_container_width=True):
            st.session_state.page = "login"
            st.experimental_rerun()
            return
    with col2:
        if st.button("Skapa konto", use_container_width=True):
            st.session_state.page = "register"
            st.experimental_rerun()
            return


# --- Inloggning ---
def login():
    st.markdown(f'<h2 style="color:{random_green()};">Logga in</h2>', unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Användarnamn", key="login_username", placeholder="Ditt användarnamn")
        password = st.text_input("Lösenord", type="password", key="login_password", placeholder="Ditt lösenord")

        submitted = st.form_submit_button("Logga in")
        if submitted:
            if username == "" or password == "":
                st.error("Fyll i både användarnamn och lösenord.")
            else:
                global users_df
                if username in users_df["username"].values:
                    pw_stored = users_df.loc[users_df["username"] == username, "password"].values[0]
                    if password == pw_stored:
                        st.session_state.logged_in = True
                        st.session_state.user = username
                        st.session_state.page = "home"
                        st.success(f"Välkommen, {username}!")
                        st.experimental_rerun()
                        return
                    else:
                        st.error("Fel lösenord.")
                else:
                    st.error("Användarnamnet finns inte.")

    if st.button("Tillbaka", use_container_width=True):
        st.session_state.page = "startsida"
        st.experimental_rerun()
        return


# --- Registrering ---
def register():
    st.markdown(f'<h2 style="color:{random_green()};">Skapa konto</h2>', unsafe_allow_html=True)
    with st.form("register_form", clear_on_submit=False):
        username = st.text_input("Välj användarnamn", key="register_username", placeholder="Nytt användarnamn")
        password = st.text_input("Välj lösenord", type="password", key="register_password", placeholder="Nytt lösenord")

        submitted = st.form_submit_button("Skapa konto")
        if submitted:
            if username == "" or password == "":
                st.error("Fyll i både användarnamn och lösenord.")
            else:
                global users_df
                if username in users_df["username"].values:
                    st.error("Användarnamnet är redan upptaget.")
                else:
                    # Lägg till konto och spara
                    new_user = {"username": username, "password": password}
                    users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
                    users_df.to_csv("users.csv", index=False)
                    st.success("Kontot skapat! Logga in med dina uppgifter.")
                    st.session_state.page = "login"
                    st.experimental_rerun()
                    return

    if st.button("Tillbaka", use_container_width=True):
        st.session_state.page = "startsida"
        st.experimental_rerun()
        return


# --- Startsida efter inloggning ---
def home():
    st.markdown(f'<h2 style="color:{random_green()};">Hej {st.session_state.user}!</h2>', unsafe_allow_html=True)
    st.markdown(f'<h4 style="color:{random_green()};">Vad vill du göra?</h4>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Ny logg", use_container_width=True):
            st.session_state.page = "ny_logg"
            st.experimental_rerun()
            return
    with col2:
        if st.button("Mina fångster", use_container_width=True):
            st.session_state.page = "mina_fangster"
            st.experimental_rerun()
            return
    with col3:
        if st.button("Logga ut", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "startsida"
            st.experimental_rerun()
            return


# --- Ny logg ---
def ny_logg():
    st.markdown(f'<h2 style="color:{random_green()};">Ny fångst</h2>', unsafe_allow_html=True)
    with st.form("ny_logg_form", clear_on_submit=True):
        datum = st.date_input("Datum", key="datum")
        art = st.text_input("Art", key="art")
        vikt = st.number_input("Vikt (kg)", min_value=0.0, format="%.2f", key="vikt")
        langd = st.number_input("Längd (cm)", min_value=0.0, format="%.1f", key="langd")
        plats = st.text_input("Plats", key="plats")
        meddelande = st.text_area("Meddelande", key="meddelande")

        submitted = st.form_submit_button("Spara logg")
        if submitted:
            global df
            ny_post = {
                "username": st.session_state.user,
                "datum": datum.strftime("%Y-%m-%d"),
                "art": art,
                "vikt": vikt,
                "langd": langd,
                "plats": plats,
                "meddelande": meddelande,
            }
            df = pd.concat([df, pd.DataFrame([ny_post])], ignore_index=True)
            df.to_csv("fangster.csv", index=False)
            st.success("Fångst sparad!")
            st.session_state.page = "home"
            st.experimental_rerun()
            return

    if st.button("Tillbaka", use_container_width=True):
        st.session_state.page = "home"
        st.experimental_rerun()
        return


# --- Visa mina fångster ---
def visa_mina_fangster():
    st.markdown(f'<h2 style="color:{random_green()};">Mina fångster</h2>', unsafe_allow_html=True)

    global df
    mina_fangster = df[df["username"] == st.session_state.user]

    if mina_fangster.empty:
        st.info("Du har inga registrerade fångster än.")
    else:
        for idx, row in mina_fangster.iterrows():
            st.markdown(f"""
                <div style='background-color:{BEIGE}; padding:10px; margin-bottom:10px; border-radius:8px;'>
                    <b style="color:{random_green()};">Datum:</b> {row['datum']} <br>
                    <b style="color:{random_green()};">Art:</b> {row['art']} <br>
                    <b style="color:{random_green()};">Vikt (kg):</b> {row['vikt']} <br>
                    <b style="color:{random_green()};">Längd (cm):</b> {row['langd']} <br>
                    <b style="color:{random_green()};">Plats:</b> {row['plats']} <br>
                    <b style="color:{random_green()};">Meddelande:</b> {row['meddelande']} <br>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Vill du ta bort en logg?**")
        idx_to_delete = st.selectbox("Välj logg att ta bort (Datum - Art)", 
                                    options=[f"{row['datum']} - {row['art']}" for _, row in mina_fangster.iterrows()])
        if st.button("Ta bort vald logg"):
            # Hitta raden och ta bort
            del_index = mina_fangster[(mina_fangster["datum"] + " - " + mina_fangster["art"]) == idx_to_delete].index[0]
            df.drop(index=del_index, inplace=True)
            df.to_csv("fangster.csv", index=False)
            st.success("Logg borttagen!")
            st.experimental_rerun()
            return

    if st.button("Tillbaka", use_container_width=True):
        st.session_state.page = "home"
        st.experimental_rerun()
        return


# --- Main-funktion som styr navigation ---
def main():
    if "page" not in st.session_state:
        st.session_state.page = "startsida"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None

    # Färg för hela appen
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BEIGE};
        color: {BLACK};
    }}
    /* Ändra placeholder text färg i inputs (mörkgrönt) */
    input::placeholder, textarea::placeholder {{
        color: {GREENS[1]} !important;
        opacity: 1 !important;
    }}
    /* Ändra etikettfärg i formulär */
    label {{
        color: {GREENS[2]} !important;
        font-weight: bold;
    }}
    /* Ändra knapptext och bakgrund */
    button {{
        background-color: {GREENS[3]} !important;
        color: {BEIGE} !important;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.logged_in:
        if st.session_state.page == "startsida":
            startsida()
        elif st.session_state.page == "login":
            login()
        elif st.session_state.page == "register":
            register()
        else:
            # Om något annat värde - visa startsida
            st.session_state.page = "startsida"
            st.experimental_rerun()
    else:
        # Inloggad användare
        if st.session_state.page == "home":
            home()
        elif st.session_state.page == "ny_logg":
            ny_logg()
        elif st.session_state.page == "mina_fangster":
            visa_mina_fangster()
        else:
            # Om något annat värde - hem sidan
            st.session_state.page = "home"
            st.experimental_rerun()


if __name__ == "__main__":
    main()
    
