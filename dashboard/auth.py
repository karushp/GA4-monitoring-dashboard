import os
import secrets

import streamlit as st
from dotenv import load_dotenv

from dashboard.settings import APP_ROOT, PAGE_TITLE

_ENV_FILE = APP_ROOT / ".env"
_SESSION_AUTHENTICATED = "authenticated"

load_dotenv(_ENV_FILE, override=False)


def _env_credential(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def expected_username() -> str | None:
    return _env_credential("DASHBOARD_USERNAME", "username")


def expected_password() -> str | None:
    return _env_credential("DASHBOARD_PASSWORD", "password")


def credentials_configured() -> bool:
    return bool(expected_username() and expected_password())


def verify_credentials(username: str, password: str) -> bool:
    expected_user = expected_username()
    expected_pass = expected_password()
    if not expected_user or not expected_pass:
        return False
    user_ok = secrets.compare_digest(username, expected_user)
    pass_ok = secrets.compare_digest(password, expected_pass)
    return user_ok and pass_ok


def is_authenticated() -> bool:
    return bool(st.session_state.get(_SESSION_AUTHENTICATED))


def render_login_page() -> None:
    st.title(PAGE_TITLE)

    _, center, _ = st.columns([1, 1.4, 1], gap="large")
    with center:
        st.subheader("Sign in")

        if not credentials_configured():
            st.error(
                "Login is not configured. Add `username` and `password` to a `.env` file "
                "in the project root (see `.env.example`)."
            )
            return

        with st.form("login", clear_on_submit=False):
            username = st.text_input("Username", autocomplete="username")
            password = st.text_input(
                "Password", type="password", autocomplete="current-password"
            )
            submitted = st.form_submit_button(
                "Sign in", type="primary", use_container_width=True
            )

        if submitted:
            if verify_credentials(username, password):
                st.session_state[_SESSION_AUTHENTICATED] = True
                st.rerun()
            else:
                st.error("Invalid username or password.")


def render_logout_button() -> None:
    if st.button("Sign out", use_container_width=True):
        st.session_state.pop(_SESSION_AUTHENTICATED, None)
        st.rerun()


def ensure_authenticated() -> bool:
    if is_authenticated():
        return True
    render_login_page()
    return False
