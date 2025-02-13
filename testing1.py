import random

from config import ADJECTIVES, ANIMALS, BASE_URL
import streamlit as st

st.session_state['random_animal'] = None

# Retrieve existing session_id from the URL, or generate a new one
query_params = st.query_params
session_id = query_params.get("session_id", f'{random.choice(ADJECTIVES)}-{random.choice(ANIMALS)}')

# Store session_id in session state
st.session_state.session_id = session_id

# Update the URL dynamically with the session ID
st.query_params["session_id"] = session_id

# Construct the shareable link
shareable_link = f"{BASE_URL}/?session_id={session_id}"

# Display the link
st.write("Share this session link:")
st.code(shareable_link)

if not st.session_state.random_animal:
    random_animal = random.choice(ANIMALS)
    st.session_state.random_animal = random_animal

st.subheader(f'A random animal: {random.choice(ANIMALS)}')