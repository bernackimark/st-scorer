from copy import deepcopy
import numpy as np
import streamlit as st
import pandas as pd

@st.dialog('Add Player')
def add_player() -> None:
    player_name = st.text_input('Name:')
    if st.button("Add"):
        if not len(player_name.strip()):
            st.warning('Please enter a name')
            return
        try:
            st.session_state.model.add_player(player_name)
            st.rerun()
        except ValueError as e:  # should throw if someone in the game already has that name
            st.error(e)

@st.dialog('Remove Player')
def remove_player() -> None:
    player_name = st.selectbox('Remove', [p.name for p in st.session_state.model.players], label_visibility="hidden")
    if st.button("Remove"):
        try:
            st.session_state.model.remove_player(player_name)
            st.rerun()
        except ValueError as e:  # should throw if that name isn't in the model
            st.error(e)

def st_score_pad():
    # TODO: pull player_ledger_dict from db
    print(f'{st.session_state.model.players = }')
    print(f'{st.session_state.model.player_ledger_dict = }')

    col_a, col_b, col_c = st.columns([4, 1, 1], vertical_alignment='bottom')
    col_a.header(f'{st.session_state.model.name} up to {st.session_state.model.game_over_score}')
    if col_b.button('➕'):
        add_player()
    if col_c.button('➖'):
        remove_player()

    # Allow users to edit and add rows. cell input must be integers or None
    edited_data = st.data_editor(st.session_state.model.player_ledger_dict,
                                 hide_index=True, key="edited_data", num_rows="dynamic",  # Allow adding new rows
                                 use_container_width=True,
                                 column_config={col: st.column_config.NumberColumn(col, step=1, default=None)
                                                for col in st.session_state.model.player_ledger_dict})

    # when a new row is added, data_editor sneakily sets the new values as np.nan instead of None
    for name, ledger in edited_data.items():
        ledger = [None if isinstance(score, float) and np.isnan(score) else score for score in ledger]
        edited_data[name] = ledger

    # if the data has been updated, add/remove any new/removed players & update ledgers
    if edited_data != st.session_state.model.player_ledger_dict:
        # print('xxx', edited_data)
        [st.session_state.model.add_player(name) for name in edited_data if name not in st.session_state.model.player_names]
        [st.session_state.model.remove_player(name) for name in st.session_state.model.player_names if name not in edited_data]
        for p in st.session_state.model.players:
            p.ledger = edited_data.get(p.name)
        # print('yyy', st.session_state.model.players)
        # TODO: write player_ledger_dict to db
        st.rerun()  # Refresh UI to maintain read-only total row

    # Create a layout for displaying progress bars in columns
    progress_columns = st.columns(len(st.session_state.model.players))

    # Show progress bars for each column, st.progress() value must be 0 <= value <= 100
    for i, (player_name, total_score) in enumerate(st.session_state.model.player_current_scores.items()):
        progress_percent = total_score / st.session_state.model.game_over_score
        progress_percent_clamped = 0 if progress_percent < 0 else 1 if progress_percent > 1 else progress_percent
        progress = int(progress_percent_clamped * 100)
        with progress_columns[i]:
            st.write(f"{player_name} Total: {int(total_score)}")
            st.progress(progress)  # Display the progress bar

    if st.session_state.model.is_game_over:
        winner_name, winner_score = st.session_state.model.winner_name_and_score
        st.write(f'{winner_name} won with {int(winner_score)} {"point" if winner_score == 1 else "points"}')
        st.balloons()
