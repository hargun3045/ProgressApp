import streamlit as st
import numpy as np
import pandas as pd
from collections import defaultdict
import datetime
from streamlit.errors import StreamlitAPIException
import helper
import time
def app():
    st.title('Set Target')
    st.markdown("---")

    muscle = ['LLTB', 'Core', 'PDT', 'GHQC']
    @st.cache(persist=True, allow_output_mutation=True)
    def load_data(filename,date = False):
        if date:
            df = pd.read_csv(filename,parse_dates=['date'])
        else:
            df = pd.read_csv(filename)
        return df
    if 'target' not in st.session_state:
        st.session_state.target = load_data('data/target.csv', date= True)
    if 'map' not in st.session_state:
        st.session_state.map = load_data('data/MAP.csv')
    if 'target_display' not in st.session_state:
        st.session_state.target_display = load_data('data/display_target.csv', date = True)
    st.session_state.target_display[['Set','Weight','Reps']] = st.session_state.target_display[['Set','Weight','Reps']].astype(str)

    st.session_state.dict1 = st.session_state.map.to_dict()
    st.session_state.map_dict = [dict(zip(st.session_state.dict1['Exercise'].values(),st.session_state.dict1[i].values())) for i in muscle]
    st.session_state.map_dict = dict(zip(muscle, st.session_state.map_dict))


    col = ['Date','Day','Exercise','Set','Reps','Weight']
    date = st.date_input('Enter Date:', key = 'target_date1')
    upper = list(st.session_state.map[st.session_state.map['Body']=='Upper Body']['Exercise'].values)
    lower = list(st.session_state.map[st.session_state.map['Body']=='Lower Body']['Exercise'].values)
    exc_type = st.selectbox('Exercise Type:',options = ('Standalone','Sequence'),key ='target_type')

    if exc_type == 'Standalone':
        body_inp = st.selectbox('Upper Body/Lower Body', ('Upper Body','Lower Body'),key = 'target_body_type')
        if body_inp == 'Upper Body':
            exercise = st.selectbox('Select Exercise',options = upper, key = 'post_work_type_1')
        elif body_inp=='Lower Body':
            exercise = st.selectbox('Select Exercise',options = lower, key = 'post_work_type_2')
        sets = st.selectbox('Enter number of sets:',(1,2,3,4,5), key = 'post_workout_set')

        reps_cols = defaultdict(list)
        weight_col = defaultdict(list)
        reps_cols = st.columns(sets)
        weight_col = st.columns(sets)
        reps, weights = [], []
        for i in range(sets):
            reps.append(reps_cols[i].number_input('Reps:', min_value = 1, value = 1, step = 1, format = '%d', key = 'reps'+str(i)))
            weights.append(weight_col[i].number_input('Weight (KG):', min_value = 1, value = 1, step = 1, format = '%d', key = 'weights'+str(i)))
        volume = np.multiply(reps, weights)

    elif exc_type == 'Sequence':
        upper_col, lower_col = st.columns(2)
        with upper_col:
            upper_bods = st.multiselect('Upper Body', options = upper, key = 'target_upper')
        with lower_col:
            lower_bods = st.multiselect('Lower Body', options = lower, key = 'target_lower')
        sets = st.selectbox('Enter number of sets:',(1,2,3,4,5), key = 'target_set')
        reps_col = defaultdict(list)
        weight_col = defaultdict(list)
        reps, weights = [], []
        bods = upper_bods+lower_bods
        try:
            reps_cols = st.columns(len(bods))
            weight_col = st.columns(len(bods)) 
        except StreamlitAPIException:
            reps_cols = st.columns(1)
            weight_col = st.columns(1)
        for i, j in enumerate(bods):
            reps.append(reps_cols[i].number_input('Reps( '+j+' ):' ,min_value = 1, value = 1, step = 1, format = '%d', key = 'reps'+str(i)))
            weights.append(weight_col[i].number_input('Weight(KG):', min_value = 1, value = 1, step = 1, format = '%d', key = 'weights'+str(i)))
        volume = np.multiply(reps, weights)
        
    display_list = []
    exercise_list = []
    for i in range(sets):
        if exc_type == 'Standalone':
            exercise_dict = {'date':pd.to_datetime(date),'Date':date.strftime('%d-%b-%Y'),'Exercise':exercise, 'Set':i+1, 'Reps':reps[i], 'Weight':weights[i], 'Volume':volume[i], 'LLTB':st.session_state.map_dict['LLTB'][exercise]*volume[i], 'PDT':st.session_state.map_dict['PDT'][exercise]*volume[i], 'Core':st.session_state.map_dict['Core'][exercise]*volume[i], 'GHQC':st.session_state.map_dict['GHQC'][exercise]*volume[i]}
            display_dict  = {'date':pd.to_datetime(date),'Date':date.strftime('%d-%b-%Y'),'Day':pd.to_datetime(date).day_name(),'Exercise':exercise, 'Set':str(i+1), 'Reps':str(reps[i]), 'Weight':str(weights[i]), 'Volume':volume[i], 'LLTB':st.session_state.map_dict['LLTB'][exercise]*volume[i], 'PDT':st.session_state.map_dict['PDT'][exercise]*volume[i], 'Core':st.session_state.map_dict['Core'][exercise]*volume[i], 'GHQC':st.session_state.map_dict['GHQC'][exercise]*volume[i]}
            display_list.append(display_dict) 
            exercise_list.append(exercise_dict)
        elif exc_type == 'Sequence':
            exercise_dict = {'date':pd.to_datetime(date),'Date':date.strftime('%d-%b-%Y'),'Day':pd.to_datetime(date).day_name(),'Exercise':','.join(bods), 'Set':i+1, 'Reps':reps, 'Weight':weights,'Volume':volume, 'LLTB': sum(np.multiply(volume,[st.session_state.map_dict['LLTB'][i] for i in bods])),'PDT': sum(np.multiply(volume,[st.session_state.map_dict['PDT'][i] for i in bods])), 'Core': sum(np.multiply(volume,[st.session_state.map_dict['Core'][i] for i in bods])),'GHQC': sum(np.multiply(volume,[st.session_state.map_dict['GHQC'][i] for i in bods]))}
            display_dict = {'date':pd.to_datetime(date),'Date':date.strftime('%d-%b-%Y'),'Day':pd.to_datetime(date).day_name(),'Exercise':','.join(bods), 'Set':str(i+1), 'Reps':','.join([ str(i) for i in reps]), 'Weight':','.join([str(i) for i in weights]), 'Volume':volume, 'LLTB': sum(np.multiply(volume,[st.session_state.map_dict['LLTB'][i] for i in bods])),'PDT': sum(np.multiply(volume,[st.session_state.map_dict['PDT'][i] for i in bods])), 'Core': sum(np.multiply(volume,[st.session_state.map_dict['Core'][i] for i in bods])),'GHQC': sum(np.multiply(volume,[st.session_state.map_dict['GHQC'][i] for i in bods]))}
            display_dict['Volume'] = sum(volume)
            exercise_dict['Volume'] = sum(volume)
            exercise_list.append(exercise_dict)
            display_list.append(display_dict)


    add_col, _ , _ , undo_col = st.columns([1,2,2,1])
    add = add_col.button('ADD')
    undo = undo_col.button('Undo')
    if add:
        st.session_state.target_copy = st.session_state.target.copy(deep=True)
        st.session_state.display_copy = st.session_state.target_display.copy(deep=True)
        st.session_state.target = st.session_state.target.append(exercise_list, ignore_index = True)
        st.session_state.target_display = st.session_state.target_display.append(display_list, ignore_index=True)
    if undo:
        st.session_state.target = st.session_state.target_copy
        st.session_state.target_display = st.session_state.display_copy

    st.markdown('---')


    with st.expander('See schedule'):
        col1,col2,col3 = st.columns([1,2,2])
        col1.markdown('Delete by Day:')
        select_date = col2.date_input('Select the date to delete:',value = st.session_state.target.iloc[0]['date'].date(),key = 'target_date2')
        select_date = select_date.strftime('%Y-%m-%d')
        exercise_option = list(st.session_state.target_display[st.session_state.target_display['date']==select_date]['Exercise'].unique())
        exercise_option.append('All')
        sel_exercise_option = col3.selectbox('Select Exercise to delete',options =exercise_option,key = 'target_inp4')


        delete_day = col1.button('Delete',key='day')
        if delete_day:
            if sel_exercise_option == "All":
                st.session_state.target = st.session_state.target.drop(st.session_state.target[st.session_state.target['date']==select_date].index).reset_index(drop=True)
                st.session_state.target_display = st.session_state.target_display.drop(st.session_state.target_display[st.session_state.target_display['date']==select_date].index).reset_index(drop=True)
            else:
                st.session_state.target = st.session_state.target.drop(st.session_state.target[(st.session_state.target['date']==select_date) & (st.session_state.target['Exercise']==sel_exercise_option)].index).reset_index(drop=True)
                st.session_state.target_display = st.session_state.target_display.drop(st.session_state.target_display[(st.session_state.target_display['date']==select_date) & (st.session_state.target_display['Exercise']==sel_exercise_option)].index).reset_index(drop=True)
        col4, col5= st.columns([1,4])
        col4.markdown('Delete by week')
        try:
            first_date, second_date = col5.date_input('Select the week you want to delete:',value = [datetime.date.today()-datetime.timedelta(1),datetime.date.today()],key = 'target_date3')
        except ValueError:
            time.sleep(30)
            st.write("Choose second date")
        first_date = first_date.strftime('%Y-%m-%d')
        second_date = second_date.strftime('%Y-%m-%d')
        delete_week = col4.button('Delete',key = 'week')
        if delete_week:
            st.session_state.target = st.session_state.target.drop(st.session_state.target[(st.session_state.target['date']>=first_date) & (st.session_state.target['date']<=second_date)].index).reset_index(drop=True)
            st.session_state.target_display = st.session_state.target_display.drop(st.session_state.target_display[(st.session_state.target_display['date']>=first_date) & (st.session_state.target_display['date']<=second_date)].index).reset_index(drop=True)
        st.write('Schedule for this week')
        st.table(st.session_state.target_display[col])
    _,_,col2,_,_ = st.columns(5)
    confirm = col2.button('Confirm changes')
    if confirm:
        st.session_state.target.to_csv('data/target.csv', index=False)
        st.session_state.target_display.to_csv('data/display_target.csv', index=False)
        #trash_code.upload_blob(credentials, project)