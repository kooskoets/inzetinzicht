import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="InzetInzicht", layout="wide")

API_URL = "http://backend:8000"  # in Docker netwerk
if "token" not in st.session_state:
    st.session_state["token"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "name" not in st.session_state:
    st.session_state["name"] = None

def login():
    with st.form("login_form"):
        st.write("Log in")
        username = st.text_input("Gebruikersnaam")
        password = st.text_input("Wachtwoord", type="password")
        submitted = st.form_submit_button("Inloggen")
        if submitted:
            try:
                resp = requests.post(f"{API_URL}/login", json={"username":username,"password":password}, timeout=5)
                resp.raise_for_status()
                data = resp.json()
                st.session_state["token"] = data["token"]
                st.session_state["role"] = data["role"]
                st.session_state["name"] = data["name"]
                st.success(f"Ingelogd als {data['name']}")
                st.experimental_rerun()
            except Exception as e:
                st.error("Inloggen mislukt")

if st.session_state["token"] is None:
    st.title("InzetInzicht - Inloggen")
    login()
    st.stop()

st.sidebar.write(f"👤 {st.session_state['name']} ({st.session_state['role']})")
if st.button("Uitloggen"):
    st.session_state["token"] = None
    st.experimental_rerun()

# dashboard
st.title("InzetInzicht - Dashboard")
try:
    tasks = requests.get(f"{API_URL}/tasks", params={"token": st.session_state["token"]}, timeout=5).json()
    df = pd.DataFrame(tasks)
    if df.empty:
        st.info("Geen taken gevonden.")
    else:
        semesters = ["S1","S2"]
        semester = st.selectbox("Semester", ["Alle"] + semesters)
        if semester != "Alle":
            df = df[df["semester"] == semester]
        st.dataframe(df, use_container_width=True)
        st.write("Totaal uren:", df["uren"].sum())
except Exception as e:
    st.error("Kan taken niet ophalen. Controleer of backend draait.")