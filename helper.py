import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import plotly as po
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
# from google.cloud import storage
import google.auth
import os
from glob import glob
import json
from google.oauth2 import service_account

muscle =['LLTB', 'Core', 'PDT', 'GHQC']
# app.py trash
# def auth_gcp():
#     key_dict = json.loads(st.secrets["textkey"])
#     credentials = service_account.Credentials.from_service_account_info(key_dict)
#     project = credentials.project_id
#     return credentials, project

# def download_blob(credentials, project, filename, username):
#     bucket_name = 'arty-bucket'
#     prefix = 'dataset-records/poc/'+username+'/'
#     storage_client = storage.Client(credentials=credentials, project = project)
#     bucket = storage_client.bucket(bucket_name)
#     blobs = bucket.list_blobs(prefix=prefix)
#     for blob in blobs:
#         filename = blob.name.replace(prefix, '') 
#         blob.download_to_filename('data/'+filename)
        
# def upload_blob(credentials, project, filename, username, all=False):
#     bucket_name = 'arty-bucket'
#     prefix = 'dataset-records/poc/'+username
#     storage_client = storage.Client(credentials=credentials, project = project)
#     bucket = storage_client.bucket(bucket_name)
#     if all:
#         for file_path in glob('data/*'):
#             file_name = file_path.replace('data\\','')
#             blob = bucket.blob('dataset-records/poc/'+username+'/'+file_name) 
#             blob.upload_from_filename(file_path)

def map_workout(df, map_df):
    dict1 = map_df.to_dict()
    map_dict = [dict(zip(dict1['Exercise'].values(),dict1[i].values())) for i in muscle]
    for i in muscle:
        df[i] = df['Exercise'].apply(lambda row: [map_dict[i][v[0]] if type(row) is list else map_dict[i][v] for v in [row]])
    df['Volume'] = df['Weight']*df['Reps']
    df['LLTB'] = df['Volume']*df['LLTB']
    df['Core'] = df['Volume']*df['Core']
    df['PDT'] = df['Volume']*df['PDT']
    df['GHQC'] = df['Volume']*df['GHQC']
    return df
def type_summary(df, select_muscle='All'):
    if select_muscle=='All':
        col = 'Volume'
    else:
        col = select_muscle
    df_d_a_group = df.groupby(['date','Exercise'],sort=False).sum().reset_index()
    df_d_a_group['Set'] = df.groupby(['date','Exercise'],sort=False)['Set'].max().reset_index()['Set'].astype(int).tolist()
    df_d_a_group['Type'] = df.groupby(['date','Exercise'],sort=False)['Type'].max().reset_index()['Type'].to_list()
    color_map = {"Strength":'#636EFA','Speed':'#EF553B','Hypertrophy':'#00CC96','Endurance':'#AB63FA','Conditioning':'#FFA15A'}
    type_df = df_d_a_group[['Type',col]].groupby(['Type']).sum().reset_index().sort_values(by=col,ascending=False)
    type_rat =px.bar(data_frame = type_df, y= 'Type', x = col, color='Type',orientation='h', color_discrete_map=color_map)
    type_rat.update_traces(textfont=dict(color='#262730'))
    type_rat.update_xaxes(showgrid = False)
    type_rat.update_layout(autosize=True, height=350, width=700, xaxis_title ="Volume", yaxis_title = '',
                            margin=dict(t=10, b=20, l=10, r=10),
                            plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
                            title_font=dict(size=25, color='#262730', family="Muli, sans-serif"),
                            font=dict(color='#262730'), modebar_remove = ['zoom','pan','select','zoomIn','zoomOut','autoScale'],
                            legend=dict(font =dict(size =10),orientation="v", yanchor="bottom", y=0.5, xanchor="right", x= 1.2), legend_title_text = ''
                            )
    return type_rat

def create_mask(df, num_days, date_col, today=datetime.date.today()):
    day = today - timedelta(num_days)
    df = df[(df[date_col]>=pd.to_datetime(day)) & (df[date_col]<=pd.to_datetime(today))]
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
        df_sum = df[(df['date']>=pd.to_datetime(week_start)) & (df['date']<=pd.to_datetime(week_end))]['Volume'].sum()
        target_sum = target[(target['date']>=pd.to_datetime(week_start)) & (target['date']<=pd.to_datetime(week_end))]['Volume'].sum()
    else:
        df_sum = df[(df['date']>=pd.to_datetime(week_start)) & (df['date']<=pd.to_datetime(week_end))][muscle].sum()
        target_sum = target[(target['date']>=pd.to_datetime(week_start)) & (target['date']<=pd.to_datetime(week_end))][muscle].sum()
    pie =go.Figure(go.Pie(labels = ['Remaining','Completed'], values= [target_sum-df_sum, df_sum] ,hole = 0.8,  marker_colors=['#ffffff','#636efa'],direction ='clockwise', sort=False))
    pie.update_traces( textinfo = 'none', marker = dict( line = dict(color = '#1F77B4', width = 0.5)))
    pie.update_layout(autosize=True, height=250, width=500,
                        margin=dict(t=40, b=30, l=40, r=40),
                        plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
                        title_font=dict(size=25, color='#262730', family="Muli, sans-serif"),
                        font=dict(color='#262730'), showlegend =False
                        )
    pie.update_layout(annotations =[ go.layout.Annotation(text = '<b>'+str(int((df_sum/target_sum)*100))+' <br> percent <b>' , xref='paper', yref = 'paper', align = 'center', showarrow = False, font = dict(family = '\'EA Font v1.5 by Ghettoshark\'',size =20))])

    return pie

def stack_bar(df):
    df_d_a_group = df.groupby(['date','Exercise'],sort=False).sum().reset_index()
    df_d_a_group['Set'] = df.groupby(['date','Exercise'],sort=False)['Set'].max().reset_index()['Set'].astype(int).tolist()
    df_d_a_group['Type'] = df.groupby(['date','Exercise'],sort=False)['Type'].max().reset_index()['Type'].to_list()
    temp_df = df_d_a_group[muscle+['Type']].groupby(['Type']).sum().transpose()
    temp_df = temp_df.reset_index().rename(columns={'index':'Type'})
    fig = go.Figure()
    try:
        fig.add_trace(go.Bar(name='Strength', y=temp_df['Strength'], x=temp_df['Type'], width = 0.4))
    except KeyError:
        pass
    try:
        fig.add_trace(go.Bar(name='Speed', y=temp_df['Speed'], x=temp_df['Type'], width = 0.4))
    except KeyError:
        pass
    try:
        fig.add_trace(go.Bar(name='Hypertrophy', y=temp_df['Hypertrophy'], x=temp_df['Type'], width = 0.4))
    except KeyError:
        pass
    try:
        fig.add_trace(go.Bar(name='Endurance', y=temp_df['Endurance'], x=temp_df['Type'], width = 0.4))
    except KeyError:
        pass
    try:
        fig.add_trace(go.Bar(name='Conditioning', y=temp_df['Conditioning'], x = temp_df['Type'], width = 0.4) )
    except KeyError:
        pass
        
    fig.update_layout(barmode='stack',autosize=True, height=300, width=500, xaxis_title='', yaxis_title="Volume",plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
                            title_font=dict(size=15, color='#262730', family="Muli, sans-serif"),
                            font=dict(color='#262730'))
    return fig
def line_chart(workout, target):
    workout_data = workout.groupby(['date'],sort=False)['Volume'].sum().reset_index()
    target_data = target.groupby(['date'], sort=False)['Volume'].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = workout_data['date'], y= workout_data['Volume'], mode= 'lines', name = 'Workout', line = dict(color='firebrick', width = 1.5)))
    fig.add_trace(go.Scatter(x = target_data['date'], y= target_data['Volume'], mode= 'lines', name = 'Target', line = dict(color='royalblue', width = 1.5)))
    fig.update_layout(autosize=True, height=300, width=500, xaxis_title='Date', yaxis_title="Volume",plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
                            title_font=dict(size=15, color='#262730', family="Muli, sans-serif"),
                            font=dict(color='#262730'))
    return fig

def volume_chart(df):
    date_df = df.groupby('date')[muscle].sum()
    date_df = date_df.reset_index()
    today = datetime.datetime.today()
    ninety_days = today - timedelta(days=90)
    thirty_days = today - timedelta(days=28)
    fifteen_days = today - timedelta(days=14)
    past_week = today - timedelta(days=7)
    ninety_mask = (date_df['date'] > ninety_days) & (date_df['date'] <= today)
    thirty_mask = (date_df['date'] > thirty_days) & (date_df['date'] <= today)
    fifteen_mask = (date_df['date'] > fifteen_days) & (date_df['date'] <= today)
    week_mask = (date_df['date'] > past_week) & (date_df['date'] <= today)
    total_graph = px.line(x = date_df['date'], y=date_df['LLTB'])
    total_graph.update_yaxes(showgrid=False)
    total_graph.update_xaxes(showgrid=False)
    total_graph.update_layout(barmode='group',autosize=True, height=300, width=1000, xaxis_title='Date', yaxis_title="Volume",plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
                            title_font=dict(size=5, color='#262730', family="Muli, sans-serif"),
                            font=dict(color='#262730',size=10))
    total_graph.update_layout(
        updatemenus=[
            dict(
                type = "buttons",
                direction = "left",
                buttons=list([
                    dict(
                        args=[{'x':[date_df['date']],'y':[date_df['LLTB']] ,"type":"line"}],
                        label="Full Data",
                        visible=True,
                        method="restyle"
                    ),
                    dict(
                        args=[{'x':[date_df.loc[ninety_mask]['date']],'y':[date_df.loc[ninety_mask]['LLTB']],"type":"bar"}],
                        label="90 days",
                        visible=True,
                        method="restyle"
                    ),
                    dict(
                        args=[{'x':[date_df.loc[thirty_mask]['date']],'y':[date_df.loc[thirty_mask]['LLTB']],"type":"bar"}],
                        label="30 days",
                        visible=True,
                        method="restyle"
                    ),
                    dict(
                        args=[{'x':[date_df.loc[fifteen_mask]['date']],'y':[date_df.loc[fifteen_mask]['LLTB']],"type":"bar"}],
                        label="15 days",
                        visible=True,
                        method="restyle"
                    ),
                    dict(
                        args=[{'x':[date_df.loc[week_mask]['date']],'y':[date_df.loc[week_mask]['LLTB']],"type":"bar"}],
                        label="7 days",
                        visible=True,
                        method="restyle"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.11,
                xanchor="left",
                y=1.5,
                yanchor="top"
            ),
        ]
    )
    return total_graph


def day_plot(df):
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_df = df.groupby('Day').sum()[muscle].loc[day_order]
    day_df = day_df.div(day_df.sum(axis=1),axis=0)*100
    day_df = day_df.stack().reset_index().rename(columns={'level_1':'Muscle', 0:'Value'})
    day_df['Value'] = day_df['Value'].round(2)
    day_plot = px.bar(data_frame=day_df, x = 'Day',y='Value',color='Muscle',color_continuous_scale=px.colors.sequential.Viridis)
    day_plot.update_layout(barmode='group',title = 'Workday Distribution',autosize=True, height=300, width=1000, xaxis_title='Day', yaxis_title="Percentage",plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
                            title_font=dict(size=15, color='#262730', family="Muli, sans-serif"),
                            font=dict(color='#262730'))
    return day_plot