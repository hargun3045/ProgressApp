import streamlit as st
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import overview
import progress
import deep_dive
import target
import add_exercise
import post_workout
import plotly as po
import plotly.express as px
import plotly.graph_objects as go
import os
# from google.cloud import storage
# import google.auth
# import trash_code

#credentials, project = trash_code.auth_gcp()

#trash_code.download_blob(credentials, project)


st.set_page_config(page_title="Analytics",layout='wide')

PAGES = {
    "Overview": overview,
    "Progress": progress,
    "Data": deep_dive,
    "Set Target":target,
    "Post Workout":post_workout,
    'Add exercise':add_exercise
}

st.sidebar.title('Navigator')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()
