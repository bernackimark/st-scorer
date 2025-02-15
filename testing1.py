"""
CREATE TABLE session_data (
    session_id TEXT PRIMARY KEY,
    data JSONB NOT NULL
);
"""

"""Example app creating a session ID, storing/retrieving to/from db"""

import streamlit as st
import psycopg2
import json
import os
import random
from urllib.parse import urlencode

# Database connection details
DB_CONFIG = {
    "dbname": "your_db_name",
    "user": "your_db_user",
    "password": "your_db_password",
    "host": "your_db_host",
    "port": "your_db_port",
}


# Establish database connection
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


# Ensure session data exists in the database
def get_or_create_session_data(session_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Try to fetch existing session data
    cur.execute("SELECT data FROM session_data WHERE session_id = %s;", (session_id,))
    row = cur.fetchone()

    if row:
        session_data = row[0]  # Retrieved JSON data
    else:
        # Initialize new session data
        session_data = {"message": "Welcome!", "count": 0}
        cur.execute("INSERT INTO session_data (session_id, data) VALUES (%s, %s::jsonb);",
                    (session_id, json.dumps(session_data)))
        conn.commit()

    cur.close()
    conn.close()
    return session_data


# Save session data to the database
def save_session_data(session_id, session_data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE session_data SET data = %s::jsonb WHERE session_id = %s;",
                (json.dumps(session_data), session_id))
    conn.commit()
    cur.close()
    conn.close()


# Generate session ID if not provided in the URL
query_params = st.query_params
session_id = query_params.get("session_id")

if not session_id:
    session_id = f"session-{random.randint(1000, 9999)}"
    query_params["session_id"] = session_id  # Update URL

# Retrieve session data from the database
session_data = get_or_create_session_data(session_id)

# Store in Streamlit session state
if "shared_data" not in st.session_state:
    st.session_state.shared_data = session_data

st.title("Shared Streamlit Session")

# Display the shareable link
base_url = os.getenv("BASE_URL", "http://localhost:8501")
shareable_link = f"{base_url}?{urlencode({'session_id': session_id})}"
st.write("Share this link to collaborate in the same session:")
st.code(shareable_link)

# Editable fields
st.session_state.shared_data["message"] = st.text_input("Message", st.session_state.shared_data.get("message", ""))
st.session_state.shared_data["count"] = st.number_input("Counter", value=st.session_state.shared_data.get("count", 0),
                                                        step=1)

# Save changes
if st.button("Save"):
    save_session_data(session_id, st.session_state.shared_data)
    st.success("Session data saved!")

