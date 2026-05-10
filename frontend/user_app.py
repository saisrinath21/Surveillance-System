import streamlit as st
import requests

import os

from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv('BASE_URL')
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
        if res.status_code == 201:
            st.success("Registration successful. Please log in.")
            st.session_state["page"] = "login"
        elif res.status_code == 409:
            st.error(res.json().get("error", "Registration failed as User already exist."))
        else:
            st.json(res.json().get("error", "Unexpected error occured during registration."))
        
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

    elif new_user_clicked:
        st.session_state["page"] = "register"
    elif forgot_clicked:
        st.session_state["page"] = "forgot password"

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

def incoming_whatsapp():
    st.subheader("Incoming WhatsApp Messages")
    cookies = st.session_state.get("cookies", {})

    col1, col2 = st.columns([1, 1])
    with col1:
        if(st.button("OK", key="ok_btn")):
            incoming_msg = "OK"

    with col2:
        if(st.button("NOT OK", key="not_ok_btn")):
            incoming_msg = "NOT OK"
    res = session.post("incoming-whatsapp?", data={"From": st.session_state.get("phone", ""), "Body": incoming_msg}, cookies=cookies)
    if res.status_code == 200:
        st.success("Got the response from the user")
    else:
        st.error("Failed to get response from the user")

def logout():
    res = session.get(f"{BASE_URL}/logout", cookies=session.cookies)
    if res.status_code == 200:
        st.session_state.clear()
        st.success("Logged out successfully")

def detection_controls():
    st.subheader("Detection Control")
    cookies = st.session_state.get("cookies", {})

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Activate Detection"):
            res = session.get(f"{BASE_URL}/activate", cookies=cookies)
            try:
                st.write(res.json())
            except Exception:
                st.error("Could not parse server response.")
                st.text(res.text)

    with col2:
        if st.button("Deactivate Detection"):
            res = session.get(f"{BASE_URL}/deactivate", cookies=cookies)
            try:
                st.write(res.json())
            except Exception:
                st.error("Could not parse server response.")
                st.text(res.text)


def view_alerts():
    """Display alert history and responses"""
    st.subheader("Alert History")
    cookies = st.session_state.get("cookies", {})
    
    try:
        res = session.get(f"{BASE_URL}/get-alerts", cookies=cookies)
        if res.status_code == 200:
            data = res.json()
            alerts = data.get('alerts', [])
            
            if not alerts:
                st.info("No alerts yet. Your detection system is monitoring.")
                return
            
            st.write(f"**Total Alerts: {len(alerts)}**")
            
            # Filter options
            col1, col2 = st.columns([1, 1])
            with col1:
                filter_status = st.selectbox(
                    "Filter by Status",
                    ["All", "Pending", "Resolved"],
                    key="alert_status_filter"
                )
            
            # Display alerts in reverse chronological order
            for idx, alert in enumerate(alerts):
                alert_id = alert.get('id', idx)
                timestamp = alert.get('timestamp', 'N/A')
                status = alert.get('status', 'Unknown')
                user_response = alert.get('user_response', 'No response')
                police_called = alert.get('police_called', 0)
                image_url = alert.get('image_url', '')
                
                # Apply filter
                if filter_status != "All" and status.lower() != filter_status.lower():
                    continue
                
                if status == 'pending':
                    status_color = "🔴"
                    status_text = "PENDING"
                elif status == 'resolved':
                    if user_response == 'OK':
                        status_color = "🟢"
                        status_text = "RESOLVED - OK"
                    elif user_response == 'NOT OK':
                        status_color = "🔴"
                        status_text = "RESOLVED - NOT OK"
                    else:
                        status_color = "🟡"
                        status_text = "RESOLVED - NO RESPONSE"
                else:
                    status_color = "⚪"
                    status_text = status.upper()
                
                # Create expandable alert card
                with st.expander(f"{status_color} Alert #{alert_id} - {timestamp}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Timestamp:** {timestamp}")
                        st.write(f"**Status:** {status_text}")
                        st.write(f"**Your Response:** {user_response if user_response else 'Waiting...'}")
                        
                        if police_called:
                            st.success("🚔 Police were notified and called")
                        else:
                            if status == 'pending':
                                st.warning("⏳ Awaiting your response on WhatsApp")
                    
                    with col2:
                        if image_url:
                            st.image(image_url, caption="Alert Frame", width=250)
                        else:
                            st.info("No image available")
                
                st.divider()
        else:
            st.error(res.json().get('error', 'Failed to fetch alerts'))
    except Exception as e:
        st.error(f"Error fetching alerts: {str(e)}")


def main():
    st.title("User Surveillance System")
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if st.session_state["logged_in"]:
        menu = ["Detection", "Alert History", "Logout"]
        choice = st.sidebar.selectbox("Navigation", menu)
        
        # Display username in sidebar
        st.sidebar.write(f"Logged in as: **{st.session_state.get('username', 'User')}**")
        
        if choice == "Detection":
            detection_controls()
        elif choice == "Alert History":
            view_alerts()
        elif choice == "Logout":
            logout()
    else:
        if st.session_state["page"] == "login":
            login()
        elif st.session_state["page"] == "register":
            register()
        elif st.session_state["page"] == "forgot password":
            forgot_password()

if __name__ == "__main__":
    main()
