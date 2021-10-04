import streamlit as st
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
import plotly as po
import plotly.express as px
import plotly.graph_objects as go
import trash_code
def app():
    muscle =['LLTB', 'Core', 'PDT', 'GHQC']
    st.title("Progress Report")
    @st.cache(persist=True, allow_output_mutation=True)
    def load_data(filename,date = False):
        if date:
            df = pd.read_csv(filename,parse_dates=['Date'])
        else:
            df = pd.read_csv(filename)
        return df
    if 'workout' not in st.session_state:
        st.session_state.workout = load_data('workout.csv', date = True)
    if 'target' not in st.session_state:
        st.session_state.target = load_data('target.csv', date= True)
    def cleanup(df):   
        df_d_a_group = df.groupby(['Date','Activity']).sum().reset_index().drop(['Month'],axis=1)
        df_d_a_group['Set #'] = df.groupby(['Date','Activity'])['Set #'].max().values
        df_d_a_group = df_d_a_group.rename(columns={'Set #':'Total Sets','Weight':'Total Weight'})
        df_d_a_group['Month'] = pd.DatetimeIndex(df_d_a_group['Date']).month
        df_d_a_group['Break Time'] = df.groupby(['Date','Activity'])['Break Time'].median().values
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
        temp_df.loc[:,'Endurance':'Strength'] = temp_df.loc[:,'Endurance':'Strength']
        temp_df = temp_df.reset_index().rename(columns={'index':'Type'})
        fig = go.Figure(data=[
        go.Bar(name='Endurance', y=temp_df['Endurance'], x=temp_df['Type']),
        go.Bar(name='Recovery', y=temp_df['Recovery'], x = temp_df['Type']),
        go.Bar(name='Strength', y=temp_df['Strength'], x=temp_df['Type'])])
        fig.update_layout(barmode='stack',title = 'Workout Type Distribution',autosize=True, height=400, width=500, xaxis_title='Workout Type', yaxis_title="Percentage",plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                            title_font=dict(size=15, color='#a5a7ab', family="Muli, sans-serif"),
                            font=dict(color='#8a8d93'))
        df_sum = df.groupby('Activity').sum()
        fig_box = go.Figure()
        fig_box.add_trace(go.Bar(x=df_sum.loc[:,'LLTB'].sort_values(ascending=False).iloc[:5].index,y=df_sum.loc[:,'LLTB'].sort_values(ascending=False).iloc[:5].values/(df_sum.loc[:,'LLTB'].sum())*100,width=[0.3, 0.3, 0.3,0.3]))
        fig_box.update_yaxes(showgrid=False)
        fig_box.update_layout(title = 'Muscle Group Distribution',autosize=True, height=400, width=500, xaxis_title='Activity', yaxis_title="Percentage",plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                                title_font=dict(size=15, color='#a5a7ab', family="Muli, sans-serif"),
                                font=dict(color='#8a8d93'))
        return fig, fig_box

    col1, col2 = st.columns(2)
    fig1, fig2 = cleanup(st.session_state.workout)
    with col1:
        st.write('Muscle Group Distribution:')
        st.write(fig1)
    with col2:
        st.write('Exercise Distribution:')
        st.write(fig2)
    deep_dive = st.button('See Data', key = 'progress_data')