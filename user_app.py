import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def register():
    st.subheader("User Registration")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    address = st.text_input("Address")
    phone = st.text_input("Phone Number")

    if st.button("Register"):
        data = {
            "username": username,
            "password": password,
            "address": address,
            "phone": phone
        }
        res = session.post(f"{BASE_URL}/register", json=data)
        st.write(res.json())

def login():
    if st.button("New User"):
        register()
        return

    st.subheader("User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        data = {"username": username, "password": password}
        res = session.post(f"{BASE_URL}/login", json=data)

        if res.status_code == 200:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["cookies"] = session.cookies.get_dict()
            st.success("Login successful")
        else:
            st.error(res.json().get("error"))


def logout():
    res = session.get(f"{BASE_URL}/logout", cookies=session.cookies)
    if res.status_code == 200:
        st.session_state.clear()
        st.success("Logged out successfully")

def detection_controls():
    st.subheader("Detection Control")
    cookies = st.session_state.get("cookies", {})

    if st.button("Activate Detection"):
        res = session.get(f"{BASE_URL}/activate", cookies=cookies)
        try:
            st.write(res.json())
        except Exception:
            st.error("Could not parse server response.")
            st.text(res.text)

    if st.button("Deactivate Detection"):
        res = session.get(f"{BASE_URL}/deactivate", cookies=cookies)
        try:
            st.write(res.json())
        except Exception:
            st.error("Could not parse server response.")
            st.text(res.text)


def main():
    st.title("User Surveillance System")
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    menu = ["Login", "Detection", "Logout"] if st.session_state["logged_in"] else ["Login"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Login":
        if not st.session_state["logged_in"]:
            login()
        else:
            st.success(f"Already logged in as {st.session_state['username']}")
    elif choice == "Detection":
        if st.session_state["logged_in"]:
            detection_controls()
        else:
            st.warning("Please log in first.")
    elif choice == "Logout":
        if st.session_state["logged_in"]:
            logout()

if __name__ == "__main__":
    main()