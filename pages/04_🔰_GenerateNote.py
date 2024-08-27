import streamlit as st
from modules.auth import get_auth
from datetime import date


if 'notes' not in st.session_state:
    st.session_state.notes = []


def save_notes_cb():
    if st.session_state.ta_notes_k == '':
        return

    st.session_state.notes.append(
        {
            'Notes': st.session_state.ta_notes_k,
            'Date': date.today()
        }
    )

st.image("./images/QSlogo.png", width = 300)
st.title('Notes')

st.markdown('''Regularly jot down essential points to avoid forgetting
    crucial information. The saved notes are temporary and will vanish
    after a page refresh. But you can download it as a csv file.
''')

st.markdown('### Notes input')
try:
    with st.form('notes', clear_on_submit=True):
        st.text_area('Notes', key='ta_notes_k')
        st.form_submit_button('Save', on_click=save_notes_cb)
except st.errors.StreamlitAPIException:
    get_auth()

else:
    st.markdown('### Notes history')
    st.dataframe(
        st.session_state.notes,
        use_container_width=True
    )