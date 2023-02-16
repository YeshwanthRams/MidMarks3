import pandas as pd
import streamlit as st 
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px

# https://yeshwanthrams-midmarks3-first-sxmyrk.streamlit.app/

st.set_page_config(layout='wide')
sb = st.sidebar

dfdata = pd.read_excel('Data/marks.xlsx')

def get_compare_state():
    with sb.expander('Compare state'):
        compare_state = st.radio('Compare State',['pick','Slide','Select'],label_visibility='collapsed') 
    return compare_state
    
compare_state = get_compare_state()

def get_graph_style():
    with sb.expander('Graph style'):
        graphy = st.radio('Graphing',['Line','Bar'],label_visibility='collapsed')

    if graphy == 'Line':
        graphy = go.Line
    if graphy == 'Bar':
        graphy = go.Bar

    return graphy

graphy = get_graph_style()

def clean():
    rdata = dfdata
    names_list = rdata.iloc[0].tolist()

    for i,value in enumerate(names_list):
        if type(value) == float:
            names_list[i] = str(value)


    c = ['D1','Q1','A1','TOT1','D2','Q2','A2','TOT2']
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
    rdata.drop(dfdata.index[0:4],inplace=True)
    rdata.drop(columns=['Sl.No','DBMS LAB','JAVA','ADE LAV','PDS LAB'],inplace=True)
    return rdata


clean_data = clean()

def get_averages():
    rdata = clean_data
    c = dfdata.columns.tolist()
    results = [element for element in c if element.endswith("_Avg")]
    mand = ['Roll.No','Name of the Student','Section']

    rdf = dfdata[mand+results]

    return rdf 

a,cd = st.tabs(['Avgs','Data'])

def cchartf(figure: px._chart_types) -> px._chart_types:
    """
    Updates the layout and axes of a specified plotly chart.
    
    Arguments:
        figure (px.Figure): The plotly chart to be updated.
    
    Returns:
        px.Figure: The updated plotly chart.
    """
    fig.update_layout(
            legend=dict(
                y = 1.1,
                orientation="h"
            )
        )
    # figure.update_layout(plot_bgcolor="#000000")
    # figure.update_xaxes(showgrid=False)
    # figure.update_yaxes(showgrid=False)

    return figure

with a:
    if compare_state == 'pick':
        c = st.columns([1,2])
    elif compare_state:
        c = st.columns(3)

    avgs = get_averages()

    subjects = avgs.columns.tolist()
    subjects = sr = subjects[3:]
    subjects = [n.split('_')[0] for n in subjects]

    with c[0]:
        section_selection = st.selectbox('section: ',list(set(avgs['Section'])))

    savg = avgs[avgs['Section'] == section_selection]

    students = []
    student2 = student1 = None

    avgslist = savg['Roll.No'].tolist()
    if compare_state == 'Slide':
        with c[1]:
            student1 = st.select_slider('First rollno',avgslist)
        with c[2]:
            student2 = st.select_slider('Second rollno',avgslist)
    elif compare_state == 'pick':
        with c[1]:
            students = st.multiselect(
                'Students selection',
                avgslist,
                default=avgslist[0],
                max_selections=4,
                help='select upto 4 students'
            )
    else:
        with c[1]:
            student1 = st.selectbox('First rollno',avgslist)
        with c[2]:
            student2 = st.selectbox('Second rollno',avgslist)


    
    datastudents = []
    if students: 
        for n in students:
            est = avgs[avgs['Roll.No'] == n].reset_index(drop=True)
            marks_list = est[est['Roll.No'] == n].loc[0,"PDSM_Avg":"Biology for Engineers (BE)_Avg"].tolist()

            datastudents.append(graphy(name=n,x=subjects,y=marks_list)) 


    if students and datastudents:
        fig = go.Figure(data=datastudents)
        fig.update_layout(
            legend=dict(
                y = 1.1,
                orientation="h"
            )
        )
        with st.expander('Graph',expanded = True):
            st.plotly_chart(cchartf(fig),use_container_width=True)


    elif student1 and student2:
        est1 = avgs[avgs['Roll.No'] == student1].reset_index(drop=True)
        est2 = avgs[avgs['Roll.No'] == student2].reset_index(drop=True)
        # st.write(avgs[avgs['Roll.No'] == student].reset_index(drop=True))
        # st.write(est[est['Roll.No'] == student].loc[0,"PDSM_Avg":"Biology for Engineers (BE)_Avg"].tolist())

        marks_list1 = est1[est1['Roll.No'] == student1].loc[0,"PDSM_Avg":"Biology for Engineers (BE)_Avg"].tolist()
        marks_list2 = est2[est2['Roll.No'] == student2].loc[0,"PDSM_Avg":"Biology for Engineers (BE)_Avg"].tolist()

        fig = go.Figure(data=[
            graphy(name=student1,x=subjects,y=marks_list1),
            graphy(name=student2,x=subjects,y=marks_list2)
        ])

        with st.expander('display',expanded = True):
            # stoggle = st.radio('Compare',['first','second'],horizontal=True,label_visibility='collapsed')
            st.plotly_chart(cchartf(fig),use_container_width=True)

with cd:
    with sb.expander('Data state'):
        data_state = st.radio('nothing',['DataFrame','table'],label_visibility='collapsed')
    with st.expander('Averages'):
        if data_state == 'DataFrame':
            st.dataframe(get_averages(),use_container_width=True)
        else:
            st.table(get_averages())
# st.write(dfdata)
