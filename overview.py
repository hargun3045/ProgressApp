import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import plotly as po
import plotly.express as px
import plotly.graph_objects as go
import trash_code

def app():
    st.title('Get Fit')
    st.header('Welcome User')
    @st.cache(persist=True, allow_output_mutation=True)
    def load_data(filename,date = False,target=True):
        if date & target:
            df = pd.read_csv(filename,parse_dates=['date'])
        elif date and not target:
            df = pd.read_csv(filename,parse_dates=['Date'])
        else:
            df = pd.read_csv(filename)
        return df
    if 'workout' not in st.session_state:
        st.session_state.workout = load_data('workout.csv', date = True, target=False)
    if 'target' not in st.session_state:
        st.session_state.target = load_data('target.csv', date= True)
    if 'map' not in st.session_state:
        st.session_state.map = load_data('MAP.csv')


    #st.session_state.workout = trash_code.map_dates(st.session_state.workout,0)
    #st.session_state.target = trash_code.map_dates(st.session_state.target,1)
    st.session_state.target = trash_code.map_target_values(st.session_state.target,st.session_state.map)

    today = datetime.date.today()
    idx = (today.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
    if idx == 1:
        mon = today
    else:
        mon = today - datetime.timedelta(idx+1)
    week_start = mon
    week_end =  week_start + datetime.timedelta(6)

    muscle =['LLTB', 'Core', 'PDT', 'GHQC']
    muscle_opt = st.selectbox('Select Muscle:',options = ['All']+muscle, key = 'overview_select1')
    col1, col2 = st.columns([2,2])
    with col1:
        st.write(trash_code.get_pies(st.session_state.workout, st.session_state.target, muscle_opt))
    with col2:
        st.write(trash_code.cleanup(st.session_state.workout, select_muscle = muscle_opt))
    with st.expander('Upcoming Schedule:'):
        st.session_state.upcoming = st.session_state.target[(st.session_state.target['date']>pd.to_datetime(today))].reset_index(drop=True)
        st.session_state.upcoming = st.session_state.upcoming[st.session_state.upcoming['Date'] == st.session_state.upcoming['Date'].unique()[0]]
        st.table(st.session_state.upcoming[['Date','Day','Exercise','Set','Reps','Weight']])
    st.button('Progress',key='overview_progress')
        






































