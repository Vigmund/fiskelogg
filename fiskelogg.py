import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Fiskelogg", page_icon="🐟")

st.title("🎣 Min Fiskelogg")

# Skapa mapp för bilder om den inte finns
if not os.path.exists("bilder"):
    os.makedirs("bilder")

# Loggfil
LOGGFIL = "fångster.csv"

# Inmatningsformulär
with st.form("loggfiske"):
    art = st.text_input("Fisksort (t.ex. gädda)")
    vikt = st.number_input("Vikt (kg)", step=0.1)
    längd = st.number_input("Längd (cm)", step=1)
    plats = st.text_input("Plats")
    kommentar = st.text_area("Kommentar")
    bild = st.file_uploader("Ladda upp en bild", type=["jpg", "jpeg", "png"])

    skicka = st.form_submit_button("Spara fångst")

if skicka:
    datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    bildnamn = ""
    if bild:
        bildnamn = f"bilder/{datum.replace(':', '-')}_{bild.name}"
        with open(bildnamn, "wb") as f:
            f.write(bild.getbuffer())

    ny_rad = {
        "Datum": datum,
        "Art": art,
        "Vikt (kg)": vikt,
        "Längd (cm)": längd,
        "Plats": plats,
        "Kommentar": kommentar,
        "Bild": bildnamn
    }

    if os.path.exists(LOGGFIL):
        df = pd.read_csv(LOGGFIL)
        df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
    else:
        df = pd.DataFrame([ny_rad])

    df.to_csv(LOGGFIL, index=False)
    st.success("🎉 Fångsten har sparats!")

# Visa logg
st.subheader("📜 Mina fångster")
if os.path.exists(LOGGFIL):
    df = pd.read_csv(LOGGFIL)
    for _, row in df[::-1].iterrows():  # visa senaste först
        st.markdown(f"**{row['Datum']} – {row['Art']} – {row['Vikt (kg)']} kg – {row['Längd (cm)']} cm**")
        st.markdown(f"📍 *{row['Plats']}*")
        st.markdown(f"✏️ {row['Kommentar']}")
        if row["Bild"] and os.path.exists(row["Bild"]):
            st.image(row["Bild"], width=300)
        st.markdown("---")
else:
    st.info("Inga fångster har loggats än.")
