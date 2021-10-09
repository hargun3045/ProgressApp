import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import plotly as po
import plotly.express as px
import plotly.graph_objects as go
import time

def app():
    st.title('Full Data')
    muscle =['LLTB', 'Core', 'PDT', 'GHQC']
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

    def convert_df(df):
        return df.to_csv(index = False).encode('utf-8')
    col1, col2 = st.columns(2)
    with col1:
        with st.expander('See workout data'):
            try:
                first_date, second_date = st.date_input('Select the dates you want to view:',value = [datetime.date.today()-datetime.timedelta(1),datetime.date.today()],key = 'dive_date3')
            except ValueError:
                pass
            temp_df = st.session_state.workout[(st.session_state.workout['date']>=pd.to_datetime(first_date)) & (st.session_state.workout['date']<=pd.to_datetime(second_date))]
            st.dataframe(temp_df)
            st.download_button('Download data',data = convert_df(temp_df),file_name = 'workout.csv')
    with col2:
        with st.expander('See Target data'):
            try:
                first_date, second_date = st.date_input('Select the dates you want to view:',value =[datetime.date.today()-datetime.timedelta(1),datetime.date.today()],key = 'dive_date4')
                temp_target_df = st.session_state.target[(st.session_state.target['date']>=pd.to_datetime(first_date)) & (st.session_state.target['date']<=pd.to_datetime(second_date))]
                st.dataframe(temp_target_df)
                st.download_button('Download data',data = convert_df(temp_target_df),file_name = 'workout.csv')
            except:
                pass