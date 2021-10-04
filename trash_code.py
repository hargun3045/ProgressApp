import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import plotly as po
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
muscle =['LLTB', 'Core', 'PDT', 'GHQC']
# app.py trash
def cleanup(df, select_muscle='All'):   
    df_d_a_group = df.groupby(['Date','Activity']).sum().reset_index().drop(['Month'],axis=1)
    df_d_a_group['Set #'] = df.groupby(['Date','Activity'])['Set #'].max().values
    df_d_a_group = df_d_a_group.rename(columns={'Set #':'Total Sets','Weight':'Total Weight'})
    df_d_a_group['Month'] = pd.DatetimeIndex(df_d_a_group['Date']).month
    #df_d_a_group['Break Time'] = df.groupby(['Date','Activity'])['Break Time'].median().values
    median_sets = df_d_a_group.groupby('Activity')['Total Sets'].median().to_dict()
    mean_weights = df_d_a_group.groupby('Activity')['Total Weight'].mean().to_dict()
    conditions =[]
    choice = []
    for i in df_d_a_group['Activity'].unique():
        conditions.append(( (df_d_a_group['Activity']==i) & (df_d_a_group['Total Weight']>mean_weights[i]) & (df_d_a_group['Total Sets']>median_sets[i]) ))
        choice.append('Endurance')
        conditions.append(( (df_d_a_group['Activity']==i) & (df_d_a_group['Total Weight']<mean_weights[i]) & (df_d_a_group['Total Sets']>=median_sets[i]) ))
        choice.append('Endurance')
        conditions.append(( (df_d_a_group['Activity']==i) & (df_d_a_group['Total Weight']<=mean_weights[i]) & (df_d_a_group['Total Sets']<=median_sets[i]) ))
        choice.append('Recovery')
        conditions.append(( (df_d_a_group['Activity']==i) & (df_d_a_group['Total Weight']>=mean_weights[i]) & (df_d_a_group['Total Sets']<median_sets[i]) ))
        choice.append('Strength')
    df_d_a_group['Type'] = np.select(conditions, choice,default ='Recovery')
    temp_df = df_d_a_group[muscle+['Type']].groupby(['Type']).sum().transpose()
    if select_muscle == 'All':
        type_rat =px.pie(data_frame = df_d_a_group, names = 'Type', hole = 0.6, color='Type', color_discrete_map={'Endurance':'#ef553b','Strength':'#00cc96','Recovery':' #636efa'})
        type_rat.update_traces(textfont=dict(color='#fff'))
        type_rat.update_layout(autosize=True, height=200, width=500,
                            margin=dict(t=40, b=30, l=40, r=40),
                            plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                            title_font=dict(size=25, color='#a5a7ab', family="Muli, sans-serif"),
                            font=dict(color='#8a8d93'),
                            legend=dict(orientation="h", yanchor="bottom", y=1.2, xanchor="right", x =1)
                            )
    else:
        type_rat =px.pie(names = temp_df.loc[select_muscle].index, values = temp_df.loc[select_muscle], hole = 0.6, color_discrete_map={'Endurance':'#ef553b','Strength':'#00cc96','Recovery':' #636efa'})
        type_rat.update_traces(textfont=dict(color='#fff'))
        type_rat.update_layout(autosize=True, height=200, width=500,
                           margin=dict(t=40, b=30, l=40, r=40),
                           plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                           title_font=dict(size=25, color='#a5a7ab', family="Muli, sans-serif"),
                           font=dict(color='#8a8d93'),
                           legend=dict(orientation="h", yanchor="bottom", y=1.2, xanchor="right", x =1)
                           )
    return type_rat

def map_dates(df, start_idx):
    today = datetime.date.today()
    idx = (today.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
    if start_idx == 1:    
        if idx == start_idx:
            day = today
        else:
            day = today - datetime.timedelta(idx+1)
        start_date = day + datetime.timedelta(df['date'].nunique()-1)    
        new_date = pd.date_range(day, start_date, freq = 'd')
        dates = df['date'].unique()
        date_map = dict(zip(dates,new_date))
        df = df.replace({'date':date_map})
        df['Date'] = df.date.dt.strftime('%d-%b-%Y')
        df['Day'] = df['date'].dt.day_name()
    else:
        if idx == start_idx:
            day = today
        else:
            day = today - datetime.timedelta(idx)
        start_date = day - datetime.timedelta(df['Date'].nunique()-1)
        new_date = pd.date_range(start_date, day, freq = 'd')
        dates = df['Date'].unique()
        date_map = dict(zip(dates,new_date))
        df = df.replace({'Date':date_map})
        df['Month'] = df["Date"].dt.month
        df['DOW'] = df['Date'].dt.day_name()
    return df
def map_target_values(df, map_df):
    dict1 = map_df.to_dict()
    map_dict = [dict(zip(dict1['Exercise'].values(),dict1[i].values())) for i in muscle]
    for j,i in enumerate(muscle):
        df[i] = df['Exercise'].map(map_dict[j])
    df['Volume'] = df['Weight']*df['Reps']
    df['LLTB'] = df['Volume']*df['LLTB']
    df['Core'] = df['Volume']*df['Core']
    df['PDT'] = df['Volume']*df['PDT']
    df['GHQC'] = df['Volume']*df['GHQC']
    return df

def map_workout(df, map_df):
    dict1 = map_df.to_dict()
    map_dict = [dict(zip(dict1['Exercise'].values(),dict1[i].values())) for i in muscle]
    for j,i in enumerate(muscle):
        df[i] = df['Activity'].map(map_dict[j])
    df['Volume'] = df['Weight']*df['Reps']
    df['LLTB'] = df['Volume']*df['LLTB']
    df['Core'] = df['Volume']*df['Core']
    df['PDT'] = df['Volume']*df['PDT']
    df['GHQC'] = df['Volume']*df['GHQC']
    df['Sum']= df[muscle].sum(axis=1)
    return df

def get_pies(df, target, muscle='All'):
    today = datetime.date.today()
    idx = (today.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
    if idx == 1:
        mon = today
    else:
        mon = today - datetime.timedelta(idx+1)
    week_start = mon
    week_end =  week_start + datetime.timedelta(6)
    if muscle == 'All':
        df_sum = df[(df['Date']>=pd.to_datetime(week_start)) & (df['Date']<=pd.to_datetime(week_end))]['Volume'].sum()
        target_sum = target[(target['date']>=pd.to_datetime(week_start)) & (target['date']<=pd.to_datetime(week_end))]['Volume'].sum()
    else:
        df_sum = df[(df['Date']>=pd.to_datetime(week_start)) & (df['Date']<=pd.to_datetime(week_end))][muscle].sum()
        target_sum = target[(target['date']>=pd.to_datetime(week_start)) & (target['date']<=pd.to_datetime(week_end))][muscle].sum()
    pie =px.pie(names = ['Completed','Remaining'], values= [df_sum, target_sum-df_sum] ,hole = 0.9, color =['Completed','Remaining'], color_discrete_map={'Remaining':'#ffffff','Completed':'#636efa'})
    pie.update_traces(textfont=dict(color='#fff'))
    pie.update_layout(autosize=True, height=200, width=500,
                        margin=dict(t=40, b=30, l=40, r=40),
                        plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                        title_font=dict(size=25, color='#a5a7ab', family="Muli, sans-serif"),
                        font=dict(color='#8a8d93'), showlegend =False
                        )
    return pie






    

#muscle =['LLTB', 'Core', 'PDT', 'GHQC']

#col1, col2 = st.columns([3,1])
#col1.image('anatomy.jpg')
#col2.selectbox('Select Muscle:',options = ('All','LLTB','PDT','Core',"GHQC"))
#col2.image(cleanup(st.session_state.workout))
#st.selectbox()
"""
col1, col2= st.columns(2)
col3, col4= st.columns(2)
button1 = col1.button('LLTB')
if button1:
    with st.expander('LOWER BACK, LATS, TRAPEIZ, BICEPS'):
        st.write('Target Volume:')
        st.write('Completed Volume:')
        st.write('Most Contribution:')
        st.write('Least Contribution:')

button2 = col2.button('Core')
if button2:
    with st.expander('Core'):
            st.write('Target Volume:')
            st.write('Completed Volume:')
            st.write('Most Contribution:')
            st.write('Least Contribution:')
button3 = col3.button('PDT')
if button3:
    with st.expander('Pectorals, Deltoids, Triceps'):
            st.write('Target Volume:')
            st.write('Completed Volume:')
            st.write('Most Contribution:')
            st.write('Least Contribution:')
button4 = col4.button('GHQC')
if button4:
    with st.expander('Glutes, Hamstrings, Quadriceps, Calves'):
            st.write('Target Volume:')
            st.write('Completed Volume:')
            st.write('Most Contribution:')
            st.write('Least Contribution:')
"""