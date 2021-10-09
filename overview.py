import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import plotly as po
import plotly.express as px
import plotly.graph_objects as go
from streamlit.state.session_state import SessionState
import helper
import target

def app():
    s = f"""<style>@import url('http://fonts.cdnfonts.com/css/ea-font');
    <style>"""
    st.markdown(s, unsafe_allow_html=True)
    st.title('Overview')    
    # text = '<h1 style = "font-family: \'EA Font v1.5 by Ghettoshark\'; margin-bottom:0; margin-top:0;color: #EC5A53; font-size: 40px;">HINDSIGHT</p>'
    # st.markdown(text,unsafe_allow_html=True)
    # text = '<h1 style = "font-family: \'EA Font v1.5 by Ghettoshark\'; margin-bottom:0; margin-top:0,color: #181A18; font-size: 20px;">User Analytics</p>'
    # st.markdown(text,unsafe_allow_html=True)
    # st.title('Hindsight')
    # st.header('Welcome User')
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
    if 'map' not in st.session_state:
        st.session_state.map = load_data('data/MAP.csv')
    if 'mask' not in st.session_state:
        st.session_state.mask = 'All'
    if 'duration' not in st.session_state:
        st.session_state.duration = 'Total Sessions'

    # st.session_state.workout = trash_code.map_dates(st.session_state.workout,0)
    # st.session_state.target = trash_code.map_dates(st.session_state.target,1)


    today = datetime.date.today()
    idx = (today.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
    if idx == 1:
        mon = today
    else:
        mon = today - datetime.timedelta(idx+1)
    week_start = mon
    week_end =  week_start + datetime.timedelta(6)
    remain_df = st.session_state.target[(st.session_state.target['date']>pd.to_datetime(today)) & (st.session_state.target['date']<=pd.to_datetime(week_end))]
    week_target_df = st.session_state.target[(st.session_state.target['date']>=pd.to_datetime(mon)) & (st.session_state.target['date']<=pd.to_datetime(week_end))]
    week_complete_df = st.session_state.workout[(st.session_state.workout['date']>pd.to_datetime(mon)) & (st.session_state.workout['date']<=pd.to_datetime(week_end))]

    muscle =['LLTB', 'Core', 'PDT', 'GHQC']
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
        # breakpoint()
        temp_df = st.session_state.workout
    else:
        temp_df = helper.create_mask(st.session_state.workout, st.session_state.mask, 'date')
    primaryColor = st.get_option("theme.primaryColor")

    num_sessions = temp_df['Date'].nunique()
    text = '<p style = "font-family: \'EA Font v1.5 by Ghettoshark\'; text-align:center; margin-bottom:0; color: Grey; font-size: 20px;">Sessions Completed</p>'
    top_col[4].markdown(text, unsafe_allow_html=True)
    num = '<p style = "font-family: \'EA Font v1.5 by Ghettoshark\'; text-align:center; margin-top:0; margin-bottom:0;color: Black; font-size: 50px;">'+str(num_sessions)+'</p>'
    

    top_col[4].markdown(num, unsafe_allow_html=True)
    col1,col2 = st.columns([3,4])
    with col1:
        st.image('anatomy1.jpg')
    with col2:
        st.write(helper.type_summary(temp_df, select_muscle = muscle_opt))
    col3, col4 = st.columns([3.5,4]) 
    with col3:
        st.write(helper.get_pies(st.session_state.workout, st.session_state.target, muscle_opt))
    remaining_session = remain_df['date'].nunique()
    if muscle_opt=='All':
        target_volume = week_target_df['Volume'].sum()
        complete_volume = week_complete_df['Volume'].sum()
    else:
        target_volume = week_target_df[muscle_opt].sum()
        complete_volume = week_complete_df[muscle_opt].sum()
    with col4:
        
        st.subheader('Targets')
        st.info('Sessions Remaining (current week) : '+str(remaining_session))
        st.info('Target Volume : '+ str(int(target_volume)))
        st.info('Completed Volume : '+ str(int(complete_volume)))

    with st.expander('Upcoming Schedule:'):
        try:
            st.session_state.upcoming = st.session_state.target[(st.session_state.target['date']>pd.to_datetime(today))].reset_index(drop=True)
            st.session_state.upcoming = st.session_state.upcoming[st.session_state.upcoming['Date'] == st.session_state.upcoming['Date'].unique()[0]]
            st.table(st.session_state.upcoming[['Date','Day','Exercise','Set','Reps','Weight']])
        except IndexError:
            st.write('You have no upcoming session scheduled. Click below to set schedule')
            set_s = st.button('Set Schedule')
    if set_s:
        target.app()
    






































