import pandas as pd
import streamlit as st
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px

# https://yeshwanthrams-midmarks3-first-sxmyrk.streamlit.app/

st.set_page_config(layout='wide')
sb = st.sidebar
sbex = lambda title : sb.expander(title)

dfdata = pd.read_excel('Data/marks.xlsx')

def clean():
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

clean_data = clean()

def get_compare_state():
    with sbex('Compare state'):
        compare_state = st.radio(
            'Compare State', ['pick', 'Slide'], label_visibility='collapsed')
    return compare_state

def get_graph_style():
    with sbex('Graph style'):
        graphy = st.radio(
            'Graphing', ['Line', 'Bar'], label_visibility='collapsed')

    if graphy == 'Line':
        return go.Line
    return go.Bar

def get_data_state():
    with sbex('Data state'):
        data_state = st.radio(
            'nothing', ['DataFrame', 'table'], label_visibility='collapsed')
    if data_state == 'DataFrame':
        return st.dataframe
    return st.table

compare_state = get_compare_state()
graphy = get_graph_style()
data_state = get_data_state()

def cchartf(figure: px._chart_types) -> px._chart_types:
    """
    Updates the layout and axes of a specified plotly chart.

    Arguments:
        figure (px.Figure): The plotly chart to be updated.

    Returns:
        px.Figure: The updated plotly chart.
    """
    figure.update_layout(
        legend=dict(
            y=1.1,
            orientation="h"
        )
    )
    # figure.update_layout(plot_bgcolor="#000000") figure.update_xaxes(showgrid=False) figure.update_yaxes(showgrid=False)
    return figure

def get_averages():
    rdata = clean_data
    c = rdata.columns.tolist()
    results = [element for element in c if element.endswith("_Avg")]
    mand = ['Roll.No', 'Name of the Student', 'Section']
    return rdata[mand+results]

def averages():
    c = st.columns(3)
    if compare_state == 'pick':
        c = st.columns([1,2])

    avgs = get_averages()

    subjects = avgs.columns.tolist()
    subjects = subjects[3:]
    subjects = [n.split('_')[0] for n in subjects]

    with c[0]:
        section_selection = st.selectbox(
            'section: ', list(set(avgs['Section'])))

    savg = avgs[avgs['Section'] == section_selection]['Roll.No'].tolist()
    
    students = []
    if compare_state == 'Slide':
        with c[1]:
            students.append(st.select_slider('First rollno', savg))
        with c[2]:
            students.append(st.select_slider('second rollno', savg))

    elif compare_state == 'pick':
        with c[1]:
            students = st.multiselect(
                'Students selection',
                savg,
                default=savg[0],
                max_selections=4,
                help='can select upto 4 students'
            )

    datastudents = []
    if students:
        for n in students:
            est = avgs[avgs['Roll.No'] == n].reset_index(drop=True)
            marks_list = est[est['Roll.No'] == n].loc[0,
                                                      "PDSM_Avg":"Biology for Engineers (BE)_Avg"].tolist()

            datastudents.append(graphy(name=n, x=subjects, y=marks_list))

    if students and datastudents:
        fig = go.Figure(data=datastudents)
        with st.expander('Graph', expanded=True):
            st.plotly_chart(cchartf(fig), use_container_width=True)
    
    with st.expander('Averages'):
        data_state(get_averages(), use_container_width=True)
        
a, cd = st.tabs(['Avgs', 'Data'])

with a:
    averages()
        
with cd:
    with st.expander('Data'):
        data_state(clean_data,use_container_width=True)
    