FROM python:3
ADD app.py /
ADD libs_mov.py /
ADD animation.py /
ADD multiapp.py /
ADD mov_kpis.py /
ADD portcall_kpis.py /

# install system dependencies for pyodbc

RUN apt-get update && apt-get install -y gcc unixodbc-dev
RUN pip install --upgrade pip
RUN pip install numpy
RUN pip install pandas
RUN pip install streamlit
RUN pip install pyodbc
RUN pip install datetime
RUN pip install python-dateutil --upgrade
RUN pip install requests
RUN pip install pydeck
RUN pip install geopandas
RUN pip install leafmap
RUN pip install matplotlib
RUN pip install ipywidgets
#RUN pip install os_sys --upgrade
#RUN pip install time

EXPOSE 8502

ENTRYPOINT ["streamlit", "run"]

CMD ["app.py"]