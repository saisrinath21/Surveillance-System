import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def police_register():
    st.subheader("Police Registration")
    code = st.text_input("Police Code")
    password = st.text_input("Password", type="password")
    address = st.text_input("Address")
    phone = st.text_input("Phone Number")

    if st.button("Register"):
        data = {
            "code": code,
            "password": password,
            "address": address,
            "phone": phone
        }
        res = session.post(f"{BASE_URL}/police-register", json=data)
        st.write(res.json())

def police_login():
    st.subheader("Police Login")
    code = st.text_input("Police Code")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        data = {"code": code, "password": password}
        res = session.post(f"{BASE_URL}/police-login", json=data)
        if res.status_code == 200:
            st.session_state["police_logged_in"] = True
            st.session_state["police_code"] = code
            st.success("Login successful")
        else:
            st.error(res.json().get("error"))

def logout():
    res = session.get(f"{BASE_URL}/logout", cookies=session.cookies)
    if res.status_code == 200:
        st.session_state.clear()
        st.success("Logged out successfully")

def main():
    st.title("Police Surveillance Dashboard")
    if "police_logged_in" not in st.session_state:
        st.session_state["police_logged_in"] = False

    menu = ["Login", "Register", "Logout"] if st.session_state["police_logged_in"] else ["Login", "Register"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Register":
        police_register()
    elif choice == "Login":
        if not st.session_state["police_logged_in"]:
            police_login()
        else:
            st.success(f"Already logged in as {st.session_state['police_code']}")
    elif choice == "Logout":
        logout()

if __name__ == "__main__":
    main()