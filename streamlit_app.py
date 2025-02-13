from scorer.models import GameLibrary
from st_score_pad import st_score_pad
import streamlit as st


# Initialize session state variables
if 'model' not in st.session_state:
    st.session_state.model = None
if 'has_game_started' not in st.session_state:
    st.session_state.has_game_started = False

if not st.session_state.model and not st.session_state.has_game_started:
    st.header('Welcome to Scorer')
    with st.form('Game Setup:', border=True):
        game_name_value = st.selectbox('Game:', sorted([g.name for g in GameLibrary]))
        play_up_to = st.number_input('Play Up To:', min_value=1)
        if st.form_submit_button('Create Game'):
            st.session_state.model = eval(f'GameLibrary.{game_name_value}({play_up_to})')
            st.rerun()

if st.session_state.model is not None and not st.session_state.has_game_started:
    st.header('Welcome to Scorer')
    with st.form('Add Players', border=True, clear_on_submit=True):
        col_a, col_b, col_c = st.columns([4, 1, 1], vertical_alignment='bottom', gap='small')
        player_name = col_a.text_input('Choose a player name: ')
        btn_add_player = col_b.form_submit_button('➕', use_container_width=True)
        if btn_add_player:
            if not len(player_name.strip()):
                st.warning('Please enter a name')
            else:
                st.session_state.model.add_player(player_name)
                st.write(f"Added players: {', '.join(st.session_state.model.player_names)}")

        btn_done_adding = col_c.form_submit_button("▶️", disabled=not bool(len(st.session_state.model.players)),
                                                   use_container_width=True)
        if btn_done_adding:
            st.session_state.has_game_started = True
            # TODO: save to db if doing a shareable game else use st session date
            st.rerun()

if st.session_state.has_game_started:
    st_score_pad()
