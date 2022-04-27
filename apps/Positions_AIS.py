import pandas as pd
import streamlit as st
import time as t
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



polygon = Polygon([ (2.158985137939453,41.30102358052782),
(2.168855667114258,41.296509788928795),
(2.1807861328125,41.299282583633726),
(2.188854217529297,41.30650419320872),
(2.1871376037597656,41.31456308095412),
(2.1793270111083984,41.323330019258144),
(2.185335159301758,41.322620972494164),
(2.19451904296875,41.31172646608111),
(2.193145751953125,41.301281502040915),
(2.182760238647461,41.29334994894031),
(2.166624069213867,41.290189955885644),
(2.155122756958008,41.297412572239566)])
        

P='\\\\apbprogs\\CLUSVTS.PORT.APB.ES\\replay_y_backup\\PosicionesAIS-2022'
data=pd.read_csv(P+'\\AIS Febrero 2022.txt', sep=';', parse_dates=[1,14], header=0, nrows=30000)

PC=data["ESCALA"]

filtro=data[data["ESCALA"] == PC]

filtro = filtro.rename(columns={'LATITUD':'latitude', 'LONGITUD':'longitude'})


filtro['point'] = filtro.apply(lambda row: Point(row['latitude'],row['longitude']),axis=1)

df_1 = filtro[filtro['point'].apply(polygon.contains)].copy()

st.write(df_1)

st.map(filtro[['latitude','longitude']])
