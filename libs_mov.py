import numpy as np
import pandas as pd
import streamlit as st
import pyodbc 
import streamlit as st
import datetime as dt
from dateutil.relativedelta import relativedelta # to add days or years
import os
import pathlib
import requests
import zipfile
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb
from ipywidgets import HTML
import matplotlib.pyplot as plt



@st.cache(allow_output_mutation=True)
def get_data(datapath,local,DBQuery):
    if local:
        return(pd.read_csv(datapath).iloc[:,1:])
    else:
        server= '172.17.5.180'
        database = 'MISNT_PROD'
        username="mmarquez"
        password ="Teleco_87"
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = cnxn.cursor()
        cursor.execute(DBQuery)
        return(pd.DataFrame([dict(zip([column[0] for column in cursor.description], row)) \
                for row in cursor.fetchall()]))

def query():
    return ("Select \
                MISNT.WAY_POINT_LOG_VIEW.JOB_TYPE_NAME As JOB_TYPE_NAME1,\
                MISNT.WAY_POINT_LOG_VIEW.WAYPOINT As WP,\
                MISNT.WAY_POINT_LOG_VIEW.ATA As ATA,\
                MISNT.WAY_POINT_LOG_VIEW.ETA As ETA,\
                MISNT.VOYAGE_JOB_VIEW.VOYAGE_NUMBER As PORTCALL,\
                MISNT.VOYAGE_JOB_VIEW.VESSEL_NAME As NAME,\
                MISNT.VOYAGE_JOB_VIEW.MIS_VESSEL_TYPENAME As CLASS,\
                MISNT.VOYAGE_JOB_VIEW.rank As RANK,\
                MISNT.VOYAGE_JOB_VIEW.STATUS_TYPE_NAME As STAT,\
                MOORERS_TO.FIRST_LINE_2 As FIRST_LINE,\
                MISNT.VOYAGE_JOB_VIEW.TO_LOCATION_CODE,\
               MISNT.VOYAGE_JOB_VIEW.TO_ORIENTATION_CODE As BERTHING_SIDE,\
                MISNT.WAY_POINT_LOG_VIEW.LOCATION_TYPE As WP_TYPE,\
                MISNT.WAY_POINT_LOG_VIEW.LOCATION_TYPE_NAME As WP_TYPE_NAME\
            From\
                MISNT.WAY_POINT_LOG_VIEW Inner Join\
                MISNT.VOYAGE_JOB_VIEW On MISNT.WAY_POINT_LOG_VIEW.VOYAGE_JOB_ID = MISNT.VOYAGE_JOB_VIEW.id Inner Join \
                (Select\
                     Min(time.ACT_JOB_START) As FIRST_LINE_2,\
                     Min(time.ACT_JOB_END) As LAST_LINE_2,\
                     job.ID\
                 From\
                     MISNT.HM_VOYAGE_JOB job Join\
                     MISNT.HM_VOYAGE_STOP stop On stop.ID = job.TO_STOP_ID Join \
                     MISNT.RR_RES_ALLOCATION linesmen On linesmen.VOYAGE_STOP_ID = stop.ID Join\
                     MISNT.RR_RES_ALLOCATION_TIME time On time.ALLOCATION_ID = linesmen.ID\
                 Where\
                     linesmen.RESOURCE_TYPE_ID = 19430\
                 Group By\
                     job.ID) MOORERS_TO On MOORERS_TO.ID = MISNT.VOYAGE_JOB_VIEW.id\
            Order By\
                MISNT.WAY_POINT_LOG_VIEW.ID")

def define_filters(periods,clase,type_mov,berthing,vessel,berth):
    with st.expander("Filtros de datos"):
        col1, col2, col3,col4 = st.columns(4)
        year_sel=periods
        with col1:
            class_sel = st.selectbox(
            'Vessel Class',
             clase)
            typemov_sel = st.selectbox(
            'Movement Type',
             type_mov)
            side_sel = st.selectbox(
            'Berthing Side',
             berthing) 

        with col2:
            vessel_sel = st.selectbox(
            'Vessel Name',
             vessel)
            dest_sel = st.selectbox(
            'Destination',
             berth)

        with col3:
            year_sel= st.multiselect(
                'Year',
                periods,
                default=["2021"])
