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

def app():

    RUTA =r"C:/users/usuario/python_course/projects/APB_OM/data/"
    Query_WP=query()
 

    #load data
    chart_data = get_data(RUTA+"MOV_DATA.csv",1,Query_WP)
    chart_data['ATA'] = pd.to_datetime(chart_data['ATA'], errors='coerce')
    chart_data['ETA'] = pd.to_datetime(chart_data['ETA'], errors='coerce')
    chart_data['FIRST_LINE'] = pd.to_datetime(chart_data['FIRST_LINE'], errors='coerce')

    #prepare data for time measurements
    aux=chart_data.copy()
    aux["WP"]="First Line"
    aux["ATA"]=aux["FIRST_LINE"]
    aux["ETA"]=aux["FIRST_LINE"]
    aux["WP_TYPE_NAME"]="Berth"
    aux["WP_TYPE"]=620.0
    aux=aux.drop("FIRST_LINE",axis=1)
    chart_data=chart_data.drop("FIRST_LINE",axis=1)
    aux=aux.drop_duplicates()
    chart_data=chart_data.append(aux)
    chart_data=chart_data[chart_data["ATA"].notna()]
    
    #define filter elements
    clase=np.append("ALL",chart_data["CLASS"].unique())
    type_mov=np.append("ALL",chart_data["JOB_TYPE_NAME1"].unique())
    vessel=np.append("ALL",chart_data["NAME"].unique())
    berthing=np.append("ALL",chart_data["BERTHING_SIDE"].unique())
    berth=np.append("ALL",chart_data["TO_LOCATION_CODE"].unique())
    origin=chart_data["WP"].unique()
    #pd.DataFrame(origin).to_csv('c:\\Users\\usuario\\python_course\\projects\\APB_OM\\apps\\WPs.csv')
    destination=chart_data["WP"].unique()  
    chart_data['period']=chart_data["ATA"].dt.year.map('{:.0f}'.format).values
    periods=pd.DataFrame(chart_data["period"].unique()).dropna().sort_values(by=0)
    
    #define layout
    st.header("Análisis de Escalas")


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
                default=["2021"] )


    sel1=np.array([(chart_data["CLASS"]==class_sel) | (class_sel=="ALL")])
    sel2=np.array([(chart_data["JOB_TYPE_NAME1"]==typemov_sel) | (typemov_sel=="ALL")])
    sel3=np.array([(chart_data["NAME"]==vessel_sel) | (vessel_sel=="ALL")])
    sel4=np.array([(chart_data["TO_LOCATION_CODE"]==dest_sel) | (dest_sel=="ALL")])
    sel5=np.array([(chart_data["BERTHING_SIDE"]==side_sel) | (side_sel=="ALL")])
    sel6=np.in1d(chart_data["period"],year_sel)
    seleccion=chart_data[(sel1 & sel2 & sel3 & sel4 & sel5 & sel6).T]

    
    #load berth geometry   
    gdf = gpd.read_file( RUTA + "Berths.geojson")
    
    #load berth position
    pos = gpd.read_file( RUTA + "Berths_pos.geojson")
    
    pos.columns=["code","pos"]
    pos["x"]=pos["pos"].x
    pos["y"]=pos["pos"].y
    
    
    #add berth position to data
    gdf = gdf.merge(pos, on="code", how="left")
  
    #calculate total portcalls per berth & add to data
    a=seleccion[["PORTCALL","TO_LOCATION_CODE"]].drop_duplicates().groupby("TO_LOCATION_CODE").size()
    a= pd.DataFrame(a)
    a.columns=["Count"]
    a.index.name="CODE"
    gdf=gdf.merge(pd.DataFrame(a), left_on="code", right_on="CODE", how="left")
    
    selected_col=["Count"]
    min_value = gdf[selected_col].min()
    max_value = gdf[selected_col].max()
    gdf=gdf.fillna(0)
    palette="autumn"
    n_colors=20
    colors = cm.get_palette(palette, n_colors)
    colors = [hex_to_rgb(c) for c in colors]
    gdf=gdf.sort_values(by='Count',axis=0,ascending=True)
    for i,ind in enumerate(gdf.index):
        index = int(i / (len(gdf) / len(colors)))
        if index >= len(colors):
            index = len(colors) - 1
        gdf.loc[ind, "R"] = colors[index][0]
        gdf.loc[ind, "G"] = colors[index][1]
        gdf.loc[ind, "B"] = colors[index][2]
    
    gdf["R"]=gdf["R"].values[::-1] #df.col2.values[::-1]
    gdf["G"]=gdf["G"].values[::-1] #df.col2.values[::-1]
    gdf["B"]=gdf["B"].values[::-1] #df.col2.values[::-1]

    initial_view_state = pdk.ViewState(
        latitude=41.35, longitude=2.15, zoom=12.2, max_zoom=16, pitch=70, bearing=260
    )
    color_exp = "[R, G, B]"
    
    gdf=gdf.fillna(value=0)

    #define layers
    
    geojson = pdk.Layer(
        "GeoJsonLayer",
        gdf,
        opacity=0.5,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        get_fill_color = [69,162,128,255],
        get_line_color=[128, 119, 27],
        get_line_width=1,
        line_width_min_pixels=1,
        elevation_scale=0,
        elevation_range=[0, 0],
        pickable=False,
    )
    
 
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=gdf,
        get_position=["x","y"],
        get_elevation="Count",
        elevation_scale=0.5,
        radius=25,
        get_fill_color=color_exp,
        get_line_color=[255, 255, 255],
        elevation_range=[0, 1000],
        pickable=True,
        extruded=True,
    )

    labels = pdk.Layer(
        "TextLayer",
        gdf,
        pickable=True,
        get_position=["x","y"],
        get_text="Count",
        get_size=3200,
        sizeUnits="meters",
        get_color=[100,100,100],
        get_angle=0,
        # Note that string constants in pydeck are explicitly passed as strings
        # This distinguishes them from columns in a data set
        getTextAnchor= "middle",
        get_alignment_baseline="center"
    )
    
    tooltip = {
        "html": "<b>Berth:</b> {name}<br><b>Value:</b> {"
        + "code"
        + "}<br><b>Portcalls:</b> {"
        + "Count"
        + "}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
    
    layers = [geojson,column_layer ]
    
    #create map object

    r = pdk.Deck(
    layers=layers,
    initial_view_state=initial_view_state,
    map_style="light",
    tooltip=tooltip,
    )
    
    with st.expander("Volumen de escalas"):
        st.metric(label="Muestras", value=a["Count"].sum())
        st.pydeck_chart(r)
    
    
    
    

   
