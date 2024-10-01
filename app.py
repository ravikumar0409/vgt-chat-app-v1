import streamlit as st
import requests
from fastapi import FastAPI, Depends, HTTPException, Request
from api_endpoints_config import *

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    /* Hide the Streamlit menu */
    .stApp > header {
        visibility: hidden;
    }
    /* Hide the deploy button */
    .stApp > footer {
        visibility: hidden;
    }
    .footer {
        position: fixed;
        left: 0;
        z-index: 100;
        bottom: 0;
        width: 100%;
        text-align: right;
        padding: 10px;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_user_access_token(username, password):
    if username and password:
        return st.session_state.get("access_token")
    return None


def authenticate_user(username, password):
    if username and password:
        form_data = {
            "username": username,
            "password": password,
        }
        try:
            response = requests.post(LOGIN_URL, data=form_data)
            if response.status_code == 200:
                access_token = response.json().get("access_token")
                st.session_state["access_token"] = access_token
                return True
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Authentication failed"),
                )
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))
    return False


def get_response(prompt, chat_mode, username, password):
    access_token = get_user_access_token(username, password)
    if access_token:
        params = {
            'prompt': prompt,
        }
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(CHAT_URL, headers=headers, params=params)
        return {"response": response}
    return None


with st.sidebar:
    st.image("vgt_logo.svg", width=300)
    st.title("VGT Multi Mode ChatBot Application")
    st.markdown("<br/>", unsafe_allow_html=True)

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        username = st.text_input(
            "Account Username", key="account_username", type="default"
        )
        password = st.text_input(
            "Account Password", key="account_password", type="password"
        )
        if st.button("Submit"):
            if authenticate_user(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["password"] = password
                st.success("Successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    else:
        username = st.session_state["username"]
        password = st.session_state["password"]
        st.markdown(f"Hello, {username}! 👋")
        if st.button("Log Out"):
            st.session_state["authenticated"] = False
            st.session_state.pop("username", None)
            st.success("You have logged out.")
            st.rerun()


if "authenticated" in st.session_state and st.session_state["authenticated"]:

    chat_mode = st.selectbox(
        "Select Chat Mode",
        ["Normal Conversation", "Document Q&A", "GIS Analytics"],
        key="chat_mode",
    )

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = get_response(prompt, chat_mode, username, password)
        if response:
            msg = response.get("response", "chatbot unable to answer the query asked!")
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)
        else:
            st.info("error occured!")
else:
    st.info("Please enter your username and password to proceed.")


st.markdown(
    '<div class="footer"><a href="https://vasundharaa.in">Developed by Vasundharaa Geo Technologies Pvt. Ltd.</a></div>',
    unsafe_allow_html=True,
)
