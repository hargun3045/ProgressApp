from pandas._config.config import options
from pandas.core.tools.datetimes import to_datetime
import streamlit as st
import numpy as np
import pandas as pd
from collections import defaultdict
import pyarrow as pa
from streamlit.errors import StreamlitAPIException
import helper
def app():
    muscle =['LLTB', 'Core', 'PDT', 'GHQC']
    st.title('Post Workout Details')
    st.markdown("---")
    @st.cache(persist=True, allow_output_mutation=True)
    def load_data(filename,date = False):
        if date:
            df = pd.read_csv(filename,parse_dates=['date'])
        else:
            df = pd.read_csv(filename)
        return df
    if 'workout' not in st.session_state:
        st.session_state.workout = load_data('data/workout.csv', date = True)
    if 'map' not in st.session_state:
        st.session_state.map = load_data('data/MAP.csv')
    if 'empty_df' not in st.session_state:
        st.session_state.empty_df = pd.DataFrame(columns = ['Date', 'Day', 'Exercise', 'Type', 'Set', 'Weight', 'Reps', 'Volume',
        'LLTB', 'Core', 'PDT', 'GHQC', 'date', 'Break Time'])
    if 'display' not in st.session_state:
        st.session_state.display = load_data('data/display.csv', date = True)
    st.session_state.display[['Set','Weight','Reps','Break Time']] = st.session_state.display[['Set','Weight','Reps','Break Time']].astype(str)
    if 'temp' not in st.session_state:
        st.session_state.temp = pd.DataFrame(columns = ['Date', 'Day', 'Exercise', 'Type', 'Set', 'Weight', 'Reps', 'Volume',
        'LLTB', 'Core', 'PDT', 'GHQC', 'date', 'Break Time'])


    st.session_state.dict1 = st.session_state.map.to_dict()
    st.session_state.map_dict = [dict(zip(st.session_state.dict1['Exercise'].values(),st.session_state.dict1[i].values())) for i in muscle]
    st.session_state.map_dict = dict(zip(muscle, st.session_state.map_dict))

    upper = list(st.session_state.map[st.session_state.map['Body']=='Upper Body']['Exercise'].values)
    lower = list(st.session_state.map[st.session_state.map['Body']=='Lower Body']['Exercise'].values)
    date = st.date_input('Enter Date:',key = 'date1')
    exc_type = st.selectbox('Exercise Type:',options = ('Standalone','Sequence'),key ='post_work_type')





    if exc_type == 'Standalone':
        body_inp = st.selectbox('Upper Body/Lower Body', ('Upper Body','Lower Body'))
        if body_inp == 'Upper Body':
            exercise = st.selectbox('Select Exercise',options = upper, key = 'post_work_type_1')
        elif body_inp=='Lower Body':
            exercise = st.selectbox('Select Exercise',options = lower, key = 'post_work_type_2')
        sets = st.selectbox('Enter number of sets:',(1,2,3,4,5), key = 'post_workout_set')

        reps_cols = defaultdict(list)
        weight_col = defaultdict(list)
        time_col = defaultdict(list)
        reps_cols = st.columns(sets)
        weight_col = st.columns(sets)
        time_col = st.columns(sets)
        reps, weights, break_time = [], [], []
        for i in range(sets):
            reps.append(reps_cols[i].number_input('Reps:', min_value = 1, value = 1, step = 1, format = '%d', key = 'reps'+str(i)))
            weights.append(weight_col[i].number_input('Weight (KG):', min_value = 1, value = 1, step = 1, format = '%d', key = 'weights'+str(i)))
            break_time.append(time_col[i].number_input('Rest (seconds):', min_value = 5, value = 5, step = 5, format = '%d', key = 'time'+str(i)))
        tempo = st.selectbox('Workout Tempo:', options=('NA','111','311','321','331'),key = 'post_work_tempo')    
        e_type = st.selectbox('Workout type:',options = ('Conditioning', 'Endurance', 'Hypertrophy', 'Speed', 'Strength'),key='type')
        notes = st.text_input('Notes:')
        volume = np.multiply(reps, weights)





    elif exc_type=='Sequence':
        upper_col, lower_col = st.columns(2)
        with upper_col:
            upper_bods = st.multiselect('Upper Body', options = upper, key = 'post_workout_upper')
        with lower_col:
            lower_bods = st.multiselect('Lower Body', options = lower, key = 'post_workout_lower')
        sets = st.selectbox('Enter number of sets:',(1,2,3,4,5), key = 'post_workout_set')
        reps_col = defaultdict(list)
        weight_col = defaultdict(list)
        #time_col = defaultdict(list)
        reps, weights, break_time = [], [], []
        bods = upper_bods+lower_bods
        try:
            reps_cols = st.columns(len(bods))
            weight_col = st.columns(len(bods))
            #time_col = st.columns(len(bods))
        except StreamlitAPIException:
            reps_cols = st.columns(1)
            weight_col = st.columns(1)
            #time_col = st.columns(1)
        for i, j in enumerate(bods):
            reps.append(reps_cols[i].number_input('Reps( '+j+' ):' ,min_value = 1, value = 1, step = 1, format = '%d', key = 'reps'+str(i)))
            weights.append(weight_col[i].number_input('Weight(KG):', min_value = 1, value = 1, step = 1, format = '%d', key = 'weights'+str(i)))
            #break_time.append(time_col[i].number_input('Rest (seconds):', min_value = 5, value = 5, step = 5, format = '%d', key = 'time'+str(i)))
        break_time = st.number_input('Rest (seconds):', min_value = 5, value = 5, step = 5, format = '%d', key = 'time'+str(i))
        tempo = st.selectbox('Workout Tempo:', options=('NA','111','311','321','331'),key = 'post_work_tempo')    
        e_type = st.selectbox('Workout type:',options = ('Conditioning', 'Endurance', 'Hypertrophy', 'Speed', 'Strength'),key='type')
        notes = st.text_input('Notes:')
        volume = np.multiply(reps, weights)



    display_list = []
    exercise_list = []
    for i in range(sets):
        if exc_type=='Standalone':
            exercise_dict = {'date':pd.to_datetime(date),'Date':date.strftime('%d-%b-%Y'),'Day':pd.to_datetime(date).day_name(),'Exercise':exercise, 'Set':i+1, 'Reps':reps[i], 'Weight':weights[i], 'Volume':volume[i], 'LLTB':st.session_state.map_dict['LLTB'][exercise]*volume[i], 'PDT':st.session_state.map_dict['PDT'][exercise]*volume[i], 'Core':st.session_state.map_dict['Core'][exercise]*volume[i], 'GHQC':st.session_state.map_dict['GHQC'][exercise]*volume[i],'Break Time':break_time[i], 'Tempo':tempo, 'Type':e_type}
            display_dict  = {'date':pd.to_datetime(date),'Date':date.strftime('%d-%b-%Y'),'Day':pd.to_datetime(date).day_name(),'Exercise':exercise, 'Set':str(i+1), 'Reps':str(reps[i]), 'Weight':str(weights[i]), 'Volume':volume[i], 'LLTB':st.session_state.map_dict['LLTB'][exercise]*volume[i], 'PDT':st.session_state.map_dict['PDT'][exercise]*volume[i], 'Core':st.session_state.map_dict['Core'][exercise]*volume[i], 'GHQC':st.session_state.map_dict['GHQC'][exercise]*volume[i],'Break Time':str(break_time[i]), 'Tempo':tempo, 'Type':e_type}
            display_list.append(display_dict)
            exercise_list.append(exercise_dict)
        elif exc_type=='Sequence':
            exercise_dict = {'date':pd.to_datetime(date),'Date':date.strftime('%d-%b-%Y'),'Day':pd.to_datetime(date).day_name(),'Exercise':bods, 'Set':i+1, 'Reps':reps, 'Weight':weights, 'Break Time':break_time, 'Volume':volume, 'LLTB': sum(np.multiply(volume,[st.session_state.map_dict['LLTB'][i] for i in bods])),'PDT': sum(np.multiply(volume,[st.session_state.map_dict['PDT'][i] for i in bods])), 'Core': sum(np.multiply(volume,[st.session_state.map_dict['Core'][i] for i in bods])),'GHQC': sum(np.multiply(volume,[st.session_state.map_dict['GHQC'][i] for i in bods])), 'Tempo':tempo, 'Type':e_type}
            display_dict = {'date':pd.to_datetime(date),'Date':date.strftime('%d-%b-%Y'),'Day':pd.to_datetime(date).day_name(),'Exercise':','.join(bods), 'Set':str(i+1), 'Reps':','.join([ str(i) for i in reps]), 'Weight':','.join([str(i) for i in weights]), 'Break Time':str(break_time), 'Volume':volume, 'LLTB': sum(np.multiply(volume,[st.session_state.map_dict['LLTB'][i] for i in bods])),'PDT': sum(np.multiply(volume,[st.session_state.map_dict['PDT'][i] for i in bods])), 'Core': sum(np.multiply(volume,[st.session_state.map_dict['Core'][i] for i in bods])),'GHQC': sum(np.multiply(volume,[st.session_state.map_dict['GHQC'][i] for i in bods])), 'Tempo':tempo, 'Type':e_type}
            display_dict['Volume'] = sum(volume)
            exercise_dict['Volume'] = sum(volume)
            exercise_list.append(exercise_dict)
            display_list.append(display_dict)



    add_col, confirm_col, reset_col = st.columns(3)
    add = add_col.button('ADD')
    confirm = confirm_col.button('Confirm')
    reset = reset_col.button('Reset')
    if add:
        st.session_state.empty_df = st.session_state.empty_df.append(exercise_list, ignore_index = True)
        st.session_state.temp = st.session_state.temp.append(display_list, ignore_index=True)
    if confirm:
        st.session_state.workout = st.session_state.workout.append(st.session_state.empty_df, ignore_index = True)
        st.session_state.display = st.session_state.display.append(st.session_state.temp, ignore_index = True)
        st.session_state.workout.to_csv('data/workout.csv', index=False)
        st.session_state.display.to_csv('data/display.csv', index=False)
    if reset:
        st.session_state.empty_df = pd.DataFrame(columns = ['Date', 'Day', 'Exercise', 'Type', 'Set', 'Weight', 'Reps', 'Volume',
        'LLTB', 'Core', 'PDT', 'GHQC', 'date', 'Break Time'])
        st.session_state.temp = pd.DataFrame(columns = ['Date', 'Day', 'Exercise', 'Type', 'Set', 'Weight', 'Reps', 'Volume',
        'LLTB', 'Core', 'PDT', 'GHQC', 'date', 'Break Time'])

    with st.expander('Today\'s workout:'):
        st.dataframe(st.session_state.temp)    


    with st.expander('Past week workout'):
        data_len = st.selectbox('Length of data:',('Past week', '2 weeks', '4 weeks', '12 weeks', 'Full data'))
        if data_len == "Past week":
            st.dataframe(helper.create_mask(st.session_state.display, 7, 'date'))
        elif data_len == "2 weeks":
            st.dataframe(helper.create_mask(st.session_state.display, 14, 'date'))
        elif data_len == "4 weeks":
            st.dataframe(helper.create_mask(st.session_state.display, 28, 'date'))
        elif data_len == "12 weeks":
            st.dataframe(helper.create_mask(st.session_state.display, 12*7, 'date'))
        elif data_len == "Full data":
            st.dataframe(st.session_state.display)

