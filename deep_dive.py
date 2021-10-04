import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import plotly as po
import plotly.express as px
import plotly.graph_objects as go
def app():
    st.title('Full Data')
    muscle =['LLTB', 'Core', 'PDT', 'GHQC']
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

    def deep_dive_data(df):
        date_df = df.groupby('Date')[muscle].sum()
        date_df = date_df.reset_index()
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_df = df.groupby('DOW').sum()[muscle].loc[day_order]
        day_df = day_df.div(day_df.sum(axis=1),axis=0)*100
        day_df = day_df.stack().reset_index().rename(columns={'level_1':'Muscle', 0:'Value'})
        day_df['Value'] = day_df['Value'].round(2)
        today = today = datetime.datetime.today()
        ninety_days = today - timedelta(days=90)
        thirty_days = today - timedelta(days=30)
        fifteen_days = today - timedelta(days=15)
        past_week = today - timedelta(days=7)
        ninety_mask = (date_df['Date'] > ninety_days) & (date_df['Date'] <= today)
        thirty_mask = (date_df['Date'] > thirty_days) & (date_df['Date'] <= today)
        fifteen_mask = (date_df['Date'] > fifteen_days) & (date_df['Date'] <= today)
        week_mask = (date_df['Date'] > past_week) & (date_df['Date'] <= today)
        total_graph = px.line(x = date_df['Date'], y=date_df['LLTB'])
        total_graph.update_yaxes(showgrid=False)
        total_graph.update_xaxes(showgrid=False)
        total_graph.update_layout(barmode='group',autosize=True, height=300, width=800, xaxis_title='Date', yaxis_title="Volume",plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                                title_font=dict(size=5, color='#a5a7ab', family="Muli, sans-serif"),
                                font=dict(color='#8a8d93',size=10))
        total_graph.update_layout(
            updatemenus=[
                dict(
                    type = "buttons",
                    direction = "left",
                    buttons=list([
                        dict(
                            args=[{'x':[date_df['Date']],'y':[date_df['LLTB']],"type":"line"}],
                            label="Full Data",
                            visible=True,
                            method="restyle"
                        ),
                        dict(
                            args=[{'x':[date_df.loc[ninety_mask]['Date']],'y':[date_df.loc[ninety_mask]['LLTB']],"type":"bar"}],
                            label="12 weeks",
                            visible=True,
                            method="restyle"
                        ),
                        dict(
                            args=[{'x':[date_df.loc[thirty_mask]['Date']],'y':[date_df.loc[thirty_mask]['LLTB']],"type":"bar"}],
                            label="4 weeks",
                            visible=True,
                            method="restyle"
                        ),
                        dict(
                            args=[{'x':[date_df.loc[fifteen_mask]['Date']],'y':[date_df.loc[fifteen_mask]['LLTB']],"type":"bar"}],
                            label="2 weeks",
                            visible=True,
                            method="restyle"
                        ),
                        dict(
                            args=[{'x':[date_df.loc[week_mask]['Date']],'y':[date_df.loc[week_mask]['LLTB']],"type":"bar"}],
                            label="Past Week",
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
        day_plot = px.bar(data_frame=day_df, x = 'DOW',y='Value',color='Muscle',color_continuous_scale=px.colors.sequential.Viridis)
        day_plot.update_layout(barmode='group',title = 'Workday Distribution',autosize=True, height=300, width=800, xaxis_title='Day', yaxis_title="Percentage",plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                                title_font=dict(size=15, color='#a5a7ab', family="Muli, sans-serif"),
                                font=dict(color='#8a8d93'))
        return total_graph, day_plot
    total_graph, day_plot = deep_dive_data(st.session_state.workout)
    watch = st.selectbox('View:',options = ('Day-wise distribution','Full data'))
    if watch == 'Day-wise distribution':
        st.write('Workout volume by Day of Week:')
        st.write(day_plot)
    else:
        st.write('Data')
        st.write(total_graph)
    with st.expander('See the data'):
        st.dataframe(st.session_state.workout)