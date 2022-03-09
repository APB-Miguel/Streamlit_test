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
import sys
sys.path.append("./libs")
import libs_mov as lm

def app():
    RUTA =r"C:/users/usuario/python_course/projects/APB_OM/data/"
    Query_WP=lm.query()
    WP_Pairs=pd.read_csv(RUTA+'WP_Pairs.csv',sep=";",header=None)

    #load data
    chart_data=lm.load_data(RUTA,Query_WP)
    
    #prepare data for time measurements
    chart_data=lm.prepare_data(chart_data)
    
    #define filter elements
    (clase,type_mov,vessel,berthing,berth,origin,destination,periods)=lm.filter_elements(chart_data)
    
    #define layout
    st.header("Análisis de Tiempos de Maniobra")

    if st.checkbox('Show Data'):
          st.write(chart_data)
    
    (class_sel,typemov_sel,side_sel,vessel_sel,dest_sel,year_sel) = lm.build_filters(periods,clase,type_mov,berthing,vessel,berth)
        
    #Define filters to apply
    seleccion=lm.apply_filters(chart_data,class_sel,typemov_sel,vessel_sel,dest_sel,side_sel,year_sel)

    #load berth geometry   
    gdf=lm.load_berths(RUTA)
        
    #calculate total portcalls per berth & add to data
    gdf=lm.calculate_portcalls(seleccion,gdf)
    
    selected_col=["Count"]
    
    min_value = gdf[selected_col].min()
    max_value = gdf[selected_col].max()
    
    gdf=lm.def_palette("autumn",12,gdf)
    
    #setup initial map view
    initial_view_state = pdk.ViewState(latitude=41.35, longitude=2.15, zoom=12.2, max_zoom=16, pitch=70, bearing=260)
    color_exp = "[R, G, B]"

    #define layers
    (layers, column_layer) =lm.define_layers(gdf,color_exp)
 
    #define tooltips
    tooltip = {
        "html": "<b>Berth:</b> {name}<br><b>Value:</b> {"
        + "code"
        + "}<br><b>Portcalls:</b> {"
        + "Count"
        + "}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
    
    #create map object
    r = pdk.Deck(
                layers=layers,
                initial_view_state=initial_view_state,
                map_style="light",
                tooltip=tooltip,
                )
    
    with st.expander("Volumen de escalas"):
        st.metric(label="Muestras", value=gdf["Count"].sum())
        st.pydeck_chart(r)
    
    (slider_t,slider_b,trip_from,trip_to)=lm.set_graph_details(origin, destination, WP_Pairs)
    
    #Calculate & display Movement times
    lm.calc_mov_times(seleccion, trip_from, trip_to,slider_t,slider_b) 

