import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def register():
    st.subheader("User Registration")
    username = st.text_input("Username", key="reg_username")
    password = st.text_input("Password", type="password", key="reg_password")
    address = st.text_input("Address", key="reg_address")
    phone = st.text_input("Phone Number", key="reg_phone")

    if st.button("Register"):
        data = {
            "username": username,
            "password": password,
            "address": address,
            "phone": phone
        }
        res = session.post(f"{BASE_URL}/register", json=data)
        st.write(res.json())
    if st.button("Back to Login", key="reg_back"):
        st.session_state["page"] = "login"

def login():
    st.subheader("User Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns([1, 1])
    login_clicked = col1.button("Login", key="login_btn")
    new_user_clicked = col2.button("New User", key="new_user_btn")
    forgot_clicked = st.button("Forgot Password?", key="forgot_btn")

    if login_clicked:
        data = {"username": username, "password": password}
        res = session.post(f"{BASE_URL}/login", json=data)

        if res.status_code == 200:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["cookies"] = session.cookies.get_dict()
            st.success("Login successful")
        else:
            st.error(res.json().get("error"))

    if new_user_clicked:
        st.session_state["page"] = "register"
    if forgot_clicked:
        st.session_state["page"] = "forgot"

def forgot_password():
    st.subheader("Forgot Password")
    fp_username = st.text_input("Enter your username", key="fp_username")
    fp_phone = st.text_input("Enter your registered phone number", key="fp_phone")
    new_password = st.text_input("Enter new password", type="password", key="fp_new_password")
    if st.button("Reset Password", key="fp_reset"):
        fp_data = {"username": fp_username, "phone": fp_phone, "new_password": new_password}
        res = session.post(f"{BASE_URL}/forgot-password", json=fp_data)
        if res.status_code == 200:
            st.success("Password reset successful. Please log in with your new password.")
        else:
            st.error(res.json().get("error", "Password reset failed."))
    if st.button("Back to Login", key="fp_back"):
        st.session_state["page"] = "login"


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
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if st.session_state["logged_in"]:
        menu = ["Detection", "Logout"]
        choice = st.sidebar.selectbox("Navigation", menu)
        if choice == "Detection":
            detection_controls()
        elif choice == "Logout":
            logout()
    else:
        if st.session_state["page"] == "login":
            login()
        elif st.session_state["page"] == "register":
            register()
        elif st.session_state["page"] == "forgot":
            forgot_password()

if __name__ == "__main__":
    main()
