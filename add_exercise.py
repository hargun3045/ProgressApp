import streamlit as st
import numpy as np
import pandas as pd
from collections import defaultdict

pd.set_option('max_colwidth', 50)

def app():
    st.title('Add New Exercise')
    st.markdown("---")
    @st.cache(persist=True, allow_output_mutation=True)
    def load_data(filename,date = False):
        if date:
            df = pd.read_csv(filename,parse_dates=['date'])
        else:
            df = pd.read_csv(filename)
        return df
    if 'map' not in st.session_state:
        st.session_state.map = load_data('data/MAP.csv')
    exercise_name = st.text_input("Exercise name:")
    body_inp = st.selectbox('Upper Body/Lower Body', ('Upper Body','Lower Body'))
    st.markdown('### Muscle group contribution')
    col1, col2, col3, col4 = st.columns(4)
    lltb = col1.number_input('LLTB:',min_value = 0.0, value = 0.0, max_value = 1.0,  step = 0.05, format = '%f',help = 'Lats | Lower Back | Trapezius | Biceps')
    pdt = col2.number_input('PDT:',min_value = 0.0, value = 0.0, max_value = 1.0,  step = 0.05, format = '%f',help = 'Pectorals | Deltoids| Triceps')
    core = col3.number_input('Core:',min_value = 0.0, value = 0.0, max_value = 1.0,  step = 0.05, format = '%f',help = 'Core')
    ghqc = col4.number_input('GHQC:',min_value = 0.0, value = 0.0, max_value = 1.0,  step = 0.05, format = '%f',help = 'Gluteus | Hamstring | Quadriceps | Calves')
    exercise_detail = {'Exercise':exercise_name, 'Body':body_inp, 'LLTB':lltb,'Core':core,'PDT':pdt,'GHQC':ghqc}
    add_col,_,_,_, confirm_col = st.columns(5)
    add = add_col.button('ADD')
    confirm = confirm_col.button('Confirm')
    if add:
        st.session_state.map = st.session_state.map.append(exercise_detail, ignore_index = True)
    if confirm:
        st.session_state.map.to_csv('data/MAP.csv')
    with st.expander('Exercise details:'):
        delete_col1, delete_col2 = st.columns(2)
        delete_col1.markdown('Delete Exercise')
        delete_exercise = delete_col1.button('Delete')
        exercise_to_be_del  = delete_col2.selectbox('Select Exercise:',options = list(st.session_state.map['Exercise'].unique())) 
        if delete_exercise:
            st.session_state.map = st.session_state.map.drop(st.session_state.map[st.session_state.map['Exercise']==exercise_to_be_del].index).reset_index(drop=True)
        st.table(st.session_state.map)