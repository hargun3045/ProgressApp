from pandas._config.config import options
import streamlit as st
import numpy as np
import pandas as pd
from collections import defaultdict
import trash_code
def app():
    st.title('Post Workout Details')
    st.markdown("---")
    @st.cache(persist=True, allow_output_mutation=True)
    def load_data(filename,date = False):
        if date:
            df = pd.read_csv(filename,parse_dates=['Date'])
        else:
            df = pd.read_csv(filename)
        return df
    if 'workout' not in st.session_state:
        st.session_state.workout = load_data('workout.csv', date = True)
    if 'map' not in st.session_state:
        st.session_state.map = load_data('MAP.csv')
    if 'empty_df' not in st.session_state:
        st.session_state.empty_df = pd.DataFrame(columns = ['Activity', 'Set #', 'Weight', 'Reps',  'Break Time'])
    upper = list(st.session_state.map[st.session_state.map['Body']=='Upper Body']['Exercise'].values)
    lower = list(st.session_state.map[st.session_state.map['Body']=='Lower Body']['Exercise'].values)
    date = st.date_input('Enter Date:',key = 'date1')
    body_inp = st.selectbox('Upper Body/Lower Body', ('Upper Body','Lower Body'))
    if body_inp == 'Upper Body':
        exercise = st.selectbox('Select Exercise',options = upper)
    elif body_inp=='Lower Body':
        exercise = st.selectbox('Select Exercise',options = lower)
    set = st.selectbox('Enter number of sets:',(1,2,3,4,5))

    reps_cols = defaultdict(list)
    weight_col = defaultdict(list)
    time_col = defaultdict(list)
    #tempo_col = defaultdict(list)
    reps_cols = st.columns(set)
    weight_col = st.columns(set)
    time_col = st.columns(set)
    #tempo_col = st.columns(set)
    reps, weights, break_time,tempos = [], [], [], []
    for i in range(set):
        reps.append(reps_cols[i].number_input('Reps:', min_value = 1, value = 1, step = 1, format = '%d', key = 'reps'+str(i)))
        weights.append(weight_col[i].number_input('Weight (KG):', min_value = 1, value = 1, step = 1, format = '%d', key = 'weights'+str(i)))
        break_time.append(time_col[i].number_input('Rest (seconds):', min_value = 5, value = 5, step = 5, format = '%d', key = 'time'+str(i)))
        #tempos.append(tempo_col[i].selectbox('Workout Tempo:', options=('NA','111','311','321','331'),key = 'tempo'+str(i)))
    tempo = st.selectbox('Workout Tempo:', options=('NA','111','311','321','331'),key = 'tempo')    
    type = st.selectbox('Workout type:',options = ('Conditioning', 'Endurance', 'Hypertrophy', 'Speed', 'Strength'),key='type')
    notes = st.text_input('Notes:')
    exercise_list = []
    for i in range(set):
        exercise_dict = {'Date':pd.to_datetime(date),'Activity':exercise, 'Set #':i+1, 'Reps':reps[i], 'Weight':weights[i], 'Break Time':break_time[i]}
        exercise_list.append(exercise_dict)
    add_col, confirm_col, reset_col = st.columns(3)
    add = add_col.button('ADD')
    confirm = confirm_col.button('Confirm')
    reset = reset_col.button('Reset')
    if add:
        st.session_state.empty_df = st.session_state.empty_df.append(exercise_list, ignore_index = True)
        st.session_state.empty_df = trash_code.map_workout(st.session_state.empty_df, st.session_state.map)
    if confirm:
        st.session_state.workout = st.session_state.workout.append(st.session_state.empty_df, ignore_index = True)
        st.session_state.workout.to_csv('workout.csv', index=False)
    if reset:
        st.session_state.empty_df = pd.DataFrame(columns = ['Activity', 'Set #', 'Weight', 'Reps',  'Break Time'])
    with st.expander('Today\'s workout:'):
        st.dataframe(st.session_state.empty_df)
    with st.expander('Past week workout'):
        data_len = st.selectbox('Length of data:',('Past week', '2 weeks', '4 weeks', '12 weeks', 'Full data'))
        st.dataframe(st.session_state.workout)
