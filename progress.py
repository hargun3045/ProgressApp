import streamlit as st
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
import plotly as po
import plotly.express as px
import plotly.graph_objects as go
import helper
def app():
    muscle =['LLTB', 'Core', 'PDT', 'GHQC']
    st.title("Progress Report")
    @st.cache(persist=True, allow_output_mutation=True)
    def load_data(filename,date = False):
        if date:
            df = pd.read_csv(filename,parse_dates=['date'])
        else:
            df = pd.read_csv(filename)
        return df
    if 'workout' not in st.session_state:
        st.session_state.workout = load_data('data/workout.csv', date = True)
    if 'target' not in st.session_state:
        st.session_state.target = load_data('data/target.csv', date= True)
    if 'mask' not in st.session_state:
        st.session_state.mask = 'All'
    if 'duration' not in st.session_state:
        st.session_state.duration = 'Total Sessions'
    muscle_opt = st.selectbox('Select Muscle:',options = ['All']+muscle, key = 'overview_select1')
    top_col = st.columns([1,1,1,1,5])
    two_week = top_col[0].button('2 weeks', key = 'overview_2week')
    four_week = top_col[1].button('4 weeks', key = 'overview_4week')
    eight_week = top_col[2].button('8 weeks', key = 'overview_8week')
    full_week = top_col[3].button('Full data', key = 'overview_full')

    if two_week:
        st.session_state.mask = 14
        st.session_state.duration = '2 weeks'
    elif four_week:
        st.session_state.mask = 4*7
        st.session_state.duration = '4 weeks'
    elif eight_week:
        st.session_state.mask = 8*7
        st.session_state.duration = '8 weeks'
    elif full_week:
        st.session_state.duration = 'Total sessions'
        st.session_state.mask = 'All'
    if st.session_state.mask == 'All':
        temp_df = st.session_state.workout
        target_temp_df = st.session_state.target
    else:
        temp_df = helper.create_mask(st.session_state.workout, st.session_state.mask, 'date')
        target_temp_df = helper.create_mask(st.session_state.target, st.session_state.mask, 'date')
    col1, col2 = st.columns(2)
    fig1 = helper.stack_bar(temp_df)
    fig0 = helper.line_chart(temp_df, target_temp_df)
    with col1:
        st.write('Target vs Completed')
        st.write(fig0)
    with col2:
        st.write('Workout Type Distribution:')
        st.write(fig1)
    fig3 = helper.volume_chart(st.session_state.workout)
    st.write('Data at a glance')
    st.write(fig3)
    fig4 = helper.day_plot(st.session_state.workout)
    st.write(fig4)
    deep_dive = st.button('See Data', key = 'progress_data')