import streamlit as st
import numpy as np
import pandas as pd
from collections import defaultdict
def app():
    st.title('Set Target')
    st.markdown("---")
    @st.cache(persist=True, allow_output_mutation=True)
    def load_data(filename,date = False):
        if date:
            df = pd.read_csv(filename,parse_dates=['date'])
        else:
            df = pd.read_csv(filename)
        return df
    if 'target' not in st.session_state:
        st.session_state.target = load_data('target.csv', date= True)
    if 'map' not in st.session_state:
        st.session_state.map = load_data('MAP.csv')

    col = ['Date','Day','Exercise','Set','Reps','Weight']
    date = st.date_input('Enter Date:', key = 'target_date1')
    upper = list(st.session_state.map[st.session_state.map['Body']=='Upper Body']['Exercise'].values)
    lower = list(st.session_state.map[st.session_state.map['Body']=='Lower Body']['Exercise'].values)
    body_inp = st.selectbox('Upper Body/Lower Body', ('Upper Body','Lower Body'))
    if body_inp == 'Upper Body':
        exercise = st.selectbox('Select Exercise',options = upper, key = 'target_inp1')
    elif body_inp=='Lower Body':
        exercise = st.selectbox('Select Exercise',options = lower, key = 'target_inp2')
    set = st.selectbox('Enter number of sets:',(1,2,3,4,5),key='target_inp3')


    reps_col = defaultdict(list)
    weights_col = defaultdict(list)
    reps_col= st.columns(set)
    weights_col = st.columns(set)
    reps, weights = [], []
    for i in range(set):
        reps.append(reps_col[i].number_input('Enter the reps:', min_value = 1, value = 1, step = 1, format = '%d', key = 'target_reps'+str(i)))
        weights.append(weights_col[i].number_input('Enter the weights:', min_value = 1, value = 1, step = 1, format = '%d', key = 'target_weights'+str(i)))
    exercise_list = []
    for i in range(set):
        exercise_dict = {'date':pd.to_datetime(date),'Date':date.strftime('%d-%b-%Y'),'Exercise':exercise, 'Set':i+1, 'Reps':reps[i], 'Weight':weights[i]}
        exercise_list.append(exercise_dict)



    add = st.button('ADD')
    if add:
        st.session_state.target = st.session_state.target.append(exercise_list, ignore_index = True)
        st.session_state.target['Day'] = st.session_state.target['date'].dt.day_name()
    st.markdown('---')

    with st.expander('See schedule'):
        col1,col2,col3 = st.columns([1,2,2])
        col1.markdown('Delete by Day:')
        select_date = col2.date_input('Select the date to delete:',value = st.session_state.target.iloc[0]['date'].date(),key = 'target_date2')
        select_date = select_date.strftime('%Y-%m-%d')
        exercise_option = list(st.session_state.target[st.session_state.target['date']==select_date]['Exercise'].unique())
        exercise_option.append('All')
        sel_exercise_option = col3.selectbox('Select Exercise to delete',options =exercise_option,key = 'target_inp4')
        delete_day = col1.button('Delete',key='day')
        if delete_day:
            if sel_exercise_option == "All":
                st.session_state.target = st.session_state.target.drop(st.session_state.target[st.session_state.target['date']==select_date].index).reset_index(drop=True)
            else:
                st.session_state.target = st.session_state.target.drop(st.session_state.target[(st.session_state.target['date']==select_date) & (st.session_state.target['Exercise']==sel_exercise_option)].index).reset_index(drop=True)
        col4, col5= st.columns([1,4])
        col4.markdown('Delete by week')
        first_date, second_date = col5.date_input('Select the week you want to delete:',value = [st.session_state.target.iloc[0]['date'].date(),st.session_state.target.iloc[1]['date'].date()],key = 'target_date3')
        first_date = first_date.strftime('%Y-%m-%d')
        second_date = second_date.strftime('%Y-%m-%d')
        delete_week = col4.button('Delete',key = 'week')
        if delete_week:
            st.session_state.target = st.session_state.target.drop(st.session_state.target[(st.session_state.target['date']>=first_date) & (st.session_state.target['date']<=second_date)].index).reset_index(drop=True)
        st.write('Schedule for this week')
        st.table(st.session_state.target[col])
    _,_,col2,_,_ = st.columns(5)
    confirm = col2.button('Confirm changes')
    if confirm:
        st.session_state.target.to_csv('target.csv')