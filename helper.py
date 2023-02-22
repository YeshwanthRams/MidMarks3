import pandas as pd 
import streamlit as st 
import plotly.graph_objects as go
import plotly.express as px

def clean(dfdata: pd.DataFrame):
    rdata = dfdata
    names_list = rdata.iloc[0].tolist()

    for i, value in enumerate(names_list):
        if type(value) == float:
            names_list[i] = str(value)

    c = ['D1', 'Q1', 'A1', 'TOT1', 'D2', 'Q2', 'A2', 'TOT2']
    f = []

    s = None
    count = 0
    for n in names_list:
        if n != 'nan':
            if count != 0:
                f.append(s + '_' + 'Avg')
                count = 0
            s = n
            f.append(n)

        if n == 'nan':
            if s in f:
                f.remove(s)
            f.append(s + '_' + c[count])
            count += 1

    rdata.columns = f
    rdata.drop(dfdata.index[0:4], inplace=True)
    rdata.drop(columns=['Sl.No', 'DBMS LAB', 'JAVA',
               'ADE LAV', 'PDS LAB'], inplace=True)
    return rdata
