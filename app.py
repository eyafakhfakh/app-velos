# app.py · Application Streamlit — Prévision de la demande de vélos en libre-service
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Prévision Vélos", page_icon="🚲", layout="centered")


@st.cache_resource
def charger_modele():
    return joblib.load("model.joblib")


modele = charger_modele()

st.title("🚲 Prévoir la demande horaire de vélos")
st.write(
    "Renseignez les conditions calendaires et météorologiques de l'heure à prévoir, "
    "puis cliquez sur **Estimer la demande**."
)

saisons = {1: "1 - Printemps", 2: "2 - Été", 3: "3 - Automne", 4: "4 - Hiver"}
jours = {
    0: "0 - Dimanche", 1: "1 - Lundi", 2: "2 - Mardi", 3: "3 - Mercredi",
    4: "4 - Jeudi", 5: "5 - Vendredi", 6: "6 - Samedi"
}
meteos = {
    1: "1 - Clair / peu nuageux",
    2: "2 - Brume / nuageux",
    3: "3 - Pluie légère / neige",
    4: "4 - Forte pluie / orage"
}

col1, col2 = st.columns(2)
with col1:
    season = st.selectbox("Saison", options=list(saisons.keys()), format_func=lambda x: saisons[x], index=1)
    mnth = st.slider("Mois (1 à 12)", min_value=1, max_value=12, value=6)
    hr = st.slider("Heure de la journée (0 à 23h)", min_value=0, max_value=23, value=8)
    weekday = st.selectbox("Jour de la semaine", options=list(jours.keys()), format_func=lambda x: jours[x], index=2)
    holiday = st.selectbox("Jour férié ?", options=[0, 1], format_func=lambda x: "Oui" if x == 1 else "Non", index=0)

with col2:
    workingday = st.selectbox("Jour ouvré ?", options=[0, 1], format_func=lambda x: "Oui" if x == 1 else "Non", index=1)
    weathersit = st.selectbox("Situation météo", options=list(meteos.keys()), format_func=lambda x: meteos[x], index=0)
    temp = st.slider("Température normalisée (0 à 1)", min_value=0.0, max_value=1.0, value=0.60, step=0.01)
    hum = st.slider("Humidité normalisée (0 à 1)", min_value=0.0, max_value=1.0, value=0.55, step=0.01)
    windspeed = st.slider("Vitesse du vent normalisée (0 à 1)", min_value=0.0, max_value=1.0, value=0.15, step=0.01)

if st.button("Estimer la demande"):
    donnees_heure = pd.DataFrame([{
        "season": season,
        "mnth": mnth,
        "hr": hr,
        "weekday": weekday,
        "holiday": holiday,
        "workingday": workingday,
        "weathersit": weathersit,
        "temp": temp,
        "hum": hum,
        "windspeed": windspeed,
    }])
    prediction = max(0.0, float(modele.predict(donnees_heure)[0]))
    st.metric("Demande horaire estimée", f"{prediction:.0f} vélos / heure")
    if prediction >= 400:
        st.warning("Forte affluence prévue : prévoir un réapprovisionnement prioritaire des stations.")
    else:
        st.info("Affluence modérée ou faible : régulation standard.")

st.caption(
    "Limites : modèle Random Forest appris sur les données historiques de Washington (2011) et évalué sur 2012. "
    "Il fournit une estimation globale à l'échelle de la ville (et non par station) comme aide à la décision."
)
